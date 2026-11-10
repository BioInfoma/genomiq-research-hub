"""
Unit tests for deduplication and canonical identifier normalization.
"""
import pytest
from core.deduplication import normalize_doi, normalize_pmid, token_jaccard_similarity, clean_title_for_comparison


def test_normalize_doi():
    assert normalize_doi("https://doi.org/10.1038/s41586-023-05896-x") == "10.1038/s41586-023-05896-x"
    assert normalize_doi("http://dx.doi.org/10.1038/nature11252/") == "10.1038/nature11252"
    assert normalize_doi("doi: 10.1038/NBT.4235 ") == "10.1038/nbt.4235"
    assert normalize_doi(None) is None
    assert normalize_doi("") is None


def test_normalize_pmid():
    assert normalize_pmid("37165242") == "37165242"
    assert normalize_pmid("PMID: 37165242 ") == "37165242"
    assert normalize_pmid(None) is None


def test_title_similarity():
    t1 = "A draft human pangenome reference"
    t2 = "A Draft Human Pangenome Reference."
    assert token_jaccard_similarity(t1, t2) == 1.0

    t3 = "The somatic mutation landscape and genomic classifications of colorectal cancer"
    t4 = "Somatic mutation landscape in human colorectal cancer"
    sim = token_jaccard_similarity(t3, t4)
    assert sim > 0.4
