"""
Metadata Sanitizer (Anti-Tracking & OPSEC Engine)
Strips EXIF, GPS, camera serials, timestamps, and geolocation tags from uploaded imagery.
"""

import io
from typing import Dict, Any, Tuple
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

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

            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, str(tag_id))

                if tag_name in ["Make", "Model", "Software", "LensModel", "BodySerialNumber"]:
                    leaks["device_info"][tag_name] = str(value)

                elif tag_name in ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
                    if not leaks["timestamp"]:
                        leaks["timestamp"] = str(value)

                elif tag_name == "GPSInfo":
                    leaks["has_gps"] = True
                    gps_dict = {}
                    for gps_tag_id, gps_val in value.items():
                        sub_tag = GPSTAGS.get(gps_tag_id, str(gps_tag_id))
                        gps_dict[sub_tag] = str(gps_val)
                    leaks["gps_info"] = gps_dict

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

        # Create new image with pure pixel data only
        data = list(image.getdata())
        sanitized_img = Image.new(image.mode, image.size)
        sanitized_img.putdata(data)

        audit_log = {
            "opsec_status": "CLEARED",
            "stripped_tags": leaks["raw_tags_count"],
            "gps_eliminated": leaks["has_gps"],
            "device_fingerprint_cleared": len(leaks["device_info"]) > 0,
            "original_leaks_found": leaks
        }

        return sanitized_img, audit_log
