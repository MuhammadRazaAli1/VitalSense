import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from core.database import get_user_predictions
from core.helpers import format_dt


KEY_INDICATORS = {
    "Diabetes": [("Glucose", "Glucose", "mg/dL", "lower"),
                 ("BMI", "BMI", "kg/m\u00B2", "lower"),
                 ("BloodPressure", "Blood Pressure", "mm Hg", "lower")],
    "Heart Disease": [("chol", "Cholesterol", "mg/dL", "lower"),
                      ("trestbps", "Resting BP", "mm Hg", "lower"),
                      ("thalach", "Max Heart Rate", "bpm", "higher")],
    "Parkinson's": [("MDVP_Jitter_pct", "Vocal Jitter", "%", "lower"),
                    ("MDVP_Shimmer", "Vocal Shimmer", "", "lower"),
                    ("HNR", "Harmonics-to-Noise", "dB", "higher")],
}


def _status(prev_risk, latest_risk):
    diff = latest_risk - prev_risk
    if diff < -0.05:
        return "Improving", "improving", "\u25BC"
    if diff > 0.05:
        return "Worsening", "worsening", "\u25B2"
    return "Stable", "stable", "\u2014"


def _percent_change(prev, curr):
    if prev == 0:
        return 0.0
    return ((curr - prev) / abs(prev)) * 100


