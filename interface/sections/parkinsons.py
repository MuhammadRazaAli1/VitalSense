import json
import streamlit as st
from core.ml_models import get_parkinsons_model, predict_disease, PARKINSONS_FEATURES
from core.database import save_prediction, get_latest_prediction
from core.helpers import risk_gauge, show_result_banner, show_advice, format_dt


def render(user):
    meta = get_parkinsons_model()

    left, right = st.columns([1.35, 1])

    with left:
        with st.container(border=True):
            st.markdown("### Voice Biomarker Inputs")
            st.caption(
                f"Model accuracy: {meta['accuracy']*100:.1f}% \u2022 Algorithm: Random Forest \u2022 "
                "22 acoustic measures from sustained phonation"
            )

            with st.form("parkinsons_form"):
                values = {}
                rows = [PARKINSONS_FEATURES[i:i+3] for i in range(0, len(PARKINSONS_FEATURES), 3)]
                for row in rows:
                    cols = st.columns(len(row))
                    for col, (key, desc, lo, hi, default) in zip(cols, row):
                        with col:
                            label = key.replace("_", " ")
                            step = 0.0001 if (isinstance(default, float) and abs(default) < 0.001) else (
                                0.001 if (isinstance(default, float) and abs(default) < 0.05) else 0.01
                            )
                            values[key] = st.number_input(
                                label, min_value=float(lo), max_value=float(hi),
                                value=float(default), step=float(step),
                                help=desc, format="%.5f" if step <= 0.0001 else "%.4f",
                            )

                submitted = st.form_submit_button(
                    "Run AI Parkinson's Prediction", type="primary", use_container_width=True,
                )

            if submitted:
                pred, proba = predict_disease(meta, values)
                advice_pos = "Voice biomarkers suggest potential signs consistent with Parkinson's disease."
                advice_neg = "Voice patterns are within typical ranges. Maintain neurological wellness through regular exercise."
                pid = save_prediction(
                    user_id=user["id"], disease="Parkinson's",
                    inputs_json=json.dumps(values),
                    probability=proba, risk_score=proba,
                    result="Positive" if pred else "Negative",
                    advice=advice_pos if pred else advice_neg,
                )
                st.session_state["last_parkinsons_pred_id"] = pid
                st.toast("Parkinson's prediction saved.", icon="\u2705")
                st.rerun()

    with right:
        latest = get_latest_prediction(user["id"], "Parkinson's")
        with st.container(border=True):
            st.markdown("### Latest Result")
            if latest:
                proba = latest["probability"]
                pred = latest["result"] == "Positive"
                show_result_banner(pred, "Parkinson's", proba)
                st.plotly_chart(risk_gauge(proba, "Parkinson's Risk"), use_container_width=True)
                st.markdown(f"<div class='muted' style='font-size:.85rem; text-align:center;'>Recorded: {format_dt(latest['created_at'])}</div>", unsafe_allow_html=True)
                show_advice(proba, latest["advice"] or "", latest["advice"] or "")
            else:
                st.info("No prediction yet. Submit the voice biomarker form on the left.")
