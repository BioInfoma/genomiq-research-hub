"""
Page 6: Research Documentation Management for GenomIQ Research Hub.
Captures Ideas, Methods, Notes, and Activities with Markdown support and publication linking.
"""
import json
from datetime import datetime
import streamlit as st
from database.connection import get_db
from database.models import ResearchNote, Publication


def render_notes_page():
    st.title("📝 Research Documentation Management")
    st.caption("Organize PhD research ideas, experimental methods, supervisor meeting notes, and laboratory activities.")

    tab_browse, tab_create = st.tabs(["📖 Browse Documentation", "✍️ Create New Entry"])

    with tab_create:
        st.subheader("Add New Research Documentation Entry")
        with get_db() as db:
            pubs = db.query(Publication).order_by(Publication.title.asc()).all()
            pub_options = {p.id: f"{p.title[:60]}... ({p.year or 'N/A'})" for p in pubs}
            pub_options[0] = "-- None (General Entry) --"

            with st.form("new_doc_form"):
                note_title = st.text_input("Entry Title", placeholder="e.g. Hypothesis: African pangenome graph reveals non-reference somatic driver SNVs")
                doc_type = st.selectbox(
                    "Documentation Category",
                    ["idea", "method", "note", "activity"],
                    format_func=lambda x: {
                        "idea": "💡 Research Idea / Hypothesis",
                        "method": "⚙️ Bioinformatics Method / Workflow",
                        "note": "📋 Research / Supervisor Meeting Note",
                        "activity": "🔬 Research Activity / Experiment"
                    }[x]
                )
                linked_pub_id = st.selectbox(
                    "Link to Scientific Publication (Optional)",
                    options=list(pub_options.keys()),
                    format_func=lambda x: pub_options[x]
                )
                tag_string = st.text_input("Tags (comma-separated)", placeholder="e.g. colorectal, mutect2, supervisor-feedback")
                markdown_content = st.text_area(
                    "Documentation Content (Markdown Supported)",
                    height=200,
                    placeholder="Enter detailed notes, equations, code snippets, or experimental observations..."
                )

                submitted = st.form_submit_button("💾 Save Documentation Entry", type="primary", use_container_width=True)
                if submitted:
                    if not note_title.strip() or not markdown_content.strip():
                        st.error("Please provide both a Title and Content.")
                    else:
                        tags = [t.strip() for t in tag_string.split(",") if t.strip()]
                        new_note = ResearchNote(
                            title=note_title.strip(),
                            note_type=doc_type,
                            content_markdown=markdown_content.strip(),
                            tags_json=json.dumps(tags),
                            linked_publication_id=linked_pub_id if linked_pub_id != 0 else None
                        )
                        db.add(new_note)
                        db.commit()
                        st.success(f"Documentation entry '{note_title}' saved successfully!")
                        st.rerun()

    with tab_browse:
        st.subheader("PhD Documentation Repository")
        filter_type = st.selectbox("Filter by Category", ["All Categories", "idea", "method", "note", "activity"])

        with get_db() as db:
            query = db.query(ResearchNote)
            if filter_type != "All Categories":
                query = query.filter(ResearchNote.note_type == filter_type)

            notes = query.order_by(ResearchNote.created_at.desc()).all()

            if not notes:
                st.info("No documentation entries found. Create an entry using the 'Create New Entry' tab.")
                return

            for note in notes:
                icon = "💡" if note.note_type == "idea" else "⚙️" if note.note_type == "method" else "📋" if note.note_type == "note" else "🔬"
                with st.expander(f"{icon} [{note.note_type.upper()}] {note.title} ({note.created_at.strftime('%Y-%m-%d')})"):
                    tags = json.loads(note.tags_json) if note.tags_json else []
                    if tags:
                        st.markdown("**Tags:** " + " ".join([f"`#{t}`" for t in tags]))

                    if note.publication:
                        st.markdown(f"**Linked Publication:** [{note.publication.title}](https://doi.org/{note.publication.doi})")

                    st.markdown("---")
                    st.markdown(note.content_markdown)

                    col_del, col_down = st.columns([1, 4])
                    with col_del:
                        if st.button("🗑 Delete", key=f"del_note_{note.id}"):
                            db.delete(note)
                            db.commit()
                            st.warning("Entry deleted.")
                            st.rerun()
                    with col_down:
                        md_export = f"# {note.title}\n\n**Category:** {note.note_type}\n**Date:** {note.created_at}\n\n{note.content_markdown}"
                        st.download_button("📥 Download Markdown", md_export, file_name=f"{note.title[:20]}.md", mime="text/markdown", key=f"dl_note_{note.id}")
