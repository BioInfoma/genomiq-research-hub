"""
Page 3: Intelligent Paper Recommendation Engine for GenomIQ Research Hub.
Displays the 4 weekly papers, structured rationales, learning points,
accept/reject controls, and reading pathway generation.
"""
import json
from datetime import date
import streamlit as st
from database.connection import get_db
from database.models import Recommendation, Publication, ReadingRecord
from core.recommendation import RecommendationEngine


def render_recommendations_page():
    st.title("🎯 Weekly Paper Recommendations")
    st.caption("Targeted 4-paper weekly allocation: 2 Core, 1 Computational / Methodological, 1 Complementary.")

    rec_engine = RecommendationEngine()
    current_week = f"{date.today().year}-W{date.today().isocalendar()[1]:02d}"

    tab_weekly, tab_pathway = st.tabs(["📅 Weekly 4-Paper Allocation", "🗺️ Guided Reading Pathways"])

    with tab_weekly:
        c_top1, c_top2 = st.columns([3, 1])
        with c_top1:
            st.markdown(f"### Current Schedule: **{current_week}**")
        with c_top2:
            if st.button("🔄 Regenerate Allocation", use_container_width=True):
                with st.spinner("Executing weighted 9-parameter scoring..."):
                    rec_engine.generate_weekly_recommendations(week_identifier=current_week, force_refresh=True)
                    st.success("Refreshed 4 weekly recommendations!")
                    st.rerun()

        with get_db() as db:
            recs = db.query(Recommendation).filter(Recommendation.week_identifier == current_week).all()
            if not recs:
                st.info("No recommendations generated yet for this week.")
                if st.button("Generate Recommendations Now", type="primary"):
                    rec_engine.generate_weekly_recommendations(week_identifier=current_week)
                    st.rerun()
                return

            for idx, rec in enumerate(recs, 1):
                pub = rec.publication
                track_color = "#3b82f6" if rec.category == "Core" else "#d97706" if rec.category == "Computational" else "#15803d"

                with st.expander(f"Paper {idx} [{rec.category.upper()} TRACK]: {pub.title}", expanded=True):
                    # Header badges
                    st.markdown(f"""
                        <div style="display: flex; gap: 10px; margin-bottom: 8px;">
                            <span style="background:{track_color}22; color:{track_color}; padding:2px 8px; border-radius:10px; font-weight:bold; font-size:0.8rem;">
                                {rec.category} Research Track
                            </span>
                            <span style="background:#f1f5f9; color:#475569; padding:2px 8px; border-radius:10px; font-size:0.8rem;">
                                Recommendation Score: <b>{rec.recommendation_score} / 100</b>
                            </span>
                            <span style="background:#f1f5f9; color:#475569; padding:2px 8px; border-radius:10px; font-size:0.8rem;">
                                Status: <b>{rec.status}</b>
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

                    # Publication Metadata
                    st.write(f"**Authors:** {pub.authors}")
                    st.write(f"**Journal:** *{pub.journal}* ({pub.year or 'N/A'}) | **Citations:** {pub.citation_count} | **DOI:** [{pub.doi or 'N/A'}](https://doi.org/{pub.doi})")

                    # Structured Recommendation Explanation
                    st.markdown("#### 🔍 Recommendation Rationale")
                    st.markdown(f"**Why this paper was selected:** {rec.selection_reason}")
                    st.markdown(f"**Addressed Research Interest:** `{rec.targeted_interest}`")
                    st.markdown(f"**Relevance to PhD Thesis:** {rec.phd_relevance}")

                    # 3 Learning Points
                    learnings = json.loads(rec.key_learnings_json) if rec.key_learnings_json else []
                    if learnings:
                        st.markdown("**Three Essential Things to Learn:**")
                        for l in learnings:
                            st.markdown(f"- {l}")

                    # Abstract
                    with st.expander("Show Abstract"):
                        st.write(pub.abstract)

                    # User Action Buttons
                    st.markdown("---")
                    act_col1, act_col2, act_col3, act_col4 = st.columns(4)

                    with act_col1:
                        if st.button("✅ Accept for Reading", key=f"acc_{rec.id}", use_container_width=True):
                            rec.status = "Accepted"
                            pub.reading_status = "Accepted"
                            db.commit()
                            st.success("Accepted into Reading Tracker!")
                            st.rerun()

                    with act_col2:
                        if st.button("📖 Start Reading Now", key=f"read_{rec.id}", use_container_width=True):
                            rec.status = "Accepted"
                            pub.reading_status = "Reading"
                            # Ensure reading record exists
                            rr = db.query(ReadingRecord).filter(ReadingRecord.publication_id == pub.id).first()
                            if not rr:
                                rr = ReadingRecord(publication_id=pub.id)
                                db.add(rr)
                            rr.status = "Reading"
                            rr.date_started = date.today()
                            db.commit()
                            st.success("Status updated to 'Reading'!")
                            st.rerun()

                    with act_col3:
                        if st.button("⏳ Postpone", key=f"post_{rec.id}", use_container_width=True):
                            rec.status = "Postponed"
                            db.commit()
                            st.info("Postponed recommendation.")
                            st.rerun()

                    with act_col4:
                        if st.button("❌ Reject / Replace", key=f"rej_{rec.id}", use_container_width=True):
                            rec.status = "Rejected"
                            pub.reading_status = "Not relevant"
                            db.commit()
                            st.warning("Paper marked not relevant. Generating replacement...")
                            rec_engine.generate_weekly_recommendations(week_identifier=current_week, force_refresh=True)
                            st.rerun()

    # TAB 2: Guided Reading Pathways
    with tab_pathway:
        st.subheader("🗺️ Guided Progressive Reading Pathways")
        st.caption("A structured 4-tier pathway transitioning from conceptual overviews to cutting-edge research.")

        with get_db() as db:
            available_topics = ["All Topics", "Human Pangenomics", "African Population Genomics", "Colorectal Cancer", "Bioinformatics Methods"]
            sel_topic = st.selectbox("Select Topic Focus", available_topics)

            pathway = rec_engine.generate_reading_pathway(sel_topic if sel_topic != "All Topics" else None)
            if pathway:
                for step in pathway:
                    paper = step["paper"]
                    st.markdown(f"""
                        <div class="pub-card" style="border-left-color: #6366f1;">
                            <div style="font-size: 0.85rem; font-weight: bold; color: #4338ca;">TIER {step['tier']}: {step['level'].upper()}</div>
                            <div class="pub-title"><a href="{paper.publisher_url or '#'}" target="_blank">{paper.title}</a></div>
                            <div class="pub-authors">{paper.authors} ({paper.journal}, {paper.year})</div>
                            <div style="font-size: 0.85rem; color: #1e293b; margin-top: 6px;"><b>Learning Objective:</b> {step['focus']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Add more publications to your library to assemble complete multi-tier reading pathways.")
