"""
Automated Weekly Research Digest Generator for GenomIQ Research Hub.
Compiles:
- The 4 recommended papers with rationales
- Newly published papers
- Important preprints
- Methods & software updates
- Reading tasks and milestone progress
- Markdown and HTML export
"""
from datetime import datetime, date
from typing import Dict, Any, Optional
from database.connection import get_db
from database.models import Publication, Recommendation, ReadingRecord, Task, BioinformaticsTool, WeeklyDigest


class DigestGenerator:
    def generate_digest(self, week_identifier: Optional[str] = None) -> WeeklyDigest:
        """Generates or updates the weekly digest for the specified week."""
        if not week_identifier:
            today = date.today()
            week_identifier = f"{today.year}-W{today.isocalendar()[1]:02d}"

        with get_db() as db:
            recs = db.query(Recommendation).filter(Recommendation.week_identifier == week_identifier).all()
            new_pubs = db.query(Publication).order_by(Publication.date_discovered.desc()).limit(5).all()
            preprints = db.query(Publication).filter(Publication.publication_type == "Preprint").limit(3).all()
            pending_tasks = db.query(Task).filter(Task.status.in_(["To do", "In progress"])).all()
            tools = db.query(BioinformaticsTool).filter(BioinformaticsTool.learning_status.in_(["To Learn", "Learning"])).limit(4).all()

            # Reading progress
            completed_in_rec = sum(1 for r in recs if r.status == "Completed")
            rec_count = len(recs)

            md = []
            md.append(f"# GenomIQ Weekly Research Intelligence Digest")
            md.append(f"**Week:** {week_identifier} | **Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
            md.append(f"**Supervisor Target Progress:** {completed_in_rec} of 4 papers completed ({round((completed_in_rec/4)*100)}%)\n")
            md.append("---")

            # Section 1: 4 Recommended Papers
            md.append("## 1. Supervisor-Targeted Reading Allocation (4 Papers)")
            if recs:
                for i, r in enumerate(recs, 1):
                    pub = r.publication
                    md.append(f"### Paper {i} [{r.category.upper()}]: {pub.title}")
                    md.append(f"- **Authors:** {pub.authors}")
                    md.append(f"- **Journal / Year:** {pub.journal} ({pub.year}) | **Citations:** {pub.citation_count}")
                    md.append(f"- **DOI:** [{pub.doi}](https://doi.org/{pub.doi})" if pub.doi else "- **DOI:** N/A")
                    md.append(f"- **Why Selected:** {r.selection_reason}")
                    md.append(f"- **PhD Relevance:** {r.phd_relevance}")
                    md.append(f"- **Current Reading Status:** `{r.status}`\n")
            else:
                md.append("No active recommendations generated for this week yet. Click 'Generate 4 Weekly Recommendations'.\n")

            # Section 2: Newly Published Papers
            md.append("## 2. Newly Discovered Papers in Primary Focus")
            for p in new_pubs:
                md.append(f"- **{p.title}** ({p.journal}, {p.year}) - *{p.research_topics}* [DOI: {p.doi or 'N/A'}]")
            md.append("")

            # Section 3: Important Preprints
            md.append("## 3. Notable Early-Access Preprints (bioRxiv / medRxiv)")
            if preprints:
                for pp in preprints:
                    md.append(f"- **{pp.title}** - {pp.journal} ([Preprint Link]({pp.publisher_url}))")
            else:
                md.append("- No preprints ingested yet. Run discovery to fetch latest bioRxiv preprints.")
            md.append("")

            # Section 4: Software & Methods In Progress
            md.append("## 4. Bioinformatics Methods & Software Under Review")
            for t in tools:
                md.append(f"- **{t.name}** (`{t.category}`): {t.application[:140]}... (Status: `{t.learning_status}`)")
            md.append("")

            # Section 5: Outstanding PhD Tasks & Deadlines
            md.append("## 5. Upcoming PhD Tasks & Deadlines")
            if pending_tasks:
                for t in pending_tasks:
                    due = t.due_date.strftime('%Y-%m-%d') if t.due_date else "No deadline"
                    md.append(f"- **[{t.priority.upper()}]** {t.title} (Due: {due} | Status: `{t.status}`)")
            else:
                md.append("- All scheduled tasks currently up to date.")
            md.append("")

            digest_content = "\n".join(md)

            # Persist or update digest
            digest_record = db.query(WeeklyDigest).filter(WeeklyDigest.week_identifier == week_identifier).first()
            if not digest_record:
                digest_record = WeeklyDigest(
                    week_identifier=week_identifier,
                    title=f"GenomIQ Digest - {week_identifier}",
                    content_markdown=digest_content
                )
                db.add(digest_record)
            else:
                digest_record.content_markdown = digest_content
                digest_record.generated_at = datetime.utcnow()

            db.commit()
            return digest_record
