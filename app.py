"""
AegisIMINT: Privacy-Preserving & OPSEC-Compliant Military IMINT Analyzer
Streamlit Tactical Intelligence Dashboard (100% Offline / Air-Gapped)
"""

import os
import sys
from io import BytesIO
from PIL import Image
import streamlit as st

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.opsec.anonymizer import OPSECAnonymizer
from src.vision.detector import LocalMilitaryDetector
from src.database.vector_matcher import VectorMatcher
from src.database.camouflage_db import CamouflageDatabase
from src.database.military_hardware_db import MilitaryHardwareDatabase
from src.reasoning.correlation_engine import CorrelationEngine
from src.reasoning.intelligence_reporter import IntelligenceReporter
from src.utils.visualizer import TacticalVisualizer

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AegisIMINT // Military OSINT Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM TACTICAL STYLING ---
st.markdown("""
<style>
    /* Dark tactical military theme overrides */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Courier New', Courier, monospace;
    }
    .tactical-header {
        border-bottom: 2px solid #238636;
        padding-bottom: 8px;
        margin-bottom: 18px;
    }
    .opsec-badge-safe {
        background-color: #238636;
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: bold;
        display: inline-block;
        font-size: 0.85em;
    }
    .hud-metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-left: 4px solid #2ea043;
        border-radius: 6px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .hud-title {
        color: #8b949e;
        font-size: 0.85em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .hud-value {
        color: #58a6ff;
        font-size: 1.6em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# --- SIDEBAR CONFIGURATION ---
st.sidebar.markdown("## 🛡️ AEGIS-IMINT ENGINE")
st.sidebar.caption("Air-Gapped Defense OSINT Analyzer v1.0")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔒 OPSEC Controls")
redact_faces = st.sidebar.checkbox("Auto-Redact Faces / Biometrics", value=True)
redaction_mode = st.sidebar.selectbox(
    "Redaction Style",
    ["pixelate", "censor_bar", "blur"],
    index=0,
    help="Pixelate: Tactical mosaic block. Censor bar: Solid black box. Blur: Gaussian kernel."
)
blur_intensity = st.sidebar.slider("Redaction Intensity", 5, 30, 15)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Engine Status")
st.sidebar.success("🔒 100% Air-Gapped / Offline Local")
st.sidebar.caption("Zero external network dependencies. All detections and correlations run strictly on your machine.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Hardware Cross-Reference")
all_weapons = MilitaryHardwareDatabase.get_all_weapons()
weapon_options = ["Auto-Detect / Heuristic"] + [f"{w['name']} ({w['origin_country']})" for w in all_weapons]
selected_wpn_str = st.sidebar.selectbox("Small Arms Override", weapon_options)

selected_weapon_id = None
if selected_wpn_str != "Auto-Detect / Heuristic":
    for w in all_weapons:
        if w["name"] in selected_wpn_str:
            selected_weapon_id = w["id"]
            break

all_vehicles = MilitaryHardwareDatabase.get_all_vehicles()
vehicle_options = ["None Detected in Primary Frame"] + [f"{v['name']} ({v['type']})" for v in all_vehicles]
selected_veh_str = st.sidebar.selectbox("Combat Vehicle Override", vehicle_options)

selected_vehicle_id = None
if selected_veh_str != "None Detected in Primary Frame":
    for v in all_vehicles:
        if v["name"] in selected_veh_str:
            selected_vehicle_id = v["id"]
            break


# --- MAIN HEADER ---
st.markdown('<div class="tactical-header"><h2>🎯 MILITARY IMINT & PATTERN ATTRIBUTION ANALYZER</h2><span class="opsec-badge-safe">🛡️ 100% AIR-GAPPED OPSEC MODE</span></div>', unsafe_allow_html=True)
st.write("Extract military camouflage signatures, equipment correlations, operator nations, and deployment theaters locally without leaking sensitive biometrics or raw imagery.")

# --- IMAGE INGESTION ---
col_upload, col_samples = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload Reconnaissance / OSINT Imagery (JPEG, PNG, WEBP)",
        type=["jpg", "jpeg", "png", "webp"]
    )

with col_samples:
    st.markdown("**Or Test Preset Camouflage Swatches:**")
    sample_dir = os.path.join(os.path.dirname(__file__), "data", "sample_images")
    preset_choice = st.selectbox(
        "Load Preset Sample",
        ["None (Use Upload)", "MultiCam (US / NATO / SSO)", "EMR / Digital Flora (Russia)", "Flecktarn (Germany)", "TSK Digital (Turkey)"]
    )

active_image = None

if preset_choice != "None (Use Upload)" and os.path.exists(sample_dir):
    filename_map = {
        "MultiCam (US / NATO / SSO)": "sample_multicam.png",
        "EMR / Digital Flora (Russia)": "sample_emr_digital_flora.png",
        "Flecktarn (Germany)": "sample_flecktarn.png",
        "TSK Digital (Turkey)": "sample_turkish_digital.png"
    }
    sample_path = os.path.join(sample_dir, filename_map[preset_choice])
    if os.path.exists(sample_path):
        active_image = Image.open(sample_path)
        st.info(f"Loaded synthetic reference preset: **{preset_choice}**")

elif uploaded_file is not None:
    active_image = Image.open(uploaded_file)


# --- PROCESSING PIPELINE ---
if active_image is not None:
    st.markdown("---")

    # Step 1: Pre-flight OPSEC Sanitization
    anonymizer = OPSECAnonymizer(
        redact_faces=redact_faces,
        redaction_mode=redaction_mode,
        intensity=blur_intensity
    )
    sanitized_image, opsec_manifest = anonymizer.process(active_image)

    # Step 2: Local Military Object Detection
    detector = LocalMilitaryDetector()
    detection_results = detector.analyze_image(sanitized_image)

    # Step 3: Camouflage Feature Matching
    camo_detection = next((d for d in detection_results["detections"] if d["category"] == "uniform"), None)
    camo_patch = camo_detection["crop"] if camo_detection else sanitized_image
    camo_matches = VectorMatcher.match_camouflage(camo_patch, top_k=3)

    # Step 4: Joint Correlation
    correlation = CorrelationEngine.correlate(
        camo_matches=camo_matches,
        detected_weapon_id=selected_weapon_id or ("wpn_ak74m" if "EMR" in camo_matches[0]["name"] else "wpn_m4a1"),
        detected_vehicle_id=selected_vehicle_id,
        detected_gear_id="gear_6b47_helmet" if "EMR" in camo_matches[0]["name"] else "gear_fast_helmet"
    )

    # Top Metrics Banner
    m1, m2, m3, m4 = st.columns(4)
    top_camo = camo_matches[0]
    top_country = correlation["top_candidate_nation"]
    top_conf = correlation["top_confidence_percentage"]
    theaters = correlation["suspected_theaters"][0] if correlation["suspected_theaters"] else "Global"

    with m1:
        st.markdown(f"""
        <div class="hud-metric-card">
            <div class="hud-title">Primary Pattern</div>
            <div class="hud-value" style="font-size: 1.1em; color: #3fb950;">{top_camo['name'][:22]}...</div>
            <span style="color: #8b949e; font-size: 0.85em;">Confidence: {top_camo['confidence']}%</span>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="hud-metric-card">
            <div class="hud-title">Candidate Nation / Entity</div>
            <div class="hud-value" style="font-size: 1.2em; color: #58a6ff;">{top_country}</div>
            <span style="color: #8b949e; font-size: 0.85em;">Attribution: {top_conf}%</span>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="hud-metric-card">
            <div class="hud-title">Likely Conflict Theater</div>
            <div class="hud-value" style="font-size: 1.0em; color: #d29922;">{theaters}</div>
            <span style="color: #8b949e; font-size: 0.85em;">Geographic Probability</span>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
        <div class="hud-metric-card">
            <div class="hud-title">OPSEC Assurance</div>
            <div class="hud-value" style="font-size: 1.1em; color: #bc8cff;">AIR-GAPPED</div>
            <span style="color: #8b949e; font-size: 0.85em;">Zero Data Outbound</span>
        </div>
        """, unsafe_allow_html=True)

    # Detailed Analysis Tabs
    tab_vis, tab_matrix, tab_camo, tab_report = st.tabs([
        "👁️ Tactical Vision & Detections",
        "📊 Joint Attribution Matrix",
        "🎨 Camopedia Pattern Breakdown",
        "📄 Official IMINT Dossier"
    ])

    with tab_vis:
        col_img1, col_img2 = st.columns(2)
        hud_image = TacticalVisualizer.draw_detections(sanitized_image, detection_results["detections"])

        with col_img1:
            st.markdown("#### 🔒 Sanitized Source (OPSEC Secured)")
            st.image(sanitized_image, use_container_width=True)
            st.caption(f"Stripped {opsec_manifest['metadata_sanitized']['stripped_tags']} EXIF tags. Biometrics: {opsec_manifest['biometric_sanitized']['faces_detected']} face(s) redacted.")

        with col_img2:
            st.markdown("#### 🎯 Tactical HUD Detection Overlays")
            st.image(hud_image, use_container_width=True)
            st.caption("Green: Uniform/Camouflage swatch | Red: Weapon silhouette | Cyan: Tactical headgear")

    with tab_matrix:
        st.markdown("### ⚖️ Operator Attribution Probability")
        for nation_info in correlation["all_ranked_nations"]:
            st.write(f"**{nation_info['country']}** — `{nation_info['probability_percentage']}%`")
            st.progress(nation_info["probability_percentage"] / 100.0)
            with st.expander("🔎 View Supporting Indicators"):
                for ev in nation_info["supporting_evidence"]:
                    st.markdown(f"- {ev}")

        st.markdown("### 📍 Suspected Deployment Theaters")
        for th in correlation["suspected_theaters"]:
            st.markdown(f"- **{th}**")

    with tab_camo:
        st.markdown("### 🎖️ Top Camouflage Database Matches")
        for idx, match in enumerate(camo_matches, 1):
            st.markdown(f"#### #{idx} {match['name']} — `{match['confidence']}% Match`")
            col_info, col_swatch = st.columns([3, 1])
            with col_info:
                st.write(f"**Origin Country:** {match['origin_country']}")
                st.write(f"**Design Class:** {match['pattern_type']}")
                st.write(f"**Description:** {match['description']}")
                st.markdown("**Primary Military Branches:**")
                for op in match["primary_operators"]:
                    st.markdown(f"- {op['country']} ({op['branch']})")
            with col_swatch:
                st.caption("Extracted Palette:")
                swatch_img = TacticalVisualizer.render_palette_strip(match["palette_hex"])
                st.image(swatch_img, use_container_width=True)
            st.markdown("---")

    with tab_report:
        custom_notes = st.text_area("Optional Field Observations / Analyst Notes:", "")
        if st.button("Generate Final IMINT Dossier", type="primary"):
            with st.spinner("Compiling standardized military intelligence assessment..."):
                dossier = IntelligenceReporter.generate_dossier(
                    opsec_manifest=opsec_manifest,
                    camo_matches=camo_matches,
                    correlation_result=correlation,
                    custom_notes=custom_notes
                )
                st.markdown(dossier["markdown_report"])
                st.download_button(
                    label="💾 Download Dossier (.md)",
                    data=dossier["markdown_report"],
                    file_name=f"{dossier['dossier_id']}.md",
                    mime="text/markdown"
                )

else:
    st.info("👈 Upload an image or select a preset camouflage swatch from the left to commence intelligence analysis.")
