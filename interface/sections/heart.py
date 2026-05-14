import json
import streamlit as st
from core.ml_models import get_heart_model, predict_disease, HEART_FEATURES
from core.database import save_prediction, get_latest_prediction
from core.helpers import risk_gauge, show_result_banner, show_advice, format_dt


def render(user):
    meta = get_heart_model()

    left, right = st.columns([1.35, 1])

    with left:
        with st.container(border=True):
            st.markdown("### Cardiovascular Clinical Inputs")
            st.caption(f"Model accuracy: {meta['accuracy']*100:.1f}% \u2022 Algorithm: Gradient Boosting")

            with st.form("heart_form"):
                values = {}
                rows = [HEART_FEATURES[i:i+3] for i in range(0, len(HEART_FEATURES), 3)]
                for row in rows:
                    cols = st.columns(len(row))
                    for col, (key, desc, lo, hi, default) in zip(cols, row):
                        with col:
                            if isinstance(lo, float) or isinstance(hi, float) or isinstance(default, float):
                                values[key] = st.number_input(
                                    key, min_value=float(lo), max_value=float(hi),
                                    value=float(default), step=0.1, help=desc,
                                )
                            else:
                                values[key] = st.number_input(
                                    key, min_value=int(lo), max_value=int(hi),
                                    value=int(default), step=1, help=desc,
                                )

                submitted = st.form_submit_button(
                    "Run AI Heart Disease Prediction", type="primary", use_container_width=True,
                )

            if submitted:
                pred, proba = predict_disease(meta, values)
                advice_pos = "Cardiovascular risk markers are elevated."
                advice_neg = "Your heart parameters look healthy. Maintain regular cardio exercise and a low-sodium diet."
                pid = save_prediction(
                    user_id=user["id"], disease="Heart Disease",
                    inputs_json=json.dumps(values),
                    probability=proba, risk_score=proba,
                    result="Positive" if pred else "Negative",
                    advice=advice_pos if pred else advice_neg,
                )
                st.session_state["last_heart_pred_id"] = pid
                st.toast("Heart prediction saved to your health history.", icon="\u2705")
                st.rerun()

    with right:
        latest = get_latest_prediction(user["id"], "Heart Disease")
        with st.container(border=True):
            st.markdown("### Latest Result")
            if latest:
                proba = latest["probability"]
                pred = latest["result"] == "Positive"
                show_result_banner(pred, "Heart Disease", proba)
                st.plotly_chart(risk_gauge(proba, "Heart Disease Risk"), use_container_width=True)
                st.markdown(f"<div class='muted' style='font-size:.85rem; text-align:center;'>Recorded: {format_dt(latest['created_at'])}</div>", unsafe_allow_html=True)
                show_advice(proba, latest["advice"] or "", latest["advice"] or "")
            else:
                st.info("No prediction yet. Complete the cardiac assessment on the left.")
