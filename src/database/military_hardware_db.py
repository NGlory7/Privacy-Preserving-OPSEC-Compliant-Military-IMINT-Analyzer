"""
Military Hardware Database (Oryx / SIPRI / Defense Inventory Reference)
Catalog of military small arms, armored fighting vehicles, main battle tanks,
tactical ballistic helmets, and body armor.
"""

from typing import List, Dict, Any, Optional

HARDWARE_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "weapons": [
        {
            "id": "wpn_ak74m",
            "name": "AK-74M / AK-74 Assault Rifle",
            "caliber": "5.45x39mm",
            "origin_country": "Russian Federation / USSR",
            "primary_users": [
                {"country": "Russian Federation", "units": "Ground Forces, VDV, Naval Infantry", "weight": 0.95},
                {"country": "Ukraine", "units": "Armed Forces of Ukraine, Territorial Defense", "weight": 0.90},
                {"country": "Kazakhstan", "units": "Armed Forces of Kazakhstan", "weight": 0.70},
                {"country": "Azerbaijan", "units": "Armed Forces of Azerbaijan (Khazri)", "weight": 0.75}
            ],
            "visual_cues": "Distinctive rectangular muzzle brake, polymer black/plum folding stock, 30-round curved bakelite/polymer magazine"
        },
        {
            "id": "wpn_akm",
            "name": "AKM / Type 56 Assault Rifle",
            "caliber": "7.62x39mm",
            "origin_country": "USSR / China / Global Production",
            "primary_users": [
                {"country": "Syria / Iraq (Non-State Armed Group)", "units": "ISIS / Daesh, Syrian Rebel Groups, Iraqi PMF", "weight": 0.99},
                {"country": "Somalia / Horn of Africa (Al-Shabaab)", "units": "Al-Shabaab, Somali Militias", "weight": 0.95},
                {"country": "Syria", "units": "Syrian Arab Army (SAA)", "weight": 0.85},
                {"country": "Middle East / Africa", "units": "Ubiquitous insurgent and irregular forces", "weight": 0.95}
            ],
            "visual_cues": "Classic wood handguard and buttstock, distinctive curved 7.62mm ribbed steel magazine, slant compensator"
        },
        {
            "id": "wpn_rpg7",
            "name": "RPG-7 Rocket-Propelled Grenade Launcher",
            "caliber": "40mm Launcher / 85mm PG-7V Warhead",
            "origin_country": "USSR / Global Production",
            "primary_users": [
                {"country": "Somalia / Horn of Africa (Al-Shabaab)", "units": "Al-Shabaab Anti-Armor Units, Technical Crews", "weight": 0.99},
                {"country": "Syria / Iraq (Non-State Armed Group)", "units": "Insurgents & Irregular forces", "weight": 0.90},
                {"country": "Global Insurgent / Irregular", "units": "Ubiquitous non-state anti-armor asset", "weight": 0.95}
            ],
            "visual_cues": "Conical PG-7V high-explosive warhead protruding from steel tube, wooden heat shield wrapper, dual pistol grips"
        },
        {
            "id": "wpn_pkm",
            "name": "PKM / Type 80 General-Purpose Machine Gun",
            "caliber": "7.62x54mmR",
            "origin_country": "USSR / Global Production",
            "primary_users": [
                {"country": "Somalia / Horn of Africa (Al-Shabaab)", "units": "Al-Shabaab Technical Support & Patrol Gunner", "weight": 0.98},
                {"country": "Russian Federation", "units": "Ground Forces, VDV, Naval Infantry", "weight": 0.90},
                {"country": "Middle East / Africa", "units": "Militia & Paramilitary forces", "weight": 0.90}
            ],
            "visual_cues": "Distinctive long fluted barrel with conical flash hider, top-folding carry handle, non-disintegrating belt feed box"
        },
        {
            "id": "wpn_ak12",
            "name": "AK-12 Assault Rifle (Ratnik Modernization)",
            "caliber": "5.45x39mm",
            "origin_country": "Russian Federation",
            "primary_users": [
                {"country": "Russian Federation", "units": "VDV, Spetsnaz, 1st Guards Tank Army, Naval Infantry", "weight": 0.98}
            ],
            "visual_cues": "Integrated Picatinny rails on receiver & handguard, telescoping stock, ergonomic pistol grip, birdcage flash hider"
        },
        {
            "id": "wpn_m4a1",
            "name": "M4A1 Carbine / SOPMOD",
            "caliber": "5.56x45mm NATO",
            "origin_country": "United States",
            "primary_users": [
                {"country": "United States", "units": "US Army, USMC, SOCOM, Navy SEALs", "weight": 0.98},
                {"country": "Ukraine", "units": "Foreign Legion, GUR, SSO (Western Aid)", "weight": 0.85},
                {"country": "Israel", "units": "IDF Infantry & Special Units", "weight": 0.80},
                {"country": "Turkey", "units": "Turkish Police Special Operations (PÖH)", "weight": 0.70}
            ],
            "visual_cues": "14.5 inch barrel with step for M203, flat-top receiver with optic rail, collapsible 6-position buttstock, birdcage flash hider"
        },
        {
            "id": "wpn_hk416",
            "name": "Heckler & Koch HK416",
            "caliber": "5.56x45mm NATO",
            "origin_country": "Germany",
            "primary_users": [
                {"country": "France", "units": "French Army (HK416F - Standard Issue)", "weight": 0.99},
                {"country": "Germany", "units": "KSK / Special Forces (G95)", "weight": 0.90},
                {"country": "United States", "units": "USMC (as M27 IAR), JSOC (CAG/DEVGRU)", "weight": 0.85},
                {"country": "Norway", "units": "Norwegian Armed Forces (Standard)", "weight": 0.95},
                {"country": "Turkey", "units": "SAT / SAS Naval Special Warfare Command", "weight": 0.80}
            ],
            "visual_cues": "Short-stroke gas piston system profile, proprietary free-floating quad-rail handguard, enlarged trigger guard"
        },
        {
            "id": "wpn_mpt76",
            "name": "MKE MPT-76 / MPT-55 (National Infantry Rifle)",
            "caliber": "7.62x51mm / 5.56x45mm",
            "origin_country": "Turkey",
            "primary_users": [
                {"country": "Turkey", "units": "Turkish Land Forces, Commando Brigades, Jandarma", "weight": 0.99},
                {"country": "Azerbaijan", "units": "Special Forces", "weight": 0.75},
                {"country": "Somalia", "units": "Gorgor Brigade", "weight": 0.80}
            ],
            "visual_cues": "Gas-piston AR-hybrid upper with distinctive angled venting slots, integrated carry handle/bipod, telescoping cheek-rest stock"
        },
        {
            "id": "wpn_qbz95",
            "name": "QBZ-95 / QBZ-191",
            "caliber": "5.8x42mm",
            "origin_country": "China",
            "primary_users": [
                {"country": "China", "units": "People's Liberation Army (PLA), People's Armed Police", "weight": 0.99}
            ],
            "visual_cues": "Bullpup configuration, distinctive raised carry handle with sights, curved forward grip integrated into polymer casing"
        }
    ],
    "vehicles": [
        {
            "id": "veh_toyota_hilux",
            "name": "Toyota Hilux / Land Cruiser Technical",
            "type": "Light Armed Technical / Gun Truck",
            "origin_country": "Civilian Modified / Middle East",
            "primary_users": [
                {"country": "Syria / Iraq (Non-State Armed Group)", "units": "ISIS / Daesh, Syrian Rebel Formations, PMF", "weight": 0.99},
                {"country": "Middle East / Africa", "units": "Irregular forces, state paramilitaries, border guards", "weight": 0.85}
            ],
            "visual_cues": "Civilian 4x4 pickup truck bed often mounted with DShK, ZU-23-2 or transport troop carriers"
        },
        {
            "id": "veh_btr82a",
            "name": "BTR-82A Armored Personnel Carrier",
            "type": "8x8 Wheeled IFV / APC",
            "origin_country": "Russian Federation",
            "primary_users": [
                {"country": "Russian Federation", "units": "Motor Rifle Brigades, Naval Infantry, Rosgvardia", "weight": 0.98},
                {"country": "Kazakhstan", "units": "Land Forces", "weight": 0.70},
                {"country": "Syria", "units": "Syrian Arab Army (Elite formations)", "weight": 0.60}
            ],
            "visual_cues": "8-wheel amphibious chassis, BPPU unmanned turret mounting 30mm 2A72 autocannon with night sights"
        },
        {
            "id": "veh_bmp2",
            "name": "BMP-2 Infantry Fighting Vehicle",
            "type": "Tracked IFV",
            "origin_country": "USSR / Russian Federation",
            "primary_users": [
                {"country": "Russian Federation", "units": "Russian Ground Forces", "weight": 0.90},
                {"country": "Ukraine", "units": "Armed Forces of Ukraine (Mechanized Brigades)", "weight": 0.90},
                {"country": "India", "units": "Indian Army (Sarath)", "weight": 0.85},
                {"country": "Middle East / Africa", "units": "Syria, Algeria, Yemen", "weight": 0.75}
            ],
            "visual_cues": "Low-profile tracked chassis, two-man steel turret with long 30mm 2A42 autocannon and 9M113 Konkurs ATGM launcher mounted atop"
        },
        {
            "id": "veh_bradley_m2a2",
            "name": "M2A2 / M2A3 Bradley Fighting Vehicle",
            "type": "Tracked IFV",
            "origin_country": "United States",
            "primary_users": [
                {"country": "United States", "units": "US Army Armored Brigade Combat Teams (ABCT)", "weight": 0.98},
                {"country": "Ukraine", "units": "47th Separate Mechanized Brigade (Magura)", "weight": 0.95},
                {"country": "Saudi Arabia", "units": "Royal Saudi Land Forces", "weight": 0.80}
            ],
            "visual_cues": "High tracked profile with spaced laminated armor / ERA tiles, 25mm M242 Bushmaster chain gun, twin TOW missile box launcher on left turret side"
        },
        {
            "id": "veh_kirpi",
            "name": "BMC Kirpi / Kirpi II MRAP",
            "type": "4x4 / 6x6 Mine-Resistant Ambush Protected",
            "origin_country": "Turkey",
            "primary_users": [
                {"country": "Turkey", "units": "Turkish Armed Forces, Jandarma", "weight": 0.98},
                {"country": "Ukraine", "units": "Ukrainian Marine Corps (Naval Infantry)", "weight": 0.90},
                {"country": "Somalia", "units": "Somali National Army", "weight": 0.75},
                {"country": "Libya", "units": "Government of National Accord Forces", "weight": 0.70}
            ],
            "visual_cues": "V-shaped armored monocoque hull, raised armored glass firing ports, remote controlled weapon station (SARP) on roof"
        },
        {
            "id": "veh_t72b3",
            "name": "T-72B3 / T-72B3M Main Battle Tank",
            "type": "Main Battle Tank (MBT)",
            "origin_country": "Russian Federation",
            "primary_users": [
                {"country": "Russian Federation", "units": "Russian Tank Regiments & Mechanized Forces", "weight": 0.98},
                {"country": "Belarus", "units": "Belarusian Ground Forces", "weight": 0.80}
            ],
            "visual_cues": "Cast low-profile dome turret clad in Kontakt-5 or Relikt wedge explosive reactive armor (ERA), Sosna-U multichannel gunner sight housing on left"
        }
    ],
    "tactical_gear": [
        {
            "id": "gear_fast_helmet",
            "name": "Ops-Core FAST / High-Cut Ballistic Helmet",
            "type": "Ballistic Helmet",
            "origin_country": "United States / Western Standard",
            "primary_users": [
                {"country": "Israel", "units": "IDF Sayeret Matkal, Yamam, Duvdevan, Magav, Paratroopers", "weight": 0.95},
                {"country": "United States", "units": "SOCOM, USMC Recon, SWAT", "weight": 0.95},
                {"country": "Ukraine", "units": "SSO, GUR, 3rd Assault Brigade", "weight": 0.90},
                {"country": "Turkey", "units": "ÖKK, SAT, JÖAK", "weight": 0.90},
                {"country": "Russian Federation", "units": "Spetsnaz FSB, SSO, Wagner PMC (Tor / LShZ clones)", "weight": 0.75}
            ],
            "visual_cues": "High ear-cut profile for tactical communications headsets, ARC side accessory rails, front NVG shroud bracket"
        },
        {
            "id": "gear_6b47_helmet",
            "name": "6B47 Ratnik Helmet",
            "type": "Ballistic Helmet",
            "origin_country": "Russian Federation",
            "primary_users": [
                {"country": "Russian Federation", "units": "Russian Ground Forces (Standard Issue Ratnik)", "weight": 0.98},
                {"country": "Belarus", "units": "Armed Forces of Belarus", "weight": 0.80}
            ],
            "visual_cues": "Full coverage ballistic shell with fabric EMR cover, left-side rail for tactical flashlight, front NVG mount with characteristic Ratnik screw point"
        }
    ]
}


class MilitaryHardwareDatabase:
    """Access interface to military hardware inventory records."""

    @classmethod
    def get_all_weapons(cls) -> List[Dict[str, Any]]:
        return HARDWARE_CATALOG["weapons"]

    @classmethod
    def get_all_vehicles(cls) -> List[Dict[str, Any]]:
        return HARDWARE_CATALOG["vehicles"]

    @classmethod
    def get_all_gear(cls) -> List[Dict[str, Any]]:
        return HARDWARE_CATALOG["tactical_gear"]

    @classmethod
    def find_hardware_by_id(cls, item_id: str) -> Optional[Dict[str, Any]]:
        for cat in HARDWARE_CATALOG.values():
            for item in cat:
                if item["id"] == item_id:
                    return item
        return None
