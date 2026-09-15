"""DeepGuard AI — professional Streamlit forensic workspace."""

from __future__ import annotations

import os
from datetime import datetime
from html import escape

import requests
import streamlit as st

st.set_page_config(
    page_title="DeepGuard AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.getenv("DEEPGUARD_API_URL", "http://localhost:8000").rstrip("/")
MEDIA_TYPES = ["jpg", "jpeg", "png", "webp", "bmp", "mp4", "mov", "avi", "mkv", "webm", "mp3", "wav", "m4a", "flac"]


# ──────────────────────────────────────────────────────────────────────────────
# Theme
# ──────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
  --dg-bg: #080a0e;
  --dg-panel: #0d1016;
  --dg-panel-2: #11151d;
  --dg-line: rgba(255,255,255,.08);
  --dg-line-strong: rgba(255,255,255,.13);
  --dg-text: #f4f6f8;
  --dg-muted: #8b93a1;
  --dg-soft: #b7bec9;
  --dg-accent: #ff4d5a;
  --dg-accent-soft: rgba(255,77,90,.11);
  --dg-success: #43d19e;
  --dg-warning: #f5b84b;
}

html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
.stApp { background: var(--dg-bg); color: var(--dg-text); }
.block-container { max-width: 1380px; padding: 1.25rem 2.4rem 3.5rem; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { visibility: hidden; height: 0; }
[data-testid="stDecoration"] { display: none; }
footer { visibility: hidden; }

[data-testid="stSidebar"] {
  background: #0a0c11;
  border-right: 1px solid var(--dg-line);
}
[data-testid="stSidebar"] > div:first-child { padding: 1.35rem 1rem; }

.brand {
  display:flex; align-items:center; gap:11px; padding:.2rem .35rem 1.45rem;
}
.brand-logo {
  width:37px; height:37px; border:1px solid var(--dg-line-strong); border-radius:11px;
  display:flex; align-items:center; justify-content:center; color:#fff;
  background:linear-gradient(145deg,#171b24,#0e1117);
  box-shadow:0 8px 24px rgba(0,0,0,.28);
}
.brand-logo svg { width:21px; height:21px; }
.brand-name { font-family:"Manrope",sans-serif; font-size:1rem; font-weight:800; letter-spacing:-.025em; }
.brand-sub { color:#69717e; font-size:.67rem; margin-top:2px; letter-spacing:.04em; text-transform:uppercase; }

.nav-label {
  color:#555d69; font-size:.62rem; font-weight:700; letter-spacing:.14em;
  text-transform:uppercase; padding:.7rem .55rem .45rem;
}
.sidebar-status {
  border:1px solid var(--dg-line); background:rgba(255,255,255,.018);
  border-radius:12px; padding:.8rem .85rem; margin-top:1rem;
}
.status-row { display:flex; align-items:center; gap:7px; font-size:.76rem; font-weight:600; }
.status-dot { width:7px; height:7px; border-radius:50%; background:var(--dg-success); box-shadow:0 0 0 4px rgba(67,209,158,.08); }
.status-dot.off { background:#68717d; box-shadow:none; }
.status-meta { color:#646d79; font-size:.67rem; margin-top:.45rem; line-height:1.5; }

.hero { padding:.75rem 0 1.8rem; }
.eyebrow { color:var(--dg-accent); font-size:.67rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
.hero h1 {
  font-family:"Manrope",sans-serif; font-size:2.65rem; line-height:1.05;
  letter-spacing:-.055em; margin:.38rem 0 .65rem;
}
.hero p { color:var(--dg-muted); max-width:700px; font-size:.92rem; line-height:1.7; margin:0; }

.topbar {
  display:flex; justify-content:space-between; align-items:center; padding:.2rem 0 1.4rem;
  border-bottom:1px solid var(--dg-line); margin-bottom:1.55rem;
}
.topbar-title { font-family:"Manrope",sans-serif; font-size:.84rem; font-weight:700; color:#dce0e6; }
.topbar-meta { color:#69717d; font-size:.7rem; }

.panel {
  background:var(--dg-panel); border:1px solid var(--dg-line);
  border-radius:16px; padding:1.15rem 1.2rem;
}
.panel-title { font-family:"Manrope",sans-serif; font-size:.92rem; font-weight:700; }
.panel-sub { color:#69717d; font-size:.74rem; margin-top:.25rem; line-height:1.5; }
.kicker { color:#69717d; font-size:.64rem; text-transform:uppercase; letter-spacing:.11em; font-weight:700; }
.big-number { font-family:"Manrope",sans-serif; font-size:1.65rem; font-weight:800; letter-spacing:-.045em; margin-top:.35rem; }
.metric-card {
  background:var(--dg-panel); border:1px solid var(--dg-line);
  border-radius:14px; padding:1rem 1.05rem; min-height:95px;
}
.metric-label { color:#737c89; font-size:.67rem; text-transform:uppercase; letter-spacing:.08em; font-weight:700; }
.metric-value { font-family:"Manrope",sans-serif; font-size:1.35rem; font-weight:800; letter-spacing:-.035em; margin-top:.35rem; }
.metric-note { color:#606975; font-size:.67rem; margin-top:.15rem; }

.scan-shell {
  background:linear-gradient(145deg, rgba(255,255,255,.028), rgba(255,255,255,.012));
  border:1px solid var(--dg-line-strong); border-radius:18px; padding:1.25rem;
}
.scan-drop {
  min-height:270px; border:1px dashed rgba(255,255,255,.16); border-radius:14px;
  display:flex; align-items:center; justify-content:center; text-align:center;
  background:rgba(255,255,255,.012);
}
.drop-icon {
  width:44px; height:44px; margin:0 auto .8rem; border-radius:12px;
  display:flex; align-items:center; justify-content:center;
  background:var(--dg-accent-soft); color:var(--dg-accent);
}
.drop-title { font-family:"Manrope",sans-serif; font-weight:700; font-size:.95rem; }
.drop-copy { color:#68717d; font-size:.72rem; margin-top:.3rem; }

.result-banner {
  border:1px solid var(--dg-line-strong); border-radius:16px; padding:1.15rem 1.25rem;
  background:linear-gradient(100deg, rgba(255,77,90,.07), rgba(255,255,255,.015));
}
.result-state { color:#737c89; font-size:.62rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
.result-verdict { font-family:"Manrope",sans-serif; font-size:1.8rem; font-weight:800; letter-spacing:-.05em; margin:.25rem 0; }
.result-copy { color:#858e9a; font-size:.76rem; }

.signal {
  display:flex; align-items:center; justify-content:space-between; gap:1rem;
  padding:.65rem 0; border-bottom:1px solid var(--dg-line);
}
.signal:last-child { border-bottom:0; }
.signal-name { font-size:.75rem; color:#b8bec8; }
.signal-track { flex:1; height:5px; border-radius:99px; background:#1c222c; overflow:hidden; }
.signal-fill { height:100%; background:#d9dde3; border-radius:99px; }
.signal-value { width:42px; text-align:right; font-size:.7rem; color:#858e9a; }

.history-row {
  display:grid; grid-template-columns:1.5fr .8fr .8fr .75fr; gap:1rem;
  align-items:center; padding:.85rem 0; border-bottom:1px solid var(--dg-line);
}
.history-row:last-child { border-bottom:0; }
.file-name { color:#d8dce2; font-size:.76rem; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.muted { color:#69717d; font-size:.68rem; }
.badge {
  display:inline-flex; align-items:center; width:max-content; padding:.25rem .48rem;
  border-radius:7px; font-size:.61rem; font-weight:800; letter-spacing:.05em;
  background:rgba(255,255,255,.05); color:#c8cdd5;
}
.badge.fake { background:rgba(255,77,90,.1); color:#ff8790; }
.badge.real { background:rgba(67,209,158,.1); color:#74dfb9; }

.stButton > button {
  border-radius:10px !important; min-height:2.55rem !important;
  font-family:"DM Sans",sans-serif !important; font-weight:700 !important;
  border:1px solid var(--dg-line-strong) !important;
}
.stButton > button[kind="primary"] {
  background:#f2f3f5 !important; color:#090b0f !important; border-color:#f2f3f5 !important;
}
.stButton > button:hover { border-color:rgba(255,255,255,.28) !important; }

.stTextInput input, .stSelectbox [data-baseweb="select"] > div {
  background:#0b0e13 !important; border-color:var(--dg-line-strong) !important;
  border-radius:10px !important; color:#e8ebef !important;
}
.stFileUploader section {
  background:transparent !important; border:0 !important; padding:0 !important;
}
.stFileUploader section > div { display:none; }
[data-testid="stFileUploaderDropzone"] {
  background:transparent !important; border:0 !important; padding:0 !important;
}
.stTabs [data-baseweb="tab-list"] { gap:1.2rem; border-bottom:1px solid var(--dg-line); }
.stTabs [data-baseweb="tab"] { color:#727b87; padding:.55rem .1rem; }
.stTabs [aria-selected="true"] { color:#f4f6f8 !important; }
.stAlert { border-radius:10px !important; }
div[data-testid="stMetric"] {
  background:var(--dg-panel); border:1px solid var(--dg-line); border-radius:14px; padding:.8rem 1rem;
}
div[data-testid="stMetricLabel"] { color:#737c89 !important; }
div[data-testid="stMetricValue"] { font-family:"Manrope",sans-serif; }
</style>
""",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def api_get(path: str, timeout: int = 10):
    return requests.get(API_URL + path, timeout=timeout)


def api_post_file(path: str, uploaded_file, timeout: int = 300, **data):
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }
    return requests.post(API_URL + path, files=files, data=data, timeout=timeout)


def pct(value) -> str:
    try:
        number = float(value)
        if number <= 1:
            number *= 100
        return f"{number:.1f}%"
    except (TypeError, ValueError):
        return "—"


def result_risk(result: dict) -> str:
    return str(result.get("risk_level") or result.get("details", {}).get("risk", {}).get("level") or "Unknown").title()


def verdict_class(prediction: str) -> str:
    return "fake" if str(prediction).upper() == "FAKE" else "real"


def save_result(result: dict, filename: str):
    history = st.session_state.setdefault("history", [])
    history.insert(
        0,
        {
            "filename": filename,
            "prediction": result.get("prediction", "UNKNOWN"),
            "confidence": result.get("confidence", 0),
            "fake_probability": result.get("fake_probability", 0),
            "model": result.get("model_name", "unknown"),
            "created": datetime.now().strftime("%H:%M"),
            "result": result,
        },
    )
    st.session_state["last_result"] = result
    st.session_state["last_filename"] = filename


def icon(name: str) -> str:
    paths = {
        "grid": '<path d="M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z" fill="none" stroke="currentColor" stroke-width="1.7"/>',
        "scan": '<circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="m16 16 4 4M8.5 11h5M11 8.5v5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
        "clock": '<circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 7v5l3 2" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>',
        "layers": '<rect x="4" y="5" width="16" height="5" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.7"/><rect x="4" y="14" width="16" height="5" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.7"/>',
        "settings": '<path d="M9.5 4.5h5l.8 2.1 2 .9 2-.8 1.2 4.4-1.9 1.1v2.2l1.9 1.1-1.2 4.4-2-.8-2 .9-.8 2.1h-5l-.8-2.1-2-.9-2 .8-1.2-4.4 1.9-1.1v-2.2L3.5 11l1.2-4.4 2 .8 2-.9.8-2.1Z" fill="none" stroke="currentColor" stroke-width="1.25"/><circle cx="12" cy="12" r="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/>',
        "upload": '<path d="M12 16V5m0 0L8 9m4-4 4 4M5 16v2.5h14V16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>',
    }
    return f'<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">{paths.get(name, "")}</svg>'


def render_result(result: dict):
    prediction = str(result.get("prediction", "UNKNOWN")).upper()
    fake_prob = result.get("fake_probability", result.get("confidence", 0))
    details = result.get("details") or {}
    risk = result.get("risk_level") or details.get("risk", {}).get("level") or "Unknown"
    explanation = result.get("explanation") or details.get("explanation") or []
    heatmap_url = result.get("heatmap_url")

    st.markdown(
        f"""
        <div class="result-banner">
          <div class="result-state">Forensic verdict</div>
          <div class="result-verdict">{escape(prediction)}</div>
          <div class="result-copy">Model output is probabilistic decision-support. Review the evidence before taking consequential action.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("Confidence", pct(result.get("confidence")), "Model certainty"),
        ("Fake probability", pct(fake_prob), "Estimated manipulation"),
        ("Risk level", str(risk).title(), "Forensic risk score"),
        ("Model", str(result.get("model_name", "Unknown")), str(result.get("model_version", ""))),
    ]
    for col, (label, value, note) in zip((c1, c2, c3, c4), cards):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{escape(label)}</div>'
                f'<div class="metric-value">{escape(value)}</div><div class="metric-note">{escape(note)}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns([1.15, .85], gap="large")
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Evidence & explanation</div><div class="panel-sub">Signals returned by the detection pipeline.</div>', unsafe_allow_html=True)
        if explanation:
            for item in explanation:
                st.markdown(f"**{escape(str(item))}**")
        else:
            st.caption("No textual explanation was returned for this analysis.")
        st.markdown("</div>", unsafe_allow_html=True)

        if heatmap_url:
            absolute = heatmap_url if heatmap_url.startswith("http") else API_URL + heatmap_url
            try:
                image_response = requests.get(absolute, timeout=20)
                if image_response.ok:
                    st.write("")
                    st.markdown('<div class="panel"><div class="panel-title">Forensic visualization</div><div class="panel-sub">Model attention / heatmap generated by the backend.</div>', unsafe_allow_html=True)
                    st.image(image_response.content, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            except requests.RequestException:
                pass

    with right:
        st.markdown('<div class="panel"><div class="panel-title">Technical evidence</div><div class="panel-sub">Raw structured output for verification and debugging.</div>', unsafe_allow_html=True)
        with st.expander("View JSON evidence", expanded=False):
            st.json(details)
        if result.get("sha256"):
            st.markdown(
                f'<div class="kicker">SHA-256</div><div class="muted" style="word-break:break-all;margin-top:.35rem">{escape(str(result["sha256"]))}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────────────────────────────────────

if "history" not in st.session_state:
    st.session_state["history"] = []
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "api_url" not in st.session_state:
    st.session_state["api_url"] = API_URL

API_URL = st.session_state["api_url"]


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        f'''
        <div class="brand">
          <div class="brand-logo">{icon("scan")}</div>
          <div><div class="brand-name">DeepGuard AI</div><div class="brand-sub">Digital Forensics</div></div>
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-label">Workspace</div>', unsafe_allow_html=True)
    page = st.radio(
        "Workspace navigation",
        ["Overview", "Analyze", "History", "Models"],
        format_func=lambda x: x,
        label_visibility="collapsed",
    )

    st.markdown('<div class="nav-label">System</div>', unsafe_allow_html=True)
    with st.expander("Connection", expanded=False):
        api_input = st.text_input("FastAPI URL", st.session_state["api_url"])
        if api_input.strip() != st.session_state["api_url"]:
            st.session_state["api_url"] = api_input.strip().rstrip("/")
            API_URL = st.session_state["api_url"]
            st.rerun()

    try:
        health_response = api_get("/api/health")
        health = health_response.json() if health_response.ok else {}
        api_online = health_response.ok
    except requests.RequestException:
        health, api_online = {}, False

    model_name = str(health.get("model", "—"))
    device = str(health.get("device", "—"))
    weights = "Loaded" if health.get("weights_loaded") else "Fallback / forensic"

    st.markdown(
        f"""
        <div class="sidebar-status">
          <div class="status-row"><span class="status-dot {' ' if api_online else 'off'}"></span>{'System operational' if api_online else 'API unavailable'}</div>
          <div class="status-meta">Model · {escape(model_name)}<br>Device · {escape(device)}<br>Weights · {escape(weights)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Overview
# ──────────────────────────────────────────────────────────────────────────────

if page == "Overview":
    st.markdown(
        '<div class="topbar"><div class="topbar-title">Security workspace</div><div class="topbar-meta">Local analysis environment</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero"><div class="eyebrow">DeepGuard / Overview</div><h1>Forensic intelligence, at a glance.</h1>'
        '<p>A focused workspace for detecting manipulated media, inspecting model evidence, and reviewing recent analysis activity.</p></div>',
        unsafe_allow_html=True,
    )

    total = len(st.session_state["history"])
    fake = sum(1 for x in st.session_state["history"] if str(x["prediction"]).upper() == "FAKE")
    real = sum(1 for x in st.session_state["history"] if str(x["prediction"]).upper() == "REAL")
    avg_conf = (
        sum(float(x["confidence"] or 0) for x in st.session_state["history"]) / total
        if total else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    overview_metrics = [
        ("Total scans", str(total), "This session"),
        ("Flagged", str(fake), "Likely manipulated"),
        ("Cleared", str(real), "Classified real"),
        ("Avg. confidence", pct(avg_conf), "Current session"),
    ]
    for col, (label, value, note) in zip((c1, c2, c3, c4), overview_metrics):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    left, right = st.columns([1.35, .65], gap="large")
    with left:
        st.markdown(
            '<div class="panel"><div class="panel-title">Start an investigation</div>'
            '<div class="panel-sub">Upload media to begin a forensic analysis.</div><br>',
            unsafe_allow_html=True,
        )
        a, b, c = st.columns(3)
        with a:
            st.markdown(f'<div class="kicker">{icon("scan")} Single scan</div><p class="muted">Deep analysis with model evidence.</p>', unsafe_allow_html=True)
        with b:
            st.markdown(f'<div class="kicker">{icon("layers")} Batch</div><p class="muted">Process up to eight files.</p>', unsafe_allow_html=True)
        with c:
            st.markdown(f'<div class="kicker">{icon("scan")} Live</div><p class="muted">Inspect a webcam frame.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            f'<div class="panel"><div class="panel-title">Engine status</div><div class="panel-sub">Runtime information from FastAPI.</div><br>'
            f'<div class="status-row"><span class="status-dot {" " if api_online else "off"}"></span>{"Operational" if api_online else "Offline"}</div>'
            f'<div class="muted" style="margin-top:.7rem">Default model · {escape(model_name)}<br>Inference device · {escape(device)}</div></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown('<div class="panel"><div class="panel-title">Recent investigations</div><div class="panel-sub">Analysis performed in this browser session.</div>', unsafe_allow_html=True)
    if not st.session_state["history"]:
        st.markdown(
            '<div style="padding:2rem 0;text-align:center;color:#626b77;font-size:.78rem">No investigations yet. Open Analyze to run your first scan.</div>',
            unsafe_allow_html=True,
        )
    else:
        for item in st.session_state["history"][:5]:
            cls = verdict_class(item["prediction"])
            st.markdown(
                f'<div class="history-row"><div><div class="file-name">{escape(item["filename"])}</div><div class="muted">{escape(item["model"])}</div></div>'
                f'<span class="badge {cls}">{escape(str(item["prediction"]).upper())}</span>'
                f'<div class="muted">{pct(item["confidence"])} confidence</div><div class="muted">{item["created"]}</div></div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Analyze
# ──────────────────────────────────────────────────────────────────────────────

elif page == "Analyze":
    st.markdown(
        '<div class="topbar"><div class="topbar-title">New investigation</div><div class="topbar-meta">Forensic media analysis</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero"><div class="eyebrow">DeepGuard / Analyze</div><h1>Inspect a piece of media.</h1>'
        '<p>Upload an image, video, or audio file. The backend will return a probabilistic verdict with supporting forensic evidence.</p></div>',
        unsafe_allow_html=True,
    )

    mode = st.segmented_control(
        "Analysis mode",
        ["Single", "Batch", "Live"],
        default="Single",
        label_visibility="collapsed",
    )

    if mode == "Single":
        left, right = st.columns([1.35, .65], gap="large")
        with left:
            st.markdown('<div class="scan-shell">', unsafe_allow_html=True)
            st.markdown(
                f'<div class="scan-drop"><div><div class="drop-icon">{icon("upload")}</div>'
                '<div class="drop-title">Upload evidence</div>'
                '<div class="drop-copy">Images, video or audio · up to 100 MB</div></div></div>',
                unsafe_allow_html=True,
            )
            uploaded = st.file_uploader(
                "Evidence file",
                type=MEDIA_TYPES,
                label_visibility="collapsed",
                key="single_upload",
            )
            if uploaded:
                st.success(f"Ready for analysis · {uploaded.name}")
                if uploaded.type.startswith("image/"):
                    st.image(uploaded, caption="Evidence preview", width=430)
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="panel"><div class="panel-title">Detection configuration</div><div class="panel-sub">Tune the inference path before starting.</div><br>', unsafe_allow_html=True)
            model = st.selectbox("Model", ["efficientnet", "xception", "vit"], index=0)
            ensemble = st.toggle("Ensemble analysis", value=False)
            st.markdown(
                '<div class="muted" style="line-height:1.55;margin:.55rem 0 1rem">Ensemble combines supported visual models for a broader signal. It can increase processing time.</div>',
                unsafe_allow_html=True,
            )
            run = st.button("Start forensic analysis  →", type="primary", use_container_width=True, disabled=uploaded is None)
            st.markdown("</div>", unsafe_allow_html=True)

        if run and uploaded:
            with st.spinner("Running forensic pipeline…"):
                try:
                    response = api_post_file(
                        "/api/detect/public",
                        uploaded,
                        model_name=model,
                        ensemble=str(ensemble).lower(),
                    )
                    if response.ok:
                        save_result(response.json(), uploaded.name)
                        st.success("Analysis complete.")
                    else:
                        try:
                            st.error(response.json().get("detail", response.text))
                        except ValueError:
                            st.error(response.text)
                except requests.RequestException as exc:
                    st.error("Could not reach FastAPI: " + str(exc))

        if st.session_state.get("last_result"):
            st.write("")
            render_result(st.session_state["last_result"])

    elif mode == "Batch":
        st.markdown('<div class="panel"><div class="panel-title">Batch investigation</div><div class="panel-sub">Select up to eight evidence files for sequential backend analysis.</div><br>', unsafe_allow_html=True)
        files = st.file_uploader("Evidence files", type=MEDIA_TYPES, accept_multiple_files=True, label_visibility="collapsed", key="batch_upload")
        if files:
            if len(files) > 8:
                st.error("Maximum 8 files per batch.")
            else:
                st.caption(f"{len(files)} file{'s' if len(files) != 1 else ''} selected")
                if st.button("Run batch analysis  →", type="primary"):
                    rows = []
                    progress = st.progress(0)
                    for index, file in enumerate(files, start=1):
                        try:
                            response = api_post_file("/api/detect/public", file, model_name="efficientnet", ensemble="false", timeout=300)
                            if response.ok:
                                result = response.json()
                                save_result(result, file.name)
                                rows.append((file.name, result))
                            else:
                                rows.append((file.name, {"prediction": "ERROR", "confidence": 0, "details": {"error": response.text}}))
                        except requests.RequestException as exc:
                            rows.append((file.name, {"prediction": "ERROR", "confidence": 0, "details": {"error": str(exc)}}))
                        progress.progress(index / len(files))
                    st.write("")
                    for filename, result in rows:
                        cls = verdict_class(result.get("prediction", "ERROR"))
                        st.markdown(
                            f'<div class="history-row"><div class="file-name">{escape(filename)}</div>'
                            f'<span class="badge {cls}">{escape(str(result.get("prediction","ERROR")).upper())}</span>'
                            f'<div class="muted">{pct(result.get("confidence"))}</div><div class="muted">{result.get("model_name","—")}</div></div>',
                            unsafe_allow_html=True,
                        )
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="panel"><div class="panel-title">Live frame analysis</div><div class="panel-sub">Capture a webcam frame and send it to the real-time inference endpoint.</div><br>', unsafe_allow_html=True)
        camera = st.camera_input("Capture evidence", label_visibility="collapsed")
        if camera and st.button("Analyze captured frame  →", type="primary"):
            try:
                with st.spinner("Analyzing live frame…"):
                    response = requests.post(
                        API_URL + "/api/detect/live",
                        files={"file": ("frame.jpg", camera.getvalue(), "image/jpeg")},
                        data={"include_heatmap": "true"},
                        timeout=120,
                    )
                if response.ok:
                    result = response.json()
                    save_result(result, "live-frame.jpg")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Verdict", result.get("prediction", "UNKNOWN"))
                    c2.metric("Fake probability", pct(result.get("fake_probability")))
                    c3.metric("Processing time", f'{float(result.get("processing_time_sec", 0)):.3f}s')
                    render_result(result)
                else:
                    st.error(response.text)
            except requests.RequestException as exc:
                st.error("Could not reach FastAPI: " + str(exc))
        st.markdown("</div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# History
# ──────────────────────────────────────────────────────────────────────────────

elif page == "History":
    st.markdown(
        '<div class="topbar"><div class="topbar-title">Investigation history</div><div class="topbar-meta">Browser session</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero"><div class="eyebrow">DeepGuard / History</div><h1>Recent investigations.</h1>'
        '<p>Review results generated during this session. Authenticated server-side history remains available through the FastAPI history endpoints.</p></div>',
        unsafe_allow_html=True,
    )
    if st.session_state["history"]:
        for index, item in enumerate(st.session_state["history"]):
            cls = verdict_class(item["prediction"])
            col1, col2, col3, col4, col5 = st.columns([1.6, .7, .75, .65, .45])
            with col1:
                st.markdown(f'<div class="file-name">{escape(item["filename"])}</div><div class="muted">{escape(item["model"])}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<span class="badge {cls}">{escape(str(item["prediction"]).upper())}</span>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="muted">{pct(item["confidence"])}</div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="muted">{item["created"]}</div>', unsafe_allow_html=True)
            with col5:
                if st.button("View", key=f"view_{index}"):
                    st.session_state["last_result"] = item["result"]
                    st.session_state["last_filename"] = item["filename"]
                    st.rerun()
            st.divider()
    else:
        st.markdown('<div class="panel" style="text-align:center;padding:3rem"><div class="panel-title">No investigations yet</div><div class="panel-sub">Your completed scans will appear here.</div></div>', unsafe_allow_html=True)

    if st.session_state.get("last_result"):
        st.write("")
        render_result(st.session_state["last_result"])


# ──────────────────────────────────────────────────────────────────────────────
# Models
# ──────────────────────────────────────────────────────────────────────────────

else:
    st.markdown(
        '<div class="topbar"><div class="topbar-title">Detection intelligence</div><div class="topbar-meta">Backend model registry</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero"><div class="eyebrow">DeepGuard / Models</div><h1>Detection models.</h1>'
        '<p>Understand which inference engines are exposed by the current backend and how they fit into the forensic pipeline.</p></div>',
        unsafe_allow_html=True,
    )
    try:
        response = api_get("/api/detect/models")
        if response.ok:
            payload = response.json()
            models = payload.get("models", [])
            cols = st.columns(2)
            for index, item in enumerate(models):
                with cols[index % 2]:
                    modalities = " · ".join(item.get("modalities", []))
                    st.markdown(
                        f'<div class="panel" style="margin-bottom:1rem"><div class="kicker">Phase {escape(str(item.get("phase","—")))}</div>'
                        f'<div class="panel-title" style="margin-top:.35rem">{escape(str(item.get("name","Model")))}</div>'
                        f'<div class="panel-sub" style="margin-top:.45rem">{escape(str(item.get("description","")))}</div>'
                        f'<div class="muted" style="margin-top:.8rem">Modalities · {escape(modalities)}</div></div>',
                        unsafe_allow_html=True,
                    )
            st.write("")
            st.markdown(
                f'<div class="panel"><div class="panel-title">Runtime capabilities</div><div class="panel-sub">Current backend configuration.</div><br>'
                f'<div class="history-row"><div class="file-name">Default model</div><div class="muted">{escape(str(payload.get("default","—")))}</div>'
                f'<div class="muted">Weights</div><div class="muted">{escape(str(payload.get("weights_loaded","—")))}</div></div>'
                f'<div class="history-row"><div class="file-name">Inference mode</div><div class="muted">{escape(str(payload.get("inference_mode","—")))}</div>'
                f'<div class="muted">Endpoint</div><div class="muted">/api/detect/public</div></div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.error(response.text)
    except requests.RequestException as exc:
        st.error("Could not load model registry: " + str(exc))

st.markdown(
    '<div style="border-top:1px solid rgba(255,255,255,.07);margin-top:2.4rem;padding-top:1rem;color:#505864;font-size:.65rem;display:flex;justify-content:space-between">'
    '<span>DEEPGUARD AI · DIGITAL FORENSICS</span><span>Results are probabilistic decision-support.</span></div>',
    unsafe_allow_html=True,
)
