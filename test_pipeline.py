"""
Integration Test Suite for AegisIMINT
Verifies all modules (OPSEC, Vision, Database, Reasoning) end-to-end.
"""

import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.opsec.anonymizer import OPSECAnonymizer
from src.vision.detector import LocalMilitaryDetector
from src.database.vector_matcher import VectorMatcher
from src.reasoning.correlation_engine import CorrelationEngine
from src.reasoning.intelligence_reporter import IntelligenceReporter

def test_full_pipeline():
    print("[*] Starting AegisIMINT end-to-end verification...")

    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_images", "sample_emr_digital_flora.png")
    assert os.path.exists(sample_path), f"Sample image missing at {sample_path}"

    raw_image = Image.open(sample_path)
    print(f"[+] Loaded test image: {raw_image.size}, mode: {raw_image.mode}")

    # 1. Test OPSEC Anonymizer
    anonymizer = OPSECAnonymizer(redact_faces=True, redaction_mode="pixelate")
    clean_image, manifest = anonymizer.process(raw_image)
    assert clean_image is not None
    assert manifest["opsec_certified"] is True
    print("[+] OPSEC Anonymizer: PASSED (Certified clean)")

    # 2. Test Local Military Detector
    detector = LocalMilitaryDetector()
    detections = detector.analyze_image(clean_image)
    assert detections["detections_count"] > 0
    print(f"[+] Local Detector: PASSED (Found {detections['detections_count']} tactical regions)")

    # 3. Test Vector Matcher (Camouflage classification)
    camo_crop = detections["detections"][0]["crop"]
    matches = VectorMatcher.match_camouflage(camo_crop, top_k=3)
    assert len(matches) > 0
    top_match = matches[0]
    print(f"[+] Camouflage Matcher: PASSED (Top Match: {top_match['name']} with {top_match['confidence']}% confidence)")

    # 4. Test Joint Correlation Engine
    correlation = CorrelationEngine.correlate(
        camo_matches=matches,
        detected_weapon_id="wpn_ak74m",
        detected_vehicle_id="veh_btr82a",
        detected_gear_id="gear_6b47_helmet"
    )
    assert correlation["top_candidate_nation"] is not None
    assert correlation["top_confidence_percentage"] > 0
    print(f"[+] Correlation Engine: PASSED (Attributed Nation: {correlation['top_candidate_nation']} @ {correlation['top_confidence_percentage']}%)")

    # 5. Test Intelligence Reporter
    dossier = IntelligenceReporter.generate_dossier(
        opsec_manifest=manifest,
        camo_matches=matches,
        correlation_result=correlation,
        custom_notes="Automated test verification run."
    )
    assert "DEFENSIVE OSINT / IMINT ASSESSMENT REPORT" in dossier["markdown_report"]
    print(f"[+] Intelligence Reporter: PASSED (Generated Dossier {dossier['dossier_id']})")

    print("\n[SUCCESS] ALL MODULES VERIFIED AND OPERATIONAL!")

if __name__ == "__main__":
    test_full_pipeline()
