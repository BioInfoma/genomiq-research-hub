"""
Page 9: Research Projects & Objectives for GenomIQ Research Hub.
Manages long-term PhD research tracks, objectives, and high-level milestones.
"""
from datetime import date
import streamlit as st
from database.connection import get_db
from database.models import ResearchProject, Milestone


def render_projects_page():
    st.title("🎯 Research Projects & Objectives")
    st.caption("Track core PhD dissertation objectives, funding grants, and high-level milestones.")

    with get_db() as db:
        projects = db.query(ResearchProject).all()

        for proj in projects:
            with st.container():
                st.markdown(f"""
                    <div class="pub-card" style="border-left-color: #0284c7;">
                        <div style="font-size: 1.25rem; font-weight: bold; color: #0f172a; margin-bottom: 6px;">{proj.title}</div>
                        <div style="font-size: 0.9rem; color: #334155; margin-bottom: 10px;">{proj.description}</div>
                        <div style="font-size: 0.82rem; color: #64748b;">
                            <b>Timeline:</b> {proj.start_date.strftime('%b %Y') if proj.start_date else 'N/A'} — 
                            {proj.target_end_date.strftime('%b %Y') if proj.target_end_date else 'Ongoing'} | 
                            <b>Status:</b> <span style="color:#0284c7; font-weight:bold;">{proj.status}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("##### Milestones Associated with this Project")
                milestones = db.query(Milestone).filter(Milestone.project_id == proj.id).all()
                if milestones:
                    for m in milestones:
                        m_c1, m_c2, m_c3 = st.columns([3, 1, 1])
                        with m_c1:
                            st.write(f"- **{m.title}**")
                        with m_c2:
                            st.write(f"Due: {m.due_date.strftime('%Y-%m-%d') if m.due_date else 'TBD'}")
                        with m_c3:
                            m_stat = st.selectbox(
                                "Milestone Status",
                                ["Pending", "In Progress", "Achieved"],
                                index=["Pending", "In Progress", "Achieved"].index(m.status) if m.status in ["Pending", "In Progress", "Achieved"] else 0,
                                key=f"ms_stat_{m.id}",
                                label_visibility="collapsed"
                            )
                            if m_stat != m.status:
                                m.status = m_stat
                                db.commit()
                                st.rerun()

                with st.expander("➕ Add New Milestone to this Project"):
                    with st.form(key=f"add_ms_form_{proj.id}"):
                        ms_title = st.text_input("Milestone Title", placeholder="e.g. Complete variant calling pipeline validation on 50 samples")
                        ms_due = st.date_input("Target Completion Date", value=date.today())
                        if st.form_submit_button("Add Milestone"):
                            if ms_title.strip():
                                new_ms = Milestone(project_id=proj.id, title=ms_title.strip(), due_date=ms_due, status="Pending")
                                db.add(new_ms)
                                db.commit()
                                st.success("Milestone added!")
                                st.rerun()

        st.markdown("---")
        with st.expander("➕ Create New Research Project"):
            with st.form("new_proj_form"):
                p_title = st.text_input("Project / Manuscript Title", placeholder="e.g. Benchmarking Somatic SNVs in Colorectal Cancer")
                p_desc = st.text_area("Scope and Objectives", placeholder="Key hypotheses, datasets, and planned publications.")
                p_start = st.date_input("Start Date", value=date.today())
                p_end = st.date_input("Target Defense / Submission Date")
                if st.form_submit_button("Create Project", type="primary"):
                    if p_title.strip():
                        new_p = ResearchProject(title=p_title.strip(), description=p_desc.strip(), start_date=p_start, target_end_date=p_end, status="Active")
                        db.add(new_p)
                        db.commit()
                        st.success("Project created!")
                        st.rerun()
