"""
Builds a small, labelled evaluation set from Wikimedia Commons.

    python tools/build_eval_set.py [--per-class 6]

Only freely licensed files are kept (public domain, CC0, CC BY, CC BY-SA).
Each file's licence, author and source page are written to eval/manifest.csv so
the set can be audited and attributed. Originals are downloaded (thumbnail rendering is heavily rate limited),
resized locally to 960 px and stored in eval/images/<label>/ (git-ignored; re-run this script to rebuild).

Labels come from the Commons category the file is filed under. Category filing is
done by volunteers and is occasionally wrong, so a few labels in the set may be noisy.
The script is deliberately slow (one API call every few seconds) to respect
Wikimedia's rate limits.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "eval"
API = "https://commons.wikimedia.org/w/api.php"
UA = "eval-set-builder/1.0 (open-source research tool; python-urllib)"
ALLOWED = re.compile(r"^(public domain|pd|cc0|cc[ -]by(-sa)?[ -]?\d)", re.I)

# label -> (task, catalog id, Commons categories to sample from)
CLASSES = {
    # ---- equipment: detector category + fine-grained id ----
    "wpn_ak74m": ("weapon", ["AK-74M"]),
    "wpn_akm": ("weapon", ["AKM"]),
    "wpn_rpg7": ("weapon", ["RPG-7"]),
    "wpn_pkm": ("weapon", ["PKM", "PK machine gun", "PKM machine gun", "PK machine guns"]),
    "wpn_ak12": ("weapon", ["AK-12"]),
    "wpn_m4a1": ("weapon", ["M4 carbine"]),
    "wpn_hk416": ("weapon", ["HK416", "Heckler & Koch HK416", "HK416 rifles"]),
    "wpn_mpt76": ("weapon", ["MPT-76"]),
    "wpn_qbz95": ("weapon", ["QBZ-95", "QBZ-95 assault rifle", "Type 95 assault rifle", "QBZ-95 rifles"]),
    "veh_btr82a": ("vehicle", ["BTR-82A"]),
    "veh_bmp2": ("vehicle", ["BMP-2"]),
    "veh_bradley_m2a2": ("vehicle", ["M2 Bradley", "M2A2 Bradley"]),
    "veh_kirpi": ("vehicle", ["BMC Kirpi", "Kirpi"]),
    "veh_t72b3": ("vehicle", ["T-72B3"]),
    "veh_toyota_hilux": ("vehicle", ["Technicals (vehicles)", "Technicals"]),
    # ---- camouflage on personnel ----
    "camo_multicam": ("camouflage", ["MultiCam", "Operational Camouflage Pattern"]),
    "camo_emr": ("camouflage", ["EMR camouflage pattern of the Russian military", "EMR camouflage"]),
    "camo_marpat_woodland": ("camouflage", ["MARPAT", "Marine Corps Combat Utility Uniform"]),
    "camo_flecktarn": ("camouflage", ["Flecktarn"]),
    "camo_cadpat_tw": ("camouflage", ["CADPAT", "CADPAT (TW)"]),
    "camo_m90": ("camouflage", ["M90 camouflage", "M90 (camouflage)"]),
    "camo_m81_woodland": ("camouflage", ["M81 Woodland", "Woodland (camouflage)"]),
    "camo_type07": ("camouflage", ["Type 07 camouflage", "Type 07 (camouflage)"]),
    # ---- negatives: no military content expected ----
}

# Negatives (no military content) from the COCO 2017 validation set: everyday scenes,
# several with people holding sticks, bats, rackets or skis — good false-alarm tests.
COCO_NEGATIVES = ["000000039769", "000000000139", "000000000285", "000000000632", "000000000724", "000000000776",
                  "000000000785", "000000000802", "000000000872", "000000000885", "000000001000", "000000001268"]
COCO_LICENSE = "CC BY family (Flickr images via COCO 2017; per-image licence in COCO annotations)"

_last_call = 0.0


def api(params: dict, min_interval: float = 3.0) -> dict:
    """Polite API call: spaced out, retried with backoff on rate limiting."""
    global _last_call
    params = {**params, "format": "json", "maxlag": "5"}
    url = f"{API}?{urllib.parse.urlencode(params)}"
    for attempt in range(6):
        wait = _last_call + min_interval - time.time()
        if wait > 0:
            time.sleep(wait)
        _last_call = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
            if body.startswith("You are making too many requests"):
                raise urllib.error.HTTPError(url, 429, "rate limited", {}, None)
            data = json.loads(body)
            if data.get("error", {}).get("code") == "maxlag":
                raise urllib.error.HTTPError(url, 503, "maxlag", {}, None)
            return data
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            backoff = 30 * (attempt + 1)
            print(f"    ! {exc}; waiting {backoff}s", flush=True)
            time.sleep(backoff)
    raise RuntimeError("Commons API unavailable")


def category_files(cat: str, limit: int = 200) -> list[str]:
    data = api({"action": "query", "list": "categorymembers", "cmtitle": f"Category:{cat}",
                "cmtype": "file", "cmlimit": str(limit)})
    return [m["title"] for m in data.get("query", {}).get("categorymembers", [])
            if m["title"].lower().endswith((".jpg", ".jpeg", ".png"))]


def file_info(titles: list[str]) -> dict:
    data = api({"action": "query", "titles": "|".join(titles), "prop": "imageinfo",
                "iiprop": "url|extmetadata|size|mime", "iiurlwidth": "960"})
    out = {}
    for page in data.get("query", {}).get("pages", {}).values():
        ii = (page.get("imageinfo") or [None])[0]
        if not ii:
            continue
        meta = ii.get("extmetadata", {})
        strip = lambda s: re.sub(r"<[^>]+>", "", s or "").strip()
        out[page["title"]] = {
            "url": ii.get("url"),
            "bytes": ii.get("size", 0),
            "page": ii.get("descriptionurl"),
            "license": strip(meta.get("LicenseShortName", {}).get("value")),
            "author": strip(meta.get("Artist", {}).get("value"))[:120],
        }
    return out


def download(url: str, path: Path) -> None:
    import io

    from PIL import Image

    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read()
            img = Image.open(io.BytesIO(raw)).convert("RGB")
            img.thumbnail((960, 960))
            img.save(path.with_suffix(".jpg"), quality=90)
            time.sleep(2.0)
            return
        except urllib.error.HTTPError as exc:
            if exc.code != 429:
                raise
            backoff = 60 * (attempt + 1)
            print(f"    ! image rate limited; waiting {backoff}s", flush=True)
            time.sleep(backoff)
    raise RuntimeError("image download kept failing")


def save(rows: list, path: Path) -> None:
    OUT.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["label", "task", "file", "title", "license", "author", "source"])
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-class", type=int, default=6)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--only", nargs="*", help="limit to these labels")
    args = ap.parse_args()
    random.seed(args.seed)

    manifest_path = OUT / "manifest.csv"
    rows = []
    if manifest_path.exists():
        with manifest_path.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    have = {(r["label"], r["title"]) for r in rows}

    if not args.only or "negative" in args.only:
        folder = OUT / "images" / "negative"
        folder.mkdir(parents=True, exist_ok=True)
        for cid in COCO_NEGATIVES:
            title = f"COCO val2017 {cid}"
            if ("negative", title) in have:
                continue
            url = f"http://images.cocodataset.org/val2017/{cid}.jpg"
            download(url, folder / f"coco_{cid}.jpg")
            rows.append({"label": "negative", "task": "negative", "file": f"images/negative/coco_{cid}.jpg", "title": title,
                         "license": COCO_LICENSE, "author": "COCO / Flickr contributors", "source": url})
            save(rows, manifest_path)
            print(f"    + coco_{cid}.jpg", flush=True)

    for label, (task, cats) in CLASSES.items():
        if args.only and label not in args.only:
            continue
        existing = sum(1 for r in rows if r["label"] == label)
        if existing >= args.per_class:
            print(f"[=] {label}: {existing} already")
            continue
        titles = []
        for cat in cats:
            try:
                titles += category_files(cat)
            except RuntimeError as exc:
                print(f"[!] {cat}: {exc}")
        titles = list(dict.fromkeys(titles))
        random.shuffle(titles)
        print(f"[*] {label}: {len(titles)} candidate files in {cats}", flush=True)

        added = existing
        for i in range(0, len(titles), 20):
            if added >= args.per_class:
                break
            infos = file_info(titles[i:i + 20])
            for title, info in infos.items():
                if added >= args.per_class:
                    break
                if (label, title) in have or not ALLOWED.match(info["license"] or ""):
                    continue
                if not info["url"] or info["bytes"] > 15_000_000:
                    continue
                folder = OUT / "images" / label
                folder.mkdir(parents=True, exist_ok=True)
                fname = re.sub(r"[^\w.-]+", "_", title.split(":", 1)[1].rsplit(".", 1)[0])[:90] + ".jpg"
                try:
                    download(info["url"], folder / fname)
                except Exception as exc:  # noqa: BLE001
                    print(f"    ! {title}: {exc}")
                    continue
                rows.append({"label": label, "task": task, "file": f"images/{label}/{fname}", "title": title,
                             "license": info["license"], "author": info["author"], "source": info["page"]})
                added += 1
                save(rows, manifest_path)  # resumable: progress survives interruptions
                print(f"    + {fname} ({info['license']})", flush=True)

    print(f"[+] {len(rows)} images listed in {manifest_path}")


if __name__ == "__main__":
    sys.exit(main())
