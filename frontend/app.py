import os
from pathlib import Path

import requests
import streamlit as st

st.set_page_config(
    page_title="DeepGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.getenv("DEEPGUARD_API_URL", "http://localhost:8000").rstrip("/")
MEDIA_TYPES = ["jpg", "jpeg", "png", "webp", "bmp", "mp4", "mov", "avi", "mkv", "webm", "mp3", "wav", "m4a", "flac"]

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    .block-container { max-width: 1240px; padding-top: 2rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] { border-right: 1px solid rgba(128,128,128,.18); }
    .brand { display:flex; align-items:center; gap:12px; margin-bottom:1.5rem; }
    .brand-mark { width:42px; height:42px; border-radius:12px; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#111827,#334155); color:white; font-size:21px; }
    .brand-name { font-weight:800; font-size:1.15rem; letter-spacing:-.03em; }
    .brand-sub { color:#7d8590; font-size:.72rem; margin-top:1px; }
    .hero { padding: 1.2rem 0 1.4rem; }
    .eyebrow { color:#64748b; font-size:.75rem; font-weight:700; text-transform:uppercase; letter-spacing:.12em; }
    .hero h1 { font-size:3rem; line-height:1.05; letter-spacing:-.055em; margin:.35rem 0 .7rem; }
    .hero p { color:#64748b; max-width:680px; font-size:1rem; line-height:1.7; }
    .card { border:1px solid rgba(128,128,128,.20); border-radius:16px; padding:1.15rem 1.25rem; background:rgba(255,255,255,.025); }
    .section-title { font-size:1.15rem; font-weight:750; margin:.1rem 0 .25rem; }
    .section-copy { color:#7d8590; font-size:.88rem; margin-bottom:1rem; }
    .status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; background:#22c55e; margin-right:7px; }
    .result-label { color:#64748b; font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; font-weight:700; }
    .result-value { font-size:1.55rem; font-weight:800; letter-spacing:-.03em; margin-top:.15rem; }
    .trust { color:#64748b; font-size:.75rem; line-height:1.55; }
    div[data-testid="stFileUploader"] section { border-radius:16px; }
    .stButton > button { border-radius:10px; font-weight:700; min-height:2.7rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

def api_get(path, timeout=10):
    return requests.get(API_URL + path, timeout=timeout)

def analyze(uploaded_file, endpoint="/api/detect/public", **data):
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")}
    return requests.post(API_URL + endpoint, files=files, data=data, timeout=300)

def pct(value):
    try:
        return "{:.1f}%".format(float(value) * 100)
    except (TypeError, ValueError):
        return "—"

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">🛡️</div><div><div class="brand-name">DeepGuard AI</div><div class="brand-sub">Forensic Detection Platform</div></div></div>',
        unsafe_allow_html=True,
    )
    st.caption("WORKSPACE")
    page = st.radio("Navigation", ["Scan", "Batch analysis", "Live analysis", "Models"], label_visibility="collapsed")
    st.divider()
    st.caption("SYSTEM")
    api_input = st.text_input("FastAPI endpoint", API_URL)
    if api_input.strip():
        API_URL = api_input.rstrip("/")
    try:
        health = api_get("/api/health").json()
        status = str(health.get("status", "unknown")).upper()
        st.success("API " + status)
        st.caption("Model · " + str(health.get("model", "unknown")))
        st.caption("Device · " + str(health.get("device", "unknown")))
    except requests.RequestException:
        st.error("API offline")
        st.caption("Start FastAPI on port 8000.")

if page == "Scan":
    st.markdown(
        '<div class="hero"><div class="eyebrow">Media intelligence</div><h1>Detect manipulated media.</h1><p>Upload a file and DeepGuard AI will analyze it through the detection pipeline, returning a probabilistic verdict, confidence, risk assessment, and forensic signals.</p></div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.35, 0.65], gap="large")
    with left:
        st.markdown('<div class="section-title">Upload media</div><div class="section-copy">Supported images, video and audio formats.</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Drop a file here", type=MEDIA_TYPES, label_visibility="collapsed")
        if uploaded:
            st.info("Ready · {} · {:.1f} KB".format(uploaded.name, uploaded.size / 1024))
            if uploaded.type.startswith("image/"):
                st.image(uploaded, caption="Input preview", width=420)

    with right:
        st.markdown('<div class="section-title">Analysis settings</div><div class="section-copy">Choose how the media should be evaluated.</div>', unsafe_allow_html=True)
        model = st.selectbox("Detection model", ["efficientnet", "xception", "vit"])
        ensemble = st.toggle("Ensemble analysis", value=False)
        st.markdown('<div class="trust">Ensemble mode combines available model signals when supported by the backend.</div>', unsafe_allow_html=True)
        st.write("")
        run = st.button("Run forensic analysis  →", type="primary", use_container_width=True, disabled=uploaded is None)

    if run and uploaded:
        with st.spinner("Analyzing media and generating forensic signals…"):
            try:
                response = analyze(uploaded, model_name=model, ensemble=str(ensemble).lower())
                if response.ok:
                    st.session_state["last_result"] = response.json()
                else:
                    try:
                        st.error(response.json().get("detail", response.text))
                    except ValueError:
                        st.error(response.text)
            except requests.RequestException as exc:
                st.error("API request failed: " + str(exc))

    result = st.session_state.get("last_result")
    if result:
        st.divider()
        st.markdown('<div class="section-title">Analysis result</div><div class="section-copy">Probabilistic output from the selected detection pipeline.</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        metrics = [
            ("Verdict", result.get("prediction", "UNKNOWN")),
            ("Confidence", pct(result.get("confidence"))),
            ("Fake probability", pct(result.get("fake_probability"))),
            ("Risk level", result.get("risk_level") or "Unknown"),
        ]
        for col, (label, value) in zip([c1,c2,c3,c4], metrics):
            with col:
                st.markdown('<div class="card"><div class="result-label">{}</div><div class="result-value">{}</div></div>'.format(label, value), unsafe_allow_html=True)

        st.write("")
        explanation = result.get("explanation")
        details = result.get("details") or {}
        col_a, col_b = st.columns([1.25, .75], gap="large")
        with col_a:
            st.markdown('<div class="section-title">Forensic explanation</div>', unsafe_allow_html=True)
            if explanation:
                for item in explanation:
                    st.markdown("• " + str(item))
            else:
                st.caption("No explanation was returned for this analysis.")
        with col_b:
            with st.expander("Technical details"):
                st.json(details)
        st.markdown('<div class="trust">Important: model outputs are probabilistic and should be independently verified before high-stakes use.</div>', unsafe_allow_html=True)

elif page == "Batch analysis":
    st.markdown('<div class="hero"><div class="eyebrow">High-throughput analysis</div><h1>Analyze multiple files.</h1><p>Process a small set of media files in one request and review the resulting classifications.</p></div>', unsafe_allow_html=True)
    files = st.file_uploader("Upload up to 8 files", type=MEDIA_TYPES, accept_multiple_files=True)
    if files and len(files) > 8:
        st.warning("Please select no more than 8 files.")
    if files and len(files) <= 8:
        st.caption("{} file{} selected".format(len(files), "" if len(files) == 1 else "s"))
        if st.button("Analyze batch  →", type="primary"):
            multipart = [("files", (f.name, f.getvalue(), f.type or "application/octet-stream")) for f in files]
            try:
                with st.spinner("Processing batch…"):
                    response = requests.post(API_URL + "/api/detect/batch", files=multipart, timeout=600)
                if response.ok:
                    data = response.json()
                    a,b,c = st.columns(3)
                    a.metric("Total", data.get("total", 0))
                    b.metric("Flagged fake", data.get("fake_count", 0))
                    c.metric("Classified real", data.get("real_count", 0))
                    st.divider()
                    for item in data.get("items", []):
                        st.write("**{}** · {} · {}".format(item.get("prediction","UNKNOWN"), item.get("model_name","model"), pct(item.get("confidence"))))
                else:
                    st.error(response.text)
            except requests.RequestException as exc:
                st.error("API request failed: " + str(exc))

elif page == "Live analysis":
    st.markdown('<div class="hero"><div class="eyebrow">Real-time workflow</div><h1>Analyze a live frame.</h1><p>Capture a webcam frame and send it directly to the live detection endpoint.</p></div>', unsafe_allow_html=True)
    camera = st.camera_input("Camera capture")
    if camera:
        if st.button("Analyze captured frame  →", type="primary"):
            try:
                with st.spinner("Analyzing frame…"):
                    response = requests.post(API_URL + "/api/detect/live", files={"file": ("frame.jpg", camera.getvalue(), "image/jpeg")}, data={"include_heatmap": "true"}, timeout=120)
                if response.ok:
                    data = response.json()
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Verdict", data.get("prediction", "UNKNOWN"))
                    c2.metric("Fake probability", pct(data.get("fake_probability")))
                    c3.metric("Processing time", "{:.3f}s".format(float(data.get("processing_time_sec", 0))))
                    if data.get("heatmap_b64"):
                        st.success("Forensic heatmap generated.")
                else:
                    st.error(response.text)
            except requests.RequestException as exc:
                st.error("API request failed: " + str(exc))

else:
    st.markdown('<div class="hero"><div class="eyebrow">Model intelligence</div><h1>Detection models.</h1><p>Review the models exposed by the backend and the modalities they support.</p></div>', unsafe_allow_html=True)
    try:
        response = api_get("/api/detect/models")
        if response.ok:
            models = response.json().get("models", [])
            if not models:
                st.info("No model metadata is currently available.")
            for item in models:
                with st.container(border=True):
                    col1, col2 = st.columns([1.5, .5])
                    with col1:
                        st.markdown("### " + str(item.get("name", "Model")))
                        st.write(item.get("description", "No description available."))
                        st.caption("Modalities · " + ", ".join(item.get("modalities", [])))
                    with col2:
                        st.metric("Phase", item.get("phase", "—"))
        else:
            st.error(response.text)
    except requests.RequestException as exc:
        st.error("Could not load model information: " + str(exc))

st.divider()
st.caption("DeepGuard AI · Forensic decision-support · Detection results are probabilistic.")
