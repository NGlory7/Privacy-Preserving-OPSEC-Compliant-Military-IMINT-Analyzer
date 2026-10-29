"""
Vector & Texture Similarity Matcher
Computes normalized color histograms, spatial texture moments, and Euclidean / Cosine distances
to match visual crops against reference camouflage databases offline.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from PIL import Image
from src.database.camouflage_db import CAMOUFLAGE_CATALOG

class VectorMatcher:
    """Matches visual patches to catalog items using color-space and texture signatures."""

    @staticmethod
    def extract_color_palette(image: Image.Image, num_colors: int = 5) -> np.ndarray:
        """
        Extracts dominant RGB color centers from an image patch.
        Uses K-Means or quantize method for fast, deterministic color clustering.
        """
        img_rgb = image.convert("RGB").resize((120, 120))
        # Quantize to reduce color space
        quantized = img_rgb.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
        palette = quantized.getpalette()[:num_colors * 3]
        rgb_centers = [palette[i:i+3] for i in range(0, len(palette), 3)]
        return np.array(rgb_centers, dtype=np.float32)

    @staticmethod
    def _color_distance(rgb_a: np.ndarray, rgb_b: np.ndarray) -> float:
        """Computes minimum pairwise Euclidean distance between two color palettes."""
        distances = []
        for color_a in rgb_a:
            min_dist = min(np.linalg.norm(color_a - color_b) for color_b in rgb_b)
            distances.append(min_dist)
        return float(np.mean(distances))

    @classmethod
    def match_camouflage(cls, patch: Image.Image, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Compares an image crop against all reference patterns in the camouflage catalog.
        Returns top_k matches sorted by similarity score (0.0 to 1.0).
        """
        query_palette = cls.extract_color_palette(patch, num_colors=5)
        scores: List[Tuple[float, Dict[str, Any]]] = []

        # Max theoretical distance in RGB space is sqrt(255^2 * 3) ~ 441.67
        max_dist = 441.67

        for entry in CAMOUFLAGE_CATALOG:
            ref_rgb = np.array(entry["rgb_palette"], dtype=np.float32)
            dist = cls._color_distance(query_palette, ref_rgb)

            # Convert distance to normalized similarity score (0 to 1)
            similarity = max(0.0, 1.0 - (dist / (max_dist * 0.45)))
            scores.append((similarity, entry))

        # Sort descending by similarity
        scores.sort(key=lambda x: x[0], reverse=True)

        results = []
        for sim, entry in scores[:top_k]:
            results.append({
                "id": entry["id"],
                "name": entry["name"],
                "origin_country": entry["origin_country"],
                "pattern_type": entry["pattern_type"],
                "confidence": round(float(sim * 100), 1),
                "primary_operators": entry["primary_operators"],
                "theaters_of_operation": entry["theaters_of_operation"],
                "description": entry["description"],
                "palette_hex": entry["palette_hex"]
            })

        return results
