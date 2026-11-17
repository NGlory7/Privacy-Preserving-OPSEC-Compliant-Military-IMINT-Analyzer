"""
AegisIMINT — Streamlit interface. All analysis runs locally; see src/pipeline.py.

    streamlit run app.py
"""

import os
import sys

import streamlit as st
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.camouflage_db import CamouflageDatabase  # noqa: E402
from src.database.military_hardware_db import MilitaryHardwareDatabase  # noqa: E402
from src.models import ModelsMissingError, device, models_available  # noqa: E402
from src.pipeline import analyze  # noqa: E402
from src.reasoning.intelligence_reporter import IntelligenceReporter  # noqa: E402
from src.utils.visualizer import TacticalVisualizer  # noqa: E402
from src.vision.detector import DEFAULT_THRESHOLDS  # noqa: E402

st.set_page_config(page_title="AegisIMINT", page_icon="🛡️", layout="wide")
st.markdown(
    """
<style>
  .stApp { background:#0d1117; color:#c9d1d9; }
  .card { background:#161b22; border:1px solid #30363d; border-left:4px solid #2ea043; border-radius:6px; padding:12px; }
  .card .t { color:#8b949e; font-size:.8em; text-transform:uppercase; letter-spacing:1px; }
  .card .v { color:#58a6ff; font-size:1.25em; font-weight:600; }
  .card.warn { border-left-color:#d29922; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------- sidebar ----------------
st.sidebar.markdown("## 🛡️ AegisIMINT")
avail = models_available()
if all(avail.values()):
    st.sidebar.success(f"Models found locally · running on `{device()}`")
else:
    missing = ", ".join(k for k, v in avail.items() if not v)
    st.sidebar.error(f"Missing model weights: {missing}. Run `python tools/download_models.py` once.")

st.sidebar.markdown("### Privacy")
redact_faces = st.sidebar.checkbox("Redact faces before analysis", value=True)
redaction_mode = st.sidebar.selectbox("Redaction style", ["pixelate", "censor_bar", "blur"])
intensity = st.sidebar.slider("Redaction strength", 5, 30, 15)

st.sidebar.markdown("### Detection thresholds")
thresholds = {c: st.sidebar.slider(c, 0.05, 0.6, float(v), 0.01) for c, v in DEFAULT_THRESHOLDS.items()}

st.sidebar.markdown("### Analyst identification (optional)")
st.sidebar.caption("If you recognise something by eye, set it here. It replaces the model's guess and is labelled 'analyst' in the report.")
overrides = []
for kind, items in (("weapon", MilitaryHardwareDatabase.get_all_weapons()),
                    ("vehicle", MilitaryHardwareDatabase.get_all_vehicles()),
                    ("gear", MilitaryHardwareDatabase.get_all_gear()),
                    ("camouflage", CamouflageDatabase.get_all())):
    names = {i["name"]: i["id"] for i in items}
    choice = st.sidebar.selectbox(kind.capitalize(), ["— use model —"] + list(names))
    if choice != "— use model —":
        overrides.append({"kind": kind, "id": names[choice]})

# ---------------- main ----------------
st.markdown("## Military imagery analysis — local & offline")
st.caption("Detection: OWLv2 · identification: CLIP ViT-L/14 · face redaction: YuNet. "
           "Measured accuracy is in EVALUATION.md; results are indicators to verify, not conclusions.")

upload = st.file_uploader("Image (JPEG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
if upload is None:
    st.info("Upload an image to start. Nothing leaves this machine.")
    st.stop()

try:
    with st.spinner("Analysing locally…"):
        result = analyze(Image.open(upload), redact_faces=redact_faces, redaction_mode=redaction_mode,
                         intensity=intensity, thresholds=thresholds, analyst_overrides=overrides)
except ModelsMissingError as exc:
    st.error(str(exc))
    st.stop()

det = result["detection"]
corr = result["correlation"]
man = result["opsec_manifest"]

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="card"><div class="t">Detections</div><div class="v">{det["detections_count"]}</div></div>', unsafe_allow_html=True)
camo = result["camo_matches"][0] if result["camo_matches"] else None
c2.markdown(f'<div class="card"><div class="t">Top camouflage guess</div><div class="v">{camo["name"].split(" (")[0] + f" · {camo["confidence"]:.0f}%" if camo else "—"}</div></div>', unsafe_allow_html=True)
if corr["inconclusive"]:
    c3.markdown('<div class="card warn"><div class="t">Attribution</div><div class="v">Inconclusive</div></div>', unsafe_allow_html=True)
else:
    c3.markdown(f'<div class="card"><div class="t">Attribution (evidence share)</div><div class="v">{corr["top_candidate_nation"]} · {corr["top_confidence_percentage"]}%</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card"><div class="t">Outbound connections</div><div class="v">{result["network"]["outbound_attempts_blocked"]} blocked · {result["timings"]["total_s"]} s</div></div>', unsafe_allow_html=True)

tab_vis, tab_attr, tab_report = st.tabs(["Detections", "Attribution", "Report"])

with tab_vis:
    a, b = st.columns(2)
    a.image(result["sanitized_image"], caption=(
        f"Sanitized: {man['metadata_sanitized']['stripped_tags']} metadata tags removed, "
        f"{man['biometric_sanitized'].get('faces_detected', 0)} face(s) redacted ({man['biometric_sanitized'].get('detector_backend')})"),
        width="stretch")
    b.image(TacticalVisualizer.draw_detections(result["sanitized_image"], det["detections"]),
            caption="Green: personnel · red: weapon · yellow: vehicle · blue: helmet", width="stretch")
    if not det["detections"]:
        st.warning("Nothing passed the detection thresholds. Try lowering them in the sidebar.")
    for d in det["detections"]:
        with st.expander(f"{d['label']} — detector score {d['confidence']:.2f}"):
            x, y = st.columns([1, 2])
            x.image(d["crop"], width="stretch")
            for r in d.get("identification", []):
                y.write(f"{r['name']}")
                y.progress(min(1.0, r["probability"]), text=f"{r['probability'] * 100:.0f}%")

with tab_attr:
    st.caption(corr["method"])
    if corr["inconclusive"]:
        st.warning(f"Inconclusive: {corr['inconclusive_reason']}")
    for n in corr["all_ranked_nations"]:
        st.write(f"**{n['country']}** — {n['evidence_share_percentage']}% of evidence weight")
        st.progress(n["evidence_share_percentage"] / 100)
        with st.expander("Based on"):
            for ev in n["supporting_evidence"]:
                st.markdown(f"- {ev}")
    if corr["evidence_ignored"]:
        st.markdown("**Not used (below threshold):** " + ", ".join(f"{e['kind']} `{e['id']}`" for e in corr["evidence_ignored"]))

with tab_report:
    notes = st.text_area("Analyst notes (optional)")
    dossier = IntelligenceReporter.generate_dossier(result, custom_notes=notes)
    st.markdown(dossier["markdown_report"])
    st.download_button("Download report (.md)", dossier["markdown_report"], file_name=f"{dossier['dossier_id']}.md", mime="text/markdown")
