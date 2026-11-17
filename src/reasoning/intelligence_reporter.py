"""
Markdown report generator. Reports only what the pipeline actually measured,
including the uncertainties, the evidence that was ignored and the limitations.
"""

import datetime
from typing import Any, Dict


def _p(x: float) -> str:
    return f"{x * 100:.0f}%"


class IntelligenceReporter:
    @classmethod
    def generate_dossier(cls, result: Dict[str, Any], custom_notes: str = "") -> Dict[str, Any]:
        now = datetime.datetime.now(datetime.timezone.utc)
        dossier_id = f"IMINT-{now.strftime('%Y%m%d-%H%M%S')}"
        man = result["opsec_manifest"]
        meta = man["metadata_sanitized"]
        faces = man["biometric_sanitized"]
        det = result["detection"]
        corr = result["correlation"]

        L = [
            "# Imagery Assessment Report",
            f"**ID:** `{dossier_id}` · **Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')} · **Tool:** AegisIMINT (local models)",
            "",
            "> Automated output from open-vocabulary detection (OWLv2) and image-text matching (CLIP).",
            "> Identifications can be wrong; verify every item visually before relying on it.",
            "",
            "## 1. Sanitization",
            f"- Metadata tags removed: **{meta['stripped_tags']}** · GPS present in original: **{meta['gps_eliminated']}** · "
            f"EXIF tags remaining: **{meta['remaining_exif_tags']}**",
            f"- Faces redacted: **{faces.get('faces_detected', 0)}** (detector: `{faces.get('detector_backend')}`). "
            "Small, occluded or turned-away faces may be missed.",
            f"- Outbound network attempts during analysis: **{result['network']['outbound_attempts_blocked']}** (blocked by network guard)",
            "",
            "## 2. Detections",
            f"Model: {det['model']} · thresholds: `{det['thresholds']}`",
            "",
        ]
        if not det["detections"]:
            L.append("_No object passed the detection thresholds._")
        else:
            L += ["| # | Category | Detector score | Box (x, y, w, h) | Best identification |", "|---|---|---|---|---|"]
            for i, d in enumerate(det["detections"], 1):
                ident = d.get("identification") or []
                best = "; ".join(f"{x['name']} ({_p(x['probability'])})" for x in ident[:2]) or "—"
                L.append(f"| {i} | {d['label']} | {d['confidence']:.2f} | {d['box']} | {best} |")

        L += ["", "## 3. Attribution", f"_Method: {corr['method']}._", ""]
        if corr["inconclusive"]:
            L.append(f"**Inconclusive.** {corr['inconclusive_reason']}")
        else:
            L.append(f"Leading candidate: **{corr['top_candidate_nation']}** with **{corr['top_confidence_percentage']}%** of the evidence weight.")
        if corr["all_ranked_nations"]:
            L += ["", "| Country | Evidence share | Based on |", "|---|---|---|"]
            for n in corr["all_ranked_nations"]:
                L.append(f"| {n['country']} | {n['evidence_share_percentage']}% | {'<br>'.join(n['supporting_evidence'])} |")
        if corr["evidence_ignored"]:
            L += ["", "Evidence below threshold (not used):"]
            L += [f"- {e['kind']} `{e['id']}`: {e['reason']}" for e in corr["evidence_ignored"]]
        if corr["suspected_theaters"]:
            L += ["", "Theaters associated with the used evidence: " + ", ".join(corr["suspected_theaters"])]

        if custom_notes:
            L += ["", "## 4. Analyst notes", f"> {custom_notes}"]

        L += ["", "---",
              "_For research, journalism and education. Equipment and uniforms circulate widely (captured, exported, "
              "imitated); a match is an indicator, never proof of who is in the picture._"]

        return {"dossier_id": dossier_id, "timestamp": now.isoformat(), "markdown_report": "\n".join(L),
                "structured_data": corr}
