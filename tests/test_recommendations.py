"""
Recommendation engine tests.
"""
import pytest
from database.connection import init_db, get_db
from database.seed_data import seed_all
from core.recommendation import RecommendationEngine


def test_recommendation_generation():
    init_db()
    seed_all()
    engine = RecommendationEngine()
    recs = engine.generate_weekly_recommendations(week_identifier="2026-TEST-W01", force_refresh=True)
    assert len(recs) == 4
    categories = [r.category for r in recs]
    assert "Core" in categories
    assert "Computational" in categories
    assert "Complementary" in categories
