"""
GenomIQ Research Hub: Personal PhD Research Intelligence and Management Platform
Main Streamlit Application Entrypoint.
"""
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="GenomIQ Research Hub",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

from database.connection import init_db
from database.seed_data import seed_all
from core.scheduler import start_background_scheduler
from ui.components import apply_custom_css

# Lazy import pages
from ui.pages.overview import render_overview_page
from ui.pages.discovery import render_discovery_page
from ui.pages.recommendations import render_recommendations_page
from ui.pages.reading_tracker import render_reading_tracker_page
from ui.pages.library import render_library_page
from ui.pages.notes import render_notes_page
from ui.pages.tools import render_tools_page
from ui.pages.citations import render_citations_page
from ui.pages.projects import render_projects_page
from ui.pages.tasks import render_tasks_page
from ui.pages.monitoring import render_monitoring_page
from ui.pages.reports import render_reports_page
from ui.pages.settings import render_settings_page


def main():
    # 1. Initialize database and seed starter profiles/tools
    init_db()
    seed_all()

    # 2. Start background scheduler
    start_background_scheduler()

    # 3. Apply CSS styling
    apply_custom_css()

    # 4. Sidebar Navigation
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 20px;">
                <span style="font-size: 2.2rem;">🧬</span>
                <div style="font-size: 1.3rem; font-weight: 800; color: #1e293b; letter-spacing: -0.02em;">GenomIQ</div>
                <div style="font-size: 0.78rem; color: #64748b; font-weight: 500;">PhD Research Intelligence Hub</div>
            </div>
        """, unsafe_allow_html=True)

        pages = {
            "1. Overview": render_overview_page,
            "2. Discover Literature": render_discovery_page,
            "3. Recommended Reading": render_recommendations_page,
            "4. Reading Tracker": render_reading_tracker_page,
            "5. Literature Library": render_library_page,
            "6. Research Notes": render_notes_page,
            "7. Bioinformatics Tools": render_tools_page,
            "8. Authors and Citations": render_citations_page,
            "9. Research Projects": render_projects_page,
            "10. Tasks & Milestones": render_tasks_page,
            "11. Research Monitoring": render_monitoring_page,
            "12. Reports & Digest": render_reports_page,
            "13. Settings & Profile": render_settings_page,
        }

        selected_page = st.radio(
            "Navigation",
            list(pages.keys()),
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.caption("PhD Focus: Human Genomics, Pangenomics & Colorectal Cancer Genomics")
        st.caption("Weekly Target: **4 Papers / Week**")

    # 5. Render active view
    render_func = pages[selected_page]
    render_func()


if __name__ == "__main__":
    main()
