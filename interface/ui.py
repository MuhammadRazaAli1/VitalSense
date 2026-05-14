import streamlit as st
from datetime import datetime
from core.database import authenticate_user, create_user

GLOBAL_CSS = """
<style>
:root {
  --brand: #0EA5A4;
  --brand-dark: #0B7B7A;
  --ink: #0F172A;
  --muted: #64748B;
  --bg: #F7FAFC;
  --card: #FFFFFF;
  --danger: #DC2626;
  --warn: #F59E0B;
  --ok: #10B981;
}

.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1280px; }

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0F172A 0%, #0B3B3A 100%);
}
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
  color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stButton > button {
  width: 100%;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  color: #E2E8F0;
  text-align: left;
  padding: 0.65rem 0.9rem;
  border-radius: 10px;
  font-weight: 500;
  transition: all .18s ease;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(14,165,164,0.18);
  border-color: rgba(14,165,164,0.55);
  color: #ffffff;
}
[data-testid="stSidebar"] .stButton.nav-active > button {
  background: linear-gradient(90deg, rgba(14,165,164,0.35), rgba(14,165,164,0.12));
  border-color: rgba(14,165,164,0.85);
  color: #ffffff;
  box-shadow: 0 4px 14px rgba(14,165,164,0.2);
}

.brand-block { padding: .6rem .25rem 1rem .25rem; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: .8rem; }
.brand-title { font-size: 1.45rem; font-weight: 800; letter-spacing: -.02em; color: #fff !important; }
.brand-sub { font-size: .78rem; color: #94A3B8 !important; margin-top: 2px; }

.section-label {
  font-size: .68rem; letter-spacing: .14em; text-transform: uppercase;
  color: #64748B !important; margin: 1.2rem .25rem .35rem .25rem; font-weight: 700;
}

.user-card {
  background: rgba(255,255,255,0.05);
  padding: .8rem .9rem; border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.08); margin-bottom: .8rem;
  display: flex; gap: .7rem; align-items: center;
}
.user-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, #0EA5A4, #1E40AF);
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 1.05rem;
}
.user-name { font-weight: 700; font-size: .92rem; color: #F1F5F9 !important; }
.user-meta { font-size: .72rem; color: #94A3B8 !important; }

.app-header {
  display: flex; justify-content: space-between; align-items: end;
  padding-bottom: 1rem; margin-bottom: 1.2rem;
  border-bottom: 1px solid #E2E8F0;
}
.app-header h1 {
  font-size: 1.85rem; font-weight: 800; letter-spacing: -.02em;
  color: var(--ink); margin: 0;
}
.app-header p { color: var(--muted); margin: .25rem 0 0 0; font-size: .92rem; }
.app-header .breadcrumb { font-size: .78rem; color: var(--muted); letter-spacing: .04em; text-transform: uppercase; font-weight: 600; }
.app-header .right { text-align: right; color: var(--muted); font-size: .82rem; }

.metric-card {
  background: var(--card); border-radius: 16px; padding: 1.1rem 1.2rem;
  border: 1px solid #E2E8F0;
  box-shadow: 0 1px 2px rgba(15,23,42,0.04);
  height: 100%;
}
.metric-card .label { font-size: .78rem; color: var(--muted); font-weight: 600; letter-spacing: .04em; text-transform: uppercase; }
.metric-card .value { font-size: 2rem; font-weight: 800; color: var(--ink); margin-top: .2rem; line-height: 1.1; letter-spacing: -.02em; }
.metric-card .delta { font-size: .82rem; margin-top: .35rem; font-weight: 600; }
.metric-card .delta.up { color: var(--danger); }
.metric-card .delta.down { color: var(--ok); }
.metric-card .delta.flat { color: var(--muted); }
.metric-card .accent {
  width: 38px; height: 38px; border-radius: 10px;
  background: rgba(14,165,164,.12); color: var(--brand);
  display: inline-flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 1.05rem; margin-bottom: .55rem;
}
.metric-card.alt .accent { background: rgba(220,38,38,.10); color: var(--danger); }
.metric-card.alt2 .accent { background: rgba(245,158,11,.12); color: var(--warn); }
.metric-card.alt3 .accent { background: rgba(16,185,129,.12); color: var(--ok); }

.panel {
  background: var(--card); border-radius: 16px; padding: 1.4rem 1.5rem;
  border: 1px solid #E2E8F0; box-shadow: 0 1px 2px rgba(15,23,42,0.04);
  margin-bottom: 1rem;
}
.panel h3 { font-size: 1.15rem; font-weight: 700; color: var(--ink); margin: 0 0 .25rem 0; }
.panel .sub { color: var(--muted); font-size: .9rem; margin-bottom: 1rem; }

.result-banner {
  border-radius: 14px; padding: 1.2rem 1.4rem; color: #fff; font-weight: 600;
  display: flex; gap: 1rem; align-items: center; margin: 1rem 0;
}
.result-banner.positive { background: linear-gradient(135deg, #DC2626, #991B1B); }
.result-banner.negative { background: linear-gradient(135deg, #10B981, #047857); }
.result-banner .ico {
  width: 46px; height: 46px; border-radius: 12px;
  background: rgba(255,255,255,0.18); display:flex; align-items:center; justify-content:center;
  font-size: 1.4rem; font-weight: 800;
}
.result-banner .label { font-size: .78rem; opacity: .9; letter-spacing: .12em; text-transform: uppercase; }
.result-banner .text { font-size: 1.25rem; font-weight: 800; line-height: 1.15; margin-top: 2px; }
.result-banner .meta { margin-left:auto; text-align:right; font-weight:500; font-size:.85rem; opacity:.95; }

.advice-box {
  background: #F0FDFA; border-left: 4px solid var(--brand);
  padding: 1rem 1.2rem; border-radius: 10px;
  color: #134E4A; font-size: .95rem; margin-top: .6rem;
}
.advice-box.warn { background: #FFFBEB; border-color: var(--warn); color: #78350F; }
.advice-box.danger { background: #FEF2F2; border-color: var(--danger); color: #7F1D1D; }

.timeline-item {
  display:flex; gap: 1rem; align-items:flex-start;
  padding: .9rem 1rem; border: 1px solid #E2E8F0; border-radius: 12px;
  background: #fff; margin-bottom: .6rem;
}
.timeline-item .dot {
  width: 12px; height: 12px; border-radius: 50%; margin-top: 6px; flex-shrink: 0;
}
.timeline-item .dot.pos { background: var(--danger); }
.timeline-item .dot.neg { background: var(--ok); }
.timeline-item .body { flex: 1; }
.timeline-item .title { font-weight: 700; color: var(--ink); }
.timeline-item .meta { color: var(--muted); font-size: .82rem; margin-top: 2px; }
.timeline-item .badge {
  font-size: .72rem; font-weight: 700; padding: .2rem .55rem;
  border-radius: 999px; letter-spacing: .04em; text-transform: uppercase;
}
.timeline-item .badge.pos { background: #FEE2E2; color: #991B1B; }
.timeline-item .badge.neg { background: #D1FAE5; color: #065F46; }

.recovery-card {
  background: linear-gradient(135deg, #ECFEFF 0%, #F0FDFA 100%);
  border: 1px solid #99F6E4; border-radius: 16px;
  padding: 1.3rem 1.5rem; margin-bottom: 1rem;
}
.recovery-card.improving { background: linear-gradient(135deg, #ECFDF5, #D1FAE5); border-color: #6EE7B7; }
.recovery-card.worsening { background: linear-gradient(135deg, #FEF2F2, #FEE2E2); border-color: #FCA5A5; }
.recovery-card.stable { background: linear-gradient(135deg, #F8FAFC, #F1F5F9); border-color: #CBD5E1; }
.recovery-card .label { font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; font-weight: 700; color: var(--muted); }
.recovery-card .head {
  display:flex; gap: .8rem; align-items:center; margin-bottom: .4rem;
}
.recovery-card .head .badge {
  font-weight: 800; font-size: .82rem; padding: .3rem .7rem; border-radius: 999px;
  background: rgba(255,255,255,.7); color: var(--ink);
}

.auth-wrap {
  max-width: 980px; margin: 1.5rem auto 0 auto;
  display: grid; grid-template-columns: 1fr 1fr; gap: 0;
  border-radius: 22px; overflow: hidden; box-shadow: 0 12px 38px rgba(15,23,42,0.10);
  border: 1px solid #E2E8F0; background: #fff;
}
.auth-hero {
  background: linear-gradient(135deg, #0F172A 0%, #0B7B7A 100%);
  color: #fff; padding: 2.4rem 2.2rem; display: flex; flex-direction: column;
}
.auth-hero .logo { font-size: 1.6rem; font-weight: 800; letter-spacing: -.02em; }
.auth-hero .tag { font-size: .85rem; letter-spacing: .14em; opacity: .8; text-transform: uppercase; margin-top: 4px;}
.auth-hero h2 { font-size: 1.85rem; font-weight: 800; line-height: 1.15; margin: 1.6rem 0 .6rem 0; letter-spacing: -.02em;}
.auth-hero p { opacity: .85; font-size: .95rem; line-height: 1.55; }
.auth-hero ul { list-style: none; padding: 0; margin: 1.4rem 0 0 0; }
.auth-hero ul li {
  padding: .55rem 0; font-size: .92rem; opacity: .92;
  border-top: 1px solid rgba(255,255,255,0.1);
  display:flex; gap: .65rem; align-items:center;
}
.auth-hero ul li:first-child { border-top: 0; }
.auth-hero ul li .check {
  width: 20px; height: 20px; border-radius: 50%; background: rgba(255,255,255,0.18);
  display:inline-flex; align-items:center; justify-content:center; font-size: .7rem; font-weight: 800;
}
.auth-form { padding: 2.4rem 2.2rem; }
.auth-form h3 { font-size: 1.5rem; font-weight: 800; color: var(--ink); margin: 0 0 .25rem 0; letter-spacing: -.02em;}
.auth-form .sub { color: var(--muted); margin-bottom: 1.4rem; font-size: .92rem;}

.stButton > button {
  border-radius: 10px; font-weight: 600;
}

div[data-baseweb="tab-list"] { gap: .25rem; border-bottom: 1px solid #E2E8F0; }
button[data-baseweb="tab"] { font-weight: 600; }

.report-preview {
  background: #fff; border: 1px solid #E2E8F0; border-radius: 14px;
  padding: 1.5rem 1.7rem; box-shadow: 0 6px 20px rgba(15,23,42,.06);
}
.report-preview .hospital { font-size: 1.45rem; font-weight: 800; color: #0B7B7A; letter-spacing: -.02em;}
.report-preview .strap { font-size: .78rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.report-preview hr { margin: .8rem 0; border: 0; border-top: 1px solid #E2E8F0; }
.report-preview .pat-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: .35rem 1.5rem;
  margin: .4rem 0; font-size: .9rem;
}
.report-preview .pat-grid .k { color: var(--muted); }
.report-preview .pat-grid .v { color: var(--ink); font-weight: 600; }
.report-preview .sect-title { font-weight: 800; color: #0B7B7A; margin-top: .8rem; font-size: 1rem; letter-spacing: .02em;}
.report-preview table { width: 100%; border-collapse: collapse; font-size: .88rem; margin-top: .4rem;}
.report-preview th { background: #F0FDFA; color: #0B7B7A; text-align: left; padding: .5rem .6rem; font-size:.78rem; letter-spacing: .06em; text-transform: uppercase; }
.report-preview td { padding: .5rem .6rem; border-bottom: 1px solid #F1F5F9; }

.form-help {
  font-size: .78rem; color: var(--muted); margin-top: .25rem;
}
.muted { color: var(--muted); }
.center { text-align: center; }
hr.soft { border:0; border-top: 1px solid #E2E8F0; margin: 1.2rem 0; }
</style>
"""


