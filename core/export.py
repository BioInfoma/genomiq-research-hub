"""
Export utilities for GenomIQ Research Hub.
Supports:
- BibTeX export
- RIS export (for EndNote, Zotero, Mendeley)
- Markdown note export
- CSV tabular data export
"""
import re
from typing import List
from database.models import Publication, ResearchNote, BioinformaticsTool


def generate_bibtex_key(pub: Publication) -> str:
    """Generates standard citation key e.g., 'liao2023draft'."""
    first_author = "unknown"
    if pub.authors:
        # Extract first family name
        author_match = re.search(r"([A-Za-z]+)", pub.authors)
        if author_match:
            first_author = author_match.group(1).lower()
    year = pub.year or "nd"
    first_word = "doc"
    if pub.title:
        words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", pub.title) if w.lower() not in ["the", "and", "for", "with"]]
        if words:
            first_word = words[0]
    return f"{first_author}{year}{first_word}"


def export_publications_to_bibtex(publications: List[Publication]) -> str:
    """Converts a list of publications into standard BibTeX string."""
    entries = []
    for pub in publications:
        key = generate_bibtex_key(pub)
        entry_type = "article" if pub.publication_type != "Preprint" else "unpublished"

        lines = [
            f"@{entry_type}{{{key},",
            f"  title = {{{pub.title}}},",
            f"  author = {{{pub.authors}}},",
            f"  journal = {{{pub.journal}}}," if pub.journal else "",
            f"  year = {{{pub.year}}}," if pub.year else "",
            f"  doi = {{{pub.doi}}}," if pub.doi else "",
            f"  url = {{{pub.publisher_url}}}," if pub.publisher_url else "",
            f"  note = {{Discovered via {pub.source_database} | GenomIQ Research Hub}}"
        ]
        valid_lines = [l for l in lines if l]
        entries.append("\n".join(valid_lines) + "\n}")

    return "\n\n".join(entries)


def export_publications_to_ris(publications: List[Publication]) -> str:
    """Converts publications to standard RIS format for Zotero/EndNote."""
    entries = []
    for pub in publications:
        type_tag = "JOUR" if pub.publication_type != "Preprint" else "UNPB"
        lines = [
            f"TY  - {type_tag}",
            f"TI  - {pub.title}",
        ]
        if pub.authors:
            for author in pub.authors.split(","):
                a_clean = author.strip()
                if a_clean and not a_clean.lower().startswith("et al"):
                    lines.append(f"AU  - {a_clean}")
        if pub.journal:
            lines.append(f"JO  - {pub.journal}")
        if pub.year:
            lines.append(f"PY  - {pub.year}")
        if pub.doi:
            lines.append(f"DO  - {pub.doi}")
        if pub.publisher_url:
            lines.append(f"UR  - {pub.publisher_url}")
        if pub.abstract:
            lines.append(f"AB  - {pub.abstract}")
        lines.append("ER  - ")
        entries.append("\n".join(lines))

    return "\n\n".join(entries)