def render(user):
    all_preds = get_user_predictions(user["id"])
    if not all_preds:
        st.info("Run a few predictions first \u2014 once you have at least 2 checkups for the same disease, the recovery tracker will compare them in real time.")
        return

    diseases = sorted({p["disease"] for p in all_preds})

    for disease in diseases:
        preds = [p for p in all_preds if p["disease"] == disease]
        if len(preds) < 1:
            continue
        latest = preds[0]
        prev = preds[1] if len(preds) >= 2 else None

        with st.container(border=False):
            if prev is None:
                st.markdown(
                    f"""
                    <div class='recovery-card stable'>
                      <div class='head'>
                        <div style='font-size:1.15rem;font-weight:800;color:#0F172A;'>{disease}</div>
                        <div class='badge'>Baseline Established</div>
                      </div>
                      <div class='label'>Recovery Status</div>
                      <div style='font-size:1.1rem; color:#0F172A; margin-top:.3rem;'>
                        First checkup recorded. Run another prediction with updated values to start tracking your recovery in real time.
                      </div>
                      <div style='font-size:.85rem;color:#64748B; margin-top:.4rem;'>
                        Baseline risk: <b>{latest['probability']*100:.1f}%</b> \u2022 {format_dt(latest['created_at'])}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                continue

            status, cls, arrow = _status(prev["probability"], latest["probability"])
            risk_change = (latest["probability"] - prev["probability"]) * 100

            st.markdown(
                f"""
                <div class='recovery-card {cls}'>
                  <div class='head'>
                    <div style='font-size:1.15rem;font-weight:800;color:#0F172A;'>{disease}</div>
                    <div class='badge'>{arrow} {status}</div>
                  </div>
                  <div class='label'>Real-Time Recovery Status</div>
                  <div style='display:flex; gap:2.5rem; flex-wrap:wrap; margin-top:.45rem; align-items:baseline;'>
                    <div>
                      <div style='font-size:.72rem;color:#64748B;letter-spacing:.06em;text-transform:uppercase;font-weight:700;'>Previous Risk</div>
                      <div style='font-size:1.6rem;font-weight:800;color:#0F172A;'>{prev['probability']*100:.1f}%</div>
                      <div style='font-size:.78rem;color:#64748B;'>{format_dt(prev['created_at'])}</div>
                    </div>
                    <div>
                      <div style='font-size:.72rem;color:#64748B;letter-spacing:.06em;text-transform:uppercase;font-weight:700;'>Latest Risk</div>
                      <div style='font-size:1.6rem;font-weight:800;color:#0F172A;'>{latest['probability']*100:.1f}%</div>
                      <div style='font-size:.78rem;color:#64748B;'>{format_dt(latest['created_at'])}</div>
                    </div>
                    <div>
                      <div style='font-size:.72rem;color:#64748B;letter-spacing:.06em;text-transform:uppercase;font-weight:700;'>Change</div>
                      <div style='font-size:1.6rem;font-weight:800;color:{"#DC2626" if risk_change>0 else "#10B981" if risk_change<0 else "#64748B"};'>{risk_change:+.1f} pts</div>
                      <div style='font-size:.78rem;color:#64748B;'>vs previous checkup</div>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            try:
                prev_in = json.loads(prev["inputs_json"])
                cur_in = json.loads(latest["inputs_json"])
            except Exception:
                prev_in, cur_in = {}, {}

            indicators = KEY_INDICATORS.get(disease, [])
            cols = st.columns(len(indicators)) if indicators else None
            for col, (key, label, unit, direction) in zip(cols or [], indicators):
                with col:
                    if key not in prev_in or key not in cur_in:
                        st.info(f"{label}: not enough data")
                        continue
                    p_val = float(prev_in[key])
                    c_val = float(cur_in[key])
                    pc = _percent_change(p_val, c_val)
                    improving = (pc < 0 and direction == "lower") or (pc > 0 and direction == "higher")
                    color = "#10B981" if improving else "#DC2626" if abs(pc) > 1 else "#64748B"
                    arrow_v = "\u25BC" if pc < 0 else "\u25B2" if pc > 0 else "\u2014"
                    with st.container(border=True):
                        st.markdown(
                            f"""
                            <div style='font-size:.72rem;color:#64748B;letter-spacing:.06em;text-transform:uppercase;font-weight:700;'>{label}</div>
                            <div style='display:flex;justify-content:space-between;align-items:baseline;margin-top:.3rem;'>
                              <div>
                                <div style='font-size:1.4rem;font-weight:800;color:#0F172A;'>{c_val:.2f} <span style='font-size:.85rem;color:#64748B;font-weight:500;'>{unit}</span></div>
                                <div style='font-size:.78rem;color:#64748B;'>was {p_val:.2f} {unit}</div>
                              </div>
                              <div style='text-align:right;color:{color};font-weight:700;'>
                                <div style='font-size:1.05rem;'>{arrow_v} {abs(pc):.1f}%</div>
                                <div style='font-size:.7rem;'>{"improved" if improving else "worsened" if abs(pc)>1 else "no change"}</div>
                              </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            if len(preds) >= 2:
                with st.container(border=True):
                    st.markdown(f"### {disease} \u2014 Risk Recovery Curve")
                    series = list(reversed(preds))
                    df = pd.DataFrame([{
                        "Checkup": f"#{i+1}",
                        "Date": datetime.fromisoformat(p["created_at"]).strftime("%d %b"),
                        "Risk %": round(p["probability"] * 100, 1),
                    } for i, p in enumerate(series)])
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df["Checkup"], y=df["Risk %"], mode="lines+markers+text",
                        line=dict(color="#0EA5A4", width=3, shape="spline"),
                        marker=dict(size=12, color="#0EA5A4"),
                        text=[f"{v:.0f}%" for v in df["Risk %"]],
                        textposition="top center",
                        fill="tozeroy", fillcolor="rgba(14,165,164,0.10)",
                        hovertemplate="%{customdata}<br>Risk: %{y}%<extra></extra>",
                        customdata=df["Date"],
                    ))
                    fig.update_layout(
                        height=280, margin=dict(l=10, r=10, t=20, b=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        yaxis=dict(range=[0, 105], title="Risk %", gridcolor="#E2E8F0"),
                        xaxis=dict(title="Checkup #", gridcolor="#E2E8F0"),
                    )
                    st.plotly_chart(fig, use_container_width=True)
