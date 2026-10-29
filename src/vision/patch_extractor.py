"""
Patch Extractor & Texture Normalizer
Extracts, centers, and normalizes candidate fabric or equipment swatches from images.
"""

from typing import List, Tuple
import numpy as np
from PIL import Image

class PatchExtractor:
    """Isolates and standardizes regions of interest (ROI) for classification."""

    @staticmethod
    def crop_patch(image: Image.Image, box: Tuple[int, int, int, int], target_size: Tuple[int, int] = (256, 256)) -> Image.Image:
        """
        Crops (x, y, w, h) bounding box from image and resizes with anti-aliasing.
        """
        x, y, w, h = box
        img_w, img_h = image.size

        # Clamp coordinates to image boundaries
        x1 = max(0, min(x, img_w - 1))
        y1 = max(0, min(y, img_h - 1))
        x2 = max(x1 + 1, min(x + w, img_w))
        y2 = max(y1 + 1, min(y + h, img_h))

        crop = image.crop((x1, y1, x2, y2))
        return crop.resize(target_size, Image.Resampling.LANCZOS)

    @staticmethod
    def auto_sample_center(image: Image.Image, ratio: float = 0.4) -> Image.Image:
        """
        Extracts a clean central patch from the image if explicit bounding boxes are absent.
        """
        w, h = image.size
        cw, ch = int(w * ratio), int(h * ratio)
        x1 = (w - cw) // 2
        y1 = (h - ch) // 2
        return image.crop((x1, y1, x1 + cw, y1 + ch))
