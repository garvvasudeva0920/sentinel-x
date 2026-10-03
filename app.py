import streamlit as st
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go

st.set_page_config(
    page_title="SENTINEL-X | Cyber AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Styling ----------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at 15% 10%, #102448 0%, #070d1c 38%, #050912 100%);
    color: #eef5ff;
}
.block-container {padding-top: 1.4rem; max-width: 1400px;}
.hero {
    padding: 22px 26px;
    border: 1px solid #203b67;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(11,28,57,.96), rgba(9,16,34,.96));
    box-shadow: 0 12px 40px rgba(0,0,0,.25);
}
.kicker {color:#00e5ff; font-size:13px; font-weight:700; letter-spacing:2px;}
.hero h1 {font-size:42px; margin:4px 0 2px; color:#f5f8ff;}
.hero p {color:#b9cbe7; font-size:16px; margin:0;}
.metric {
    background:#0d1b35; border:1px solid #213b66; border-radius:14px;
    padding:16px; min-height:112px;
}
.metric .label {color:#8ea9cf; font-size:12px; text-transform:uppercase; letter-spacing:1px;}
.metric .value {font-size:30px; font-weight:800; margin-top:5px;}
.panel {
    background:#0b1730; border:1px solid #203b67; border-radius:16px; padding:18px;
}
.small {color:#9fb5d7; font-size:13px;}
.status-high {color:#ff4c5b; font-weight:800;}
.status-normal {color:#30e19a; font-weight:800;}
.evidence {padding:9px 12px; margin:6px 0; background:#101f3d; border-radius:9px; color:#dbe8fb;}
div.stButton > button {
    width:100%; border-radius:10px; font-weight:700; min-height:45px;
}
</style>
""", unsafe_allow_html=True)

# ---------- Baseline + model ----------
rng = np.random.default_rng(42)
normal_train = pd.DataFrame({
    "outbound_mb": rng.normal(18, 3, 600).clip(5),
    "connections": rng.normal(38, 7, 600).clip(5),
    "new_destinations": rng.poisson(1, 600),
    "login_events": rng.normal(7, 2, 600).clip(0),
})
features = ["outbound_mb", "connections", "new_destinations", "login_events"]

model = IsolationForest(
    n_estimators=180,
    contamination=0.04,
    random_state=42
)
model.fit(normal_train[features])

baseline = normal_train[features].mean()

def get_event(simulated=False):
    if simulated:
        return {
            "outbound_mb": float(rng.normal(66, 5)),
            "connections": float(rng.normal(92, 10)),
            "new_destinations": int(rng.integers(6, 11)),
            "login_events": float(rng.normal(17, 3)),
            "device_changed": True,
        }
    return {
        "outbound_mb": float(rng.normal(18, 2.2)),
        "connections": float(rng.normal(38, 5)),
        "new_destinations": int(rng.integers(0, 3)),
        "login_events": float(rng.normal(7, 1.4)),
        "device_changed": False,
    }

def score_event(event):
    x = pd.DataFrame([event])[features]
    decision = model.decision_function(x)[0]
    # Convert Isolation Forest decision into an easy-to-read anomaly percentage.
    anomaly = float(np.clip(50 - decision * 55, 1, 99))

    volume_ratio = event["outbound_mb"] / max(baseline["outbound_mb"], 1)
    connection_ratio = event["connections"] / max(baseline["connections"], 1)

    context = 0
    if event["device_changed"]:
        context += 24
    if event["new_destinations"] >= 4:
        context += 28
    if volume_ratio >= 2.5:
        context += 25
    if connection_ratio >= 2:
        context += 20
    context = min(context, 100)

    threat_confidence = float(np.clip(
        12 + anomaly * 0.42 + context * 0.38, 0, 99
    ))
    risk = float(np.clip(
        anomaly * 0.50 + threat_confidence * 0.25 + context * 0.25, 0, 100
    ))

    return anomaly, threat_confidence, context, risk, volume_ratio, connection_ratio

# ---------- Session state ----------
if "simulated" not in st.session_state:
    st.session_state.simulated = False
if "history" not in st.session_state:
    st.session_state.history = [12, 11, 13, 10, 12, 11]

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <div class="kicker">CYBER AI HACKATHON 2026 • DEFENSIVE SECURITY MVP</div>
  <h1>🛡️ SENTINEL-X</h1>
  <p>Adaptive AI detection for previously unseen behavioural anomalies in cloud networks</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# ---------- Controls ----------
c1, c2, c3 = st.columns([1.4, 1.4, 4.2])
with c1:
    if st.button("⚡ Simulate Behavioural Shift"):
        st.session_state.simulated = True
        st.session_state.history = [12, 11, 13, 10, 12, 11, 18, 34, 57, 73, 87]
        st.rerun()
with c2:
    if st.button("↺ Reset Baseline"):
        st.session_state.simulated = False
        st.session_state.history = [12, 11, 13, 10, 12, 11]
        st.rerun()
with c3:
    st.markdown(
        '<div class="small" style="padding:10px 0 0 10px;">'
        'Safe demo mode: all telemetry is synthetic and generated inside the application.'
        '</div>',
        unsafe_allow_html=True
    )

event = get_event(st.session_state.simulated)
anomaly, threat, context, risk, volume_ratio, connection_ratio = score_event(event)

status = "HIGH RISK" if risk >= 70 else ("MEDIUM" if risk >= 35 else "NORMAL")
status_class = "status-high" if risk >= 70 else "status-normal"

# ---------- Metrics ----------
m1, m2, m3, m4 = st.columns(4)
for col, label, value, suffix in [
    (m1, "Risk Score", f"{risk:.0f}", "/100"),
    (m2, "Anomaly Score", f"{anomaly:.0f}", "%"),
    (m3, "Threat Confidence", f"{threat:.0f}", "%"),
    (m4, "Behaviour State", status, ""),
]:
    with col:
        col.markdown(
            f'<div class="metric"><div class="label">{label}</div>'
            f'<div class="value">{value}<span style="font-size:16px;color:#8ea9cf">{suffix}</span></div></div>',
            unsafe_allow_html=True
        )

st.write("")

# ---------- Main panels ----------
left, right = st.columns([1.65, 1])

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("📈 Behavioural Risk Timeline")
    hist = st.session_state.history
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, len(hist)+1)),
        y=hist,
        mode="lines+markers",
        line=dict(width=3, color="#00e5ff"),
        marker=dict(size=7, color="#00e5ff"),
        fill="tozeroy",
        fillcolor="rgba(0,229,255,0.08)"
    ))
    fig.add_hline(y=70, line_dash="dash", line_color="#ff4c5b",
                  annotation_text="HIGH-RISK THRESHOLD")
    fig.update_layout(
        height=310, margin=dict(l=10,r=10,t=10,b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b9cbe7"),
        xaxis=dict(title="Event sequence", gridcolor="#1a3155"),
        yaxis=dict(title="Risk", range=[0,100], gridcolor="#1a3155"),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🔎 Why did SENTINEL-X flag this?")
    evidence = []
    if volume_ratio >= 2.5:
        evidence.append(f"Outbound traffic is {volume_ratio:.1f}× above baseline.")
    else:
        evidence.append("Outbound traffic remains near the learned baseline.")
    if event["new_destinations"] >= 4:
        evidence.append("Previously unseen destination pattern detected.")
    else:
        evidence.append("Destination behaviour is within the expected range.")
    if connection_ratio >= 2:
        evidence.append("Connection burst is significantly above baseline.")
    else:
        evidence.append("Connection rate is within expected range.")
    if event["device_changed"]:
        evidence.append("Identity/device context changed during the event.")
    else:
        evidence.append("Identity/device context matches the expected profile.")
    for e in evidence:
        st.markdown(f'<div class="evidence">✓ {e}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<p style="margin-top:14px">Decision: <span class="{status_class}">{status}</span></p>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# ---------- Telemetry + recommendation ----------
a, b = st.columns(2)
with a:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("📡 Live Telemetry")
    telemetry = pd.DataFrame({
        "Signal": [
            "Outbound traffic",
            "Connection rate",
            "New destinations",
            "Device context"
        ],
        "Current": [
            f"{event['outbound_mb']:.1f} MB",
            f"{event['connections']:.0f}",
            str(event["new_destinations"]),
            "CHANGED" if event["device_changed"] else "EXPECTED"
        ],
        "Baseline": [
            f"{baseline['outbound_mb']:.1f} MB",
            f"{baseline['connections']:.0f}",
            "~1",
            "EXPECTED"
        ]
    })
    st.dataframe(telemetry, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

with b:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("🤖 Recommended Response")
    if risk >= 70:
        recommendation = "INVESTIGATE + CONTROLLED CONTAINMENT"
        detail = "Escalate to an analyst, preserve evidence and consider isolating the affected workload after human approval."
    elif risk >= 35:
        recommendation = "INVESTIGATE"
        detail = "Collect more context and monitor the workload for continued deviation."
    else:
        recommendation = "MONITOR"
        detail = "No immediate containment recommended; continue baseline monitoring."
    st.markdown(f"### {recommendation}")
    st.write(detail)
    st.caption("SENTINEL-X separates detection from response. High-risk scores do not automatically execute destructive actions.")
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")
st.caption("SENTINEL-X • Explainable behavioural anomaly detection • Hackathon demonstration • Synthetic telemetry only")
