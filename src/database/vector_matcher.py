"""
Camouflage matcher.

Classifies a personnel crop against the camouflage catalog with CLIP
(zero-shot prompts + optional reference photos, see src/vision/clip_classifier.py).
The colour palette of the crop is still extracted, but only for display: colour
alone cannot tell MultiCam from M81 and is not used for the decision.
"""

from typing import Any, Dict, List

import numpy as np
from PIL import Image

from src.database.camouflage_db import CamouflageDatabase
from src.vision import clip_classifier


class VectorMatcher:
    """Matches personnel crops to catalog camouflage patterns."""

    @staticmethod
    def extract_color_palette(image: Image.Image, num_colors: int = 5) -> List[str]:
        """Dominant colours of the crop as hex strings (display only)."""
        img = image.convert("RGB").resize((120, 120))
        quantized = img.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
        palette = quantized.getpalette()[: num_colors * 3]
        rgb = np.array(palette, dtype=int).reshape(-1, 3)
        return ["#%02x%02x%02x" % tuple(c) for c in rgb]

    @classmethod
    def match_camouflage(cls, patch: Image.Image, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Returns up to top_k catalog matches with a probability in percent.
        "unknown" results are dropped; an empty list means the classifier abstained.
        """
        palette = cls.extract_color_palette(patch)
        results = []
        for r in clip_classifier.classify(patch, "camouflage", top_k=top_k + 1):
            if r["id"] == clip_classifier.UNKNOWN:
                continue
            entry = CamouflageDatabase.get_by_id(r["id"])
            if not entry:
                continue
            results.append({
                "id": entry["id"],
                "name": entry["name"],
                "origin_country": entry["origin_country"],
                "pattern_type": entry["pattern_type"],
                "confidence": round(r["probability"] * 100, 1),
                "primary_operators": entry["primary_operators"],
                "theaters_of_operation": entry["theaters_of_operation"],
                "description": entry["description"],
                "palette_hex": entry["palette_hex"],
                "crop_palette_hex": palette,
            })
        return results[:top_k]
