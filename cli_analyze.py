"""
AegisIMINT CLI Analysis Utility
Command-line interface for running automated IMINT assessments on any image.
"""

import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.opsec.metadata_sanitizer import MetadataSanitizer
from src.opsec.face_redactor import FaceRedactor
from src.vision.detector import LocalMilitaryDetector
from src.database.vector_matcher import VectorMatcher
from src.reasoning.correlation_engine import CorrelationEngine
from src.reasoning.intelligence_reporter import IntelligenceReporter
from src.utils.visualizer import TacticalVisualizer

def analyze(image_path: str, output_dir: str = "output"):
    if not os.path.exists(image_path):
        print(f"[!] Error: Image not found at {image_path}")
        return

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("🎯 STARTING AIR-GAPPED AEGIS-IMINT ANALYSIS")
    print("=" * 60)

    raw_img = Image.open(image_path)
    w, h = raw_img.size
    print(f"\n[PHASE 0] Target Ingested: {os.path.basename(image_path)} ({w}x{h} px)")

    # 1. OPSEC Metadata Sanitization
    print("[PHASE 1] OPSEC Sanitization: Stripping EXIF/GPS tags...")
    clean_img, meta_audit = MetadataSanitizer.sanitize(raw_img)

    # 2. Biometric Redaction
    print("[PHASE 2] Biometrics: Detecting and redacting facial signatures...")
    redactor = FaceRedactor(mode="pixelate", intensity=15)
    redacted_img, face_audit = redactor.redact(clean_img)
    redacted_img.save(os.path.join(output_dir, "sanitized_redacted.png"))

    # 3. Local Detection
    print("[PHASE 3] Local Military Detection: Scanning uniform & equipment...")
    detector = LocalMilitaryDetector()
    detection_results = detector.analyze_image(redacted_img)
    hud_overlay = TacticalVisualizer.draw_detections(redacted_img, detection_results["detections"])
    hud_overlay.save(os.path.join(output_dir, "tactical_hud_overlay.png"))

    # 4. Camouflage / Texture Classification
    print("[PHASE 4] Camopedia Classification: Computing texture vectors...")
    camo_detection = next((d for d in detection_results["detections"] if d["category"] == "uniform"), None)
    camo_patch = camo_detection["crop"] if camo_detection else redacted_img
    camo_matches = VectorMatcher.match_camouflage(camo_patch, top_k=3)

    for i, m in enumerate(camo_matches, 1):
        print(f"   Rank #{i}: {m['name']} ({m['confidence']}% Match)")

    # 5. Joint Correlation
    print("[PHASE 5] Intelligence Matrix: Correlating cross-asset likelihood...")
    top_camo = camo_matches[0]["name"]
    inferred_wpn = "wpn_ak74m" if any(k in top_camo for k in ["EMR", "Partizan"]) else "wpn_m4a1"
    inferred_gear = "gear_6b47_helmet" if any(k in top_camo for k in ["EMR", "Partizan"]) else "gear_fast_helmet"

    correlation = CorrelationEngine.correlate(
        camo_matches=camo_matches,
        detected_weapon_id=inferred_wpn,
        detected_gear_id=inferred_gear
    )

    print(f"   🎯 Top Candidate: {correlation['top_candidate_nation']} ({correlation['top_confidence_percentage']}%)")
    print(f"   📍 Likely Theaters: {', '.join(correlation['suspected_theaters'])}")

    # 6. Dossier Generation
    print("[PHASE 6] Generating Standardized SITREP Dossier...")
    manifest = {
        "metadata_sanitized": meta_audit,
        "biometric_sanitized": face_audit
    }
    dossier = IntelligenceReporter.generate_dossier(
        opsec_manifest=manifest,
        camo_matches=camo_matches,
        correlation_result=correlation
    )

    report_path = os.path.join(output_dir, "imint_assessment_dossier.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(dossier["markdown_report"])

    print(f"\n[+] Dossier compiled: {report_path}")
    print("=" * 60)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "data", "sample_images", "sample_multicam.png")
    analyze(target)
