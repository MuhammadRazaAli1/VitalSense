import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from core.database import get_user_predictions, delete_prediction
from core.helpers import format_dt, risk_band


KEY_METRIC = {
    "Diabetes": ("Glucose", "Plasma Glucose (mg/dL)", 70, 200),
    "Heart Disease": ("chol", "Serum Cholesterol (mg/dL)", 150, 350),
    "Parkinson's": ("MDVP_Jitter_pct", "Vocal Jitter %", 0.0, 2.5),
}


def _build_timeseries(preds, key):
    rows = []
    for p in preds:
        try:
            inputs = json.loads(p["inputs_json"])
        except Exception:
            inputs = {}
        if key not in inputs:
            continue
        rows.append({
            "Date": datetime.fromisoformat(p["created_at"]),
            "Value": float(inputs[key]),
            "Risk %": round(p["probability"] * 100, 1),
            "Result": p["result"],
        })
    return pd.DataFrame(rows).sort_values("Date") if rows else pd.DataFrame()


def render(user):
    all_preds = get_user_predictions(user["id"])
    if not all_preds:
        st.info("Your health history will appear here once you run your first AI prediction. Try the Diabetes, Heart Disease, or Parkinson's modules from the sidebar.")
        return

    diseases_present = sorted({p["disease"] for p in all_preds})
    tabs = st.tabs(["All Diseases"] + diseases_present)

    with tabs[0]:
        with st.container(border=True):
            st.markdown("### Combined Risk Trend")
            st.caption(f"All {len(all_preds)} historical predictions across every disease module")
            df = pd.DataFrame([{
                "Date": datetime.fromisoformat(p["created_at"]),
                "Disease": p["disease"],
                "Risk %": round(p["probability"] * 100, 1),
                "Result": p["result"],
            } for p in all_preds]).sort_values("Date")
            color_map = {"Diabetes": "#0EA5A4", "Heart Disease": "#DC2626", "Parkinson's": "#7C3AED"}
            fig = px.line(df, x="Date", y="Risk %", color="Disease", markers=True, color_discrete_map=color_map)
            fig.update_traces(line=dict(width=3), marker=dict(size=10))
            fig.update_layout(
                height=360, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(range=[0, 100], gridcolor="#E2E8F0"),
                xaxis=dict(gridcolor="#E2E8F0"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.container(border=True):
            st.markdown("### All Predictions")
            tbl = pd.DataFrame([{
                "Date": format_dt(p["created_at"]),
                "Disease": p["disease"],
                "Result": p["result"],
                "Risk %": round(p["probability"] * 100, 1),
                "Band": risk_band(p["probability"])[0],
            } for p in all_preds])
            st.dataframe(tbl, use_container_width=True, hide_index=True)

    for tab, disease in zip(tabs[1:], diseases_present):
        with tab:
            preds = [p for p in all_preds if p["disease"] == disease]
            preds_sorted = list(reversed(preds))

            c1, c2, c3 = st.columns(3)
            risks = [p["probability"] for p in preds]
            avg = sum(risks) / len(risks)
            with c1:
                with st.container(border=True):
                    st.markdown(f"<div style='font-size:.78rem;color:#64748B;letter-spacing:.06em;text-transform:uppercase;font-weight:700;'>Total Checkups</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:1.8rem;font-weight:800;'>{len(preds)}</div>", unsafe_allow_html=True)
            with c2:
                with st.container(border=True):
                    st.markdown(f"<div style='font-size:.78rem;color:#64748B;letter-spacing:.06em;text-transform:uppercase;font-weight:700;'>Average Risk</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:1.8rem;font-weight:800;'>{avg*100:.1f}%</div>", unsafe_allow_html=True)
            with c3:
                latest_risk = preds[0]["probability"]
                with st.container(border=True):
                    st.markdown(f"<div style='font-size:.78rem;color:#64748B;letter-spacing:.06em;text-transform:uppercase;font-weight:700;'>Latest Risk</div>", unsafe_allow_html=True)
                    band, color = risk_band(latest_risk)
                    st.markdown(f"<div style='font-size:1.8rem;font-weight:800;color:{color};'>{latest_risk*100:.1f}%</div>", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown(f"### {disease} Risk Trend Over Time")
                df_risk = pd.DataFrame([{
                    "Date": datetime.fromisoformat(p["created_at"]),
                    "Risk %": round(p["probability"] * 100, 1),
                } for p in preds_sorted])
                color_map = {
                    "Diabetes": ("#0EA5A4", "rgba(14,165,164,0.18)"),
                    "Heart Disease": ("#DC2626", "rgba(220,38,38,0.18)"),
                    "Parkinson's": ("#7C3AED", "rgba(124,58,237,0.18)"),
                }
                color, fill_color = color_map[disease]
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_risk["Date"], y=df_risk["Risk %"], mode="lines+markers",
                    line=dict(color=color, width=3), marker=dict(size=10, color=color),
                    fill="tozeroy", fillcolor=fill_color,
                ))
                fig.update_layout(
                    height=300, margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(title="Risk %", range=[0, 100], gridcolor="#E2E8F0"),
                    xaxis=dict(gridcolor="#E2E8F0"),
                )
                st.plotly_chart(fig, use_container_width=True)

            key, label, lo, hi = KEY_METRIC[disease]
            ts = _build_timeseries(preds_sorted, key)
            with st.container(border=True):
                st.markdown(f"### Most Important Indicator: {label}")
                st.caption(f"This is the most clinically important parameter for {disease} \u2014 tracking it shows whether your underlying health is improving.")
                if ts.empty:
                    st.info("Not enough historical data for this metric yet.")
                else:
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(
                        x=ts["Date"], y=ts["Value"],
                        marker=dict(color=[color if r == "Positive" else "#10B981" for r in ts["Result"]]),
                        text=[f"{v:.2f}" for v in ts["Value"]], textposition="outside",
                    ))
                    fig2.update_layout(
                        height=320, margin=dict(l=10, r=10, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        yaxis=dict(title=label, gridcolor="#E2E8F0"),
                        xaxis=dict(gridcolor="#E2E8F0"),
                    )
                    st.plotly_chart(fig2, use_container_width=True)

            with st.container(border=True):
                st.markdown("### Detailed Records")
                for p in preds:
                    cls = "pos" if p["result"] == "Positive" else "neg"
                    badge = "Positive" if p["result"] == "Positive" else "Negative"
                    cols = st.columns([6, 1])
                    with cols[0]:
                        st.markdown(
                            f"""
                            <div class='timeline-item'>
                              <div class='dot {cls}'></div>
                              <div class='body'>
                                <div class='title'>{disease} \u2014 {p['probability']*100:.1f}% risk</div>
                                <div class='meta'>{format_dt(p['created_at'])} \u2022 {p['advice'] or ''}</div>
                              </div>
                              <div class='badge {cls}'>{badge}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with cols[1]:
                        if st.button("Delete", key=f"del_{p['id']}", use_container_width=True):
                            delete_prediction(p["id"], user["id"])
                            st.rerun()
