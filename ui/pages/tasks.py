"""
Page 10: Tasks & Milestones (PhD Kanban Board) for GenomIQ Research Hub.
Provides visual Kanban column management, task status transitions, and publication linking.
"""
from datetime import date, datetime
import streamlit as st
from database.connection import get_db
from database.models import Task, ResearchProject, Publication


def render_tasks_page():
    st.title("📋 Research Tasks & Kanban Board")
    st.caption("Organize day-to-day PhD computational tasks, reading goals, and pipeline milestones.")

    tab_kanban, tab_add = st.tabs(["📊 Kanban Board", "➕ Add New Task"])

    with tab_kanban:
        with get_db() as db:
            tasks = db.query(Task).all()

            col_todo, col_inprog, col_done, col_hold = st.columns(4)

            columns_spec = [
                ("To do", col_todo, "#64748b", "📝 TO DO"),
                ("In progress", col_inprog, "#2563eb", "⚡ IN PROGRESS"),
                ("Completed", col_done, "#16a34a", "✅ COMPLETED"),
                ("On hold", col_hold, "#d97706", "⏸ ON HOLD"),
            ]

            for status_name, col_handle, border_color, col_label in columns_spec:
                with col_handle:
                    status_tasks = [t for t in tasks if t.status == status_name]
                    st.markdown(f"#### {col_label} ({len(status_tasks)})")
                    st.markdown(f"<div style='border-top: 3px solid {border_color}; margin-bottom: 12px;'></div>", unsafe_allow_html=True)

                    for t in status_tasks:
                        pri_badge = "#ef4444" if t.priority == "Urgent" else "#f97316" if t.priority == "High" else "#3b82f6"
                        with st.container():
                            st.markdown(f"""
                                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:6px; padding:12px; margin-bottom:10px; box-shadow:0 1px 2px rgba(0,0,0,0.04);">
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                        <span style="background:{pri_badge}22; color:{pri_badge}; font-size:0.75rem; font-weight:bold; padding:1px 6px; border-radius:6px;">
                                            {t.priority}
                                        </span>
                                        <span style="font-size:0.75rem; color:#64748b;">
                                            {t.due_date.strftime('%b %d') if t.due_date else 'No due date'}
                                        </span>
                                    </div>
                                    <div style="font-weight:600; font-size:0.92rem; color:#0f172a; margin-bottom:4px;">{t.title}</div>
                                    <div style="font-size:0.8rem; color:#475569; margin-bottom:8px;">{t.description[:80] + '...' if len(t.description) > 80 else t.description}</div>
                                </div>
                            """, unsafe_allow_html=True)

                            # Move column dropdown
                            opts = ["To do", "In progress", "Completed", "On hold"]
                            new_st = st.selectbox(
                                "Move to",
                                opts,
                                index=opts.index(t.status),
                                key=f"kanban_move_{t.id}",
                                label_visibility="collapsed"
                            )
                            if new_st != t.status:
                                t.status = new_st
                                if new_st == "Completed":
                                    t.completed_at = datetime.utcnow()
                                db.commit()
                                st.rerun()

    with tab_add:
        st.subheader("Add a New Task")
        with get_db() as db:
            projects = db.query(ResearchProject).all()
            proj_opts = {p.id: p.title for p in projects}
            proj_opts[0] = "-- None (General Task) --"

            pubs = db.query(Publication).all()
            pub_opts = {p.id: p.title[:50] + "..." for p in pubs}
            pub_opts[0] = "-- None --"

            with st.form("create_task_form"):
                t_title = st.text_input("Task Title", placeholder="e.g. Run Mutect2 on CRC patient 10 tumor-normal pair")
                t_desc = st.text_area("Description / Command Line Checklist", placeholder="Specify pipeline options, memory limits, and target outputs.")
                c_p1, c_p2, c_p3 = st.columns(3)
                with c_p1:
                    t_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"], index=1)
                with c_p2:
                    t_status = st.selectbox("Initial Status", ["To do", "In progress", "Completed", "On hold"], index=0)
                with c_p3:
                    t_due = st.date_input("Due Date", value=date.today())

                c_l1, c_l2 = st.columns(2)
                with c_l1:
                    t_proj_id = st.selectbox("Associated Project", list(proj_opts.keys()), format_func=lambda x: proj_opts[x])
                with c_l2:
                    t_pub_id = st.selectbox("Link to Publication", list(pub_opts.keys()), format_func=lambda x: pub_opts[x])

                submitted = st.form_submit_button("Create Task", type="primary")
                if submitted:
                    if t_title.strip():
                        new_task = Task(
                            title=t_title.strip(),
                            description=t_desc.strip(),
                            priority=t_priority,
                            status=t_status,
                            due_date=t_due,
                            project_id=t_proj_id if t_proj_id != 0 else None,
                            linked_publication_id=t_pub_id if t_pub_id != 0 else None
                        )
                        db.add(new_task)
                        db.commit()
                        st.success(f"Task '{t_title}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Please enter a Task Title.")
