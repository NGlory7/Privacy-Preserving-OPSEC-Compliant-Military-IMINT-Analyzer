"""
Metadata Sanitizer (Anti-Tracking & OPSEC Engine)
Strips EXIF, GPS, camera serials, timestamps, and geolocation tags from uploaded imagery.
"""

from typing import Dict, Any, Tuple

import numpy as np
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS, GPSTAGS

GPS_IFD = 0x8825
EXIF_IFD = 0x8769

class MetadataSanitizer:
    """Detects and scrubs embedded metadata from imagery."""

    @staticmethod
    def extract_metadata(image: Image.Image) -> Dict[str, Any]:
        """
        Extracts human-readable EXIF and GPS tags from a PIL Image.
        Returns a dictionary detailing potential OPSEC leaks.
        """
        leaks = {
            "has_exif": False,
            "has_gps": False,
            "device_info": {},
            "gps_info": {},
            "timestamp": None,
            "raw_tags_count": 0
        }

        try:
            exif_data = image.getexif()
            if not exif_data:
                return leaks

            leaks["has_exif"] = True
            leaks["raw_tags_count"] = len(exif_data)

            # Base IFD + the Exif sub-IFD (where DateTimeOriginal, LensModel, serials live)
            tags = dict(exif_data.items())
            tags.update(exif_data.get_ifd(EXIF_IFD))
            leaks["raw_tags_count"] = len(tags)

            for tag_id, value in tags.items():
                tag_name = TAGS.get(tag_id, str(tag_id))
                if tag_name in ["Make", "Model", "Software", "LensModel", "BodySerialNumber", "CameraOwnerName"]:
                    leaks["device_info"][tag_name] = str(value)
                elif tag_name in ["DateTimeOriginal", "DateTime", "DateTimeDigitized"]:
                    if not leaks["timestamp"]:
                        leaks["timestamp"] = str(value)

            # GPSInfo in the base IFD is only an offset; the tags live in their own IFD
            gps = exif_data.get_ifd(GPS_IFD)
            if gps:
                leaks["has_gps"] = True
                leaks["gps_info"] = {GPSTAGS.get(k, str(k)): str(v) for k, v in gps.items()}

        except Exception as e:
            leaks["extraction_error"] = str(e)

        return leaks

    @staticmethod
    def sanitize(image: Image.Image) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Creates a clean copy of the image completely stripped of all metadata,
        ICC profiles, and EXIF segments.
        Returns: (sanitized_image, audit_log)
        """
        leaks = MetadataSanitizer.extract_metadata(image)

        # Apply the EXIF orientation first so the stripped image is not shown sideways,
        # then rebuild the image from raw pixels only (no EXIF, XMP, ICC, comments).
        oriented = ImageOps.exif_transpose(image)
        if oriented.mode not in ("RGB", "RGBA", "L"):
            oriented = oriented.convert("RGBA" if "A" in oriented.getbands() or "transparency" in oriented.info else "RGB")
        sanitized_img = Image.fromarray(np.array(oriented))

        audit_log = {
            "opsec_status": "CLEARED",
            "remaining_exif_tags": len(sanitized_img.getexif()),
            "remaining_info_keys": sorted(sanitized_img.info.keys()),
            "stripped_tags": leaks["raw_tags_count"],
            "gps_eliminated": leaks["has_gps"],
            "device_fingerprint_cleared": len(leaks["device_info"]) > 0,
            "original_leaks_found": leaks
        }

        return sanitized_img, audit_log
