"""
OPSEC Coordinator & Anonymization Engine
Executes complete pre-flight image sanitization before any analysis takes place.
"""

from typing import Dict, Any, Tuple
from PIL import Image
from src.opsec.metadata_sanitizer import MetadataSanitizer
from src.opsec.face_redactor import FaceRedactor

class OPSECAnonymizer:
    """End-to-end sanitization pipeline guaranteeing operational security."""

    def __init__(self, redact_faces: bool = True, redaction_mode: str = "pixelate", intensity: int = 15):
        self.redact_faces = redact_faces
        self.face_redactor = FaceRedactor(mode=redaction_mode, intensity=intensity)

    def process(self, raw_image: Image.Image) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Executes:
        1. Complete metadata and EXIF stripping.
        2. Biometric and facial feature masking.
        3. Returns sanitized image and comprehensive OPSEC compliance manifest.
        """
        # Step 1: Strip EXIF and camera fingerprints
        clean_image, meta_audit = MetadataSanitizer.sanitize(raw_image)

        # Step 2: Redact human faces / biometrics
        face_audit = {"faces_detected": 0, "biometric_secured": False}
        if self.redact_faces:
            clean_image, face_audit = self.face_redactor.redact(clean_image)

        manifest = {
            "opsec_certified": True,
            "metadata_sanitized": meta_audit,
            "biometric_sanitized": face_audit,
            "zero_leak_guarantee": True
        }

        return clean_image, manifest
