"""
Discovery engine unit tests.
"""
import pytest
from core.discovery import LiteratureDiscoveryEngine


def test_discovery_engine_initialization():
    engine = LiteratureDiscoveryEngine()
    assert engine.headers is not None
    assert "User-Agent" in engine.headers
