import os, requests, streamlit as st
st.set_page_config(page_title="DeepGuard AI", page_icon="🛡️", layout="wide")
API_URL = os.getenv("DEEPGUARD_API_URL", "http://localhost:8000").rstrip("/")
st.title("🛡️ DeepGuard AI")
st.caption("AI-powered deepfake detection with forensic analysis and explainable results.")
with st.sidebar:
    st.header("API Configuration")
    API_URL = st.text_input("FastAPI URL", API_URL).rstrip("/")
    try:
        h = requests.get(API_URL + "/api/health", timeout=10).json()
        st.success("API: " + str(h.get("status", "unknown")).upper())
        st.caption("Model: " + str(h.get("model", "unknown")))
        st.caption("Device: " + str(h.get("device", "unknown")))
    except requests.RequestException:
        st.error("FastAPI is unavailable")
tab1, tab2, tab3, tab4 = st.tabs(["🔎 Scan", "📦 Batch", "📹 Live", "🧠 Models"])
with tab1:
    st.subheader("Analyze media")
    f = st.file_uploader("Upload image, video, or audio", type=["jpg","jpeg","png","webp","bmp","mp4","mov","avi","mkv","webm","mp3","wav","m4a","flac"])
    model = st.selectbox("Model", ["efficientnet", "xception", "vit"])
    ensemble = st.checkbox("Enable ensemble analysis")
    if f and st.button("Run Deepfake Analysis", type="primary", use_container_width=True):
        with st.spinner("Running forensic analysis..."):
            try:
                r = requests.post(API_URL + "/api/detect/public", files={"file": (f.name, f.getvalue(), f.type)}, data={"model_name": model, "ensemble": str(ensemble).lower()}, timeout=300)
                if r.ok:
                    data = r.json()
                    c1,c2,c3 = st.columns(3)
                    c1.metric("Verdict", data.get("prediction","UNKNOWN"))
                    c2.metric("Confidence", "{:.1f}%".format(float(data.get("confidence",0))*100))
                    c3.metric("Fake probability", "{:.1f}%".format(float(data.get("fake_probability",0))*100))
                    st.write("Risk level:", data.get("risk_level") or "unknown")
                    if data.get("explanation"):
                        st.subheader("Forensic explanation")
                        for item in data["explanation"]: st.write("• " + str(item))
                    with st.expander("Technical details"): st.json(data.get("details") or {})
                else: st.error(r.text)
            except requests.RequestException as e: st.error("API request failed: " + str(e))
with tab2:
    st.subheader("Batch analysis")
    fs = st.file_uploader("Upload up to 8 files", accept_multiple_files=True, type=["jpg","jpeg","png","webp","mp4","mov","avi","mkv","webm","mp3","wav","m4a","flac"], key="batch")
    if fs and len(fs) <= 8 and st.button("Analyze batch", type="primary"):
        files = [("files", (x.name, x.getvalue(), x.type)) for x in fs]
        try:
            with st.spinner("Analyzing batch..."): r = requests.post(API_URL + "/api/detect/batch", files=files, timeout=600)
            if r.ok:
                d=r.json(); st.success("{} scans complete — {} FAKE, {} REAL.".format(d["total"],d["fake_count"],d["real_count"]))
                for x in d["items"]: st.write("**{}** — {:.1f}%".format(x["prediction"],float(x["confidence"])*100))
            else: st.error(r.text)
        except requests.RequestException as e: st.error("API request failed: " + str(e))
with tab3:
    st.subheader("Live frame analysis")
    cam = st.camera_input("Capture a frame")
    if cam and st.button("Analyze frame", type="primary"):
        try:
            r=requests.post(API_URL + "/api/detect/live", files={"file":("frame.jpg",cam.getvalue(),"image/jpeg")}, data={"include_heatmap":"true"}, timeout=120)
            if r.ok:
                d=r.json(); st.metric("Verdict",d.get("prediction","UNKNOWN")); st.metric("Fake probability","{:.1f}%".format(float(d.get("fake_probability",0))*100))
            else: st.error(r.text)
        except requests.RequestException as e: st.error("API request failed: " + str(e))
with tab4:
    st.subheader("Detection models")
    try:
        r=requests.get(API_URL + "/api/detect/models",timeout=10)
        for x in r.json().get("models",[]):
            with st.expander("{} · Phase {}".format(x["name"],x["phase"])): st.write(x["description"]); st.caption("Modalities: "+", ".join(x["modalities"]))
    except requests.RequestException: st.error("Could not load model information.")
st.divider()
st.caption("DeepGuard AI provides probabilistic forensic decision-support; independently verify high-stakes decisions.")