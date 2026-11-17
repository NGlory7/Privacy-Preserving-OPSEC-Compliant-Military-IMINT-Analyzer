"""
Local military object detector.

Uses OWLv2 (open-vocabulary detection, runs fully on this machine) with text queries
for personnel, small arms, vehicles and helmets. Every box comes from the model;
nothing is placed at fixed image positions. If nothing passes the threshold,
the detector returns zero detections and says so.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from PIL import Image

from src.vision.patch_extractor import PatchExtractor


@dataclass(frozen=True)
class Query:
    text: str
    class_name: str
    label: str
    category: str  # personnel | weapon | vehicle | gear


QUERIES: List[Query] = [
    Query("a photo of a soldier", "soldier", "Personnel", "personnel"),
    Query("a photo of a person", "soldier", "Personnel", "personnel"),
    Query("a photo of a rifle", "small_arms", "Rifle / carbine", "weapon"),
    Query("a photo of an assault rifle", "small_arms", "Rifle / carbine", "weapon"),
    Query("a photo of a machine gun", "machine_gun", "Machine gun", "weapon"),
    Query("a photo of a rocket-propelled grenade launcher", "rocket_launcher", "Rocket launcher", "weapon"),
    Query("a photo of a tank", "tank", "Tank", "vehicle"),
    Query("a photo of an armored personnel carrier", "armored_vehicle", "Armored vehicle", "vehicle"),
    Query("a photo of an armored fighting vehicle", "armored_vehicle", "Armored vehicle", "vehicle"),
    Query("a photo of a pickup truck", "pickup_truck", "Pickup truck", "vehicle"),
    Query("a photo of a military helmet", "helmet", "Helmet", "gear"),
]

# Per-category score thresholds; lower = more recall but more false alarms.
# All four were chosen from the threshold sweep in EVALUATION.md:
#   weapon 0.22 / vehicle 0.25: ~95 % recall, no false alarms on the negatives;
#   gear 0.25: 92 % recall (recall is flat from 0.20 to 0.30);
#   personnel 0.20: the highest value that still reaches the maximum recall on the camouflage set.
#   Personnel false alarms are not measured (the negative images contain people).
DEFAULT_THRESHOLDS: Dict[str, float] = {
    "personnel": 0.20,
    "weapon": 0.22,
    "vehicle": 0.25,
    "gear": 0.25,
}

CATEGORIES = ("personnel", "weapon", "vehicle", "gear")


class LocalMilitaryDetector:
    """Detects personnel, weapons, vehicles and helmets with OWLv2, locally."""

    def __init__(self, thresholds: Dict[str, float] | None = None, max_per_category: int = 8):
        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
        self.max_per_category = max_per_category

    def raw_scores(self, image: Image.Image):
        """Runs OWLv2 once. Returns (boxes[N,4] xyxy, scores[N], query_index[N]) above a low floor."""
        import torch

        from src.models import device, load_owl

        processor, model = load_owl()
        rgb = image.convert("RGB")
        img_w, img_h = rgb.size

        inputs = processor(text=[[q.text for q in QUERIES]], images=rgb, return_tensors="pt")
        inputs = {k: v.to(device()) for k, v in inputs.items()}
        inputs["pixel_values"] = inputs["pixel_values"].to(model.dtype)
        with torch.inference_mode():
            outputs = model(**inputs)

        # OWLv2 pads the image to a square (bottom/right), so boxes are scaled to the
        # padded side; they then line up with the original pixel coordinates.
        side = max(img_w, img_h)
        post = getattr(processor, "post_process_object_detection", None) or processor.post_process_grounded_object_detection
        result = post(outputs=outputs, threshold=0.05, target_sizes=torch.tensor([[side, side]]))[0]
        return result["boxes"].float().cpu(), result["scores"].float().cpu(), result["labels"].cpu()

    def analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        from torchvision.ops import nms

        rgb = image.convert("RGB")
        img_w, img_h = rgb.size
        boxes, scores, labels = self.raw_scores(rgb)

        detections: List[Dict[str, Any]] = []
        for category in CATEGORIES:
            idx = [
                i for i, lab in enumerate(labels.tolist())
                if QUERIES[lab].category == category and scores[i] >= self.thresholds[category]
            ]
            if not idx:
                continue
            cat_boxes, cat_scores = boxes[idx], scores[idx]
            keep = nms(cat_boxes, cat_scores, iou_threshold=0.5)[: self.max_per_category]
            for k in keep.tolist():
                x1, y1, x2, y2 = cat_boxes[k].tolist()
                x1, y1 = max(0.0, x1), max(0.0, y1)
                x2, y2 = min(float(img_w), x2), min(float(img_h), y2)
                if x2 - x1 < 4 or y2 - y1 < 4:
                    continue
                q = QUERIES[labels[idx[k]].item()]
                box = (int(x1), int(y1), int(x2 - x1), int(y2 - y1))
                n = sum(1 for d in detections if d["category"] == category) + 1
                detections.append({
                    "id": f"det_{category}_{n:02d}",
                    "class_name": q.class_name,
                    "label": q.label,
                    "query": q.text,
                    "confidence": round(float(cat_scores[k]), 3),
                    "box": box,
                    "crop": PatchExtractor.crop_patch(rgb, box, target_size=None),
                    "category": category,
                })

        detections.sort(key=lambda d: d["confidence"], reverse=True)
        return {
            "image_dimensions": {"width": img_w, "height": img_h},
            "detections_count": len(detections),
            "detections": detections,
            "model": "OWLv2 (google/owlv2-base-patch16-ensemble)",
            "thresholds": dict(self.thresholds),
        }
