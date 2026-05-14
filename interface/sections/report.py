import streamlit as st
from datetime import datetime
from core.database import get_user_predictions, get_latest_prediction, get_previous_prediction
from core.pdf_report import generate_report
from core.helpers import format_dt, risk_band


def render(user):
    all_preds = get_user_predictions(user["id"])
    if not all_preds:
        st.info("Generate a prediction first \u2014 then a professional medical report will be available here.")
        return

    left, right = st.columns([1.1, 1])

    with left:
        with st.container(border=True):
            st.markdown("### Generate Medical Report")
            st.caption("Choose what to include in your professional hospital-style PDF report.")

            mode = st.radio(
                "Report contents",
                [
                    "Comprehensive (latest result for every disease)",
                    "Single checkup (pick from history)",
                    "Disease-specific (all results for one disease)",
                ],
                index=0,
            )

            include_recovery = st.checkbox("Include recovery comparison (latest vs previous)", value=True)

            selected_preds = []
            recovery_pairs = []

            diseases = sorted({p["disease"] for p in all_preds})

            if mode.startswith("Comprehensive"):
                for d in diseases:
                    latest = get_latest_prediction(user["id"], d)
                    if latest:
                        selected_preds.append(latest)
                        prev = get_previous_prediction(user["id"], d, latest["id"])
                        if prev and include_recovery:
                            recovery_pairs.append((latest, prev))
            elif mode.startswith("Single"):
                opts = {f"{p['disease']} - {format_dt(p['created_at'])} - {p['probability']*100:.1f}% ({p['result']})": p
                        for p in all_preds}
                pick = st.selectbox("Select a checkup", list(opts.keys()))
                selected_preds = [opts[pick]]
                if include_recovery:
                    sel = opts[pick]
                    prev = get_previous_prediction(user["id"], sel["disease"], sel["id"])
                    if prev:
                        recovery_pairs.append((sel, prev))
            else:
                d_pick = st.selectbox("Select disease", diseases)
                selected_preds = [p for p in all_preds if p["disease"] == d_pick]
                if include_recovery and len(selected_preds) >= 2:
                    recovery_pairs.append((selected_preds[0], selected_preds[1]))

            st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

            if selected_preds:
                pdf_bytes = generate_report(user, selected_preds, recovery_pairs)
                file_name = f"MediCare_Report_{user['full_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                st.download_button(
                    label="Download Medical Report (PDF)",
                    data=pdf_bytes,
                    file_name=file_name,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )
                st.success(f"Report generated in real time \u2014 {len(selected_preds)} checkup(s) included.")
            else:
                st.warning("No checkups available for the selected option.")

    with right:
        with st.container(border=False):
            st.markdown("### Live Report Preview")
            preview_preds = selected_preds[:3] if selected_preds else []
            patient_block = f"""
              <div class='pat-grid'>
                <div><span class='k'>Patient Name:</span> <span class='v'>{user['full_name']}</span></div>
                <div><span class='k'>Patient ID:</span> <span class='v'>MC-{user['id']:05d}</span></div>
                <div><span class='k'>Age / Gender:</span> <span class='v'>{user.get('age','-')} years / {user.get('gender','-')}</span></div>
                <div><span class='k'>Blood Group:</span> <span class='v'>{user.get('blood_group','-') or '-'}</span></div>
                <div><span class='k'>Email:</span> <span class='v'>{user.get('email','-')}</span></div>
                <div><span class='k'>Contact:</span> <span class='v'>{user.get('contact','-') or '-'}</span></div>
              </div>
            """
            results_html = ""
            for p in preview_preds:
                band, color = risk_band(p["probability"])
                color_bg = "#FEE2E2" if p["result"] == "Positive" else "#D1FAE5"
                color_fg = "#991B1B" if p["result"] == "Positive" else "#065F46"
                results_html += f"""
                <div class='sect-title'>{p['disease']} Diagnostic Assessment</div>
                <table>
                  <tr><th>Field</th><th>Detail</th></tr>
                  <tr><td>Test Date</td><td>{format_dt(p['created_at'])}</td></tr>
                  <tr><td>Result</td><td><span style='background:{color_bg};color:{color_fg};padding:2px 8px;border-radius:6px;font-weight:700;'>{p['result']}</span></td></tr>
                  <tr><td>AI Risk Probability</td><td><b style='color:{color}'>{p['probability']*100:.2f}%</b> &nbsp; {band}</td></tr>
                  <tr><td>Clinical Advice</td><td>{p['advice'] or ''}</td></tr>
                </table>
                """
            extra = ""
            if len(selected_preds) > 3:
                extra = f"<p class='muted' style='margin-top:.6rem;font-size:.85rem;'>+ {len(selected_preds)-3} more checkup(s) in the full PDF.</p>"

            st.markdown(
                f"""
                <div class='report-preview'>
                  <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                    <div>
                      <div class='hospital'>MEDICARE AI HOSPITAL</div>
                      <div class='strap'>AI-Powered Multi-Disease Diagnostic Center</div>
                      <div class='muted' style='font-size:.8rem;margin-top:2px;'>College Road, 56000 Gojra, Toba Tek Singh, Punjab</div>
                    </div>
                    <div style='text-align:right;'>
                      <div style='font-weight:800;color:#0B7B7A;'>MEDICAL REPORT</div>
                      <div class='muted' style='font-size:.78rem;margin-top:2px;'>{datetime.now().strftime('%d %b %Y, %I:%M %p')}</div>
                      <div class='muted' style='font-size:.78rem;'>Report ID: MR-{user['id']:05d}-{datetime.now().strftime('%y%m%d')}</div>
                    </div>
                  </div>
                  <hr/>
                  <div class='sect-title'>Patient Information</div>
                  {patient_block}
                  {results_html}
                  {extra}
                </div>
                """,
                unsafe_allow_html=True,
            )
