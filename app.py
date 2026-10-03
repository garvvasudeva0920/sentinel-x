import streamlit as st
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import plotly.graph_objects as go
import plotly.express as px

# ============================================================
# SENTINEL-X — Cyber AI Hackathon 2026
# Safe, synthetic defensive-security demonstration
# ============================================================

st.set_page_config(
    page_title="SENTINEL-X | Adaptive Cyber AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- CSS ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background:
      radial-gradient(circle at 8% 0%, rgba(0,229,255,.10), transparent 28%),
      radial-gradient(circle at 100% 15%, rgba(93,82,255,.10), transparent 30%),
      #050914;
    color: #edf5ff;
}
.block-container { max-width: 1500px; padding-top: 1.0rem; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#071124,#050914);
    border-right: 1px solid #182d4e;
}
.hero {
    border: 1px solid #21436f;
    border-radius: 22px;
    padding: 25px 30px;
    background: linear-gradient(115deg, rgba(10,28,58,.96), rgba(8,14,29,.92));
    box-shadow: 0 20px 70px rgba(0,0,0,.28);
}
.hero-kicker { color:#00e5ff; font-size:12px; font-weight:800; letter-spacing:2.2px; }
.hero-title { font-size:42px; line-height:1.05; font-weight:800; margin:7px 0 7px; }
.hero-sub { color:#a9bfde; font-size:15px; }
.pill {
    display:inline-block; padding:5px 10px; border-radius:999px;
    background:#0c2947; border:1px solid #1d507b; color:#74eaff;
    font-size:11px; font-weight:700; margin-right:6px;
}
.card {
    background: linear-gradient(145deg,#0a1831,#081224);
    border:1px solid #1c365b; border-radius:17px; padding:18px;
    box-shadow: 0 10px 35px rgba(0,0,0,.15);
}
.card-title { color:#a9bfde; text-transform:uppercase; letter-spacing:1.2px;
    font-size:11px; font-weight:700; }
.metric-value { font-size:30px; font-weight:800; margin-top:5px; }
.metric-delta { font-size:12px; color:#65e6b0; }
.metric-delta-warn { font-size:12px; color:#ff7380; }
.section-title { font-size:22px; font-weight:800; margin:5px 0 3px; }
.muted { color:#829bbd; font-size:12px; }
.alert {
    border-radius:14px; padding:14px 16px; margin:5px 0;
    border:1px solid #6d2533; background:rgba(108,25,43,.25);
}
.alert-title { color:#ff6f7d; font-weight:800; }
.ok {
    border-radius:14px; padding:14px 16px; margin:5px 0;
    border:1px solid #185a4a; background:rgba(20,115,88,.16);
}
.ok-title { color:#5fe5ae; font-weight:800; }
.step {
    padding:13px 15px; border-radius:12px; background:#0c1b35;
    border:1px solid #1b3558; min-height:80px;
}
.step-num { color:#00e5ff; font-weight:800; font-size:12px; }
.step-name { font-weight:700; margin-top:4px; }
.step-desc { color:#8ea8c8; font-size:11px; margin-top:3px; }
div.stButton > button {
    border-radius:11px; min-height:42px; font-weight:700;
    border:1px solid #24476f;
}
div[data-testid="stMetric"] {
    background:#0a1831; border:1px solid #1c365b; border-radius:14px; padding:12px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------- Model ------------------------------
rng = np.random.default_rng(7)
features = ["outbound_mb", "connections", "new_destinations", "login_events"]

normal_train = pd.DataFrame({
    "outbound_mb": rng.normal(18, 3, 1000).clip(4),
    "connections": rng.normal(40, 7, 1000).clip(5),
    "new_destinations": rng.poisson(1, 1000),
    "login_events": rng.normal(7, 2, 1000).clip(0),
})

model = IsolationForest(
    n_estimators=250,
    contamination=0.035,
    random_state=7
)
model.fit(normal_train[features])
baseline = normal_train[features].median()

def safe_event(incident=False):
    if incident:
        return {
            "outbound_mb": float(rng.normal(82, 7)),
            "connections": float(rng.normal(108, 11)),
            "new_destinations": int(rng.integers(7, 12)),
            "login_events": float(rng.normal(20, 3)),
            "new_device": True,
            "geo_shift": True,
        }
    return {
        "outbound_mb": float(rng.normal(18, 2.5)),
        "connections": float(rng.normal(40, 5)),
        "new_destinations": int(rng.integers(0, 3)),
        "login_events": float(rng.normal(7, 1.5)),
        "new_device": False,
        "geo_shift": False,
    }

def analyze(e):
    x = pd.DataFrame([e])[features]
    raw = model.decision_function(x)[0]
    anomaly = float(np.clip(50 - raw * 58, 1, 99))

    volume = e["outbound_mb"] / max(baseline["outbound_mb"], 1)
    conn = e["connections"] / max(baseline["connections"], 1)
    context = 0
    reasons = []

    if volume > 2.5:
        context += 27
        reasons.append(f"Outbound volume is {volume:.1f}× above the learned baseline.")
    if conn > 2:
        context += 22
        reasons.append(f"Connection burst is {conn:.1f}× above the learned baseline.")
    if e["new_destinations"] >= 4:
        context += 24
        reasons.append("Destination novelty is outside the learned behavioural profile.")
    if e["new_device"]:
        context += 15
        reasons.append("A new device context is associated with the session.")
    if e["geo_shift"]:
        context += 12
        reasons.append("A geographic context shift increases the risk signal.")

    if not reasons:
        reasons = [
            "Traffic volume is consistent with the learned baseline.",
            "Destination novelty is within the expected range.",
            "Identity/device context is consistent with the profile.",
        ]

    confidence = float(np.clip(10 + anomaly*.48 + context*.32, 0, 99))
    risk = float(np.clip(anomaly*.52 + confidence*.25 + context*.23, 0, 100))

    return risk, anomaly, confidence, reasons, volume, conn

# ------------------------- State ------------------------------
if "incident" not in st.session_state:
    st.session_state.incident = False
if "events" not in st.session_state:
    st.session_state.events = 0
if "history" not in st.session_state:
    st.session_state.history = [10,12,11,13,12,14,11]
if "last_risk" not in st.session_state:
    st.session_state.last_risk = 12

# ------------------------- Sidebar ----------------------------
with st.sidebar:
    st.markdown("## 🛡️ SENTINEL-X")
    st.caption("Adaptive behavioural defence")
    st.markdown("---")
    st.markdown("**DEMO CONTROLS**")
    if st.button("⚡ Trigger synthetic anomaly", use_container_width=True):
        st.session_state.incident = True
        st.session_state.events += 1
        st.session_state.history += [22, 36, 51, 68, 84, 91]
        st.session_state.last_risk = 91
        st.rerun()
    if st.button("↺ Return to normal", use_container_width=True):
        st.session_state.incident = False
        st.session_state.events += 1
        st.session_state.history = [10,12,11,13,12,14,11]
        st.session_state.last_risk = 12
        st.rerun()
    st.markdown("---")
    st.markdown("**ENGINE STATUS**")
    st.success("AI detector online")
    st.success("Behaviour baseline loaded")
    st.success("Explainability engine online")
    st.markdown("---")
    st.caption("All telemetry shown in this MVP is synthetic. No external systems are attacked or modified.")

# ------------------------- Header ------------------------------
st.markdown("""
<div class="hero">
  <div class="hero-kicker">CYBER AI HACKATHON 2026 • DEFENSIVE SECURITY • MVP</div>
  <div class="hero-title">🛡️ SENTINEL-X</div>
  <div class="hero-sub">
    Adaptive AI that learns normal behaviour and surfaces previously unseen anomalies
    before they become high-impact incidents.
  </div>
  <div style="margin-top:13px">
    <span class="pill">ANOMALY DETECTION</span>
    <span class="pill">EXPLAINABLE AI</span>
    <span class="pill">CLOUD TELEMETRY</span>
    <span class="pill">HUMAN-IN-THE-LOOP</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.write("")

event = safe_event(st.session_state.incident)
risk, anomaly, confidence, reasons, volume_ratio, conn_ratio = analyze(event)
st.session_state.last_risk = risk

state = "HIGH RISK" if risk >= 70 else ("ELEVATED" if risk >= 35 else "NORMAL")
state_color = "#ff6878" if risk >= 70 else ("#ffc857" if risk >= 35 else "#5fe5ae")

# ---------------------- KPI row --------------------------------
cols = st.columns(5)
kpis = [
    ("RISK SCORE", f"{risk:.0f}/100", "Real-time decision score"),
    ("ANOMALY", f"{anomaly:.0f}%", "Deviation from baseline"),
    ("CONFIDENCE", f"{confidence:.0f}%", "Model + context confidence"),
    ("NOVEL SIGNALS", str(event["new_destinations"]), "New destinations observed"),
    ("STATE", state, "Current behavioural state"),
]
for c, (label, value, sub) in zip(cols, kpis):
    with c:
        st.markdown(
            f'<div class="card"><div class="card-title">{label}</div>'
            f'<div class="metric-value" style="color:{state_color if label=="STATE" else "#edf5ff"}">{value}</div>'
            f'<div class="muted">{sub}</div></div>',
            unsafe_allow_html=True
        )

st.write("")

# ---------------------- Navigation -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 SOC COMMAND CENTER",
    "🧠 AI EXPLAINABILITY",
    "🔬 DETECTION ENGINE",
    "📋 INCIDENT REPORT"
])

# ======================== TAB 1 ================================
with tab1:
    left, right = st.columns([1.65, 1])

    with left:
        st.markdown('<div class="section-title">Behavioural risk evolution</div>', unsafe_allow_html=True)
        st.markdown('<div class="muted">The detector watches deviation, not a fixed attack signature.</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=st.session_state.history,
            x=list(range(1, len(st.session_state.history)+1)),
            mode="lines+markers",
            line=dict(color="#00e5ff", width=3),
            marker=dict(color="#00e5ff", size=7),
            fill="tozeroy",
            fillcolor="rgba(0,229,255,.07)"
        ))
        fig.add_hline(y=70, line_dash="dash", line_color="#ff6878",
                      annotation_text="HIGH-RISK")
        fig.update_layout(
            height=350, margin=dict(l=0,r=0,t=15,b=0),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#9db4d4"),
            xaxis=dict(title="Event sequence", gridcolor="#172e50"),
            yaxis=dict(title="Risk score", range=[0,100], gridcolor="#172e50"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        if risk >= 70:
            st.markdown(f"""
            <div class="alert">
              <div class="alert-title">🔴 HIGH-RISK BEHAVIOUR DETECTED</div>
              <div style="margin-top:6px;color:#c7d6ea">
                Multiple behavioural signals jointly exceed the learned profile.
                This is a detection decision, not proof of compromise.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="ok">
              <div class="ok-title">🟢 BASELINE BEHAVIOUR</div>
              <div style="margin-top:6px;color:#b9d8ce">
                Current telemetry remains consistent with the learned profile.
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Detection chain")
        chain = [
            ("01","COLLECT","Synthetic cloud/network telemetry"),
            ("02","BASELINE","Learn normal behavioural profile"),
            ("03","DETECT","Isolation Forest anomaly scoring"),
            ("04","CORRELATE","Contextual risk enrichment"),
            ("05","EXPLAIN","Human-readable evidence"),
        ]
        for n, name, desc in chain:
            st.markdown(
                f'<div class="step"><span class="step-num">{n}</span>'
                f'<div class="step-name">{name}</div><div class="step-desc">{desc}</div></div>',
                unsafe_allow_html=True
            )

    st.write("")
    a,b,c = st.columns(3)
    with a:
        st.markdown(f'<div class="card"><div class="card-title">OUTBOUND TRAFFIC</div><div class="metric-value">{event["outbound_mb"]:.1f} MB</div><div class="muted">Baseline: {baseline["outbound_mb"]:.1f} MB</div></div>', unsafe_allow_html=True)
    with b:
        st.markdown(f'<div class="card"><div class="card-title">CONNECTION RATE</div><div class="metric-value">{event["connections"]:.0f}</div><div class="muted">Baseline: {baseline["connections"]:.0f}</div></div>', unsafe_allow_html=True)
    with c:
        st.markdown(f'<div class="card"><div class="card-title">IDENTITY CONTEXT</div><div class="metric-value">{("CHANGED" if event["new_device"] else "EXPECTED")}</div><div class="muted">Device + geography context</div></div>', unsafe_allow_html=True)

# ======================== TAB 2 ================================
with tab2:
    st.markdown('<div class="section-title">Why did the AI flag this?</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">SENTINEL-X exposes the evidence behind its score instead of returning a black-box alert.</div>', unsafe_allow_html=True)
    st.write("")
    l,r = st.columns([1.1,1])

    with l:
        reason_df = pd.DataFrame({
            "Signal": ["Traffic deviation","Connection burst","Destination novelty","Identity context","Geo context"],
            "Contribution": [
                max(0, volume_ratio*22),
                max(0, conn_ratio*18),
                event["new_destinations"]*6,
                15 if event["new_device"] else 0,
                12 if event["geo_shift"] else 0,
            ]
        })
        fig2 = px.bar(reason_df, x="Contribution", y="Signal", orientation="h",
                      text="Contribution")
        fig2.update_traces(marker_color="#00e5ff", texttemplate="%{text:.0f}")
        fig2.update_layout(height=340, margin=dict(l=0,r=0,t=10,b=0),
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font=dict(color="#9db4d4"), xaxis_title="Relative evidence",
                           yaxis_title="", showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    with r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Evidence collected")
        for reason in reasons:
            st.markdown(f'<div class="step" style="margin:7px 0">✓ {reason}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ======================== TAB 3 ================================
with tab3:
    st.markdown('<div class="section-title">Detection engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">A lightweight unsupervised model demonstrates detection of behavioural novelty without relying on a hard-coded attack signature.</div>', unsafe_allow_html=True)
    st.write("")
    l,r = st.columns(2)

    with l:
        engine_df = pd.DataFrame({
            "Component": ["Telemetry ingestion","Behaviour baseline","Isolation Forest","Context enrichment","Explainability"],
            "Status": ["ONLINE","LOADED","ONLINE","ONLINE","ONLINE"],
            "Purpose": [
                "Normalised event features",
                "Median profile of normal activity",
                "Unsupervised anomaly score",
                "Identity + novelty context",
                "Evidence for analyst review"
            ]
        })
        st.dataframe(engine_df, use_container_width=True, hide_index=True)

    with r:
        radar = go.Figure(go.Scatterpolar(
            r=[min(100, anomaly+5), min(100, confidence), min(100, event["new_destinations"]*9),
               85 if event["new_device"] else 20, 78 if event["geo_shift"] else 15],
            theta=["Anomaly","Confidence","Novelty","Identity","Geo"],
            fill="toself",
            line=dict(color="#00e5ff")
        ))
        radar.update_layout(
            height=340, margin=dict(l=30,r=30,t=20,b=20),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#9db4d4"),
            polar=dict(bgcolor="rgba(0,0,0,0)",
                       radialaxis=dict(range=[0,100], gridcolor="#203b5e"),
                       angularaxis=dict(gridcolor="#203b5e")),
            showlegend=False
        )
        st.plotly_chart(radar, use_container_width=True)

# ======================== TAB 4 ================================
with tab4:
    st.markdown('<div class="section-title">Analyst-ready incident report</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Generated from the current synthetic event for the hackathon demonstration.</div>', unsafe_allow_html=True)
    st.write("")
    report = pd.DataFrame([
        ["Incident ID","SX-DEMO-2026-001"],
        ["Detection state",state],
        ["Risk score",f"{risk:.0f}/100"],
        ["Anomaly score",f"{anomaly:.0f}%"],
        ["Threat confidence",f"{confidence:.0f}%"],
        ["Outbound traffic",f"{event['outbound_mb']:.1f} MB"],
        ["New destinations",str(event["new_destinations"])],
        ["Device context","Changed" if event["new_device"] else "Expected"],
        ["Geographic context","Changed" if event["geo_shift"] else "Expected"],
    ], columns=["Field","Value"])
    st.dataframe(report, use_container_width=True, hide_index=True)

    if risk >= 70:
        st.warning("Recommended action: escalate for analyst validation, preserve evidence, and consider controlled containment after human approval.")
    else:
        st.success("Recommended action: continue monitoring; no immediate containment is recommended.")

st.write("")
st.markdown(
    '<div style="text-align:center;color:#617999;font-size:11px;padding:15px">'
    'SENTINEL-X • Defensive AI prototype • Synthetic telemetry • Human-in-the-loop response'
    '</div>',
    unsafe_allow_html=True
)
