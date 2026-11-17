"""
Face redactor.

Detects faces locally with OpenCV's YuNet DNN detector (models/face_detection_yunet_2023mar.onnx)
and falls back to the Haar cascade bundled with OpenCV if YuNet is not downloaded.
Detected faces are pixelated, blurred or blacked out before any other analysis runs.

Limitations: faces that are very small, heavily occluded (balaclavas, goggles) or seen
from behind may not be detected; check the redacted image before sharing it.
"""

from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:  # pragma: no cover
    cv2 = None
    OPENCV_AVAILABLE = False

from src.models import YUNET_PATH


class FaceRedactor:
    def __init__(self, mode: str = "pixelate", intensity: int = 15, score_threshold: float = 0.6, padding: float = 0.15):
        """
        mode: 'pixelate', 'blur' or 'censor_bar'
        padding: grow each face box by this fraction so hairline / chin are covered too
        """
        self.mode = mode
        self.intensity = max(5, intensity)
        self.padding = padding
        self.score_threshold = score_threshold
        self.backend = "none"
        self._yunet = None
        self._haar = None

        if not OPENCV_AVAILABLE:
            return
        if YUNET_PATH.is_file() and hasattr(cv2, "FaceDetectorYN"):
            # Load from memory: OpenCV cannot open file paths with non-ASCII characters on Windows
            buf = np.frombuffer(YUNET_PATH.read_bytes(), dtype=np.uint8)
            self._yunet = cv2.FaceDetectorYN.create("onnx", buf, np.empty(0, dtype=np.uint8),
                                                    (320, 320), score_threshold, 0.3, 5000)
            self.backend = "yunet"
        else:
            self._haar = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            self.backend = "haar"

    def detect_faces(self, image_np: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Returns (x, y, w, h) boxes, padded and clamped to the image."""
        if self.backend == "none":
            return []
        h, w = image_np.shape[:2]
        raw: List[Tuple[float, float, float, float]] = []
        if self.backend == "yunet":
            bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            # YuNet works best around 640 px; scale large images down and boxes back up
            scale = min(1.0, 1280 / max(h, w))
            small = cv2.resize(bgr, (int(w * scale), int(h * scale))) if scale < 1 else bgr
            self._yunet.setInputSize((small.shape[1], small.shape[0]))
            _, faces = self._yunet.detect(small)
            if faces is not None:
                raw = [tuple(f[:4] / scale) for f in faces]
        else:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            raw = [tuple(map(float, f)) for f in self._haar.detectMultiScale(gray, 1.1, 5, minSize=(24, 24))]

        boxes = []
        for x, y, bw, bh in raw:
            px, py = bw * self.padding, bh * self.padding
            x1, y1 = max(0, int(x - px)), max(0, int(y - py))
            x2, y2 = min(w, int(x + bw + px)), min(h, int(y + bh + py))
            if x2 > x1 and y2 > y1:
                boxes.append((x1, y1, x2 - x1, y2 - y1))
        return boxes

    def redact(self, pil_image: Image.Image, custom_boxes: List[Tuple[int, int, int, int]] = None) -> Tuple[Image.Image, Dict[str, Any]]:
        image_np = np.array(pil_image.convert("RGB"))
        boxes = custom_boxes if custom_boxes is not None else self.detect_faces(image_np)

        for (x, y, w, h) in boxes:
            roi = image_np[y:y + h, x:x + w]
            if roi.size == 0:
                continue
            if self.mode == "censor_bar":
                image_np[y:y + h, x:x + w] = [15, 15, 15]
            elif self.mode == "blur" and OPENCV_AVAILABLE:
                k = max(15, self.intensity * 2 + 1) | 1
                image_np[y:y + h, x:x + w] = cv2.GaussianBlur(roi, (k, k), 30)
            else:
                rh, rw = roi.shape[:2]
                small = Image.fromarray(roi).resize((max(1, rw // self.intensity), max(1, rh // self.intensity)), Image.Resampling.BILINEAR)
                image_np[y:y + h, x:x + w] = np.array(small.resize((rw, rh), Image.Resampling.NEAREST))

        return Image.fromarray(image_np), {
            "faces_detected": len(boxes),
            "redaction_mode": self.mode,
            "detector_backend": self.backend,
            "bounding_boxes": boxes,
        }
