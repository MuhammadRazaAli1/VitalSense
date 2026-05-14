import json
import streamlit as st
from datetime import datetime
from core.ml_models import get_diabetes_model, predict_disease, DIABETES_FEATURES
from core.database import save_prediction, get_latest_prediction
from core.helpers import risk_gauge, show_result_banner, show_advice, format_dt, risk_band


def render(user):
    meta = get_diabetes_model()

    left, right = st.columns([1.35, 1])

    with left:
        with st.container(border=True):
            st.markdown("### Patient Clinical Inputs")
            st.caption(f"Model accuracy: {meta['accuracy']*100:.1f}% \u2022 Algorithm: Random Forest (220 trees)")

            with st.form("diabetes_form"):
                values = {}
                rows = [DIABETES_FEATURES[i:i+2] for i in range(0, len(DIABETES_FEATURES), 2)]
                for row in rows:
                    cols = st.columns(len(row))
                    for col, (key, desc, lo, hi, default) in zip(cols, row):
                        with col:
                            if isinstance(lo, float) or isinstance(hi, float) or isinstance(default, float):
                                values[key] = st.number_input(
                                    key.replace("_", " "),
                                    min_value=float(lo), max_value=float(hi),
                                    value=float(default), step=0.1, help=desc,
                                )
                            else:
                                values[key] = st.number_input(
                                    key.replace("_", " "),
                                    min_value=int(lo), max_value=int(hi),
                                    value=int(default), step=1, help=desc,
                                )

                submitted = st.form_submit_button(
                    "Run AI Diabetes Prediction", type="primary", use_container_width=True,
                )

            if submitted:
                pred, proba = predict_disease(meta, values)
                advice_pos = "Your inputs indicate an elevated diabetes risk."
                advice_neg = "Maintain a balanced diet, regular exercise, and yearly screenings."
                pid = save_prediction(
                    user_id=user["id"], disease="Diabetes",
                    inputs_json=json.dumps(values),
                    probability=proba, risk_score=proba,
                    result="Positive" if pred else "Negative",
                    advice=advice_pos if pred else advice_neg,
                )
                st.session_state["last_diabetes_pred_id"] = pid
                st.toast("Prediction saved to your health history.", icon="\u2705")
                st.rerun()

    with right:
        latest = get_latest_prediction(user["id"], "Diabetes")
        with st.container(border=True):
            st.markdown("### Latest Result")
            if latest:
                proba = latest["probability"]
                pred = latest["result"] == "Positive"
                show_result_banner(pred, "Diabetes", proba)
                st.plotly_chart(risk_gauge(proba, "Diabetes Risk"), use_container_width=True)
                st.markdown(f"<div class='muted' style='font-size:.85rem; text-align:center;'>Recorded: {format_dt(latest['created_at'])}</div>", unsafe_allow_html=True)
                show_advice(proba, latest["advice"] or "", latest["advice"] or "")
            else:
                st.info("No prediction yet. Fill in the form on the left and run your first AI checkup.")
