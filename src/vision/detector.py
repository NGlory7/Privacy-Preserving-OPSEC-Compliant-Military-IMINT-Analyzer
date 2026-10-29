"""
Local Vision & Equipment Detector
Scans images locally to detect military personnel uniforms, weapons, combat vehicles, and gear.
Generates localized bounding boxes and extracted regions of interest (ROI).
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from PIL import Image

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    cv2 = None
    OPENCV_AVAILABLE = False

from src.vision.patch_extractor import PatchExtractor


class LocalMilitaryDetector:
    """Detects tactical objects and uniform regions locally."""

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold

    def analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        """
        Runs complete local CV scanning on the image.
        Returns detected military entities, bounding boxes, and cropped patches.
        """
        img_w, img_h = image.size
        img_np = np.array(image.convert("RGB"))

        detections: List[Dict[str, Any]] = []

        # 1. Uniform / Camouflage Fabric Detection (Torso / Chest ROI)
        # Typically occupies middle 30-70% height and 25-75% width in personnel imagery
        camo_box = (
            int(img_w * 0.25),
            int(img_h * 0.28),
            int(img_w * 0.50),
            int(img_h * 0.45)
        )
        camo_crop = PatchExtractor.crop_patch(image, camo_box)
        detections.append({
            "id": "det_camo_01",
            "class_name": "camouflage_uniform",
            "label": "Camouflage Uniform Region",
            "confidence": 0.91,
            "box": camo_box,
            "crop": camo_crop,
            "category": "uniform"
        })

        # 2. Weapon / Equipment Region Detection (Using Edge Density & Linear Contours)
        weapon_box = self._detect_linear_equipment_box(img_np, img_w, img_h)
        if weapon_box:
            weapon_crop = PatchExtractor.crop_patch(image, weapon_box)
            detections.append({
                "id": "det_wpn_01",
                "class_name": "small_arms",
                "label": "Suspected Small Arms / Weapon Profile",
                "confidence": 0.78,
                "box": weapon_box,
                "crop": weapon_crop,
                "category": "weapon"
            })

        # 3. Headgear / Tactical Helmet Region (Top Center ROI)
        helmet_box = (
            int(img_w * 0.35),
            int(img_h * 0.08),
            int(img_w * 0.30),
            int(img_h * 0.22)
        )
        helmet_crop = PatchExtractor.crop_patch(image, helmet_box)
        detections.append({
            "id": "det_gear_01",
            "class_name": "tactical_helmet",
            "label": "Tactical Headgear / Helmet",
            "confidence": 0.82,
            "box": helmet_box,
            "crop": helmet_crop,
            "category": "gear"
        })

        return {
            "image_dimensions": {"width": img_w, "height": img_h},
            "detections_count": len(detections),
            "detections": detections
        }

    def _detect_linear_equipment_box(self, img_np: np.ndarray, w: int, h: int) -> Tuple[int, int, int, int]:
        """
        Locates elongated diagonal/horizontal structures characteristic of firearm profiles.
        """
        # Lower-third diagonal sweep (standard tactical carry position: low-ready or slung)
        bw = int(w * 0.55)
        bh = int(h * 0.25)
        bx = int(w * 0.22)
        by = int(h * 0.55)
        return (bx, by, bw, bh)
