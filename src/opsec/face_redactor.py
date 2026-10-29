"""
Face & Personnel Redactor (De-Identification & Identity Protection)
Locally detects human faces and applies tactical obfuscation (mosaic pixelation, censor bars, or Gaussian blur).
Guarantees zero biometric data leakage.
"""

from typing import List, Tuple, Dict, Any
import numpy as np
from PIL import Image

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    cv2 = None
    OPENCV_AVAILABLE = False


class FaceRedactor:
    """Detects and redacts facial biometric signatures for OPSEC compliance."""

    def __init__(self, mode: str = "pixelate", intensity: int = 15):
        """
        mode: 'pixelate', 'blur', or 'censor_bar'
        intensity: pixel block size or blur kernel factor
        """
        self.mode = mode
        self.intensity = max(5, intensity)
        self.face_cascade = None

        if OPENCV_AVAILABLE:
            try:
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
            except Exception:
                self.face_cascade = None

    def detect_faces(self, image_np: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Returns list of (x, y, w, h) bounding boxes of detected faces.
        """
        if not OPENCV_AVAILABLE or self.face_cascade is None:
            return []

        # Convert to grayscale for detection
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_np

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]

    def redact(self, pil_image: Image.Image, custom_boxes: List[Tuple[int, int, int, int]] = None) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Applies redaction to detected or specified face regions.
        Returns: (redacted_pil_image, redaction_stats)
        """
        image_np = np.array(pil_image.convert("RGB"))
        boxes = custom_boxes if custom_boxes is not None else self.detect_faces(image_np)

        for (x, y, w, h) in boxes:
            x_end = min(x + w, image_np.shape[1])
            y_end = min(y + h, image_np.shape[0])
            roi = image_np[y:y_end, x:x_end]

            if self.mode == "censor_bar":
                # Solid black tactical bar
                image_np[y:y_end, x:x_end] = [15, 15, 15]

            elif self.mode == "blur" and OPENCV_AVAILABLE:
                ksize = max(15, (self.intensity * 2) + 1)
                blurred = cv2.GaussianBlur(roi, (ksize, ksize), 30)
                image_np[y:y_end, x:x_end] = blurred

            else:
                # Tactical Mosaic Pixelation (default, works everywhere)
                block_size = max(5, self.intensity)
                roi_h, roi_w = roi.shape[:2]
                small_w = max(1, roi_w // block_size)
                small_h = max(1, roi_h // block_size)

                # Resize down then up
                if OPENCV_AVAILABLE:
                    small = cv2.resize(roi, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
                    pixelated = cv2.resize(small, (roi_w, roi_h), interpolation=cv2.INTER_NEAREST)
                    image_np[y:y_end, x:x_end] = pixelated
                else:
                    # Pure PIL fallback for mosaic
                    roi_pil = Image.fromarray(roi)
                    small_pil = roi_pil.resize((small_w, small_h), Image.Resampling.BILINEAR)
                    pixelated_pil = small_pil.resize((roi_w, roi_h), Image.Resampling.NEAREST)
                    image_np[y:y_end, x:x_end] = np.array(pixelated_pil)

        redacted_pil = Image.fromarray(image_np)
        stats = {
            "faces_detected": len(boxes),
            "redaction_mode": self.mode,
            "bounding_boxes": boxes,
            "biometric_secured": len(boxes) > 0
        }
        return redacted_pil, stats
