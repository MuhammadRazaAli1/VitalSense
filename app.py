import streamlit as st
from interface.ui import inject_global_styles, render_sidebar, render_top_header, render_login_page
from core.database import init_db, get_user_by_id
from interface.sections import (
    dashboard,
    diabetes,
    heart,
    parkinsons,
    history,
    recovery,
    report,
)

st.set_page_config(
    page_title="MediCare AI - Multi-Disease Prediction",
    page_icon="\U0001F3E5",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
inject_global_styles()

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "active_section" not in st.session_state:
    st.session_state.active_section = "Dashboard"

if not st.session_state.user_id:
    render_login_page()
    st.stop()

user = get_user_by_id(st.session_state.user_id)
if not user:
    st.session_state.user_id = None
    st.rerun()

active = render_sidebar(user)
render_top_header(user, active)

routes = {
    "Dashboard": dashboard.render,
    "Diabetes Prediction": diabetes.render,
    "Heart Disease Prediction": heart.render,
    "Parkinson's Disease Prediction": parkinsons.render,
    "Health History": history.render,
    "Recovery Tracker": recovery.render,
    "Medical Report": report.render,
}

routes[active](user)
