"""
Page 5: Literature Library for GenomIQ Research Hub.
Provides comprehensive catalog search, filtering, status updates, and citation export.
"""
import streamlit as st
import pandas as pd
from database.connection import get_db
from database.models import Publication
from core.export import export_publications_to_bibtex, export_publications_to_ris


def render_library_page():
    st.title("📚 Central Literature Library")
    st.caption("Browse, query, filter, and export all ingested scientific literature.")

    with get_db() as db:
        # Search & Filter Controls
        f_c1, f_c2, f_c3, f_c4 = st.columns([3, 1, 1, 1])
        with f_c1:
            search_text = st.text_input("🔍 Search Title, Author, DOI, or Keywords", placeholder="e.g. pangenome, 10.1038, hifiasm...")
        with f_c2:
            status_filter = st.selectbox("Reading Status", ["All Statuses", "Unread", "Recommended", "Accepted", "Reading", "Completed", "Revisit"])
        with f_c3:
            cat_filter = st.selectbox("Category", ["All Categories", "Core", "Computational", "Complementary", "Landmark", "Methodological", "Review"])
        with f_c4:
            oa_only = st.checkbox("Open Access Only", value=False)

        # Build query
        query = db.query(Publication)
        if search_text.strip():
            term = f"%{search_text.strip()}%"
            query = query.filter(
                (Publication.title.ilike(term)) |
                (Publication.authors.ilike(term)) |
                (Publication.doi.ilike(term)) |
                (Publication.abstract.ilike(term))
            )
        if status_filter != "All Statuses":
            query = query.filter(Publication.reading_status == status_filter)
        if cat_filter != "All Categories":
            query = query.filter(Publication.paper_category == cat_filter)
        if oa_only:
            query = query.filter(Publication.is_open_access == True)

        pubs = query.order_by(Publication.date_discovered.desc()).all()
        total_count = len(pubs)

        st.markdown(f"**Found {total_count} matching publication(s)**")

        # Export bar
        e_c1, e_c2, _ = st.columns([1, 1, 2])
        if pubs:
            with e_c1:
                bibtex_data = export_publications_to_bibtex(pubs)
                st.download_button("📥 Export BibTeX", bibtex_data, file_name="genomiq_library.bib", mime="text/plain", use_container_width=True)
            with e_c2:
                ris_data = export_publications_to_ris(pubs)
                st.download_button("📥 Export RIS (Zotero)", ris_data, file_name="genomiq_library.ris", mime="application/x-research-info-systems", use_container_width=True)

        st.markdown("---")

        if not pubs:
            st.info("No publications match your filter criteria. Try broadening your query or run discovery to ingest new papers.")
            return

        for p in pubs:
            badge_class = "badge-core" if p.paper_category == "Core" else "badge-comp" if p.paper_category == "Computational" else "badge-landmark"
            with st.container():
                st.markdown(f"""
                    <div class="pub-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span class="badge {badge_class}">{p.paper_category}</span>
                            <span style="font-size: 0.8rem; color: #475569;">
                                Status: <b>{p.reading_status}</b> | Discovered: {p.date_discovered.strftime('%Y-%m-%d') if p.date_discovered else 'N/A'}
                            </span>
                        </div>
                        <div class="pub-title"><a href="{p.publisher_url or '#'}" target="_blank" style="text-decoration:none; color:#0f172a;">{p.title}</a></div>
                        <div class="pub-authors">{p.authors}</div>
                        <div class="pub-meta">
                            <span>🏛 {p.journal or 'Journal'} ({p.year or 'N/A'})</span>
                            <span>⭐ Citations: {p.citation_count}</span>
                            <span>{'🟢 Open Access' if p.is_open_access else '🔒 Subscription'}</span>
                            <span>Source: {p.source_database}</span>
                            <span>DOI: {p.doi or 'N/A'}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                with st.expander(f"Details & Actions: {p.title[:50]}..."):
                    st.write(f"**Abstract:** {p.abstract}")
                    if p.pdf_url:
                        st.markdown(f"📄 [Direct PDF Download]({p.pdf_url})")

                    act_c1, act_c2, act_c3 = st.columns(3)
                    with act_c1:
                        target_stat = st.selectbox(
                            "Change Status",
                            ["Unread", "Recommended", "Accepted", "Reading", "Completed", "Revisit", "Not relevant"],
                            index=["Unread", "Recommended", "Accepted", "Reading", "Completed", "Revisit", "Not relevant"].index(p.reading_status) if p.reading_status in ["Unread", "Recommended", "Accepted", "Reading", "Completed", "Revisit", "Not relevant"] else 0,
                            key=f"status_sel_{p.id}"
                        )
                        if target_stat != p.reading_status:
                            p.reading_status = target_stat
                            db.commit()
                            st.success(f"Updated status to {target_stat}")
                            st.rerun()

                    with act_c2:
                        bm_label = "⭐ Remove Bookmark" if p.is_bookmarked else "☆ Bookmark Paper"
                        if st.button(bm_label, key=f"bm_{p.id}"):
                            p.is_bookmarked = not p.is_bookmarked
                            db.commit()
                            st.rerun()

                    with act_c3:
                        if st.button("🗑 Remove Paper", key=f"del_{p.id}"):
                            db.delete(p)
                            db.commit()
                            st.warning("Paper removed from library.")
                            st.rerun()
