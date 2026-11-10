"""
Page 4: Four-Paper Weekly Reading Tracker for GenomIQ Research Hub.
Facilitates in-depth reading, note capture, method recording, and progress against supervisor target.
"""
from datetime import date
import streamlit as st
from database.connection import get_db
from database.models import Publication, ReadingRecord, Recommendation
from core.reading_tracker import ReadingTrackerService


def render_reading_tracker_page():
    st.title("📖 Weekly Reading Tracker")
    st.caption("Document insights, critical methods, findings, and progress against the supervisor's 4-paper target.")

    tracker = ReadingTrackerService()
    kpis = tracker.get_weekly_kpis()

    # Progress bar and stats
    c1, c2, c3 = st.columns(3)
    c1.metric("Weekly Target Progress", f"{kpis['completed_this_week']} / 4 Papers", f"{kpis['completion_percentage']}%")
    c2.metric("Currently Reading", kpis["in_progress"])
    c3.metric("Total Documented Hours", f"{kpis['total_reading_hours']} hrs")

    st.progress(min(kpis["completion_percentage"] / 100.0, 1.0))
    st.markdown("---")

    # Get active papers to track: either currently recommended this week or in progress
    with get_db() as db:
        current_week = kpis["week_identifier"]
        recs = db.query(Recommendation).filter(Recommendation.week_identifier == current_week).all()
        rec_pub_ids = [r.publication_id for r in recs]

        # Fetch publications
        pubs_to_track = db.query(Publication).filter(
            (Publication.id.in_(rec_pub_ids)) | (Publication.reading_status.in_(["Reading", "Accepted"]))
        ).all()

        if not pubs_to_track:
            st.info("No active papers currently in reading tracker. Accept papers from the 'Recommended Reading' page or Library.")
            return

        for p in pubs_to_track:
            rr = db.query(ReadingRecord).filter(ReadingRecord.publication_id == p.id).first()
            if not rr:
                rr = ReadingRecord(publication_id=p.id, status=p.reading_status)
                db.add(rr)
                db.flush()

            status_badge_color = "#15803d" if p.reading_status == "Completed" else "#ca8a04" if p.reading_status == "Reading" else "#2563eb"

            with st.expander(f"[{p.reading_status.upper()}] {p.title}", expanded=(p.reading_status == "Reading")):
                st.markdown(f"""
                    <div style="font-size:0.85rem; color:#475569; margin-bottom: 8px;">
                        <b>Authors:</b> {p.authors} | <b>Journal:</b> {p.journal} ({p.year}) | <b>DOI:</b> <a href="https://doi.org/{p.doi}" target="_blank">{p.doi}</a>
                    </div>
                """, unsafe_allow_html=True)

                if p.pdf_url:
                    st.markdown(f"📥 [Direct Open Access PDF Link]({p.pdf_url})")

                with st.form(key=f"track_form_{p.id}"):
                    f_col1, f_col2, f_col3 = st.columns(3)
                    with f_col1:
                        new_status = st.selectbox(
                            "Reading Status",
                            ["Recommended", "Accepted", "Reading", "Completed", "Revisit", "Not relevant"],
                            index=["Recommended", "Accepted", "Reading", "Completed", "Revisit", "Not relevant"].index(p.reading_status) if p.reading_status in ["Recommended", "Accepted", "Reading", "Completed", "Revisit", "Not relevant"] else 0
                        )
                    with f_col2:
                        duration_add = st.number_input("Add Reading Time (Minutes)", min_value=0, max_value=480, value=30, step=15)
                    with f_col3:
                        star_rating = st.slider("Scientific Value / Rating", min_value=1, max_value=5, value=rr.rating or 4)

                    st.markdown("##### Structured PhD Reading Reflection")
                    findings = st.text_area("1. Main Biological & Computational Findings", value=rr.main_findings or "", height=80, placeholder="Key empirical results, novel genomic loci, benchmark statistics...")
                    methods = st.text_area("2. Important Methods, Algorithms & Datasets", value=rr.important_methods or "", height=80, placeholder="Algorithms used (e.g. string graphs, Mutect2 flags, sample cohorts)...")
                    limitations = st.text_area("3. Methodological Limitations & Blind Spots", value=rr.limitations or "", height=80, placeholder="Unaddressed biases, coverage depth constraints, lack of validation cohorts...")
                    phd_application = st.text_area("4. Direct Relevance & Application to PhD", value=rr.phd_relevance or "", height=80, placeholder="How can this paper be cited in Chapter 1 or applied to our cancer dataset?")
                    notes = st.text_area("5. General Personal Notes & Questions Raised", value=rr.personal_notes or "", height=80, placeholder="Questions to ask supervisor at next committee meeting...")

                    save_btn = st.form_submit_button("💾 Save Reading Record & Update Status", type="primary", use_container_width=True)

                    if save_btn:
                        tracker.update_reading_progress(
                            publication_id=p.id,
                            status=new_status,
                            duration_minutes=int(duration_add),
                            personal_notes=notes,
                            main_findings=findings,
                            important_methods=methods,
                            limitations=limitations,
                            phd_relevance=phd_application,
                            rating=int(star_rating)
                        )
                        st.success(f"Updated record for '{p.title[:40]}...' (Status: {new_status})")
                        st.rerun()
