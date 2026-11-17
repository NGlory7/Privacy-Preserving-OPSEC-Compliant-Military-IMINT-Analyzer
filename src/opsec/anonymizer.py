"""
Pre-flight sanitization: strip metadata, then redact faces, before any analysis runs.
"""

from typing import Any, Dict, Tuple

from PIL import Image

from src.opsec.face_redactor import FaceRedactor
from src.opsec.metadata_sanitizer import MetadataSanitizer


class OPSECAnonymizer:
    def __init__(self, redact_faces: bool = True, redaction_mode: str = "pixelate", intensity: int = 15):
        self.redact_faces = redact_faces
        self.face_redactor = FaceRedactor(mode=redaction_mode, intensity=intensity)

    def process(self, raw_image: Image.Image) -> Tuple[Image.Image, Dict[str, Any]]:
        clean_image, meta_audit = MetadataSanitizer.sanitize(raw_image)

        face_audit: Dict[str, Any] = {"faces_detected": 0, "detector_backend": "disabled"}
        if self.redact_faces:
            clean_image, face_audit = self.face_redactor.redact(clean_image)

        manifest = {
            # Verifiable facts, not certifications
            "metadata_removed": meta_audit["remaining_exif_tags"] == 0,
            "metadata_sanitized": meta_audit,
            "faces_redacted": self.redact_faces,
            "biometric_sanitized": face_audit,
        }
        return clean_image, manifest
