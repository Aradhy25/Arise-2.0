"""DeepGuard AI — interactive forensic command center."""

from __future__ import annotations

import os
from datetime import datetime
from html import escape

import requests
import streamlit as st

st.set_page_config(
    page_title="DeepGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = os.getenv("DEEPGUARD_API_URL", "http://localhost:8000").rstrip("/")
MEDIA_TYPES = ["jpg", "jpeg", "png", "webp", "bmp", "pdf", "mp4", "mov", "avi", "mkv", "webm", "mp3", "wav", "m4a", "flac"]


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

:root{
 --bg:#070a0f;--panel:#0d121a;--panel2:#111824;--line:rgba(255,255,255,.085);
 --text:#f5f7fa;--muted:#8993a3;--cyan:#35d7ff;--red:#ff5263;--purple:#9b7cff;
 --green:#42d6a0;--amber:#f5bb55;
}
html,body,[class*="css"]{font-family:"DM Sans",sans-serif}
.stApp{background:radial-gradient(circle at 78% 5%,rgba(53,215,255,.055),transparent 27%),var(--bg);color:var(--text)}
.block-container{max-width:1450px;padding:1.2rem 2.4rem 3.5rem}
[data-testid="stHeader"]{background:transparent}.stAppDeployButton{display:none}
footer{visibility:hidden}
[data-testid="stSidebar"]{background:#090d13;border-right:1px solid var(--line)}
[data-testid="stSidebar"]>div:first-child{padding:1.1rem .9rem}

.brand{display:flex;align-items:center;gap:11px;padding:.2rem .45rem 1.35rem}
.brand-mark{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;
 background:linear-gradient(145deg,rgba(53,215,255,.18),rgba(155,124,255,.12));border:1px solid rgba(53,215,255,.22);
 color:var(--cyan);font-size:1.25rem;box-shadow:0 0 28px rgba(53,215,255,.08)}
.brand-name{font:800 1rem "Manrope";letter-spacing:-.03em}.brand-sub{font-size:.62rem;color:#626d7d;letter-spacing:.12em;text-transform:uppercase;margin-top:2px}
.nav-caption{font-size:.61rem;color:#596474;text-transform:uppercase;letter-spacing:.15em;font-weight:800;padding:.65rem .55rem .4rem}
.sidebar-status{margin-top:1rem;padding:.8rem;border:1px solid var(--line);border-radius:13px;background:linear-gradient(145deg,rgba(255,255,255,.025),transparent)}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:7px;background:var(--green);box-shadow:0 0 0 4px rgba(66,214,160,.08)}
.dot.off{background:#6b7481;box-shadow:none}
.status-title{font-size:.75rem;font-weight:700}.status-meta{font-size:.65rem;color:#687384;line-height:1.55;margin-top:.45rem}

.topline{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);padding:.25rem 0 1rem;margin-bottom:1.4rem}
.breadcrumb{font-size:.72rem;color:#758092}.breadcrumb b{color:#dce2ea}
.pill{display:inline-flex;align-items:center;gap:6px;padding:.34rem .6rem;border:1px solid var(--line);border-radius:99px;font-size:.63rem;color:#aab3c0;background:rgba(255,255,255,.025)}
.hero{padding:.35rem 0 1.55rem}.eyebrow{color:var(--cyan);font-size:.64rem;font-weight:800;letter-spacing:.17em;text-transform:uppercase}
.hero h1{font:800 2.65rem/1.04 "Manrope";letter-spacing:-.055em;margin:.35rem 0 .65rem}
.hero p{max-width:760px;color:var(--muted);font-size:.88rem;line-height:1.7;margin:0}

.panel{background:linear-gradient(145deg,rgba(255,255,255,.028),rgba(255,255,255,.012));border:1px solid var(--line);border-radius:16px;padding:1.1rem}
.panel-title{font:700 .92rem "Manrope"}.panel-sub{color:#6f7a8a;font-size:.7rem;line-height:1.5;margin-top:.25rem}
.metric{position:relative;overflow:hidden;background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:1rem;min-height:105px}
.metric:after{content:"";position:absolute;right:-20px;top:-20px;width:65px;height:65px;border-radius:50%;background:var(--metric-color);opacity:.09;filter:blur(3px)}
.metric-label{font-size:.62rem;text-transform:uppercase;letter-spacing:.1em;color:#727d8d;font-weight:800}
.metric-value{font:800 1.55rem "Manrope";letter-spacing:-.045em;margin-top:.35rem}.metric-note{font-size:.65rem;color:#626d7d;margin-top:.2rem}
.action-card{background:var(--panel);border:1px solid var(--line);border-radius:15px;padding:1rem;min-height:120px}
.action-icon{font-size:1.2rem;margin-bottom:.55rem}.action-title{font:700 .82rem "Manrope"}.action-copy{font-size:.66rem;color:#6f7a89;line-height:1.5;margin-top:.3rem}

.section-head{display:flex;justify-content:space-between;align-items:end;margin:1.4rem 0 .7rem}.section-head h2{font:700 1rem "Manrope";margin:0}.section-head span{font-size:.65rem;color:#606b7b}

.scan-zone{border:1px dashed rgba(53,215,255,.28);background:radial-gradient(circle at 50% 20%,rgba(53,215,255,.055),transparent 45%),#0b1118;border-radius:16px;padding:1.35rem}
.scan-zone-inner{min-height:180px;display:grid;place-items:center;text-align:center;border:1px dashed rgba(255,255,255,.08);border-radius:12px}
.scan-icon{font-size:2rem;margin-bottom:.5rem}.scan-title{font:700 1rem "Manrope"}.scan-copy{color:#6e7989;font-size:.68rem;margin-top:.25rem}
.result{border-radius:16px;padding:1.1rem;border:1px solid var(--line);background:linear-gradient(110deg,rgba(53,215,255,.055),rgba(255,255,255,.015))}
.verdict{font:800 1.85rem "Manrope";letter-spacing:-.05em}.result-label{font-size:.6rem;letter-spacing:.14em;text-transform:uppercase;color:#758092;font-weight:800}
.badge{display:inline-flex;padding:.26rem .5rem;border-radius:7px;font-size:.6rem;font-weight:800;letter-spacing:.05em;background:rgba(255,255,255,.05);color:#cbd2db}
.badge.fake{background:rgba(255,82,99,.12);color:#ff8b96}.badge.real{background:rgba(66,214,160,.12);color:#73e0b8}
.badge.warn{background:rgba(245,187,85,.12);color:#f8ca78}
.signal{display:flex;align-items:center;gap:.65rem;padding:.55rem 0;border-bottom:1px solid var(--line)}.signal:last-child{border-bottom:0}
.signal-name{width:125px;font-size:.66rem;color:#aeb6c2}.track{height:5px;flex:1;background:#1b2430;border-radius:99px;overflow:hidden}.fill{height:100%;background:linear-gradient(90deg,var(--cyan),var(--purple));border-radius:99px}.signal-value{width:42px;text-align:right;font-size:.62rem;color:#788394}
.history-row{display:grid;grid-template-columns:1.55fr .7fr .75fr .6fr;gap:1rem;align-items:center;padding:.8rem 0;border-bottom:1px solid var(--line)}
.history-row:last-child{border-bottom:0}.filename{font-size:.72rem;font-weight:700;color:#d9dee6;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.muted{font-size:.64rem;color:#687384}

.stButton>button{border-radius:10px!important;min-height:2.5rem!important;background:#111721!important;border:1px solid rgba(255,255,255,.1)!important;color:#e8ecf1!important;font-weight:700!important}
.stButton>button:hover{border-color:rgba(53,215,255,.42)!important;color:#fff!important;box-shadow:0 0 18px rgba(53,215,255,.06)}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#28c8ee,#6d7cff)!important;border:0!important;color:#061016!important;box-shadow:0 8px 24px rgba(53,215,255,.12)}
.stTextInput input,.stSelectbox [data-baseweb="select"]>div{background:#0b1017!important;border-color:var(--line)!important;border-radius:10px!important}
.stTabs [data-baseweb="tab-list"]{gap:1rem;border-bottom:1px solid var(--line)}.stTabs [data-baseweb="tab"]{font-size:.72rem;color:#758092}.stTabs [aria-selected="true"]{color:#fff!important}
[data-testid="stFileUploaderDropzone"]{background:#0a1017!important;border:1px dashed rgba(53,215,255,.25)!important;border-radius:12px!important}
.stProgress>div>div>div>div{background:linear-gradient(90deg,var(--cyan),var(--purple))}
div[data-testid="stMetric"]{background:var(--panel);border:1px solid var(--line);border-radius:13px}
hr{border-color:var(--line)!important}
</style>
""",
    unsafe_allow_html=True,
)


def api_get(path: str, timeout: int = 10):
    return requests.get(API_URL + path, timeout=timeout)


def api_post_file(path: str, uploaded_file, timeout: int = 300, **data):
    return requests.post(
        API_URL + path,
        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type or "application/octet-stream")},
        data=data,
        timeout=timeout,
    )


def pct(value) -> str:
    try:
        n = float(value or 0)
        if n <= 1:
            n *= 100
        return f"{n:.1f}%"
    except (TypeError, ValueError):
        return "—"


def verdict_class(value: str) -> str:
    return "fake" if str(value).upper() == "FAKE" else "real"


def save_result(result: dict, filename: str):
    history = st.session_state.setdefault("history", [])
    history.insert(0, {
        "filename": filename,
        "prediction": result.get("prediction", "UNKNOWN"),
        "confidence": result.get("confidence", 0),
        "model": result.get("model_name", "unknown"),
        "created": datetime.now().strftime("%H:%M"),
        "result": result,
    })
    st.session_state["last_result"] = result


def render_parameter_evidence(result: dict):
    details = result.get("details") or {}
    media = str(result.get("media_type", "unknown"))
    signals = details.get("signals") or {}
    st.markdown('<div class="section-head"><h2>Forensic parameters</h2><span>Measured evidence</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    if media == "image":
        labels = [
            ("Model fake probability", signals.get("model_fake_prob")),
            ("Forensic ELA", signals.get("forensic_ela_score", signals.get("ela_score"))),
            ("Frequency anomaly", signals.get("forensic_frequency_score", signals.get("frequency_score"))),
            ("Noise inconsistency", signals.get("forensic_noise_score", signals.get("noise_score"))),
            ("RGB correlation anomaly", signals.get("forensic_color_score", signals.get("color_score"))),
            ("Face confidence", details.get("face_confidence")),
            ("Full-frame probability", signals.get("full_frame_fake_prob")),
        ]
    elif media == "audio":
        labels = [
            ("Model fake probability", signals.get("model_fake_probability")),
            ("Spectral flatness", signals.get("spectral_flatness")),
            ("High-frequency ratio", signals.get("high_freq_ratio")),
            ("ZCR mean", signals.get("zcr_mean")),
            ("ZCR variability", signals.get("zcr_std")),
        ]
    elif media == "document":
        labels = [
            ("Document fake probability", details.get("fake_probability")),
            ("Maximum page probability", signals.get("max_page_fake_probability")),
            ("Mean page probability", signals.get("mean_page_fake_probability")),
            ("Structural anomaly flags", signals.get("structural_flag_count")),
            ("Pages analyzed", signals.get("pages_analyzed")),
        ]
    elif media == "video":
        labels = [
            ("Visual fake probability", details.get("fake_probability")),
            ("Audio fake probability", details.get("audio_fake_probability")),
            ("Suspicious frame ratio", (result.get("suspicious_frames", 0) / max(result.get("frames_analyzed", 1), 1))),
            ("Frames analyzed", result.get("frames_analyzed")),
            ("A/V alignment score", (details.get("audio_video_consistency") or {}).get("alignment_score")),
        ]
    else:
        labels = []
    shown = 0
    for label, value in labels:
        if value is None:
            continue
        shown += 1
        if isinstance(value, (int, float)):
            width = min(max(float(value) * 100 if float(value) <= 1 else float(value), 0), 100)
            display = pct(value) if float(value) <= 1 else escape(str(value))
        else:
            width = 0
            display = escape(str(value))
        st.markdown(f'<div class="signal"><div class="signal-name">{escape(label)}</div><div class="track"><div class="fill" style="width:{width:.1f}%"></div></div><div class="signal-value">{display}</div></div>', unsafe_allow_html=True)
    if not shown:
        st.caption("No structured modality-specific parameters were returned.")
    if details.get("provenance"):
        with st.expander("Originality / provenance signals", expanded=False):
            st.json(details["provenance"])
    if details.get("structure"):
        with st.expander("Document structure evidence", expanded=False):
            st.json(details["structure"])
    if details.get("pages"):
        with st.expander("Page-by-page evidence", expanded=False):
            st.json(details["pages"])
    st.markdown("</div>", unsafe_allow_html=True)


def render_result(result: dict):
    prediction = str(result.get("prediction", "UNKNOWN")).upper()
    details = result.get("details") or {}
    fake_prob = result.get("fake_probability", result.get("confidence", 0))
    risk = result.get("risk_level") or details.get("risk", {}).get("level") or "Unknown"
    explanation = result.get("explanation") or details.get("explanation") or []

    st.markdown(
        f'<div class="result"><div class="result-label">Forensic verdict</div>'
        f'<div class="verdict">{escape(prediction)}</div>'
        f'<div class="muted">Probabilistic decision-support · verify evidence before consequential decisions.</div></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    cols = st.columns(4)
    metrics = [
        ("Confidence", pct(result.get("confidence")), "Model certainty", "var(--cyan)"),
        ("Fake probability", pct(fake_prob), "Manipulation estimate", "var(--red)"),
        ("Risk level", str(risk).title(), "Forensic risk", "var(--amber)"),
        ("Model", str(result.get("model_name", "Unknown")), str(result.get("model_version", "")), "var(--purple)"),
    ]
    for col, (label, value, note, color) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric" style="--metric-color:{color}"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{escape(value)}</div><div class="metric-note">{escape(note)}</div></div>',
                unsafe_allow_html=True,
            )

    left, right = st.columns([1.15, .85], gap="large")
    with left:
        st.markdown('<div class="section-head"><h2>Evidence signals</h2><span>Model-supported indicators</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        if explanation:
            for item in explanation:
                st.markdown(f"• {escape(str(item))}")
        else:
            signals = [("Visual consistency", fake_prob), ("Compression anomalies", float(fake_prob or 0) * .82), ("Model confidence", result.get("confidence", 0))]
            for name, value in signals:
                st.markdown(
                    f'<div class="signal"><div class="signal-name">{name}</div><div class="track"><div class="fill" style="width:{min(max(float(value or 0)*100 if float(value or 0)<=1 else float(value or 0),0),100):.1f}%"></div></div><div class="signal-value">{pct(value)}</div></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

        heatmap_url = result.get("heatmap_url")
        if heatmap_url:
            absolute = heatmap_url if str(heatmap_url).startswith("http") else API_URL + heatmap_url
            try:
                image_response = requests.get(absolute, timeout=20)
                if image_response.ok:
                    st.markdown('<div class="section-head"><h2>Forensic visualization</h2><span>Attention / heatmap</span></div>', unsafe_allow_html=True)
                    st.image(image_response.content, use_container_width=True)
            except requests.RequestException:
                pass

    with right:
        st.markdown('<div class="section-head"><h2>Technical evidence</h2><span>Auditable output</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        with st.expander("View structured JSON", expanded=False):
            st.json(details)
        if result.get("sha256"):
            st.markdown(f'<div class="metric-label">SHA-256</div><div class="muted" style="word-break:break-all;margin-top:.4rem">{escape(str(result["sha256"]))}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    render_parameter_evidence(result)


if "history" not in st.session_state:
    st.session_state["history"] = []
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "api_url" not in st.session_state:
    st.session_state["api_url"] = API_URL
if "page" not in st.session_state:
    st.session_state["page"] = "Overview"

API_URL = st.session_state["api_url"]


with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-mark">◈</div><div><div class="brand-name">DeepGuard AI</div><div class="brand-sub">Digital Forensics</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nav-caption">Command center</div>', unsafe_allow_html=True)
    nav = [("◉", "Overview"), ("⌁", "Analyze"), ("◷", "History"), ("◇", "Models")]
    for glyph, name in nav:
        if st.button(f"{glyph}  {name}", key=f"nav_{name}", use_container_width=True, type="primary" if st.session_state["page"] == name else "secondary"):
            st.session_state["page"] = name
            st.rerun()

    st.markdown('<div class="nav-caption">System</div>', unsafe_allow_html=True)
    with st.expander("Connection settings", expanded=False):
        api_input = st.text_input("FastAPI URL", st.session_state["api_url"])
        if api_input.strip() != st.session_state["api_url"]:
            st.session_state["api_url"] = api_input.strip().rstrip("/")
            API_URL = st.session_state["api_url"]
            st.rerun()

    try:
        health_response = api_get("/api/health")
        health = health_response.json() if health_response.ok else {}
        online = health_response.ok
    except requests.RequestException:
        health, online = {}, False

    model_name = str(health.get("model", "—"))
    device = str(health.get("device", "—"))
    weights = "Loaded" if health.get("weights_loaded") else "Fallback / forensic"
    st.markdown(
        f'<div class="sidebar-status"><div class="status-title"><span class="dot {" " if online else "off"}"></span>{"System operational" if online else "API unavailable"}</div>'
        f'<div class="status-meta">Model · {escape(model_name)}<br>Device · {escape(device)}<br>Weights · {escape(weights)}</div></div>',
        unsafe_allow_html=True,
    )


page = st.session_state["page"]
st.markdown(
    f'<div class="topline"><div class="breadcrumb">DeepGuard AI / <b>{escape(page)}</b></div>'
    f'<div class="pill"><span class="dot {" " if online else "off"}"></span>{"LIVE ENGINE" if online else "OFFLINE"}</div></div>',
    unsafe_allow_html=True,
)


if page == "Overview":
    st.markdown(
        '<div class="hero"><div class="eyebrow">Security command center</div><h1>See the signal. Follow the evidence.</h1>'
        '<p>A professional workspace for deepfake detection, forensic inspection, model intelligence, and investigation review.</p></div>',
        unsafe_allow_html=True,
    )
    total = len(st.session_state["history"])
    fake = sum(str(x["prediction"]).upper() == "FAKE" for x in st.session_state["history"])
    real = sum(str(x["prediction"]).upper() == "REAL" for x in st.session_state["history"])
    avg = sum(float(x["confidence"] or 0) for x in st.session_state["history"]) / total if total else 0

    cols = st.columns(4)
    for col, (label, value, note, color) in zip(cols, [
        ("Investigations", total, "This browser session", "var(--cyan)"),
        ("Flagged", fake, "Likely manipulated", "var(--red)"),
        ("Cleared", real, "Classified real", "var(--green)"),
        ("Avg confidence", pct(avg), "Current session", "var(--purple)"),
    ]):
        with col:
            st.markdown(f'<div class="metric" style="--metric-color:{color}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-head"><h2>Quick actions</h2><span>Choose an investigation path</span></div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    for col, title, copy, glyph, target in [
        (a, "Single investigation", "Upload one evidence file and inspect a complete forensic result.", "⌁", "Analyze"),
        (b, "Batch screening", "Screen multiple files sequentially for rapid triage.", "▦", "Analyze"),
        (c, "Live capture", "Capture a webcam frame and evaluate it in real time.", "◉", "Analyze"),
    ]:
        with col:
            st.markdown(f'<div class="action-card"><div class="action-icon">{glyph}</div><div class="action-title">{title}</div><div class="action-copy">{copy}</div></div>', unsafe_allow_html=True)
            if st.button(f"Open {title}  →", key=f"quick_{target}_{title}", use_container_width=True):
                st.session_state["page"] = target
                st.session_state["analysis_mode"] = "Single" if "Single" in title else ("Batch" if "Batch" in title else "Live")
                st.rerun()

    st.markdown('<div class="section-head"><h2>Recent investigations</h2><span>Latest 5</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    if not st.session_state["history"]:
        st.markdown('<div style="padding:2rem;text-align:center;color:#667181;font-size:.72rem">No investigations yet. Start a scan to populate the command center.</div>', unsafe_allow_html=True)
    else:
        for i, item in enumerate(st.session_state["history"][:5]):
            cls = verdict_class(item["prediction"])
            st.markdown(
                f'<div class="history-row"><div><div class="filename">{escape(item["filename"])}</div><div class="muted">{escape(item["model"])}</div></div>'
                f'<div><span class="badge {cls}">{escape(str(item["prediction"]).upper())}</span></div><div class="muted">{pct(item["confidence"])}</div><div class="muted">{item["created"]}</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("Inspect", key=f"inspect_home_{i}"):
                st.session_state["last_result"] = item["result"]
                st.session_state["page"] = "History"
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


elif page == "Analyze":
    st.markdown(
        '<div class="hero"><div class="eyebrow">Investigation workspace</div><h1>Analyze digital evidence.</h1>'
        '<p>Choose your workflow, configure the inference engine, and keep the resulting evidence in one place.</p></div>',
        unsafe_allow_html=True,
    )
    modes = ["Single", "Batch", "Live"]
    default_mode = st.session_state.get("analysis_mode", "Single")
    mode = st.segmented_control("Workflow", modes, default=default_mode if default_mode in modes else "Single", label_visibility="collapsed")
    st.session_state["analysis_mode"] = mode

    if mode == "Single":
        left, right = st.columns([1.3, .7], gap="large")
        with left:
            st.markdown('<div class="scan-zone"><div class="scan-zone-inner"><div><div class="scan-icon">↥</div><div class="scan-title">Drop evidence into the investigation</div><div class="scan-copy">Image · PDF · video · audio · maximum 100 MB</div></div></div>', unsafe_allow_html=True)
            uploaded = st.file_uploader("Evidence file", type=MEDIA_TYPES, label_visibility="collapsed", key="single_upload")
            st.markdown("</div>", unsafe_allow_html=True)
            if uploaded and uploaded.type.startswith("image/"):
                st.image(uploaded, caption="Evidence preview", width=500)

        with right:
            st.markdown('<div class="panel"><div class="panel-title">Inference configuration</div><div class="panel-sub">Select the engine and analysis depth.</div><br>', unsafe_allow_html=True)
            model = st.selectbox("Detection engine", ["automatic multimodal"], index=0)
            ensemble = False
            st.markdown('<div class="muted" style="margin:.55rem 0 1rem">DeepGuard automatically routes images, PDFs, audio, and video to their modality-specific detector and evidence pipeline.</div>', unsafe_allow_html=True)
            run = st.button("Run forensic analysis  →", type="primary", use_container_width=True, disabled=uploaded is None)
            st.markdown("</div>", unsafe_allow_html=True)

        if run and uploaded:
            with st.spinner("Executing forensic pipeline…"):
                try:
                    response = api_post_file("/api/detect/public", uploaded, model_name="automatic", ensemble="false")
                    if response.ok:
                        save_result(response.json(), uploaded.name)
                        st.success("Investigation completed.")
                    else:
                        try:
                            st.error(response.json().get("detail", response.text))
                        except ValueError:
                            st.error(response.text)
                except requests.RequestException as exc:
                    st.error("Could not reach FastAPI: " + str(exc))

        if st.session_state.get("last_result"):
            st.markdown('<div class="section-head"><h2>Investigation result</h2><span>Latest analysis</span></div>', unsafe_allow_html=True)
            render_result(st.session_state["last_result"])

    elif mode == "Batch":
        st.markdown('<div class="panel"><div class="panel-title">Batch screening</div><div class="panel-sub">Process up to eight evidence files through the public detection endpoint.</div><br>', unsafe_allow_html=True)
        files = st.file_uploader("Evidence files", type=MEDIA_TYPES, accept_multiple_files=True, label_visibility="collapsed", key="batch_upload")
        if files:
            st.caption(f"{len(files)} evidence file(s) selected")
            if len(files) > 8:
                st.error("Maximum 8 files per batch.")
            elif st.button("Start batch screening  →", type="primary"):
                progress = st.progress(0)
                rows = []
                for i, file in enumerate(files, 1):
                    try:
                        response = api_post_file("/api/detect/public", file, model_name="efficientnet", ensemble="false")
                        if response.ok:
                            result = response.json()
                            save_result(result, file.name)
                            rows.append((file.name, result))
                        else:
                            rows.append((file.name, {"prediction": "ERROR", "confidence": 0}))
                    except requests.RequestException:
                        rows.append((file.name, {"prediction": "ERROR", "confidence": 0}))
                    progress.progress(i / len(files))
                st.success(f"Batch complete · {len(rows)} file(s) processed")
                for filename, result in rows:
                    cls = verdict_class(result.get("prediction", "ERROR"))
                    st.markdown(f'<div class="history-row"><div class="filename">{escape(filename)}</div><div><span class="badge {cls}">{escape(str(result.get("prediction","ERROR")).upper())}</span></div><div class="muted">{pct(result.get("confidence"))}</div><div class="muted">{escape(str(result.get("model_name","efficientnet")))}</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="panel"><div class="panel-title">Live capture</div><div class="panel-sub">Capture a webcam frame and submit it to the live inference endpoint.</div><br>', unsafe_allow_html=True)
        camera = st.camera_input("Capture evidence", label_visibility="collapsed")
        if camera and st.button("Analyze live frame  →", type="primary"):
            try:
                with st.spinner("Analyzing live frame…"):
                    response = requests.post(API_URL + "/api/detect/live", files={"file": ("frame.jpg", camera.getvalue(), "image/jpeg")}, data={"include_heatmap": "true"}, timeout=120)
                if response.ok:
                    result = response.json()
                    save_result(result, "live-frame.jpg")
                    render_result(result)
                else:
                    st.error(response.text)
            except requests.RequestException as exc:
                st.error("Could not reach FastAPI: " + str(exc))
        st.markdown("</div>", unsafe_allow_html=True)


elif page == "History":
    st.markdown(
        '<div class="hero"><div class="eyebrow">Case review</div><h1>Investigation history.</h1>'
        '<p>Review, reopen, and inspect results generated during this browser session.</p></div>',
        unsafe_allow_html=True,
    )
    if not st.session_state["history"]:
        st.markdown('<div class="panel" style="text-align:center;padding:3rem"><div class="panel-title">No investigations yet</div><div class="panel-sub">Completed scans will appear here.</div></div>', unsafe_allow_html=True)
    else:
        for i, item in enumerate(st.session_state["history"]):
            cls = verdict_class(item["prediction"])
            c1, c2, c3, c4, c5 = st.columns([1.6,.65,.7,.55,.5])
            with c1:
                st.markdown(f'<div class="filename">{escape(item["filename"])}</div><div class="muted">{escape(item["model"])}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<span class="badge {cls}">{escape(str(item["prediction"]).upper())}</span>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="muted">{pct(item["confidence"])}</div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="muted">{item["created"]}</div>', unsafe_allow_html=True)
            with c5:
                if st.button("Open", key=f"open_history_{i}"):
                    st.session_state["last_result"] = item["result"]
                    st.rerun()
            st.divider()
    if st.session_state.get("last_result"):
        st.markdown('<div class="section-head"><h2>Selected investigation</h2><span>Evidence detail</span></div>', unsafe_allow_html=True)
        render_result(st.session_state["last_result"])


else:
    st.markdown(
        '<div class="hero"><div class="eyebrow">Model intelligence</div><h1>Detection models.</h1>'
        '<p>Inspect the model registry exposed by the current FastAPI runtime and understand the available inference paths.</p></div>',
        unsafe_allow_html=True,
    )
    try:
        response = api_get("/api/detect/models")
        if response.ok:
            payload = response.json()
            models = payload.get("models", [])
            if models:
                cols = st.columns(2)
                for i, item in enumerate(models):
                    with cols[i % 2]:
                        st.markdown(
                            f'<div class="panel" style="margin-bottom:1rem"><div class="eyebrow">PHASE {escape(str(item.get("phase","—")))}</div>'
                            f'<div class="panel-title" style="margin-top:.35rem">{escape(str(item.get("name","Model")))}</div>'
                            f'<div class="panel-sub" style="margin-top:.45rem">{escape(str(item.get("description","")))}</div>'
                            f'<div class="muted" style="margin-top:.75rem">Modalities · {escape(" · ".join(item.get("modalities", [])))}</div></div>',
                            unsafe_allow_html=True,
                        )
            st.markdown('<div class="section-head"><h2>Runtime capabilities</h2><span>Current backend</span></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="panel"><div class="history-row"><div class="filename">Default model</div><div class="muted">{escape(str(payload.get("default","—")))}</div><div class="muted">Weights</div><div class="muted">{escape(str(payload.get("weights_loaded","—")))}</div></div>'
                f'<div class="history-row"><div class="filename">Inference mode</div><div class="muted">{escape(str(payload.get("inference_mode","—")))}</div><div class="muted">Endpoint</div><div class="muted">/api/detect/public</div></div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.error(response.text)
    except requests.RequestException as exc:
        st.error("Could not load model registry: " + str(exc))


st.markdown(
    '<div style="border-top:1px solid rgba(255,255,255,.07);margin-top:2.5rem;padding-top:1rem;color:#4e5968;font-size:.62rem;display:flex;justify-content:space-between">'
    '<span>DEEPGUARD AI · DIGITAL FORENSICS</span><span>Probabilistic decision-support · verify high-stakes findings</span></div>',
    unsafe_allow_html=True,
)
