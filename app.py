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
from st_supabase_connection import SupabaseConnection

st.set_page_config(
    page_title="MediCareAI",
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


# Supabase Client initialize karein (yeh secrets se khud detail utha lega)
conn = st.connection("supabase", type=SupabaseConnection)

st.title("MediCareAI - Permanent Data Storage")

# Example Form data collect karne ke liye
with st.form("patient_form"):
    patient_name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=1, max_value=120)
    diagnosis = st.text_area("Diagnosis / AI Analysis")
    
    submit_button = st.form_submit_button(label="Save Data Permanently")

if submit_button:
    if patient_name and diagnosis:
        # Data dictionary jo table mein insert karni hai
        data_to_insert = {
            "patient_name": patient_name,
            "age": age,
            "diagnosis": diagnosis
        }
        
        try:
            # 'your_table_name' ko apni actual Supabase table name se badli karein
            response = conn.table("your_table_name").insert(data_to_insert).execute()
            
            st.success("🎉 Data kamyabi se permanent database mein save ho gaya!")
            st.json(response.data)
        except Exception as e:
            st.error(f"Masla aya: {e}")
    else:
        st.warning("Meherbani karke saari fields fill karein.")
