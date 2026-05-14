import plotly.graph_objects as go
import streamlit as st
from datetime import datetime


def parse_dt(s: str) -> datetime:
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return datetime.utcnow()


def format_dt(s: str) -> str:
    return parse_dt(s).strftime("%d %b %Y, %I:%M %p")


def risk_band(prob: float):
    if prob < 0.3:
        return "Low Risk", "#10B981"
    if prob < 0.6:
        return "Moderate Risk", "#F59E0B"
    if prob < 0.8:
        return "High Risk", "#EA580C"
    return "Very High Risk", "#DC2626"


def risk_gauge(prob: float, title: str = "Risk Probability"):
    band, color = risk_band(prob)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        number={"suffix": "%", "font": {"size": 36, "color": "#0F172A"}},
        title={"text": f"<b>{title}</b><br><span style='font-size:0.85em;color:#64748B'>{band}</span>",
               "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#CBD5E1"},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "#F8FAFC",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "#D1FAE5"},
                {"range": [30, 60], "color": "#FEF3C7"},
                {"range": [60, 80], "color": "#FED7AA"},
                {"range": [80, 100], "color": "#FECACA"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.78,
                "value": prob * 100,
            },
        },
    ))
    fig.update_layout(
        height=260, margin=dict(l=10, r=10, t=70, b=10),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(family="sans-serif"),
    )
    return fig


def metric_card(label: str, value: str, delta: str = "", delta_dir: str = "flat",
                accent_letters: str = "", variant: str = ""):
    cls = "metric-card"
    if variant:
        cls += f" {variant}"
    delta_html = f"<div class='delta {delta_dir}'>{delta}</div>" if delta else ""
    accent_html = f"<div class='accent'>{accent_letters}</div>" if accent_letters else ""
    return f"""
    <div class='{cls}'>
      {accent_html}
      <div class='label'>{label}</div>
      <div class='value'>{value}</div>
      {delta_html}
    </div>
    """


def show_result_banner(positive: bool, disease: str, prob: float):
    band, _ = risk_band(prob)
    if positive:
        text = f"Elevated {disease} Risk Detected"
        cls = "positive"
        ico = "!"
    else:
        text = f"No Significant {disease} Risk Detected"
        cls = "negative"
        ico = "OK"
    st.markdown(
        f"""
        <div class='result-banner {cls}'>
          <div class='ico'>{ico}</div>
          <div>
            <div class='label'>Prediction Result</div>
            <div class='text'>{text}</div>
          </div>
          <div class='meta'>Probability: {prob*100:.1f}%<br/>{band}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_advice(prob: float, advice_pos: str, advice_neg: str):
    if prob >= 0.8:
        cls = "danger"
        text = advice_pos + " Please consult a qualified physician immediately for confirmatory tests."
    elif prob >= 0.5:
        cls = "warn"
        text = advice_pos + " Schedule a clinical consultation within the next 1-2 weeks."
    elif prob >= 0.3:
        cls = ""
        text = "Borderline indicators detected. Maintain a healthy lifestyle and re-test in 3 months. " + advice_neg
    else:
        cls = ""
        text = advice_neg
    st.markdown(f"<div class='advice-box {cls}'>{text}</div>", unsafe_allow_html=True)
