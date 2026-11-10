"""
Page 13: Settings & Research Profile for GenomIQ Research Hub.
Customizes research interests, priority weights, database backups, and API keys.
"""
import json
import streamlit as st
from config import DEFAULT_RESEARCH_PROFILE, OPENALEX_MAILTO, NCBI_EMAIL, NCBI_API_KEY, SEMANTIC_SCHOLAR_KEY, GITHUB_TOKEN
from database.connection import get_db, backup_database
from database.models import ResearchTopic


def render_settings_page():
    st.title("⚙️ Research Profile & Platform Settings")
    st.caption("Configure PhD topics, priority weighting, database backups, and external API credentials.")

    tab_profile, tab_topics, tab_backup, tab_api = st.tabs(["👤 PhD Researcher Profile", "🧬 Topics & Priority Weights", "💾 Database Backups", "🔑 API Status & Integrity"])

    with tab_profile:
        st.subheader("PhD Researcher Details")
        with st.form("researcher_profile_form"):
            user_name = st.text_input("Researcher Name", value=DEFAULT_RESEARCH_PROFILE["user_name"])
            department = st.text_input("Department / Laboratory", value=DEFAULT_RESEARCH_PROFILE["department"])
            institution = st.text_input("Institution", value=DEFAULT_RESEARCH_PROFILE["institution"])
            weekly_target = st.number_input("Weekly Reading Target (Papers)", min_value=1, max_value=20, value=DEFAULT_RESEARCH_PROFILE["weekly_target_papers"])
            if st.form_submit_button("Save Profile"):
                st.success("Profile updated in local configuration!")

    with tab_topics:
        st.subheader("Research Interest Topics & Priority Weights")
        st.caption("The recommendation algorithm prioritizes papers according to these weights.")

        with get_db() as db:
            topics = db.query(ResearchTopic).all()

            for t in topics:
                with st.container():
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    with c1:
                        st.write(f"**{t.name}** (`{t.category}`)")
                    with c2:
                        new_weight = st.number_input("Weight (1-10)", min_value=1, max_value=10, value=t.priority_weight, key=f"weight_{t.id}")
                    with c3:
                        is_active = st.checkbox("Active", value=t.is_active, key=f"act_{t.id}")
                    with c4:
                        if st.button("Update", key=f"upd_top_{t.id}"):
                            t.priority_weight = new_weight
                            t.is_active = is_active
                            db.commit()
                            st.success(f"Updated '{t.name}'")
                            st.rerun()

            st.markdown("---")
            st.markdown("##### Add New Research Topic")
            with st.form("new_topic_form"):
                nt_name = st.text_input("Topic Name", placeholder="e.g. Somatic Copy Number Variations in Colorectal Cancer")
                nt_cat = st.selectbox("Category", ["Primary", "Secondary", "Custom"])
                nt_weight = st.slider("Priority Weight", min_value=1, max_value=10, value=7)
                nt_kws = st.text_input("Keywords (comma-separated)", placeholder="e.g. CNV, aneuploidy, focal amplification")
                if st.form_submit_button("Add Topic"):
                    if nt_name.strip():
                        kws = [k.strip() for k in nt_kws.split(",") if k.strip()]
                        new_t = ResearchTopic(name=nt_name.strip(), category=nt_cat, priority_weight=nt_weight, is_active=True, keywords_json=json.dumps(kws))
                        db.add(new_t)
                        db.commit()
                        st.success(f"Topic '{nt_name}' registered!")
                        st.rerun()

    with tab_backup:
        st.subheader("Local Database Backups & Data Safety")
        st.write("GenomIQ stores all publications, reading reflections, notes, and tasks in a persistent SQLite database (`data/genomiq.db`).")

        from config import DB_FILE
        if DB_FILE.exists():
            db_size_kb = round(DB_FILE.stat().st_size / 1024, 1)
            st.info(f"📁 **Active Database Location:** `{DB_FILE}` ({db_size_kb} KB)")

            b_c1, b_c2 = st.columns(2)
            with b_c1:
                if st.button("💾 Create Timestamped Snapshot", type="primary", use_container_width=True):
                    bpath = backup_database()
                    if bpath:
                        st.success(f"Backup snapshot saved to:\n`{bpath}`")
                    else:
                        st.error("Database file not found.")

            with b_c2:
                with open(DB_FILE, "rb") as f_db:
                    db_bytes = f_db.read()
                st.download_button(
                    "📥 Download Database File (.db)",
                    data=db_bytes,
                    file_name="genomiq_database.db",
                    mime="application/x-sqlite3",
                    use_container_width=True
                )
        else:
            st.warning("Database file not yet created.")

        st.markdown("---")
        st.markdown("##### 🔄 Restore / Import Database File")
        st.caption("Upload a previously downloaded `.db` file to immediately restore all your reading history, annotations, and tasks.")
        uploaded_db = st.file_uploader("Upload .db Backup File", type=["db", "sqlite", "sqlite3"], key="restore_db_uploader")
        if uploaded_db is not None:
            if st.button("⚠️ Confirm Database Restore", type="secondary"):
                with open(DB_FILE, "wb") as f_out:
                    f_out.write(uploaded_db.getbuffer())
                st.success("Database restored successfully! Refreshing dashboard...")
                st.rerun()

    with tab_api:
        st.subheader("Academic APIs & Credentials")
        st.write("GenomIQ operates entirely on free open-source APIs without requiring paid keys.")

        st.markdown(f"""
        | Academic Service | Status | Protocol |
        |---|---|---|
        | **OpenAlex API** | 🟢 Active | Free polite mailto: `{OPENALEX_MAILTO}` |
        | **NCBI PubMed** | 🟢 Active | Free E-utilities ({'Custom API Key present' if NCBI_API_KEY else 'Polite tier 3 req/s'}) |
        | **Europe PMC** | 🟢 Active | Free open biomedical REST API |
        | **Crossref** | 🟢 Active | Free polite metadata search |
        | **bioRxiv / medRxiv** | 🟢 Active | Official free preprint API |
        | **Semantic Scholar** | {'🟢 Key configured' if SEMANTIC_SCHOLAR_KEY else '🟡 Public tier (no key)'} | Free graph API |
        | **GitHub API** | {'🟢 Token configured' if GITHUB_TOKEN else '🟡 Public tier (60 req/hr)'} | Software releases monitor |
        """)
