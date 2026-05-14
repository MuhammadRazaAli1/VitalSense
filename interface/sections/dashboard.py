import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from core.database import get_user_predictions, count_predictions, get_latest_prediction
from core.helpers import metric_card, format_dt, risk_band


DISEASES = ["Diabetes", "Heart Disease", "Parkinson's"]
DISEASE_COLORS = {"Diabetes": "#0EA5A4", "Heart Disease": "#DC2626", "Parkinson's": "#7C3AED"}


def render(user):
    all_preds = get_user_predictions(user["id"])
    counts = count_predictions(user["id"])

    total = len(all_preds)
    positive = sum(1 for p in all_preds if p["result"] == "Positive")
    if all_preds:
        avg_risk = sum(p["probability"] for p in all_preds) / len(all_preds)
        last_dt = format_dt(all_preds[0]["created_at"])
    else:
        avg_risk = 0.0
        last_dt = "No checkups yet"

    cols = st.columns(4)
    with cols[0]:
        st.markdown(metric_card(
            "Total Checkups", str(total),
            f"Last: {last_dt}" if total else "Run your first prediction",
            "flat", "TC",
        ), unsafe_allow_html=True)
    with cols[1]:
        st.markdown(metric_card(
            "Positive Findings", str(positive),
            f"{(positive/total*100):.0f}% of checkups" if total else "0%",
            "up" if positive else "flat", "PF", "alt",
        ), unsafe_allow_html=True)
    with cols[2]:
        band, _ = risk_band(avg_risk) if total else ("\u2014", "")
        st.markdown(metric_card(
            "Average Risk", f"{avg_risk*100:.1f}%" if total else "\u2014",
            band, "up" if avg_risk > 0.5 else "down" if avg_risk > 0 else "flat",
            "AR", "alt2",
        ), unsafe_allow_html=True)
    with cols[3]:
        diseases_tested = len([d for d in DISEASES if counts.get(d, 0) > 0])
        st.markdown(metric_card(
            "Diseases Monitored", f"{diseases_tested} / 3",
            "Complete coverage" if diseases_tested == 3 else "Try all 3 modules",
            "down" if diseases_tested == 3 else "flat", "DM", "alt3",
        ), unsafe_allow_html=True)

    st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

    g1, g2 = st.columns([1.5, 1])

    with g1:
        with st.container(border=True):
            st.markdown("### Risk Trend Over Time")
            st.caption("Real-time tracking of your AI risk scores across all diseases")

            if not all_preds:
                st.info("Once you complete prediction checkups, your risk trend will appear here.")
            else:
                rows = []
                for p in all_preds:
                    rows.append({
                        "Date": datetime.fromisoformat(p["created_at"]),
                        "Disease": p["disease"],
                        "Risk %": round(p["probability"] * 100, 1),
                    })
                df = pd.DataFrame(rows).sort_values("Date")
                fig = px.line(
                    df, x="Date", y="Risk %", color="Disease",
                    markers=True, color_discrete_map=DISEASE_COLORS,
                )
                fig.update_traces(line=dict(width=3), marker=dict(size=9))
                fig.update_layout(
                    height=320, margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(range=[0, 100], gridcolor="#E2E8F0"),
                    xaxis=dict(gridcolor="#E2E8F0"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                    font=dict(family="sans-serif"),
                )
                st.plotly_chart(fig, use_container_width=True)

    with g2:
        with st.container(border=True):
            st.markdown("### Latest by Disease")
            st.caption("Your most recent prediction per disease module")
            for d in DISEASES:
                latest = get_latest_prediction(user["id"], d)
                if latest:
                    band, color = risk_band(latest["probability"])
                    st.markdown(
                        f"""
                        <div style='display:flex;justify-content:space-between;align-items:center;
                                    padding:.65rem .85rem; border:1px solid #E2E8F0; border-radius:10px;
                                    margin-bottom:.5rem; background:#fff;'>
                          <div>
                            <div style='font-weight:700;color:#0F172A;'>{d}</div>
                            <div style='font-size:.78rem;color:#64748B;'>{format_dt(latest['created_at'])}</div>
                          </div>
                          <div style='text-align:right;'>
                            <div style='font-weight:800;color:{color};font-size:1.1rem;'>{latest['probability']*100:.1f}%</div>
                            <div style='font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:{color};font-weight:700;'>{band}</div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div style='display:flex;justify-content:space-between;align-items:center;
                                    padding:.65rem .85rem; border:1px dashed #CBD5E1; border-radius:10px;
                                    margin-bottom:.5rem; background:#F8FAFC;'>
                          <div>
                            <div style='font-weight:700;color:#0F172A;'>{d}</div>
                            <div style='font-size:.78rem;color:#94A3B8;'>No checkup yet</div>
                          </div>
                          <div style='font-size:.78rem;color:#94A3B8;font-weight:700;'>Pending</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    g3, g4 = st.columns(2)
    with g3:
        with st.container(border=True):
            st.markdown("### Distribution of Outcomes")
            if not all_preds:
                st.info("No data yet to plot.")
            else:
                df_out = pd.DataFrame(all_preds)
                grouped = df_out.groupby(["disease", "result"]).size().reset_index(name="Count")
                fig = px.bar(
                    grouped, x="disease", y="Count", color="result", barmode="group",
                    color_discrete_map={"Positive": "#DC2626", "Negative": "#10B981"},
                    labels={"disease": "Disease"},
                )
                fig.update_layout(
                    height=290, margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(gridcolor="#E2E8F0"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                )
                st.plotly_chart(fig, use_container_width=True)

    with g4:
        with st.container(border=True):
            st.markdown("### Recent Activity")
            if not all_preds:
                st.info("Activity will appear here as you run checkups.")
            else:
                for p in all_preds[:6]:
                    cls = "pos" if p["result"] == "Positive" else "neg"
                    badge = "Positive" if p["result"] == "Positive" else "Negative"
                    st.markdown(
                        f"""
                        <div class='timeline-item'>
                          <div class='dot {cls}'></div>
                          <div class='body'>
                            <div class='title'>{p['disease']} Prediction</div>
                            <div class='meta'>{format_dt(p['created_at'])} \u2022 Risk: {p['probability']*100:.1f}%</div>
                          </div>
                          <div class='badge {cls}'>{badge}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
