"""
Page 1: Overview Dashboard for GenomIQ Research Hub.
"""
from datetime import date
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from database.connection import get_db
from database.models import Publication, ReadingRecord, Recommendation, Task, ResearchProject, Milestone
from core.reading_tracker import ReadingTrackerService
from ui.components import render_kpi


def render_overview_page():
    st.title("🔬 Research Intelligence & Overview")
    st.caption("PhD Progress Dashboard | Bioinformatics, Human Genomics & Cancer Genomics")

    tracker = ReadingTrackerService()
    kpis = tracker.get_weekly_kpis()

    # KPI Top Bar
    c1, c2, c3, c4 = st.columns(4)
    render_kpi(c1, "Weekly Reading Target", f"{kpis['completed_this_week']} / {kpis['weekly_target']}", f"{kpis['completion_percentage']}% completed this week")
    render_kpi(c2, "Library Size", kpis["total_in_library"], "Total ingested scientific papers")
    render_kpi(c3, "Total Papers Read", kpis["total_completed_all_time"], f"{kpis['total_reading_hours']} documented reading hours")
    render_kpi(c4, "Pending Recommendations", kpis["recommended"], f"Target week: {kpis['week_identifier']}")

    # Progress Bar against 4-paper weekly target
    st.markdown("#### Weekly 4-Paper Reading Commitment")
    pct_val = min(kpis["completion_percentage"] / 100.0, 1.0)
    st.progress(pct_val)
    if kpis["completed_this_week"] >= 4:
        st.success("🎉 Outstanding! You have met your supervisor's 4-paper reading goal for this week!")
    else:
        st.info(f"💡 You need **{max(0, 4 - kpis['completed_this_week'])} more paper(s)** completed to fulfill this week's supervisor target.")

    st.markdown("---")

    # Main Grid: Left = Recommendations & Active Reading, Right = Analytics & Tasks
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📚 Active Weekly Recommendations")
        with get_db() as db:
            current_week = kpis["week_identifier"]
            recs = db.query(Recommendation).filter(Recommendation.week_identifier == current_week).all()
            if recs:
                for r in recs:
                    pub = r.publication
                    badge_class = "badge-core" if r.category == "Core" else "badge-comp" if r.category == "Computational" else "badge-compl"
                    with st.container():
                        st.markdown(f"""
                            <div class="pub-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <span class="badge {badge_class}">{r.category} Track</span>
                                    <span style="font-size: 0.8rem; color: #64748b;">Status: <b>{pub.reading_status}</b></span>
                                </div>
                                <div class="pub-title"><a href="{pub.publisher_url or '#'}" target="_blank" style="text-decoration: none; color: #0f172a;">{pub.title}</a></div>
                                <div class="pub-authors">{pub.authors}</div>
                                <div class="pub-meta">
                                    <span>🏛 {pub.journal or 'Journal'} ({pub.year or 'N/A'})</span>
                                    <span>⭐ Citations: {pub.citation_count}</span>
                                    <span>{'🟢 Open Access' if pub.is_open_access else '🔒 Subscription'}</span>
                                </div>
                                <div class="rec-rationale-box">
                                    <small><b>Why selected:</b> {r.selection_reason}</small>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No recommendations generated for this week yet.")
                if st.button("Generate 4 Weekly Recommendations Now"):
                    from core.recommendation import RecommendationEngine
                    engine = RecommendationEngine()
                    engine.generate_weekly_recommendations(force_refresh=True)
                    st.rerun()

        # Recently Discovered Papers
        st.subheader("⚡ Recently Ingested Papers")
        with get_db() as db:
            recent_pubs = db.query(Publication).order_by(Publication.date_discovered.desc()).limit(4).all()
            for rp in recent_pubs:
                st.markdown(f"- **[{rp.title}]({rp.publisher_url or '#'})** — *{rp.journal}* ({rp.year}) | `{rp.paper_category}`")

    with col_right:
        st.subheader("📊 Research Topic Distribution")
        df_topics = tracker.get_topic_distribution()
        if not df_topics.empty:
            fig = px.bar(
                df_topics.head(6),
                x="Total",
                y="Topic",
                orientation="h",
                color="Completed",
                color_continuous_scale="Blues",
                labels={"Total": "Papers in Library", "Completed": "Completed"},
                height=280
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig, use_container_width=True)

        # Active Tasks & Deadlines
        st.subheader("📌 Urgent PhD Tasks")
        with get_db() as db:
            tasks = db.query(Task).filter(Task.status.in_(["To do", "In progress"])).order_by(Task.due_date.asc()).limit(5).all()
            if tasks:
                for t in tasks:
                    due = t.due_date.strftime("%b %d") if t.due_date else "No due date"
                    pri_color = "red" if t.priority == "Urgent" else "orange" if t.priority == "High" else "blue"
                    st.markdown(f"- **{t.title}** <span style='color:{pri_color}; font-size:0.8rem;'>({t.priority.upper()})</span> — *Due: {due}*", unsafe_allow_html=True)
            else:
                st.info("No active tasks. Add tasks in the Tasks & Milestones tab.")
