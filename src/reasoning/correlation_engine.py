"""
Joint Correlation & Probability Matrix Engine
Synthesizes detected camouflage patterns, small arms, combat vehicles, and gear
to statistically compute the most probable operator nations, military branches, and operational theaters.
"""

from typing import List, Dict, Any
from collections import defaultdict
from src.database.military_hardware_db import HARDWARE_CATALOG

class CorrelationEngine:
    """Computes cross-asset intelligence correlation matrix."""

    @classmethod
    def correlate(
        cls,
        camo_matches: List[Dict[str, Any]],
        detected_weapon_id: str = None,
        detected_vehicle_id: str = None,
        detected_gear_id: str = None
    ) -> Dict[str, Any]:
        """
        Calculates joint probability across all detected assets.
        Returns ranked candidate nations, unit types, and theaters of operation.
        """
        nation_scores = defaultdict(float)
        evidence_breakdown = defaultdict(list)
        theater_frequencies = defaultdict(float)

        # 1. Incorporate Camouflage Evidence
        top_camo = camo_matches[0] if camo_matches else None
        if top_camo:
            camo_conf = top_camo["confidence"] / 100.0
            for op in top_camo.get("primary_operators", []):
                country = op["country"]
                score_increment = op["weight"] * camo_conf * 1.5
                nation_scores[country] += score_increment
                evidence_breakdown[country].append(
                    f"Camouflage match: {top_camo['name']} ({op['branch']})"
                )

            for th in top_camo.get("theaters_of_operation", []):
                theater_frequencies[th] += 1.2

        # 2. Incorporate Weapon Evidence
        if detected_weapon_id:
            for wpn in HARDWARE_CATALOG["weapons"]:
                if wpn["id"] == detected_weapon_id:
                    for user in wpn["primary_users"]:
                        country = user["country"]
                        score_increment = user["weight"] * 1.4
                        nation_scores[country] += score_increment
                        evidence_breakdown[country].append(
                            f"Small arms correlation: {wpn['name']} ({user['units']})"
                        )
                    break

        # 3. Incorporate Vehicle Evidence
        if detected_vehicle_id:
            for veh in HARDWARE_CATALOG["vehicles"]:
                if veh["id"] == detected_vehicle_id:
                    for user in veh["primary_users"]:
                        country = user["country"]
                        score_increment = user["weight"] * 2.0  # Heavy armor is high-confidence discriminator
                        nation_scores[country] += score_increment
                        evidence_breakdown[country].append(
                            f"Combat vehicle match: {veh['name']} ({user['units']})"
                        )
                    break

        # 4. Incorporate Tactical Gear Evidence
        if detected_gear_id:
            for gear in HARDWARE_CATALOG["tactical_gear"]:
                if gear["id"] == detected_gear_id:
                    for user in gear["primary_users"]:
                        country = user["country"]
                        score_increment = user["weight"] * 1.1
                        nation_scores[country] += score_increment
                        evidence_breakdown[country].append(
                            f"Tactical gear alignment: {gear['name']} ({user['units']})"
                        )
                    break

        # Normalize Scores to Percentages
        total_score = sum(nation_scores.values()) or 1.0
        ranked_nations = []
        for country, raw_score in sorted(nation_scores.items(), key=lambda x: x[1], reverse=True):
            pct = round((raw_score / total_score) * 100, 1)
            ranked_nations.append({
                "country": country,
                "probability_percentage": pct,
                "raw_score": round(raw_score, 2),
                "supporting_evidence": evidence_breakdown[country]
            })

        # Rank Theaters
        ranked_theaters = sorted(theater_frequencies.items(), key=lambda x: x[1], reverse=True)
        theaters_list = [th[0] for th in ranked_theaters[:3]] or ["Global / Unspecified Deployment Theater"]

        top_candidate = ranked_nations[0] if ranked_nations else {
            "country": "Inconclusive / Mixed Paramilitary Signature",
            "probability_percentage": 0.0,
            "supporting_evidence": ["Insufficient correlation threshold reached"]
        }

        return {
            "top_candidate_nation": top_candidate["country"],
            "top_confidence_percentage": top_candidate["probability_percentage"],
            "all_ranked_nations": ranked_nations[:5],
            "suspected_theaters": theaters_list,
            "correlation_matrix_status": "COMPUTED_LOCALLY",
            "assets_evaluated": {
                "camouflage": top_camo["name"] if top_camo else "None",
                "weapon": detected_weapon_id or "Auto-inferred from visual silhouette",
                "vehicle": detected_vehicle_id or "Not detected in primary frame",
                "gear": detected_gear_id or "Standard tactical helmet"
            }
        }
