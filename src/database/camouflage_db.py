"""
Camouflage Knowledge Base (Camopedia Reference Catalog)
Standardized dataset of global military camouflage patterns, primary state and non-state operators,
associated branches, and typical theaters of deployment.
"""

from typing import List, Dict, Any, Optional

CAMOUFLAGE_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "camo_multicam",
        "name": "MultiCam / OCP (Operational Camouflage Pattern)",
        "origin_country": "United States",
        "pattern_type": "Disruptive / Multi-Terrain Gradient",
        "palette_hex": ["#544f3d", "#7c7558", "#9e9474", "#3b3628", "#7a6b4f"],
        "rgb_palette": [[84, 79, 61], [124, 117, 88], [158, 148, 116], [59, 54, 40], [122, 107, 79]],
        "primary_operators": [
            {"country": "United States", "branch": "US Army / US Air Force / SOCOM", "weight": 0.95},
            {"country": "United Kingdom", "branch": "British Army (MTP Variant)", "weight": 0.85},
            {"country": "Ukraine", "branch": "Armed Forces of Ukraine / SSO / GUR", "weight": 0.90},
            {"country": "Turkey", "branch": "Special Forces Command (ÖKK) / Police Special Ops", "weight": 0.80},
            {"country": "Australia", "branch": "Australian Defence Force (AMCU Variant)", "weight": 0.85},
            {"country": "Poland", "branch": "Wojska Specjalne (GROM / Formoza - Suez Variant)", "weight": 0.80},
            {"country": "Georgia", "branch": "Georgian Defence Forces", "weight": 0.70}
        ],
        "theaters_of_operation": [
            "Eastern Europe / Ukraine",
            "Middle East / Levant",
            "Central Asia / Afghanistan",
            "Global Expeditionary"
        ],
        "description": "7-color multi-environment camouflage pattern designed for Crye Precision. Adopted or adapted globally by elite and standard units."
    },
    {
        "id": "camo_emr",
        "name": "EMR (Edinaya Maskirovochnaya Rascvetka / Digital Flora / Tsifra)",
        "origin_country": "Russian Federation",
        "pattern_type": "Digital / Pixelated",
        "palette_hex": ["#2d3a27", "#1c2417", "#435835", "#8f8664", "#0f140e"],
        "rgb_palette": [[45, 58, 39], [28, 36, 23], [67, 88, 53], [143, 134, 100], [15, 20, 14]],
        "primary_operators": [
            {"country": "Russian Federation", "branch": "Ground Forces (SV) / VDV (Airborne) / Naval Infantry", "weight": 0.98},
            {"country": "Belarus", "branch": "Special Operations Forces / Armed Forces of Belarus", "weight": 0.85}
        ],
        "theaters_of_operation": [
            "Eastern Europe / Ukraine",
            "Caucasus",
            "Syria (Desert/Arid Variant)",
            "Central Asia"
        ],
        "description": "Standard-issue Russian military digital pixelated camouflage adopted under the Ratnik modernization program in 2008."
    },
    {
        "id": "camo_marpat_woodland",
        "name": "MARPAT Woodland (Marine Pattern)",
        "origin_country": "United States",
        "pattern_type": "Digital / Pixelated",
        "palette_hex": ["#1e291e", "#3a4a34", "#5b4a3a", "#101410"],
        "rgb_palette": [[30, 41, 30], [58, 74, 52], [91, 74, 58], [16, 20, 16]],
        "primary_operators": [
            {"country": "United States", "branch": "United States Marine Corps (USMC)", "weight": 0.98},
            {"country": "Georgia", "branch": "Special Operations Forces", "weight": 0.60}
        ],
        "theaters_of_operation": [
            "Temperate Woodland / Amphibious Theaters",
            "Asia-Pacific",
            "Global Deployment"
        ],
        "description": "Proprietary digital pixelated camouflage developed specifically for the US Marine Corps incorporating miniature USMC Eagle, Globe, and Anchor emblems."
    },
    {
        "id": "camo_flecktarn",
        "name": "Flecktarn (5-Farben-Tarndruck)",
        "origin_country": "Germany",
        "pattern_type": "Flecktarn / Dot Disruptive",
        "palette_hex": ["#313d29", "#556b2f", "#2b2319", "#8b7d6b", "#141713"],
        "rgb_palette": [[49, 61, 41], [85, 107, 47], [43, 35, 25], [139, 125, 107], [20, 23, 19]],
        "primary_operators": [
            {"country": "Germany", "branch": "Bundeswehr (Heer / Luftwaffe / Marine)", "weight": 0.98},
            {"country": "Ukraine", "branch": "Foreign Volunteer Units / Territorial Defense", "weight": 0.65}
        ],
        "theaters_of_operation": [
            "Central Europe",
            "Eastern Europe / Ukraine",
            "Baltic / Northern Europe"
        ],
        "description": "5-color dot pattern engineered to soften hard contour edges across European temperate woodland biomes."
    },
    {
        "id": "camo_cadpat_tw",
        "name": "CADPAT TW (Canadian Disruptive Pattern - Temperate Woodland)",
        "origin_country": "Canada",
        "pattern_type": "Digital / Pixelated",
        "palette_hex": ["#1b3219", "#3b582b", "#665239", "#0e150c"],
        "rgb_palette": [[27, 50, 25], [59, 88, 43], [102, 82, 57], [14, 21, 12]],
        "primary_operators": [
            {"country": "Canada", "branch": "Canadian Armed Forces (Army / Special Operations)", "weight": 0.99}
        ],
        "theaters_of_operation": [
            "North America / Arctic & Boreal",
            "Baltic (NATO Forward Presence)"
        ],
        "description": "Pioneering computer-generated pixelated pattern that inspired worldwide digital military camouflage adoption."
    },
    {
        "id": "camo_m90",
        "name": "M90 Splinter Pattern",
        "origin_country": "Sweden",
        "pattern_type": "Splinter / Geometric Hard Edge",
        "palette_hex": ["#1b3520", "#3d6d33", "#749b58", "#121914"],
        "rgb_palette": [[27, 53, 32], [61, 109, 51], [116, 155, 88], [18, 25, 20]],
        "primary_operators": [
            {"country": "Sweden", "branch": "Swedish Armed Forces (Försvarsmakten)", "weight": 0.98}
        ],
        "theaters_of_operation": [
            "Fennoscandia / Nordic Forests",
            "Baltic Sea Region"
        ],
        "description": "Distinctive geometric hard-angled splinter pattern tailored for the taiga and pine forests of Scandinavia."
    },
    {
        "id": "camo_type07",
        "name": "Type 07 Universal / Ocean / Arid",
        "origin_country": "China",
        "pattern_type": "Digital / Pixelated",
        "palette_hex": ["#4a5448", "#788575", "#2d342c", "#a2ab9f"],
        "rgb_palette": [[74, 84, 72], [120, 133, 117], [45, 52, 44], [162, 171, 159]],
        "primary_operators": [
            {"country": "China", "branch": "People's Liberation Army (PLA Army / PLAGF)", "weight": 0.99}
        ],
        "theaters_of_operation": [
            "East Asia / Indo-Pacific",
            "Sino-Indian Border (Himalayan / High Altitude)",
            "Taiwan Strait Littoral"
        ],
        "description": "Digital pixelated camouflage pattern standard with the PLA throughout the 2010s before the introduction of Xingkong."
    },
    {
        "id": "camo_turkish_digital",
        "name": "TSK Digital Nano Pattern",
        "origin_country": "Turkey",
        "pattern_type": "Digital / Pixelated",
        "palette_hex": ["#5a5c46", "#7d785a", "#9b9273", "#3a382c"],
        "rgb_palette": [[90, 92, 70], [125, 120, 90], [155, 146, 115], [58, 56, 44]],
        "primary_operators": [
            {"country": "Turkey", "branch": "Turkish Land Forces (Kara Kuvvetleri) / Gendarmerie (Jandarma)", "weight": 0.98},
            {"country": "Azerbaijan", "branch": "Azerbaijani Land Forces", "weight": 0.75},
            {"country": "Somalia", "branch": "Gorgor Special Forces (Trained by TSK)", "weight": 0.70}
        ],
        "theaters_of_operation": [
            "Anatolia / Southeastern Turkey",
            "Northern Syria (Euphrates Shield / Olive Branch / Peace Spring)",
            "Northern Iraq",
            "South Caucasus / Karabakh"
        ],
        "description": "Turkish Armed Forces micro-digital pattern engineered for Mediterranean, steppic, and arid/mountainous topography."
    },
    {
        "id": "camo_atacs_fg",
        "name": "A-TACS FG (Foliage Green) / AU (Arid)",
        "origin_country": "United States (Commercial / Non-state)",
        "pattern_type": "Organic Noise / Micro-Macro Gradient",
        "palette_hex": ["#3e4533", "#606b4e", "#8c8f73", "#23261d"],
        "rgb_palette": [[62, 69, 51], [96, 107, 78], [140, 143, 115], [35, 38, 29]],
        "primary_operators": [
            {"country": "Russian Federation", "branch": "Rosgvardia (SOBR / OMON) / FSB Alpha / PMCs (Wagner/Redut)", "weight": 0.90},
            {"country": "Middle Eastern Militias", "branch": "Non-State Armed Groups / PMCs", "weight": 0.65}
        ],
        "theaters_of_operation": [
            "Eastern Europe / Donbas",
            "Syria / Middle East",
            "Sahel / Sub-Saharan Africa"
        ],
        "description": "Organic mathematical noise pattern widely adopted by Russian specialized internal security forces and global private military companies."
    },
    {
        "id": "camo_m81_woodland",
        "name": "M81 BDU Woodland",
        "origin_country": "United States",
        "pattern_type": "Disruptive / Macro Organic",
        "palette_hex": ["#2e3d23", "#4e593c", "#5c4028", "#121411"],
        "rgb_palette": [[46, 61, 35], [78, 89, 60], [92, 64, 40], [18, 20, 17]],
        "primary_operators": [
            {"country": "United States", "branch": "Historical (Pre-2005) / MARSOC Raider Reg.", "weight": 0.60},
            {"country": "Kurdish Peshmerga / SDF", "branch": "Regional Armed Units", "weight": 0.85},
            {"country": "Various (Global)", "branch": "Latin American & African Militaries", "weight": 0.75}
        ],
        "theaters_of_operation": [
            "Global / Latin America / Middle East / Africa",
            "Historical Cold War & Gulf War"
        ],
        "description": "Iconic 4-color high-contrast woodland pattern; ubiquitous across paramilitary forces, insurgent groups, and developing militaries."
    },
    {
        "id": "camo_idf_olive",
        "name": "IDF Olive Drab / Tactical Ranger Green (Madei Bet)",
        "origin_country": "Israel",
        "pattern_type": "Solid Subdued / Low-Visibility Tactical Green",
        "palette_hex": ["#59564c", "#4c4a41", "#3b3933", "#6e6c64", "#171615"],
        "rgb_palette": [[89, 86, 76], [76, 74, 65], [59, 57, 51], [110, 108, 100], [23, 22, 21]],
        "primary_operators": [
            {"country": "Israel", "branch": "Israel Defense Forces (IDF) / Magav (Border Police) / Yamam / Sayeret Units", "weight": 0.99}
        ],
        "theaters_of_operation": [
            "Middle East / Levant",
            "West Bank / Central Command",
            "Gaza Perimeter / Southern Command",
            "Northern Border (Lebanon / Golan Heights)"
        ],
        "description": "Standard Israeli military issue combat uniform. Unlike most global armies using disruptive pixelated or multi-terrain camo, Israel utilizes solid tactical olive drab / ranger green across standard infantry, paratroopers, and special operations units."
    },
    {
        "id": "camo_partizan_autumn",
        "name": "Partizan-M / SS-Autumn (SS-Leto Osen)",
        "origin_country": "Russian Federation",
        "pattern_type": "Disruptive Oak Leaf / Dot Transitional",
        "palette_hex": ["#8d856e", "#675f4b", "#ada382", "#3e372a", "#11100d"],
        "rgb_palette": [[141, 133, 110], [103, 95, 75], [173, 163, 130], [62, 55, 42], [17, 16, 13]],
        "primary_operators": [
            {"country": "Russian Federation", "branch": "Spetsnaz GRU / VDV (Airborne) Reconnaissance / Naval Infantry Recon", "weight": 0.98},
            {"country": "Belarus", "branch": "Special Operations Forces", "weight": 0.75}
        ],
        "theaters_of_operation": [
            "Eastern Europe / Taiga / Ukraine",
            "Caucasus (Mountainous / Mixed Woodland)",
            "Central Asia"
        ],
        "description": "Russian military transitional oversuit pattern designed by SSO/SPOSN. Combines ochre-yellow autumn background with irregular olive-green spots; quintessential signature of Russian military scouts, VDV reconnaissance, and Spetsnaz GRU."
    },
    {
        "id": "camo_black_standard_tactical",
        "name": "All-Black Tactical / Insurgent Dress (Black Standard)",
        "origin_country": "Syria / Iraq / Levant (Non-State Formations)",
        "pattern_type": "Solid Monochrome / Tactical Jet Black",
        "palette_hex": ["#201e1c", "#0c0908", "#060505", "#020203", "#2d2a28"],
        "rgb_palette": [[32, 30, 28], [12, 9, 8], [6, 5, 5], [2, 2, 3], [45, 42, 40]],
        "primary_operators": [
            {"country": "Syria / Iraq (Non-State Armed Group)", "branch": "ISIS / Daesh / Islamic State Militant Formations", "weight": 0.99},
            {"country": "International / Special Police", "branch": "Counter-Terrorism Units (SWAT / Black Tactical)", "weight": 0.40}
        ],
        "theaters_of_operation": [
            "Levant / Syria & Iraq (Euphrates River Valley / Raqqa / Mosul)",
            "Middle East / Arid Urban Warzones",
            "Sahel / Sub-Saharan Africa (ISWAP / ISGS)"
        ],
        "description": "Characteristic all-black tactical attire, balaclavas, and tunics popularized by ISIS/Daesh for parade, execution, and elite shock-troop operations (Jaish al-Khilafa)."
    },
    {
        "id": "camo_east_africa_woodland",
        "name": "East African / Insurgent Mixed Woodland (Al-Shabaab)",
        "origin_country": "Somalia / East Africa / Horn of Africa",
        "pattern_type": "Disruptive Woodland / Brushstroke Variant",
        "palette_hex": ["#5c534a", "#3e3832", "#766b60", "#1a1416", "#bcad93"],
        "rgb_palette": [[92, 83, 74], [64, 56, 50], [118, 107, 96], [26, 20, 22], [188, 173, 147]],
        "primary_operators": [
            {"country": "Somalia / Horn of Africa (Al-Shabaab)", "branch": "Harakat al-Shabaab al-Mujahideen / Regional Militias", "weight": 0.99},
            {"country": "Sub-Saharan Africa", "branch": "Regional Insurgent Formations & Bush War Militias", "weight": 0.80}
        ],
        "theaters_of_operation": [
            "Horn of Africa / Somalia (Lower Shabelle / Jubaland / Puntland)",
            "East Africa / Kenya Borderlands (Boni Forest)",
            "Sahel / Sub-Saharan Savanna & Scrubland"
        ],
        "description": "High-contrast earthy woodland/brushstroke camouflage vest worn over mismatched civil/militant tunics, white calligraphic headbands, and dark balaclavas; hallmark of Al-Shabaab technical teams in southern Somalia."
    }
]


class CamouflageDatabase:
    """Access interface to global camouflage archives."""

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        return CAMOUFLAGE_CATALOG

    @classmethod
    def get_by_id(cls, camo_id: str) -> Optional[Dict[str, Any]]:
        for item in CAMOUFLAGE_CATALOG:
            if item["id"] == camo_id:
                return item
        return None

    @classmethod
    def search_by_country(cls, country_name: str) -> List[Dict[str, Any]]:
        results = []
        c_lower = country_name.lower()
        for item in CAMOUFLAGE_CATALOG:
            for op in item.get("primary_operators", []):
                if c_lower in op["country"].lower():
                    results.append(item)
                    break
        return results
