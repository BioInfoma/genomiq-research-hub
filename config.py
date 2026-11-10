"""
GenomIQ Research Hub - Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Load environment variables if .env exists
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# Database configuration with Cloud & Secrets fallback
DB_FILE = DATA_DIR / "genomiq.db"

_db_url = os.getenv("DATABASE_URL")
if not _db_url:
    try:
        import streamlit as _st
        if hasattr(_st, "secrets") and "DATABASE_URL" in _st.secrets:
            _db_url = _st.secrets["DATABASE_URL"]
    except Exception:
        pass

if _db_url:
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    DATABASE_URL = _db_url
else:
    DATABASE_URL = f"sqlite:///{DB_FILE.as_posix()}"

# App metadata
APP_TITLE = "GenomIQ Research Hub"
APP_SUBTITLE = "Personal PhD Research Intelligence & Management Platform"
APP_VERSION = "1.0.0"

# User default research profile
DEFAULT_RESEARCH_PROFILE = {
    "user_name": "PhD Candidate",
    "department": "Bioinformatics & Human Genomics",
    "institution": "Genomics Research Institute",
    "primary_focus": [
        "Human Genomics and Pangenomics",
        "Cancer Genomics & Somatic Variation",
        "Colorectal Cancer Genomics",
        "Functional Genomics & Transcriptomics",
        "Bioinformatics Algorithms & Pipelines",
    ],
    "secondary_focus": [
        "Pathogen Genomics & Surveillance",
        "Phylodynamics & Molecular Evolution",
    ],
    "weekly_target_papers": 4,
}

# API Configs (Free / Polite contact info)
OPENALEX_MAILTO = os.getenv("OPENALEX_MAILTO", "phd.researcher@example.org")
NCBI_EMAIL = os.getenv("NCBI_EMAIL", "phd.researcher@example.org")
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")
SEMANTIC_SCHOLAR_KEY = os.getenv("SEMANTIC_SCHOLAR_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Default request timeout (seconds)
HTTP_TIMEOUT = 12
