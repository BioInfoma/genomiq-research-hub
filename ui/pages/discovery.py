"""
Page 2: Literature Discovery Engine for GenomIQ Research Hub.
Searches OpenAlex, PubMed, Europe PMC, Crossref, and bioRxiv.
"""
import streamlit as st
from database.connection import get_db
from database.models import SearchProfile, Publication
from core.discovery import LiteratureDiscoveryEngine


def render_discovery_page():
    st.title("🔍 Automated Literature Discovery")
    st.caption("Live query across OpenAlex, PubMed, Europe PMC, Crossref, and bioRxiv with deduplication.")

    tab_profile, tab_custom, tab_profiles_mgmt = st.tabs(["🚀 Run Search Profile", "🔎 Custom Academic Query", "⚙️ Manage Profiles"])

    engine = LiteratureDiscoveryEngine()

    # TAB 1: Run Search Profile
    with tab_profile:
        st.subheader("Select Configured PhD Search Profile")
        with get_db() as db:
            profiles = db.query(SearchProfile).filter(SearchProfile.is_active == True).all()
            profile_names = [p.name for p in profiles]

        if profile_names:
            selected_prof_name = st.selectbox("Choose Research Profile", profile_names)
            with get_db() as db:
                curr_p = db.query(SearchProfile).filter(SearchProfile.name == selected_prof_name).first()

            if curr_p:
                st.info(f"**Query String:** `{curr_p.query_string}`\n\n*{curr_p.description}*")
                c_src1, c_src2 = st.columns([3, 1])
                with c_src1:
                    sources = st.multiselect(
                        "Target Free Academic APIs",
                        ["OpenAlex", "PubMed", "Europe PMC", "bioRxiv", "Crossref"],
                        default=["OpenAlex", "PubMed", "Europe PMC", "bioRxiv"]
                    )
                with c_src2:
                    limit_val = st.number_input("Limit per Source", min_value=2, max_value=25, value=6, step=2)

                if st.button("🚀 Execute Discovery Run", type="primary", use_container_width=True):
                    with st.spinner(f"Querying {len(sources)} academic repositories for '{curr_p.name}'..."):
                        res = engine.execute_unified_search(
                            query=curr_p.query_string,
                            sources=sources,
                            limit_per_source=int(limit_val),
                            persist=True,
                            research_topic_tag=curr_p.name.replace("PROFILE ", "")
                        )
                        st.success(f"Discovery complete! Fetched {res['total_fetched']} records across sources. Added **{res['new_saved']} new unique papers** to library ({res['duplicates_skipped']} duplicates skipped).")
                        st.json(res["sources"])
        else:
            st.warning("No search profiles found.")

    # TAB 2: Custom Academic Query
    with tab_custom:
        st.subheader("Live Multi-Database Keyword / Boolean / DOI Search")
        cq_col1, cq_col2 = st.columns([3, 1])
        with cq_col1:
            custom_query = st.text_input("Enter keywords, gene names, DOIs, or author names", value="colorectal cancer somatic mutations KRAS")
        with cq_col2:
            custom_limit = st.selectbox("Max results per source", [5, 10, 15, 20], index=1)

        custom_sources = st.multiselect(
            "Target Academic Databases",
            ["OpenAlex", "PubMed", "Europe PMC", "bioRxiv", "Crossref"],
            default=["OpenAlex", "PubMed", "Europe PMC"]
        )

        auto_save = st.checkbox("Automatically persist new unique papers to central literature library", value=True)

        if st.button("🔎 Search Academic Repositories", use_container_width=True):
            if not custom_query.strip():
                st.error("Please enter a search query.")
            else:
                with st.spinner("Searching free academic APIs..."):
                    res = engine.execute_unified_search(
                        query=custom_query.strip(),
                        sources=custom_sources,
                        limit_per_source=int(custom_limit),
                        persist=auto_save,
                        research_topic_tag=custom_query.strip()
                    )
                    st.success(f"Discovered {res['total_fetched']} records. New unique papers persisted: {res['new_saved']} ({res['duplicates_skipped']} duplicates filtered out).")

                    # Preview recently saved records
                    with get_db() as db:
                        latest_pubs = db.query(Publication).order_by(Publication.id.desc()).limit(res['new_saved'] or 5).all()
                        for p in latest_pubs:
                            with st.expander(f"📄 {p.title} ({p.journal or 'N/A'}, {p.year})"):
                                st.write(f"**Authors:** {p.authors}")
                                st.write(f"**DOI:** {p.doi or 'N/A'} | **PMID:** {p.pmid or 'N/A'} | **Source:** {p.source_database}")
                                st.write(f"**Abstract:** {p.abstract}")
                                if p.publisher_url:
                                    st.markdown(f"[View Publisher / Article Page]({p.publisher_url})")

    # TAB 3: Manage Search Profiles
    with tab_profiles_mgmt:
        st.subheader("Create or Edit Search Profiles")
        with st.form("new_profile_form"):
            prof_name = st.text_input("Profile Name", placeholder="e.g. PROFILE 11: Single-Cell Spatial Transcriptomics")
            prof_desc = st.text_area("Description", placeholder="Describe the biological or computational scope.")
            prof_query = st.text_input("Query String", placeholder="e.g. spatial transcriptomics single-cell colorectal cancer")
            submitted = st.form_submit_button("Add Search Profile")
            if submitted:
                if prof_name and prof_query:
                    with get_db() as db:
                        new_p = SearchProfile(name=prof_name.strip(), description=prof_desc.strip(), query_string=prof_query.strip(), is_active=True)
                        db.add(new_p)
                        db.commit()
                    st.success(f"Profile '{prof_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Please provide both Profile Name and Query String.")
