"""
Tactical Visualizer & HUD Overlay Utility
Draws tactical bounding boxes, targeting crosshairs, OPSEC redaction tags,
and color palette swatches over imagery.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class TacticalVisualizer:
    """Renders military HUD overlays and detection bounding boxes."""

    # Tactical color schemes
    COLOR_CAMO = (46, 204, 113)      # Emerald Green
    COLOR_WEAPON = (231, 76, 60)     # Alert Red
    COLOR_VEHICLE = (241, 196, 15)   # Amber Yellow
    COLOR_GEAR = (52, 152, 219)      # Tactical Cyan
    COLOR_OPSEC = (155, 89, 182)     # Purple / Redacted

    @classmethod
    def draw_detections(cls, image: Image.Image, detections: List[Dict[str, Any]]) -> Image.Image:
        """
        Draws tactical military-style corner brackets and badges on detected entities.
        """
        overlay = image.copy().convert("RGB")
        draw = ImageDraw.Draw(overlay)
        font = ImageFont.load_default()

        for det in detections:
            x, y, w, h = det["box"]
            cat = det.get("category", "")
            label = f"{det['label']} [{int(det['confidence'] * 100)}%]"

            if cat == "weapon":
                color = cls.COLOR_WEAPON
            elif cat == "vehicle":
                color = cls.COLOR_VEHICLE
            elif cat == "gear":
                color = cls.COLOR_GEAR
            else:
                color = cls.COLOR_CAMO

            # Tactical corner brackets (Length: 15px)
            corner_len = min(20, w // 4, h // 4)
            th = 3

            # Top-Left
            draw.line([(x, y), (x + corner_len, y)], fill=color, width=th)
            draw.line([(x, y), (x, y + corner_len)], fill=color, width=th)
            # Top-Right
            draw.line([(x + w, y), (x + w - corner_len, y)], fill=color, width=th)
            draw.line([(x + w, y), (x + w, y + corner_len)], fill=color, width=th)
            # Bottom-Left
            draw.line([(x, y + h), (x + corner_len, y + h)], fill=color, width=th)
            draw.line([(x, y + h), (x, y + h - corner_len)], fill=color, width=th)
            # Bottom-Right
            draw.line([(x + w, y + h), (x + w - corner_len, y + h)], fill=color, width=th)
            draw.line([(x + w, y + h), (x + w, y + h - corner_len)], fill=color, width=th)

            # Label banner
            bbox = font.getbbox(label)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.rectangle([(x, y - text_h - 6), (x + text_w + 8, y)], fill=color)
            draw.text((x + 4, y - text_h - 4), label, fill=(10, 10, 10), font=font)

        return overlay

    @classmethod
    def render_palette_strip(cls, hex_colors: List[str], width: int = 300, height: int = 40) -> Image.Image:
        """
        Creates a visual horizontal strip of the camouflage color swatches.
        """
        if not hex_colors:
            return Image.new("RGB", (width, height), (30, 30, 30))

        strip = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(strip)
        slot_w = width / len(hex_colors)

        for i, hx in enumerate(hex_colors):
            x1 = int(i * slot_w)
            x2 = int((i + 1) * slot_w)
            # Convert hex to rgb
            h_clean = hx.lstrip("#")
            rgb = tuple(int(h_clean[j:j+2], 16) for j in (0, 2, 4))
            draw.rectangle([(x1, 0), (x2, height)], fill=rgb)

        return strip
