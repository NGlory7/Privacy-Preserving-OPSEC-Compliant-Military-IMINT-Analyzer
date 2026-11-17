"""
AegisIMINT command-line analysis.

    python cli_analyze.py path/to/image.jpg [--out output] [--weapon wpn_ak74m] [--vehicle veh_t72b3] ...

Writes the sanitized image, a detection overlay and a Markdown report to --out.
"""

import argparse
import json
import os
import sys

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import ModelsMissingError  # noqa: E402
from src.pipeline import analyze  # noqa: E402
from src.reasoning.intelligence_reporter import IntelligenceReporter  # noqa: E402
from src.utils.visualizer import TacticalVisualizer  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Offline military imagery analysis")
    ap.add_argument("image")
    ap.add_argument("--out", default="output")
    ap.add_argument("--no-face-redaction", action="store_true")
    ap.add_argument("--json", action="store_true", help="also write the full result as JSON")
    for kind in ("weapon", "vehicle", "gear", "camouflage"):
        ap.add_argument(f"--{kind}", help=f"analyst-identified {kind} catalog id (overrides the model)")
    args = ap.parse_args()

    if not os.path.exists(args.image):
        print(f"[!] Image not found: {args.image}")
        return 1
    os.makedirs(args.out, exist_ok=True)

    overrides = [{"kind": k, "id": getattr(args, k)} for k in ("weapon", "vehicle", "gear", "camouflage") if getattr(args, k)]
    try:
        result = analyze(Image.open(args.image), redact_faces=not args.no_face_redaction, analyst_overrides=overrides)
    except ModelsMissingError as exc:
        print(f"[!] {exc}")
        return 2

    det = result["detection"]
    man = result["opsec_manifest"]
    print(f"[1] Metadata: {man['metadata_sanitized']['stripped_tags']} tags removed, GPS present: {man['metadata_sanitized']['gps_eliminated']}")
    print(f"[2] Faces redacted: {man['biometric_sanitized']['faces_detected']} ({man['biometric_sanitized']['detector_backend']})")
    print(f"[3] Detections ({det['model']}): {det['detections_count']}")
    for d in det["detections"]:
        ident = d.get("identification")
        extra = f" → {ident[0]['name']} p={ident[0]['probability']:.2f}" if ident else ""
        print(f"    - {d['label']:<16} score {d['confidence']:.2f}  box {d['box']}{extra}")
    corr = result["correlation"]
    if corr["inconclusive"]:
        print(f"[4] Attribution: INCONCLUSIVE — {corr['inconclusive_reason']}")
    else:
        print(f"[4] Attribution (evidence share, not probability): {corr['top_candidate_nation']} {corr['top_confidence_percentage']}%")
    print(f"[5] Outbound network attempts blocked: {result['network']['outbound_attempts_blocked']} · time {result['timings']['total_s']} s")

    result["sanitized_image"].save(os.path.join(args.out, "sanitized_redacted.png"))
    TacticalVisualizer.draw_detections(result["sanitized_image"], det["detections"]).save(os.path.join(args.out, "detections_overlay.png"))
    dossier = IntelligenceReporter.generate_dossier(result)
    with open(os.path.join(args.out, f"{dossier['dossier_id']}.md"), "w", encoding="utf-8") as f:
        f.write(dossier["markdown_report"])
    if args.json:
        slim = {k: v for k, v in result.items() if k != "sanitized_image"}
        for d in slim["detection"]["detections"]:
            d.pop("crop", None)
        with open(os.path.join(args.out, "result.json"), "w", encoding="utf-8") as f:
            json.dump(slim, f, indent=2, default=str)
    print(f"[+] Outputs written to {args.out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
