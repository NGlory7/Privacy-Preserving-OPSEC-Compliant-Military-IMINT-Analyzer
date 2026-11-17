"""Model tests: skipped automatically when weights are not downloaded."""

import pytest
from PIL import Image, ImageDraw

from src.models import models_available

pytestmark = pytest.mark.skipif(not all(models_available().values()), reason="run tools/download_models.py first")


def test_blank_image_gives_no_detections_and_inconclusive():
    from src.pipeline import analyze

    result = analyze(Image.new("RGB", (640, 480), (128, 128, 128)))
    assert result["detection"]["detections_count"] == 0
    assert result["correlation"]["inconclusive"]
    assert result["network"]["outbound_attempts_blocked"] == 0


def test_boxes_depend_on_image_content():
    """The old detector returned the same fixed boxes for every image; this must not."""
    from src.vision.detector import LocalMilitaryDetector

    det = LocalMilitaryDetector(thresholds={"personnel": 0.05, "weapon": 0.05, "vehicle": 0.05, "gear": 0.05})
    a = Image.new("RGB", (640, 480), (200, 200, 200))
    ImageDraw.Draw(a).rectangle([40, 300, 260, 460], fill=(60, 70, 50))
    b = a.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    boxes_a = [d["box"] for d in det.analyze_image(a)["detections"]]
    boxes_b = [d["box"] for d in det.analyze_image(b)["detections"]]
    assert boxes_a != boxes_b or not boxes_a
