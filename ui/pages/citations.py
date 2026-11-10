"""
Page 8: Authors and Citation Tracking for GenomIQ Research Hub.
Tracks influential researchers, publication citation networks, and exports citation data.
"""
import streamlit as st
from database.connection import get_db
from database.models import Author, Publication
from core.export import export_publications_to_bibtex, export_publications_to_ris


def render_citations_page():
    st.title("👥 Author & Citation Intelligence")
    st.caption("Track influential researchers, citation networks, and export reference callsets.")

    tab_network, tab_authors, tab_add_author = st.tabs(["📊 Citation Analytics", "⭐ Followed Researchers", "➕ Follow New Author"])

    with tab_network:
        st.subheader("Publication Impact & Citation Counts")
        with get_db() as db:
            pubs = db.query(Publication).order_by(Publication.citation_count.desc()).all()

            if not pubs:
                st.info("No publications in library. Discover papers first.")
                return

            c1, c2 = st.columns([1, 1])
            with c1:
                st.download_button(
                    "📥 Export All References (BibTeX)",
                    export_publications_to_bibtex(pubs),
                    file_name="genomiq_all_citations.bib",
                    mime="text/plain",
                    use_container_width=True
                )
            with c2:
                st.download_button(
                    "📥 Export All References (RIS)",
                    export_publications_to_ris(pubs),
                    file_name="genomiq_all_citations.ris",
                    mime="text/plain",
                    use_container_width=True
                )

            st.markdown("---")
            for p in pubs:
                with st.expander(f"⭐ [{p.citation_count} Citations] {p.title} ({p.year or 'N/A'})"):
                    st.write(f"**Authors:** {p.authors}")
                    st.write(f"**Journal:** {p.journal}")
                    st.write(f"**DOI:** [{p.doi}](https://doi.org/{p.doi})" if p.doi else "**DOI:** N/A")
                    st.write(f"**Primary Source:** {p.source_database}")
                    if p.doi:
                        st.markdown(f"🔗 [Explore Direct Citations on OpenAlex](https://openalex.org/works?filter=doi:{p.doi})")
                        st.markdown(f"🔗 [Explore on Europe PMC](https://europepmc.org/search?query={p.doi})")

    with tab_authors:
        st.subheader("Followed Researchers & Principal Investigators")
        with get_db() as db:
            authors = db.query(Author).all()
            if not authors:
                # Add sample seed authors in human genomics if empty
                sample_authors = [
                    Author(name="Heng Li", affiliation="Dana-Farber Cancer Institute / Harvard Medical School", orcid="0000-0003-4874-2874", is_followed=True, h_index=110, notes="Lead developer of minimap2, bwa, hifiasm, samtools."),
                    Author(name="Benedict Paten", affiliation="UC Santa Cruz Genomics Institute", orcid="0000-0002-4648-9533", is_followed=True, h_index=65, notes="Co-leader of Human Pangenome Reference Consortium, Minigraph-Cactus, VG."),
                    Author(name="Gad Getz", affiliation="Broad Institute of MIT and Harvard", orcid="0000-0002-5369-1224", is_followed=True, h_index=130, notes="Pioneer in cancer genomics, Mutect, MutSigCV, somatic mutation discovery."),
                ]
                for sa in sample_authors:
                    db.add(sa)
                db.commit()
                authors = db.query(Author).all()

            for auth in authors:
                with st.container():
                    st.markdown(f"""
                        <div class="pub-card" style="border-left-color: #8b5cf6;">
                            <div style="font-size: 1.1rem; font-weight: bold; color: #1e293b;">{auth.name}</div>
                            <div style="font-size: 0.85rem; color: #64748b;">{auth.affiliation}</div>
                            <div style="font-size: 0.82rem; margin-top: 6px;">
                                <span><b>ORCID:</b> {auth.orcid or 'N/A'}</span> | 
                                <span><b>Estimated h-index:</b> {auth.h_index}</span>
                            </div>
                            <div style="margin-top: 6px; font-size: 0.85rem; color: #334155;"><b>Research Scope:</b> {auth.notes}</div>
                        </div>
                    """, unsafe_allow_html=True)

    with tab_add_author:
        st.subheader("Follow a New Researcher")
        with st.form("add_author_form"):
            a_name = st.text_input("Full Name", placeholder="e.g. Karen Miga")
            a_affil = st.text_input("Affiliation", placeholder="e.g. UC Santa Cruz Genomics Institute")
            a_orcid = st.text_input("ORCID (Optional)", placeholder="e.g. 0000-0002-xxxx-xxxx")
            a_notes = st.text_area("Research Areas / Reason to Follow", placeholder="e.g. Co-chair of Telomere-to-Telomere Consortium and centromere genomics.")
            submitted = st.form_submit_button("Follow Researcher", type="primary")
            if submitted:
                if a_name.strip():
                    with get_db() as db:
                        new_a = Author(name=a_name.strip(), affiliation=a_affil.strip(), orcid=a_orcid.strip(), notes=a_notes.strip(), is_followed=True)
                        db.add(new_a)
                        db.commit()
                    st.success(f"Now following {a_name}!")
                    st.rerun()
                else:
                    st.error("Please provide the researcher's name.")
