"""
Page 12: Reports & Automated Weekly Digest for GenomIQ Research Hub.
Generates comprehensive research digests, reading trend reports, and export files.
"""
from datetime import date
import streamlit as st
import plotly.express as px
import pandas as pd
from database.connection import get_db
from database.models import WeeklyDigest, ReadingRecord, Publication
from core.digest import DigestGenerator
from core.reading_tracker import ReadingTrackerService


def render_reports_page():
    st.title("📊 Research Intelligence Reports & Digests")
    st.caption("Weekly automated research digests, reading consistency analytics, and supervisor reporting.")

    gen = DigestGenerator()
    tracker = ReadingTrackerService()
    current_week = f"{date.today().year}-W{date.today().isocalendar()[1]:02d}"

    tab_digest, tab_analytics = st.tabs(["📑 Weekly Research Digest", "📈 Long-Term Reading Analytics"])

    with tab_digest:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader(f"Weekly Intelligence Digest ({current_week})")
        with c2:
            if st.button("🔄 Synthesize Fresh Digest", type="primary", use_container_width=True):
                with st.spinner("Synthesizing literature intelligence, preprints, and tasks..."):
                    gen.generate_digest(current_week)
                    st.success("Synthesized fresh weekly digest!")
                    st.rerun()

        with get_db() as db:
            digest = db.query(WeeklyDigest).filter(WeeklyDigest.week_identifier == current_week).first()
            if not digest:
                st.info("No digest compiled for this week yet. Click 'Synthesize Fresh Digest' to generate.")
                digest = gen.generate_digest(current_week)

            # Download buttons
            d_c1, d_c2, _ = st.columns([1, 1, 2])
            with d_c1:
                st.download_button(
                    "📥 Export as Markdown",
                    digest.content_markdown,
                    file_name=f"genomiq_digest_{current_week}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with d_c2:
                html_export = f"<html><head><title>GenomIQ Digest {current_week}</title><style>body{{font-family:sans-serif; line-height:1.6; max-width:800px; margin:auto; padding:20px;}}</style></head><body><pre style='white-space: pre-wrap;'>{digest.content_markdown}</pre></body></html>"
                st.download_button(
                    "📥 Export as HTML",
                    html_export,
                    file_name=f"genomiq_digest_{current_week}.html",
                    mime="text/html",
                    use_container_width=True
                )

            st.markdown("---")
            st.markdown(digest.content_markdown)

    with tab_analytics:
        st.subheader("PhD Reading Velocity & Topic Coverage")
        with get_db() as db:
            records = db.query(ReadingRecord).all()
            if not records:
                st.info("No reading records documented yet.")
                return

            completed_records = [r for r in records if r.status == "Completed"]
            total_minutes = sum(r.reading_duration_minutes or 0 for r in records)

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Papers Read (All Time)", len(completed_records))
            m2.metric("Accumulated Reading Hours", f"{round(total_minutes/60, 1)} hrs")
            m3.metric("Average Rating Given", f"{round(sum(r.rating or 0 for r in completed_records) / max(1, len(completed_records)), 1)} / 5 ⭐")

            # Topic distribution chart
            df_topics = tracker.get_topic_distribution()
            if not df_topics.empty:
                st.markdown("#### Reading by Research Domain")
                fig = px.bar(
                    df_topics,
                    x="Topic",
                    y=["Total", "Completed"],
                    barmode="group",
                    labels={"value": "Count", "variable": "Metric"},
                    title="Domain Saturation: Ingested vs Completed Papers",
                    color_discrete_map={"Total": "#93c5fd", "Completed": "#1d4ed8"}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
