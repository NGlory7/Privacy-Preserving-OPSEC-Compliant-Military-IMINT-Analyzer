"""
Fine-grained identification with CLIP, locally.

Two modes, combined when both are available:
  * zero-shot: compares the crop to text prompts written for each catalog entry;
  * few-shot:  compares the crop to reference photos you place under
               data/reference/<kind>/<catalog_id>/*.jpg (nearest class centroid).

Every class list also contains an "other / unknown" option, so the classifier can
abstain instead of forcing a catalog match on something it has never seen.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Sequence

from PIL import Image

from src.models import ROOT

REFERENCE_DIR = ROOT / "data" / "reference"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
UNKNOWN = "unknown"

# Prompt sets per catalog id. Several phrasings per class are averaged ("prompt ensembling").
PROMPTS: Dict[str, Dict[str, List[str]]] = {
    "weapon": {
        "wpn_ak74m": ["an AK-74M assault rifle with a black polymer stock", "a Kalashnikov AK-74 rifle"],
        "wpn_akm": ["an AKM assault rifle with wooden furniture", "a Kalashnikov AKM rifle with a wooden stock"],
        "wpn_rpg7": ["an RPG-7 rocket-propelled grenade launcher", "a soldier carrying an RPG-7 launcher"],
        "wpn_pkm": ["a PKM general-purpose machine gun", "a belt-fed PK machine gun"],
        "wpn_ak12": ["an AK-12 assault rifle with a Picatinny rail", "a modern Russian AK-12 rifle"],
        "wpn_m4a1": ["an M4 carbine", "an M4A1 carbine with a collapsible stock"],
        "wpn_hk416": ["a Heckler & Koch HK416 rifle", "an HK416 assault rifle"],
        "wpn_mpt76": ["an MPT-76 Turkish infantry rifle", "a Turkish MKE MPT-76 battle rifle"],
        "wpn_qbz95": ["a QBZ-95 bullpup rifle", "a Chinese QBZ-95 bullpup assault rifle"],
        UNKNOWN: ["some other firearm", "a weapon", "an object"],
    },
    "vehicle": {
        "veh_toyota_hilux": ["a Toyota Hilux pickup truck", "a technical pickup truck with a mounted machine gun"],
        "veh_btr82a": ["a BTR-82A eight-wheeled armored personnel carrier", "a Russian BTR-82 8x8 APC"],
        "veh_bmp2": ["a BMP-2 tracked infantry fighting vehicle", "a Soviet BMP-2 IFV"],
        "veh_bradley_m2a2": ["an M2 Bradley infantry fighting vehicle", "an American Bradley fighting vehicle"],
        "veh_kirpi": ["a BMC Kirpi MRAP armored vehicle", "a Turkish Kirpi mine-resistant vehicle"],
        "veh_t72b3": ["a T-72B3 main battle tank", "a Russian T-72 tank"],
        UNKNOWN: ["some other vehicle", "a car", "a truck", "another type of tank"],
    },
    "gear": {
        "gear_fast_helmet": ["an Ops-Core FAST high-cut ballistic helmet", "a high-cut helmet with rails and night vision mount"],
        "gear_6b47_helmet": ["a Russian 6B47 Ratnik helmet", "a Russian army helmet with a camouflage cover"],
        UNKNOWN: ["some other helmet", "a hat", "a head"],
    },
    "camouflage": {
        "camo_multicam": ["a soldier wearing MultiCam camouflage", "MultiCam OCP camouflage uniform"],
        "camo_emr": ["a soldier wearing Russian EMR digital flora camouflage", "Russian pixelated EMR camouflage uniform"],
        "camo_marpat_woodland": ["a soldier wearing MARPAT woodland digital camouflage", "US Marine Corps MARPAT woodland uniform"],
        "camo_flecktarn": ["a soldier wearing German Flecktarn camouflage", "Flecktarn spotted camouflage uniform"],
        "camo_cadpat_tw": ["a soldier wearing Canadian CADPAT camouflage", "CADPAT temperate woodland digital uniform"],
        "camo_m90": ["a soldier wearing Swedish M90 splinter camouflage", "M90 angular splinter camouflage uniform"],
        "camo_type07": ["a soldier wearing Chinese Type 07 digital camouflage", "PLA Type 07 camouflage uniform"],
        "camo_turkish_digital": ["a soldier wearing Turkish army digital camouflage", "Turkish Armed Forces pixel camouflage uniform"],
        "camo_atacs_fg": ["a soldier wearing A-TACS camouflage", "A-TACS FG camouflage uniform"],
        "camo_m81_woodland": ["a soldier wearing M81 woodland camouflage", "M81 BDU woodland camouflage uniform"],
        "camo_idf_olive": ["a soldier wearing a plain olive green uniform", "Israeli army olive drab uniform"],
        "camo_partizan_autumn": ["a soldier wearing Partizan leaf camouflage", "Russian SS-Leto Partizan camouflage suit"],
        "camo_black_standard_tactical": ["a person wearing an all-black tactical uniform", "black combat clothing"],
        "camo_east_africa_woodland": ["a fighter wearing mixed woodland camouflage", "mixed improvised woodland camouflage clothing"],
        UNKNOWN: ["a person in civilian clothes", "some other uniform", "a person"],
    },
}


def _features(out):
    """transformers <5 returns a tensor; >=5 returns an output object whose pooler_output is the projected embedding."""
    return out if hasattr(out, "float") else out.pooler_output


def _encode_text(prompts: Sequence[str]):
    import torch

    from src.models import device, load_clip

    processor, model = load_clip()
    tok = processor(text=list(prompts), return_tensors="pt", padding=True).to(device())
    with torch.inference_mode():
        emb = _features(model.get_text_features(**tok))
    return torch.nn.functional.normalize(emb.float(), dim=-1)


def encode_images(images: Sequence[Image.Image]):
    import torch

    from src.models import device, load_clip

    processor, model = load_clip()
    pix = processor(images=[im.convert("RGB") for im in images], return_tensors="pt")["pixel_values"]
    with torch.inference_mode():
        emb = _features(model.get_image_features(pixel_values=pix.to(device(), dtype=model.dtype)))
    return torch.nn.functional.normalize(emb.float(), dim=-1)


@lru_cache(maxsize=None)
def _text_bank(kind: str):
    """One averaged, normalised text embedding per class."""
    import torch

    ids = list(PROMPTS[kind].keys())
    vecs = []
    for cid in ids:
        e = _encode_text([f"a photo of {p}" for p in PROMPTS[kind][cid]]).mean(0)
        vecs.append(torch.nn.functional.normalize(e, dim=-1))
    return ids, torch.stack(vecs)


def reference_files(kind: str) -> Dict[str, List[Path]]:
    base = REFERENCE_DIR / kind
    out: Dict[str, List[Path]] = {}
    if base.is_dir():
        for d in sorted(p for p in base.iterdir() if p.is_dir()):
            files = [f for f in sorted(d.iterdir()) if f.suffix.lower() in IMAGE_EXTS]
            if files:
                out[d.name] = files
    return out


@lru_cache(maxsize=None)
def _reference_bank(kind: str):
    """Class centroids from reference photos (few-shot). Returns (ids, matrix) or (None, None)."""
    import torch

    refs = reference_files(kind)
    if not refs:
        return None, None
    ids, vecs = [], []
    for cid, files in refs.items():
        emb = encode_images([Image.open(f) for f in files]).mean(0)
        ids.append(cid)
        vecs.append(torch.nn.functional.normalize(emb, dim=-1))
    return ids, torch.stack(vecs)


def classify(crop: Image.Image, kind: str, top_k: int = 3, use_references: bool = True) -> List[Dict]:
    """
    Returns the top_k classes as [{"id", "probability"}], probabilities summing to 1
    over all classes including "unknown".
    """
    return classify_embedding(encode_images([crop])[0], kind, top_k, use_references)


def classify_embedding(img_emb, kind: str, top_k: int = 3, use_references: bool = True,
                       exclude_reference=None) -> List[Dict]:
    import torch

    ids, text = _text_bank(kind)
    text = text.to(img_emb.device)
    # CLIP's learned logit scale is ~100
    probs = torch.softmax(100.0 * img_emb @ text.T, dim=-1)

    if use_references:
        ref_ids, ref = (exclude_reference if exclude_reference is not None else _reference_bank(kind))
        if ref_ids:
            ref_logits = torch.full((len(ids),), -1e4, device=img_emb.device)
            sims = img_emb @ ref.to(img_emb.device).T
            for j, cid in enumerate(ref_ids):
                if cid in ids:
                    ref_logits[ids.index(cid)] = 100.0 * sims[j]
            # Unknown keeps its zero-shot score; reference classes get the mean of both views
            ref_probs = torch.softmax(ref_logits, dim=-1)
            unk = ids.index(UNKNOWN)
            ref_probs = ref_probs * (1 - probs[unk])
            ref_probs[unk] = probs[unk]
            probs = 0.5 * probs + 0.5 * ref_probs

    order = torch.argsort(probs, descending=True)[:top_k]
    return [{"id": ids[i], "probability": round(float(probs[i]), 4)} for i in order.tolist()]
