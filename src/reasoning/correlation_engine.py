"""
Attribution engine.

Combines the identifications that the models actually produced (camouflage, weapon,
vehicle, helmet) into a ranking of candidate operator countries.

How it works, plainly:
  score(country) = Σ  kind_weight × model_probability × operator_weight
over every identification above ``min_probability``. ``operator_weight`` values are
hand-assigned in the catalogs (they are expert priors, not learned). The output is a
*relative evidence share*, not a calibrated probability, and the engine reports
"inconclusive" when there is too little evidence or no clear leader.
Nothing is inferred from defaults: if the models saw no weapon, no weapon is used.
"""

from collections import defaultdict
from typing import Any, Dict, List, Optional

from src.database.camouflage_db import CamouflageDatabase
from src.database.military_hardware_db import MilitaryHardwareDatabase

# How much one identification of each kind counts relative to the others.
KIND_WEIGHTS = {"vehicle": 2.0, "camouflage": 1.5, "weapon": 1.4, "gear": 1.1}


def _operators(kind: str, item_id: str) -> tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    if kind == "camouflage":
        entry = CamouflageDatabase.get_by_id(item_id)
        if not entry:
            return None, []
        return entry, [{"country": o["country"], "weight": o["weight"], "detail": o["branch"]}
                       for o in entry.get("primary_operators", [])]
    entry = MilitaryHardwareDatabase.find_hardware_by_id(item_id)
    if not entry:
        return None, []
    return entry, [{"country": u["country"], "weight": u["weight"], "detail": u.get("units", "")}
                   for u in entry.get("primary_users", [])]


class CorrelationEngine:
    @classmethod
    def correlate(
        cls,
        evidence: List[Dict[str, Any]],
        min_probability: float = 0.35,
        min_lead_ratio: float = 1.25,
    ) -> Dict[str, Any]:
        """
        evidence: [{"kind": "camouflage"|"weapon"|"vehicle"|"gear", "id": catalog_id,
                    "probability": 0-1, "source": "model"|"analyst"}]
        """
        nation_scores: Dict[str, float] = defaultdict(float)
        reasons: Dict[str, List[str]] = defaultdict(list)
        theaters: Dict[str, float] = defaultdict(float)
        used, ignored = [], []

        for ev in evidence:
            prob = float(ev.get("probability", 0))
            if prob < min_probability:
                ignored.append({**ev, "reason": f"probability {prob:.2f} < {min_probability}"})
                continue
            entry, ops = _operators(ev["kind"], ev["id"])
            if not entry:
                ignored.append({**ev, "reason": "unknown catalog id"})
                continue
            used.append({**ev, "name": entry["name"]})
            w = KIND_WEIGHTS[ev["kind"]] * prob
            for op in ops:
                nation_scores[op["country"]] += w * op["weight"]
                origin = "analyst override" if ev.get("source") == "analyst" else f"model p={prob:.2f}"
                reasons[op["country"]].append(f"{ev['kind']}: {entry['name']} — {op['detail']} ({origin})")
            for th in entry.get("theaters_of_operation", []):
                theaters[th] += w

        total = sum(nation_scores.values())
        ranked = []
        for country, raw in sorted(nation_scores.items(), key=lambda x: x[1], reverse=True):
            share = round(raw / total * 100, 1) if total else 0.0
            ranked.append({
                "country": country,
                "evidence_share_percentage": share,
                "probability_percentage": share,  # kept for older callers
                "raw_score": round(raw, 3),
                "supporting_evidence": reasons[country],
            })

        # The leader must outweigh the runner-up by a clear factor, otherwise we don't pick one
        lead_ratio = (ranked[0]["raw_score"] / ranked[1]["raw_score"]) if len(ranked) > 1 and ranked[1]["raw_score"] else float("inf")
        inconclusive = not used or lead_ratio < min_lead_ratio

        top = ranked[0] if ranked and not inconclusive else None
        return {
            "inconclusive": inconclusive,
            "inconclusive_reason": (
                "No identification passed the probability threshold." if not used
                else f"Leader outweighs the runner-up only {lead_ratio:.2f}x (needs {min_lead_ratio}x)." if inconclusive
                else None
            ),
            "top_candidate_nation": top["country"] if top else "Inconclusive",
            "top_confidence_percentage": top["evidence_share_percentage"] if top else 0.0,
            "all_ranked_nations": ranked[:5],
            "suspected_theaters": [t for t, _ in sorted(theaters.items(), key=lambda x: x[1], reverse=True)[:3]],
            "evidence_used": used,
            "evidence_ignored": ignored,
            "method": "weighted evidence share (hand-set catalog weights × model probabilities); not a calibrated probability",
        }