def inject_global_styles():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


NAV_ITEMS = [
    ("Dashboard", "DSH"),
    ("Diabetes Prediction", "DBT"),
    ("Heart Disease Prediction", "HRT"),
    ("Parkinson's Disease Prediction", "PRK"),
    ("Health History", "HST"),
    ("Recovery Tracker", "REC"),
    ("Medical Report", "RPT"),
]


def _initials(name: str) -> str:
    parts = [p for p in (name or "").strip().split() if p]
    if not parts:
        return "U"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def render_sidebar(user) -> str:
    with st.sidebar:
        st.markdown(
            """
            <div class='brand-block'>
              <div class='brand-title'>MediCare AI</div>
              <div class='brand-sub'>Multi-Disease Prediction Suite</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class='user-card'>
              <div class='user-avatar'>{_initials(user['full_name'])}</div>
              <div>
                <div class='user-name'>{user['full_name']}</div>
                <div class='user-meta'>Patient ID: MC-{user['id']:05d}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div class='section-label'>Navigation</div>", unsafe_allow_html=True)
        active = st.session_state.active_section
        for name, _ in NAV_ITEMS:
            css_class = "nav-active" if name == active else ""
            st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
            if st.button(name, key=f"nav_{name}", use_container_width=True):
                st.session_state.active_section = name
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-label'>Account</div>", unsafe_allow_html=True)
        if st.button("Sign Out", key="signout_btn", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.active_section = "Dashboard"
            st.rerun()

    return st.session_state.active_section


SECTION_META = {
    "Dashboard": ("Health Overview", "Real-time summary of your AI health checkups"),
    "Diabetes Prediction": ("Diabetes Risk Assessment", "Instant ML-based diabetes risk evaluation"),
    "Heart Disease Prediction": ("Heart Disease Risk", "AI cardiovascular risk analysis with 13 clinical inputs"),
    "Parkinson's Disease Prediction": ("Parkinson's Voice Analysis", "Detect Parkinson's risk from vocal biomarkers"),
    "Health History": ("Longitudinal Health History", "Trends and graphs across all your past checkups"),
    "Recovery Tracker": ("Recovery Tracker", "Comparison of your latest checkup with previous ones"),
    "Medical Report": ("Medical Report", "Professional hospital-style PDF report"),
}


def render_top_header(user, active: str):
    title, sub = SECTION_META.get(active, (active, ""))
    now = datetime.now().strftime("%A, %d %B %Y \u2022 %I:%M %p")
    st.markdown(
        f"""
        <div class='app-header'>
          <div>
            <div class='breadcrumb'>MediCare AI / {active}</div>
            <h1>{title}</h1>
            <p>{sub}</p>
          </div>
          <div class='right'>
            <div>Welcome back,</div>
            <div style='font-weight:700;color:var(--ink);font-size:.95rem;'>{user['full_name']}</div>
            <div style='margin-top:2px;'>{now}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_page():
    st.markdown(
        """
        <div style='text-align:center; padding: 2rem 0 0.5rem 0;'>
          <div style='font-size: 2rem; font-weight: 800; letter-spacing: -.02em; color: #0F172A;'>MediCare AI</div>
          <div style='color:#64748B; font-size:.95rem; margin-top:4px;'>AI-Powered Multi-Disease Prediction & Recovery Tracking</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_pad_l, col_main, col_pad_r = st.columns([1, 4, 1])
    with col_main:
        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            with st.container(border=True):
                st.markdown(
                    "<h3 style='margin-top:.2rem; margin-bottom:.1rem; font-weight:800;'>Welcome back</h3>"
                    "<p class='muted' style='margin-bottom:1.2rem;'>Sign in to access your health dashboard.</p>",
                    unsafe_allow_html=True,
                )
                with st.form("login_form", clear_on_submit=False):
                    identifier = st.text_input("Username or Email", placeholder="e.g. raza_ali or you@example.com")
                    password = st.text_input("Password", type="password", placeholder="Enter your password")
                    submitted = st.form_submit_button("Sign In Securely", use_container_width=True, type="primary")
                    if submitted:
                        if not identifier or not password:
                            st.error("Please enter both your username/email and password.")
                        else:
                            user = authenticate_user(identifier, password)
                            if user:
                                st.session_state.user_id = user["id"]
                                st.session_state.active_section = "Dashboard"
                                st.success(f"Welcome back, {user['full_name']}!")
                                st.rerun()
                            else:
                                st.error("Invalid credentials. Please try again or create an account.")

        with tab_register:
            with st.container(border=True):
                st.markdown(
                    "<h3 style='margin-top:.2rem; margin-bottom:.1rem; font-weight:800;'>Create your account</h3>"
                    "<p class='muted' style='margin-bottom:1.2rem;'>Register to start tracking your health journey securely.</p>",
                    unsafe_allow_html=True,
                )
                with st.form("register_form", clear_on_submit=False):
                    c1, c2 = st.columns(2)
                    with c1:
                        full_name = st.text_input("Full Name *", placeholder="Muhammad Raza Ali")
                        username = st.text_input("Username *", placeholder="raza_ali")
                        age = st.number_input("Age *", min_value=10, max_value=110, value=22, step=1)
                        blood_group = st.selectbox(
                            "Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"], index=8
                        )
                    with c2:
                        email = st.text_input("Email *", placeholder="you@example.com")
                        password = st.text_input("Password *", type="password", placeholder="Min 6 characters")
                        gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
                        contact = st.text_input("Contact Number", placeholder="+92 300 0000000")

                    submitted = st.form_submit_button("Create My Account", use_container_width=True, type="primary")
                    if submitted:
                        errors = []
                        if not full_name.strip():
                            errors.append("Full name is required.")
                        if not username.strip() or len(username.strip()) < 3:
                            errors.append("Username must be at least 3 characters.")
                        if "@" not in email or "." not in email:
                            errors.append("Please enter a valid email address.")
                        if len(password) < 6:
                            errors.append("Password must be at least 6 characters.")
                        if errors:
                            for e in errors:
                                st.error(e)
                        else:
                            uid = create_user(full_name, username, email, password, int(age), gender, blood_group, contact)
                            if uid is None:
                                st.error("That username or email is already registered. Please sign in instead.")
                            else:
                                st.session_state.user_id = uid
                                st.session_state.active_section = "Dashboard"
                                st.success("Account created successfully! Redirecting...")
                                st.rerun()
