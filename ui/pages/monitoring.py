"""
Page 11: Web & Research Monitoring for GenomIQ Research Hub.
Monitors GitHub releases for bioinformatics tools and RSS feeds from preprint servers and journals.
"""
import streamlit as st
from database.connection import get_db
from database.models import MonitoredEntity
from core.monitoring import WebMonitoringService


def render_monitoring_page():
    st.title("📡 Web & Research Monitoring")
    st.caption("Automated tracking of bioinformatics software releases (GitHub) and preprint feeds (bioRxiv/journals).")

    service = WebMonitoringService()

    c_top1, c_top2 = st.columns([3, 1])
    with c_top1:
        st.write("Active monitors periodically scan for tool releases, new issues, and published journal TOCs.")
    with c_top2:
        if st.button("🔄 Refresh All Feeds & Releases", use_container_width=True, type="primary"):
            with st.spinner("Checking GitHub API and RSS feeds..."):
                updates = service.refresh_all_monitors()
                st.success(f"Scanned feeds! Received updates from {len(updates)} monitored sources.")
                st.rerun()

    tab_active, tab_add = st.tabs(["📋 Monitored Sources", "➕ Add New Monitor"])

    with tab_active:
        with get_db() as db:
            entities = db.query(MonitoredEntity).all()
            if not entities:
                st.info("No sources being monitored. Add a GitHub repository or RSS feed below.")
                return

            for e in entities:
                icon = "🐙" if e.entity_type == "github_repo" else "📰"
                with st.expander(f"{icon} {e.name} ({e.entity_type})"):
                    st.write(f"**Target URL:** [{e.url}]({e.url})")
                    st.write(f"**Last Scanned:** {e.last_checked.strftime('%Y-%m-%d %H:%M UTC') if e.last_checked else 'Never'}")

                    if e.latest_title:
                        st.markdown(f"#### Latest Discovered Item")
                        st.markdown(f"- **Title:** [{e.latest_title}]({e.latest_link or '#'})")
                        if e.latest_snippet:
                            st.caption(e.latest_snippet)
                    else:
                        st.info("No recent items recorded. Click 'Refresh All Feeds' to scan.")

                    col_del, _ = st.columns([1, 4])
                    with col_del:
                        if st.button("🗑 Stop Monitoring", key=f"del_mon_{e.id}"):
                            db.delete(e)
                            db.commit()
                            st.warning("Removed monitor.")
                            st.rerun()

    with tab_add:
        st.subheader("Add a New Source to Monitor")
        with st.form("new_monitor_form"):
            m_name = st.text_input("Source Name", placeholder="e.g. Nextflow GitHub Releases, Nature Genetics TOC")
            m_type = st.selectbox("Source Type", ["github_repo", "rss_feed", "journal", "lab"])
            m_url = st.text_input("URL / Identifier", placeholder="e.g. nextflow-io/nextflow or https://www.nature.com/ng.rss")
            submitted = st.form_submit_button("Add Monitor", type="primary")
            if submitted:
                if m_name.strip() and m_url.strip():
                    with get_db() as db:
                        repo_id = m_url.replace("https://github.com/", "").strip("/") if m_type == "github_repo" else ""
                        new_e = MonitoredEntity(name=m_name.strip(), entity_type=m_type, url=m_url.strip(), feed_or_repo=repo_id, is_active=True)
                        db.add(new_e)
                        db.commit()
                    st.success(f"Added monitor for '{m_name}'!")
                    st.rerun()
                else:
                    st.error("Please provide both Name and URL.")
