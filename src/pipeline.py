"""
End-to-end analysis pipeline shared by the CLI, the Streamlit app and the evaluator.

    sanitize (EXIF + faces)  →  detect (OWLv2)  →  identify crops (CLIP)  →  attribute

The whole run executes inside ``network_guard.offline()``: any outbound connection
attempt raises immediately and is counted in the result.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from PIL import Image

from src.database.camouflage_db import CamouflageDatabase
from src.database.military_hardware_db import MilitaryHardwareDatabase
from src.database.vector_matcher import VectorMatcher
from src.opsec import network_guard
from src.opsec.anonymizer import OPSECAnonymizer
from src.reasoning.correlation_engine import CorrelationEngine
from src.vision import clip_classifier
from src.vision.detector import LocalMilitaryDetector

# detection category → classifier kind
KIND_FOR_CATEGORY = {"weapon": "weapon", "vehicle": "vehicle", "gear": "gear"}


def _catalog_name(kind: str, item_id: str) -> str:
    if item_id == clip_classifier.UNKNOWN:
        return "Not in catalog / unknown"
    entry = CamouflageDatabase.get_by_id(item_id) if kind == "camouflage" else MilitaryHardwareDatabase.find_hardware_by_id(item_id)
    return entry["name"] if entry else item_id


def analyze(
    image: Image.Image,
    *,
    redact_faces: bool = True,
    redaction_mode: str = "pixelate",
    intensity: int = 15,
    thresholds: Optional[Dict[str, float]] = None,
    analyst_overrides: Optional[List[Dict[str, str]]] = None,
    max_people: int = 3,
) -> Dict[str, Any]:
    """
    analyst_overrides: [{"kind": "weapon"|"vehicle"|"gear"|"camouflage", "id": catalog_id}]
        Things the analyst identified by eye. They enter the attribution with
        probability 1.0 and are labelled "analyst" in the report.
    """
    timings: Dict[str, float] = {}
    t0 = time.perf_counter()

    with network_guard.offline() as net:
        # 1. OPSEC sanitization
        sanitized, manifest = OPSECAnonymizer(redact_faces, redaction_mode, intensity).process(image)
        timings["sanitize_s"] = time.perf_counter() - t0

        # 2. Detection
        t = time.perf_counter()
        detection = LocalMilitaryDetector(thresholds=thresholds).analyze_image(sanitized)
        timings["detect_s"] = time.perf_counter() - t

        # 3. Fine-grained identification of each equipment crop
        t = time.perf_counter()
        best: Dict[str, Dict[str, Any]] = {}
        for det in detection["detections"]:
            kind = KIND_FOR_CATEGORY.get(det["category"])
            if not kind:
                continue
            ranking = clip_classifier.classify(det["crop"], kind, top_k=3)
            det["identification"] = [{**r, "name": _catalog_name(kind, r["id"])} for r in ranking]
            top = ranking[0]
            if top["id"] != clip_classifier.UNKNOWN and top["probability"] > best.get(kind, {}).get("probability", 0):
                best[kind] = {"kind": kind, "id": top["id"], "probability": top["probability"],
                              "source": "model", "detection_id": det["id"]}

        # 4. Camouflage of the most confident personnel detections
        people = [d for d in detection["detections"] if d["category"] == "personnel"][:max_people]
        camo_matches: List[Dict[str, Any]] = []
        for det in people:
            matches = VectorMatcher.match_camouflage(det["crop"], top_k=3)
            det["identification"] = [{"id": m["id"], "name": m["name"], "probability": m["confidence"] / 100} for m in matches]
            if matches and (not camo_matches or matches[0]["confidence"] > camo_matches[0]["confidence"]):
                camo_matches = matches
                best["camouflage"] = {"kind": "camouflage", "id": matches[0]["id"],
                                      "probability": matches[0]["confidence"] / 100,
                                      "source": "model", "detection_id": det["id"]}
        timings["identify_s"] = time.perf_counter() - t

        # 5. Attribution
        evidence = list(best.values())
        for ov in analyst_overrides or []:
            evidence = [e for e in evidence if e["kind"] != ov["kind"]]
            evidence.append({"kind": ov["kind"], "id": ov["id"], "probability": 1.0, "source": "analyst"})
        correlation = CorrelationEngine.correlate(evidence)

    timings["total_s"] = time.perf_counter() - t0
    return {
        "sanitized_image": sanitized,
        "opsec_manifest": manifest,
        "detection": detection,
        "camo_matches": camo_matches,
        "evidence": evidence,
        "correlation": correlation,
        "network": {"outbound_attempts_blocked": net["blocked_attempts"], "hosts": net["hosts"]},
        "timings": {k: round(v, 2) for k, v in timings.items()},
    }
