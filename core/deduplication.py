"""
Deduplication and record normalization utilities for GenomIQ Research Hub.
Ensures scientific integrity by preventing duplicate publications using
canonical DOI, PMID, and fuzzy title matching.
"""
import re
from typing import Optional, Tuple
from database.models import Publication


def normalize_doi(doi: Optional[str]) -> Optional[str]:
    """Cleans and standardizes a Digital Object Identifier (DOI)."""
    if not doi:
        return None
    cleaned = str(doi).strip().lower()
    cleaned = re.sub(r"^https?://(dx\.)?doi\.org/", "", cleaned)
    cleaned = re.sub(r"^doi:\s*", "", cleaned)
    cleaned = cleaned.strip().strip("/")
    return cleaned if cleaned else None


def normalize_pmid(pmid: Optional[str]) -> Optional[str]:
    """Standardizes a PubMed Unique Identifier (PMID)."""
    if not pmid:
        return None
    cleaned = re.sub(r"[^\d]", "", str(pmid).strip())
    return cleaned if cleaned else None


def clean_title_for_comparison(title: str) -> str:
    """Removes punctuation and casing for robust string similarity."""
    if not title:
        return ""
    text = title.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [w for w in text.split() if len(w) > 2]
    return " ".join(tokens)


def token_jaccard_similarity(str1: str, str2: str) -> float:
    """Calculates Jaccard token overlap between two strings."""
    tokens1 = set(clean_title_for_comparison(str1).split())
    tokens2 = set(clean_title_for_comparison(str2).split())
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)


def find_existing_duplicate(session, doi: Optional[str] = None, pmid: Optional[str] = None, title: Optional[str] = None) -> Tuple[bool, Optional[Publication]]:
    """
    Checks if a publication already exists in the database.
    Order of verification:
    1. Canonical DOI exact match.
    2. PMID exact match.
    3. High-confidence title similarity (Jaccard > 0.85).
    """
    norm_doi = normalize_doi(doi)
    if norm_doi:
        existing = session.query(Publication).filter(Publication.doi == norm_doi).first()
        if existing:
            return True, existing

    norm_pmid = normalize_pmid(pmid)
    if norm_pmid:
        existing = session.query(Publication).filter(Publication.pmid == norm_pmid).first()
        if existing:
            return True, existing

    if title and len(title.strip()) > 15:
        # Check against recent or candidate titles with similar first words
        clean_target = clean_title_for_comparison(title)
        first_few_words = " ".join(clean_target.split()[:3])
        if first_few_words:
            candidates = session.query(Publication).filter(Publication.title.ilike(f"%{first_few_words}%")).all()
            for cand in candidates:
                sim = token_jaccard_similarity(title, cand.title)
                if sim >= 0.85:
                    return True, cand

    return False, None
