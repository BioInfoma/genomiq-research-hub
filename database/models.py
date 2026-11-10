"""
Database models for GenomIQ Research Hub using SQLAlchemy 2.0.
"""
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, Date, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    authors = Column(Text, default="")  # Comma-separated or full string
    abstract = Column(Text, default="")
    doi = Column(String(120), unique=True, nullable=True, index=True)
    pmid = Column(String(30), unique=True, nullable=True, index=True)
    year = Column(Integer, nullable=True, index=True)
    publication_date = Column(String(30), default="")
    journal = Column(String(255), default="", index=True)
    publication_type = Column(String(60), default="Journal Article")  # Journal Article, Preprint, Review, Benchmark
    keywords = Column(Text, default="")  # JSON or comma-separated
    research_topics = Column(Text, default="")  # Comma-separated or JSON
    citation_count = Column(Integer, default=0)
    is_open_access = Column(Boolean, default=False)
    pdf_url = Column(String(500), default="")
    publisher_url = Column(String(500), default="")
    source_database = Column(String(60), default="Manual")  # OpenAlex, PubMed, Europe PMC, Crossref, bioRxiv, Semantic Scholar
    date_discovered = Column(DateTime, default=datetime.utcnow, index=True)
    relevance_score = Column(Float, default=0.0)
    reading_status = Column(String(40), default="Unread", index=True)  # Unread, Recommended, Accepted, Reading, Completed, Revisit, Not relevant
    is_bookmarked = Column(Boolean, default=False)
    paper_category = Column(String(50), default="Core")  # Core, Computational, Complementary, Landmark, Foundational, Review

    # Relationships
    reading_records = relationship("ReadingRecord", back_populates="publication", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="publication", cascade="all, delete-orphan")
    notes = relationship("ResearchNote", back_populates="publication")
    tasks = relationship("Task", back_populates="publication")

    def __repr__(self):
        return f"<Publication(id={self.id}, doi='{self.doi}', title='{self.title[:30]}...')>"


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    affiliation = Column(String(350), default="")
    orcid = Column(String(50), nullable=True, index=True)
    openalex_id = Column(String(100), nullable=True)
    is_followed = Column(Boolean, default=False, index=True)
    h_index = Column(Integer, default=0)
    notes = Column(Text, default="")


class ResearchTopic(Base):
    __tablename__ = "research_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), unique=True, nullable=False)
    category = Column(String(50), default="Primary")  # Primary (Human / Cancer / Functional Genomics), Secondary (Pathogen / Evolution), Custom
    priority_weight = Column(Integer, default=5)  # 1 - 10
    is_active = Column(Boolean, default=True)
    keywords_json = Column(Text, default="[]")  # JSON list of keywords


class SearchProfile(Base):
    __tablename__ = "search_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), unique=True, nullable=False)
    description = Column(Text, default="")
    query_string = Column(Text, nullable=False)
    filter_open_access = Column(Boolean, default=False)
    target_sources = Column(String(255), default="OpenAlex,PubMed,Europe PMC,bioRxiv")
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    publication_id = Column(Integer, ForeignKey("publications.id", ondelete="CASCADE"), nullable=False)
    week_identifier = Column(String(20), nullable=False, index=True)  # e.g., '2026-W45'
    category = Column(String(50), default="Core")  # Core, Computational, Complementary
    recommendation_score = Column(Float, default=0.0)
    selection_reason = Column(Text, default="")
    targeted_interest = Column(String(255), default="")
    phd_relevance = Column(Text, default="")
    key_learnings_json = Column(Text, default="[]")  # JSON list of 3 things
    status = Column(String(30), default="Pending", index=True)  # Pending, Accepted, Rejected, Postponed, Completed
    created_at = Column(DateTime, default=datetime.utcnow)

    publication = relationship("Publication", back_populates="recommendations")


class ReadingRecord(Base):
    __tablename__ = "reading_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    publication_id = Column(Integer, ForeignKey("publications.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), default="Recommended")  # Recommended, Accepted, Reading, Completed, Revisit, Not relevant
    date_started = Column(Date, nullable=True)
    date_completed = Column(Date, nullable=True)
    reading_duration_minutes = Column(Integer, default=0)
    personal_notes = Column(Text, default="")
    main_findings = Column(Text, default="")
    important_methods = Column(Text, default="")
    limitations = Column(Text, default="")
    questions_raised = Column(Text, default="")
    phd_relevance = Column(Text, default="")
    potential_applications = Column(Text, default="")
    rating = Column(Integer, default=0)  # 1 to 5 stars
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    publication = relationship("Publication", back_populates="reading_records")


class ResearchNote(Base):
    __tablename__ = "research_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    note_type = Column(String(40), default="note", index=True)  # idea, method, note, activity
    content_markdown = Column(Text, nullable=False)
    tags_json = Column(Text, default="[]")
    linked_publication_id = Column(Integer, ForeignKey("publications.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    publication = relationship("Publication", back_populates="notes")


class BioinformaticsTool(Base):
    __tablename__ = "bioinformatics_tools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, default="")
    category = Column(String(80), default="Variant calling", index=True)
    application = Column(Text, default="")
    input_formats = Column(String(200), default="FASTQ, BAM, VCF")
    sequencing_tech = Column(String(200), default="Illumina, PacBio HiFi, ONT")
    algorithms = Column(Text, default="")
    install_instructions = Column(Text, default="")
    doc_url = Column(String(300), default="")
    github_url = Column(String(300), default="")
    associated_doi = Column(String(120), default="")
    advantages = Column(Text, default="")
    limitations = Column(Text, default="")
    personal_experience = Column(Text, default="")
    learning_status = Column(String(40), default="To Learn", index=True)  # To Learn, Learning, Proficient, Expert
    created_at = Column(DateTime, default=datetime.utcnow)


class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    status = Column(String(40), default="Active")  # Active, Completed, On Hold
    start_date = Column(Date, default=date.today)
    target_end_date = Column(Date, nullable=True)

    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("research_projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String(40), default="Pending")  # Pending, In Progress, Achieved

    project = relationship("ResearchProject", back_populates="milestones")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("research_projects.id", ondelete="SET NULL"), nullable=True)
    linked_publication_id = Column(Integer, ForeignKey("publications.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    status = Column(String(40), default="To do", index=True)  # To do, In progress, Completed, On hold
    priority = Column(String(30), default="Medium")  # Low, Medium, High, Urgent
    due_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("ResearchProject", back_populates="tasks")
    publication = relationship("Publication", back_populates="tasks")


class MonitoredEntity(Base):
    __tablename__ = "monitored_entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    entity_type = Column(String(50), default="rss_feed")  # rss_feed, github_repo, journal, lab
    url = Column(String(500), nullable=False)
    feed_or_repo = Column(String(255), default="")  # e.g., 'lh3/minimap2' or feed URL
    last_checked = Column(DateTime, nullable=True)
    latest_title = Column(String(500), default="")
    latest_link = Column(String(500), default="")
    latest_snippet = Column(Text, default="")
    is_active = Column(Boolean, default=True)


class WeeklyDigest(Base):
    __tablename__ = "weekly_digests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    week_identifier = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content_markdown = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
