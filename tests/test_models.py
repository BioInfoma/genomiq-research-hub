"""
Database models and persistence test suite.
"""
import pytest
from database.connection import init_db, get_db
from database.models import Publication, ReadingRecord, BioinformaticsTool, ResearchTopic


def test_database_init_and_crud():
    init_db()
    with get_db() as db:
        # Create test pub
        pub = Publication(
            title="Test Automated Genomics Benchmarking",
            authors="Smith, J. et al.",
            doi="10.1000/test.12345",
            pmid="99999999",
            year=2024,
            journal="Test Journal",
            reading_status="Unread"
        )
        db.add(pub)
        db.commit()

        # Query
        found = db.query(Publication).filter(Publication.doi == "10.1000/test.12345").first()
        assert found is not None
        assert found.title == "Test Automated Genomics Benchmarking"

        # Cleanup
        db.delete(found)
        db.commit()
