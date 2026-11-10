"""
Reading Tracker Service and Academic Reading Analytics for GenomIQ Research Hub.
Manages status workflows, reading reflections, structured notes, and KPI statistics.
"""
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from database.connection import get_db
from database.models import Publication, ReadingRecord, Recommendation


class ReadingTrackerService:
    def update_reading_progress(
        self,
        publication_id: int,
        status: str,
        duration_minutes: int = 0,
        personal_notes: str = "",
        main_findings: str = "",
        important_methods: str = "",
        limitations: str = "",
        questions_raised: str = "",
        phd_relevance: str = "",
        potential_applications: str = "",
        rating: int = 0
    ) -> bool:
        """Updates reading record and synchronizes publication reading status."""
        with get_db() as db:
            pub = db.query(Publication).filter(Publication.id == publication_id).first()
            if not pub:
                return False

            pub.reading_status = status

            record = db.query(ReadingRecord).filter(ReadingRecord.publication_id == publication_id).first()
            if not record:
                record = ReadingRecord(publication_id=publication_id)
                db.add(record)

            record.status = status
            if duration_minutes > 0:
                record.reading_duration_minutes += duration_minutes

            if personal_notes:
                record.personal_notes = personal_notes
            if main_findings:
                record.main_findings = main_findings
            if important_methods:
                record.important_methods = important_methods
            if limitations:
                record.limitations = limitations
            if questions_raised:
                record.questions_raised = questions_raised
            if phd_relevance:
                record.phd_relevance = phd_relevance
            if potential_applications:
                record.potential_applications = potential_applications
            if rating > 0:
                record.rating = rating

            if status == "Reading" and not record.date_started:
                record.date_started = date.today()
            elif status == "Completed":
                if not record.date_started:
                    record.date_started = date.today()
                record.date_completed = date.today()

            # Synchronize recommendation status if linked
            rec = db.query(Recommendation).filter(Recommendation.publication_id == publication_id).first()
            if rec:
                if status == "Completed":
                    rec.status = "Completed"
                elif status in ["Reading", "Accepted"]:
                    rec.status = "Accepted"
                elif status == "Not relevant":
                    rec.status = "Rejected"

            db.commit()
            return True

    def get_weekly_kpis(self, week_identifier: Optional[str] = None) -> Dict[str, Any]:
        """Calculates reading KPIs against the 4-paper supervisor target."""
        if not week_identifier:
            today = date.today()
            week_identifier = f"{today.year}-W{today.isocalendar()[1]:02d}"

        with get_db() as db:
            recs = db.query(Recommendation).filter(Recommendation.week_identifier == week_identifier).all()
            rec_count = len(recs)
            rec_pub_ids = [r.publication_id for r in recs]

            records = db.query(ReadingRecord).filter(ReadingRecord.publication_id.in_(rec_pub_ids)).all() if rec_pub_ids else []

            completed = sum(1 for r in records if r.status == "Completed")
            reading = sum(1 for r in records if r.status == "Reading")
            accepted = sum(1 for r in records if r.status in ["Accepted", "Reading", "Completed"])

            target = 4
            completion_pct = min(round((completed / target) * 100, 1), 100.0)

            # All time statistics
            total_completed = db.query(ReadingRecord).filter(ReadingRecord.status == "Completed").count()
            total_in_library = db.query(Publication).count()

            # Minutes spent
            total_minutes = sum(r.reading_duration_minutes or 0 for r in db.query(ReadingRecord).all())

            return {
                "week_identifier": week_identifier,
                "weekly_target": target,
                "recommended": rec_count,
                "accepted": accepted,
                "in_progress": reading,
                "completed_this_week": completed,
                "completion_percentage": completion_pct,
                "total_completed_all_time": total_completed,
                "total_in_library": total_in_library,
                "total_reading_hours": round(total_minutes / 60, 1)
            }

    def get_topic_distribution(self) -> pd.DataFrame:
        """Returns topic coverage across all publications and completed readings."""
        with get_db() as db:
            pubs = db.query(Publication).all()
            if not pubs:
                return pd.DataFrame(columns=["Topic", "Total", "Completed"])

            topic_counts = {}
            for p in pubs:
                t_str = p.research_topics or "Unclassified"
                for topic in [t.strip() for t in t_str.split(",") if t.strip()]:
                    if topic not in topic_counts:
                        topic_counts[topic] = {"Total": 0, "Completed": 0}
                    topic_counts[topic]["Total"] += 1
                    if p.reading_status == "Completed":
                        topic_counts[topic]["Completed"] += 1

            rows = [{"Topic": k, "Total": v["Total"], "Completed": v["Completed"]} for k, v in topic_counts.items()]
            df = pd.DataFrame(rows)
            if not df.empty:
                df = df.sort_values(by="Total", ascending=False)
            return df
