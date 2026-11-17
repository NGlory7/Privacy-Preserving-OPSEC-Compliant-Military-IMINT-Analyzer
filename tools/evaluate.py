"""
Measures the analyzer on the labelled set built by tools/build_eval_set.py and writes
EVALUATION.md + eval/results.json.

    python tools/evaluate.py

What is measured
  1. Detection (image level): does OWLv2 find the expected category (weapon / vehicle /
     personnel) in images that contain it, and how often does it fire on negatives?
     Reported for several thresholds so the trade-off is visible.
  2. Fine-grained identification: top-1 / top-3 accuracy of CLIP over the catalog
     entries of that kind, using the best detection crop (or the whole image if the
     detector found nothing). Chance level is listed next to every number.
  3. Camouflage: top-1 / top-3 on personnel crops, zero-shot and few-shot
     (leave-one-out: every other eval image of the same pattern acts as reference).
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import torch  # noqa: E402
from PIL import Image  # noqa: E402

from src.opsec import network_guard  # noqa: E402
from src.vision import clip_classifier  # noqa: E402
from src.vision.detector import DEFAULT_THRESHOLDS, QUERIES, LocalMilitaryDetector  # noqa: E402
from src.vision.patch_extractor import PatchExtractor  # noqa: E402

EVAL = ROOT / "eval"
SWEEP = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40]
EXPECTED_CATEGORY = {"weapon": "weapon", "vehicle": "vehicle", "camouflage": "personnel"}


def pct(x: float) -> str:
    return f"{100 * x:.0f}%"


def main() -> None:
    rows = list(csv.DictReader((EVAL / "manifest.csv").open(encoding="utf-8")))
    rows = [r for r in rows if (EVAL / r["file"]).is_file()]
    if not rows:
        sys.exit("No eval images. Run tools/build_eval_set.py first.")
    print(f"[*] {len(rows)} images")

    det = LocalMilitaryDetector()
    per_image = []
    times = []

    with network_guard.offline() as net:
        for i, r in enumerate(rows, 1):
            img = Image.open(EVAL / r["file"]).convert("RGB")
            t = time.perf_counter()
            boxes, scores, labels = det.raw_scores(img)
            cat_of = [QUERIES[l].category for l in labels.tolist()]
            # best score per category (for the threshold sweep)
            best = defaultdict(float)
            best_box = {}
            for b, s, c in zip(boxes.tolist(), scores.tolist(), cat_of):
                if s > best[c]:
                    best[c], best_box[c] = s, b

            entry = {"label": r["label"], "task": r["task"], "file": r["file"], "best": dict(best)}
            want = EXPECTED_CATEGORY.get(r["task"])
            if want:
                if want in best_box and best[want] >= DEFAULT_THRESHOLDS[want]:
                    x1, y1, x2, y2 = best_box[want]
                    crop = PatchExtractor.crop_patch(img, (int(x1), int(y1), int(x2 - x1), int(y2 - y1)), None)
                    entry["crop_source"] = "detection"
                else:
                    crop, entry["crop_source"] = img, "full_image"
                entry["embedding"] = clip_classifier.encode_images([crop])[0].cpu()
            times.append(time.perf_counter() - t)
            per_image.append(entry)
            print(f"  {i}/{len(rows)} {r['label']}", end="\r", flush=True)

        # ---- 1. detection sweep ----
        detection = {}
        for task, want in EXPECTED_CATEGORY.items():
            pos = [e for e in per_image if e["task"] == task]
            if not pos:
                continue
            detection[task] = {f"{t:.2f}": sum(e["best"].get(want, 0) >= t for e in pos) / len(pos) for t in SWEEP}
            detection[task]["n"] = len(pos)
        neg = [e for e in per_image if e["task"] == "negative"]
        false_alarm = {}
        for cat in ("weapon", "vehicle"):
            if neg:
                false_alarm[cat] = {f"{t:.2f}": sum(e["best"].get(cat, 0) >= t for e in neg) / len(neg) for t in SWEEP}
                false_alarm[cat]["n"] = len(neg)

        # ---- 2/3. identification ----
        ident = {}
        for task, kind in (("weapon", "weapon"), ("vehicle", "vehicle"), ("camouflage", "camouflage")):
            items = [e for e in per_image if e["task"] == task and "embedding" in e]
            labels_present = sorted({e["label"] for e in items})
            if not items:
                continue
            n_classes = len([k for k in clip_classifier.PROMPTS[kind] if k != clip_classifier.UNKNOWN])
            res = {"n": len(items), "classes_in_eval": len(labels_present), "catalog_classes": n_classes,
                   "chance_top1": 1 / n_classes, "chance_top3": min(1, 3 / n_classes)}
            for mode in ("zero_shot", "few_shot_loo"):
                top1 = top3 = 0
                per_class = defaultdict(lambda: [0, 0])
                for j, e in enumerate(items):
                    ref = None
                    if mode == "few_shot_loo":
                        groups = defaultdict(list)
                        for k, o in enumerate(items):
                            if k != j:
                                groups[o["label"]].append(o["embedding"])
                        ids = [g for g in groups]
                        mat = torch.stack([torch.nn.functional.normalize(torch.stack(groups[g]).mean(0), dim=-1) for g in ids])
                        ref = (ids, mat)
                    out = clip_classifier.classify_embedding(
                        e["embedding"], kind, top_k=3,
                        use_references=(mode == "few_shot_loo"), exclude_reference=ref)
                    ranked = [o["id"] for o in out]
                    top1 += ranked[0] == e["label"]
                    top3 += e["label"] in ranked
                    per_class[e["label"]][0] += ranked[0] == e["label"]
                    per_class[e["label"]][1] += 1
                res[mode] = {"top1": top1 / len(items), "top3": top3 / len(items),
                             "per_class_top1": {k: f"{a}/{b}" for k, (a, b) in sorted(per_class.items())}}
            res["crops_from_detection"] = sum(e.get("crop_source") == "detection" for e in items) / len(items)
            ident[task] = res

    results = {
        "images": len(per_image),
        "by_label": {k: sum(1 for e in per_image if e["label"] == k) for k in sorted({e["label"] for e in per_image})},
        "detection_recall": detection,
        "false_alarm_on_negatives": false_alarm,
        "identification": ident,
        "seconds_per_image_median": round(statistics.median(times), 2),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "outbound_network_attempts": net["blocked_attempts"],
        "thresholds": DEFAULT_THRESHOLDS,
    }
    (EVAL / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_markdown(results)
    print("\n[+] EVALUATION.md and eval/results.json written")


def write_markdown(r: dict) -> None:
    L = ["# Evaluation", "",
         "Produced by `python tools/evaluate.py` on the Wikimedia Commons set built by",
         "`python tools/build_eval_set.py` (licences and sources in `eval/manifest.csv`).",
         "The set is small, so treat every number as a rough indication with wide error bars.", "",
         f"- Images: **{r['images']}** · device: `{r['device']}` · median time per image (detection + one CLIP crop): **{r['seconds_per_image_median']} s**",
         f"- Outbound network attempts during the run: **{r['outbound_network_attempts']}** (network guard active)", "",
         "## 1. Detection (image level)", "",
         "Share of images where OWLv2 finds the expected category at each score threshold.", "",
         "| Set | n | " + " | ".join(f"≥{t:.2f}" for t in SWEEP) + " |",
         "|---|---|" + "---|" * len(SWEEP)]
    for task, d in r["detection_recall"].items():
        L.append(f"| {task} → {EXPECTED_CATEGORY[task]} found | {d['n']} | " + " | ".join(pct(d[f'{t:.2f}']) for t in SWEEP) + " |")
    for cat, d in r["false_alarm_on_negatives"].items():
        L.append(f"| negatives → {cat} (false alarm) | {d['n']} | " + " | ".join(pct(d[f'{t:.2f}']) for t in SWEEP) + " |")
    L += ["", f"Default thresholds used by the app: `{r['thresholds']}`.", "",
          "## 2. Fine-grained identification", "",
          "Top-k accuracy over the catalog entries of that kind (chance level in brackets).",
          "*Few-shot* = the other eval photos of each class are used as reference images (leave-one-out),",
          "which is what you get by putting a few photos in `data/reference/<kind>/<id>/`.", "",
          "| Kind | n | classes | zero-shot top-1 | zero-shot top-3 | few-shot top-1 | few-shot top-3 | crop from detector |",
          "|---|---|---|---|---|---|---|---|"]
    for task, d in r["identification"].items():
        L.append(f"| {task} | {d['n']} | {d['classes_in_eval']}/{d['catalog_classes']} | "
                 f"{pct(d['zero_shot']['top1'])} ({pct(d['chance_top1'])}) | {pct(d['zero_shot']['top3'])} ({pct(d['chance_top3'])}) | "
                 f"{pct(d['few_shot_loo']['top1'])} | {pct(d['few_shot_loo']['top3'])} | {pct(d['crops_from_detection'])} |")
    L += ["", "### Per class (zero-shot top-1 / few-shot top-1)", ""]
    for task, d in r["identification"].items():
        zs, fs = d["zero_shot"]["per_class_top1"], d["few_shot_loo"]["per_class_top1"]
        L.append(f"**{task}:** " + " · ".join(f"`{k}` {zs[k]} / {fs[k]}" for k in zs))
        L.append("")
    missing = [k for k in ("weapon", "vehicle", "camouflage") if k not in r["identification"]]
    L += ["## What this does not measure", ""]
    if missing:
        L.append(f"- **Not measured yet: {', '.join(missing)}.** The eval set has no images for it; "
                 "run `python tools/build_eval_set.py` (Wikimedia Commons rate-limits it heavily, so it can take hours) "
                 "and re-run this script.")
    absent = [cid for kind in ("weapon", "vehicle", "gear", "camouflage") for cid in clip_classifier.PROMPTS[kind]
              if cid != clip_classifier.UNKNOWN and cid not in r["by_label"]]
    L += [f"- **Catalog classes without eval images** (no free photos found on Commons): {', '.join(f'`{a}`' for a in absent)}.",
          "- **Camouflage images without a detected person** (fabric swatches, uniforms on display) are classified on the "
          "whole image; see the *crop from detector* column.",
          "- **Hard negatives:** the negatives are everyday COCO scenes (people with bats, skis, rackets…); "
          "tractors, hunters or airsoft players were not tested.",
          "- **Personnel / helmet thresholds** are untuned starting values; only weapon and vehicle thresholds were checked against the sweep above.",
          "- **Box accuracy (IoU):** labels are image-level, not hand-drawn boxes.",
          "- **Face redaction recall:** the set has no face annotations. Always check the redacted image yourself.",
          "- **Attribution:** country ranking is a deterministic function of the identifications above and the",
          "  hand-set catalog weights; it is only as good as those inputs.", ""]
    (ROOT / "EVALUATION.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
