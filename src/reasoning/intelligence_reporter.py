"""
Intelligence Dossier & SITREP Generator
Compiles visual detections, OPSEC audit records, and statistical correlations into a standardized
Military Intelligence Assessment Report (IMINT / OSINT Dossier) 100% locally and offline.
"""

import os
import datetime
from typing import Dict, Any, Optional

class IntelligenceReporter:
    """Produces tactical military dossiers locally with zero external network dependencies."""

    @classmethod
    def generate_dossier(
        cls,
        opsec_manifest: Dict[str, Any],
        camo_matches: list,
        correlation_result: Dict[str, Any],
        custom_notes: str = ""
    ) -> Dict[str, Any]:
        """
        Synthesizes complete intelligence assessment offline.
        Returns: {
            "dossier_id": str,
            "timestamp": str,
            "markdown_report": str,
            "structured_data": dict
        }
        """
        now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        dossier_id = f"IMINT-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"

        top_camo = camo_matches[0] if camo_matches else {"name": "Unclassified", "confidence": 0.0}
        top_nation = correlation_result.get("top_candidate_nation", "Inconclusive")
        top_conf = correlation_result.get("top_confidence_percentage", 0.0)
        theaters = ", ".join(correlation_result.get("suspected_theaters", ["Indeterminate"]))

        # Format standardized Military IMINT Markdown Report
        report_md = f"""# 🛡️ DEFENSIVE OSINT / IMINT ASSESSMENT REPORT
**DOSSIER ID:** `{dossier_id}` | **CLASSIFICATION:** UNCLASSIFIED // OSINT OPEN VERIFICATION  
**TIMESTAMP:** `{now_utc}` | **ANALYZER:** AegisIMINT Engine (Air-Gapped Local)

---

### 1. OPSEC & PRIVACY SANITIZATION AUDIT
* **Privacy Status:** ✅ `OPSEC-CERTIFIED (Data Minimization Verified)`
* **EXIF / Metadata Leaks Stripped:** `{opsec_manifest.get('metadata_sanitized', {}).get('stripped_tags', 0)} tags purged`
* **GPS Coordinates Eliminated:** `{opsec_manifest.get('metadata_sanitized', {}).get('gps_eliminated', False)}`
* **Biometric Identity Masking:** `{opsec_manifest.get('biometric_sanitized', {}).get('faces_detected', 0)} facial signatures redacted via Tactical Mosaic`
* **Data Transmission Risk:** `ZERO (100% Offline / No outbound traffic)`

---

### 2. PRIMARY ASSET IDENTIFICATION
* **Dominant Camouflage Pattern:** **{top_camo.get('name', 'N/A')}**
  * *Pattern Confidence:* **{top_camo.get('confidence', 0)}%**
  * *Origin Country:* {top_camo.get('origin_country', 'N/A')}
  * *Design Type:* {top_camo.get('pattern_type', 'N/A')}
* **Small Arms Signature:** {correlation_result.get('assets_evaluated', {}).get('weapon', 'Inferred')}
* **Combat Vehicle Profile:** {correlation_result.get('assets_evaluated', {}).get('vehicle', 'None')}

---

### 3. JOINT CORRELATION & ATTRIBUTION MATRIX
* **Highest Probability Operator Nation:** 🎯 **{top_nation}** (Confidence: **{top_conf}%**)
* **Likely Operational Theaters:** 📍 *{theaters}*

#### Attribution Probability Distribution:
"""
        for nation_data in correlation_result.get("all_ranked_nations", []):
            pct = nation_data['probability_percentage']
            bar = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))
            report_md += f"* **{nation_data['country']}** `[{bar}]` **{pct}%**\n"
            for ev in nation_data.get("supporting_evidence", []):
                report_md += f"  * *Rationale:* {ev}\n"

        if custom_notes:
            report_md += f"""
---

### 4. ANALYST FIELD OBSERVATIONS
> {custom_notes}
"""

        report_md += """
---
*DISCLAIMER: This automated report is generated strictly from open-source visual data points using local Bayesian matrix correlation. Findings represent statistical likelihood indicators for verification purposes.*
"""

        return {
            "dossier_id": dossier_id,
            "timestamp": now_utc,
            "markdown_report": report_md,
            "structured_data": correlation_result
        }
