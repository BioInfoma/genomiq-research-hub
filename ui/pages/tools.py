"""
Page 7: Bioinformatics Software and Methods Database for GenomIQ Research Hub.
Catalogs core algorithms, assemblers, variant callers, and monitors learning progress.
"""
import streamlit as st
from database.connection import get_db
from database.models import BioinformaticsTool


def render_tools_page():
    st.title("🛠️ Bioinformatics Software & Methods Database")
    st.caption("Track, evaluate, and master computational genomics tools, assemblers, and variant callers.")

    tab_catalog, tab_add = st.tabs(["🗂️ Software Catalog", "➕ Add New Tool / Method"])

    with tab_catalog:
        with get_db() as db:
            categories = ["All Categories"] + sorted(list({t.category for t in db.query(BioinformaticsTool.category).distinct() if t.category}))
            statuses = ["All Statuses", "To Learn", "Learning", "Proficient", "Expert"]

            f_c1, f_c2 = st.columns(2)
            with f_c1:
                sel_cat = st.selectbox("Filter by Category", categories)
            with f_c2:
                sel_status = st.selectbox("Filter by Learning Status", statuses)

            query = db.query(BioinformaticsTool)
            if sel_cat != "All Categories":
                query = query.filter(BioinformaticsTool.category == sel_cat)
            if sel_status != "All Statuses":
                query = query.filter(BioinformaticsTool.learning_status == sel_status)

            tools = query.order_by(BioinformaticsTool.name.asc()).all()

            st.markdown(f"**Tracking {len(tools)} Bioinformatics Tool(s)**")

            for t in tools:
                status_color = "#15803d" if t.learning_status == "Expert" else "#2563eb" if t.learning_status == "Proficient" else "#d97706" if t.learning_status == "Learning" else "#64748b"

                with st.expander(f"🔧 {t.name} — {t.category} ({t.learning_status})"):
                    st.markdown(f"""
                        <div style="display: flex; gap: 10px; margin-bottom: 8px;">
                            <span style="background:{status_color}22; color:{status_color}; padding:2px 10px; border-radius:12px; font-weight:bold; font-size:0.8rem;">
                                {t.learning_status}
                            </span>
                            <span style="background:#f1f5f9; color:#475569; padding:2px 10px; border-radius:12px; font-size:0.8rem;">
                                Category: <b>{t.category}</b>
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"**Description:** {t.description}")
                    st.markdown(f"**PhD Application:** {t.application}")

                    c_m1, c_m2 = st.columns(2)
                    with c_m1:
                        st.markdown(f"**Supported Formats:** `{t.input_formats}`")
                        st.markdown(f"**Sequencing Tech:** `{t.sequencing_tech}`")
                        st.markdown(f"**Underlying Algorithms:** {t.algorithms}")
                    with c_m2:
                        st.markdown(f"**Key Advantages:** {t.advantages}")
                        st.markdown(f"**Limitations:** {t.limitations}")
                        if t.github_url:
                            st.markdown(f"🐙 [GitHub Repository]({t.github_url})")
                        if t.doc_url:
                            st.markdown(f"📖 [Official Documentation]({t.doc_url})")

                    if t.personal_experience:
                        st.info(f"💡 **Personal Notes & Hands-on Experience:**\n\n{t.personal_experience}")

                    # Update status
                    stat_col, exp_col, save_col = st.columns([1, 2, 1])
                    with stat_col:
                        new_ls = st.selectbox(
                            "Update Status",
                            ["To Learn", "Learning", "Proficient", "Expert"],
                            index=["To Learn", "Learning", "Proficient", "Expert"].index(t.learning_status),
                            key=f"tool_status_{t.id}"
                        )
                    with exp_col:
                        new_exp = st.text_input("Append Personal Experience", key=f"tool_exp_{t.id}", placeholder="Notes from pipeline benchmark run...")
                    with save_col:
                        if st.button("Update Tool", key=f"tool_btn_{t.id}"):
                            t.learning_status = new_ls
                            if new_exp.strip():
                                t.personal_experience = (t.personal_experience or "") + f"\n- {new_exp.strip()}"
                            db.commit()
                            st.success("Tool updated!")
                            st.rerun()

    with tab_add:
        st.subheader("Register a New Bioinformatics Tool or Computational Method")
        with st.form("add_tool_form"):
            t_name = st.text_input("Tool Name", placeholder="e.g. Sentieon DNAscope, Snakemake, Clair3")
            t_cat = st.selectbox(
                "Category",
                ["Genome assembly", "Read alignment", "Variant calling", "Structural variant detection",
                 "Copy number analysis", "Variant annotation", "Graph genome analysis", "RNA-seq analysis",
                 "Single-cell analysis", "Phylogenetics", "Phylodynamics", "Statistical genetics", "Functional genomics"]
            )
            t_desc = st.text_area("Description", placeholder="Summary of tool capabilities and architecture.")
            t_app = st.text_input("PhD Research Application", placeholder="e.g. Somatic variant calling in low-purity colorectal biopsies.")
            t_seq = st.text_input("Sequencing Technologies", placeholder="e.g. PacBio HiFi, Illumina NovaSeq, ONT R10.4")
            t_gh = st.text_input("GitHub URL", placeholder="https://github.com/...")
            t_doc = st.text_input("Documentation URL", placeholder="https://...")
            t_adv = st.text_input("Key Advantages", placeholder="e.g. 5x faster runtime, lower false-positive indel rate.")
            t_lim = st.text_input("Known Limitations", placeholder="e.g. High memory requirement, closed source.")
            t_stat = st.selectbox("Learning Status", ["To Learn", "Learning", "Proficient", "Expert"])

            submitted = st.form_submit_button("Add Tool to Database", type="primary")
            if submitted:
                if not t_name.strip():
                    st.error("Tool Name is required.")
                else:
                    with get_db() as db:
                        new_t = BioinformaticsTool(
                            name=t_name.strip(),
                            category=t_cat,
                            description=t_desc.strip(),
                            application=t_app.strip(),
                            sequencing_tech=t_seq.strip(),
                            github_url=t_gh.strip(),
                            doc_url=t_doc.strip(),
                            advantages=t_adv.strip(),
                            limitations=t_lim.strip(),
                            learning_status=t_stat
                        )
                        db.add(new_t)
                        db.commit()
                    st.success(f"Tool '{t_name}' added to database!")
                    st.rerun()
