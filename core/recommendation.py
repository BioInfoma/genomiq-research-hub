"""
Intelligent Paper Recommendation Engine for GenomIQ Research Hub.
Implements the 9-parameter weighted algorithm to select the 4 weekly papers
expected by the PhD supervisor:
- 2 Core Research Papers
- 1 Computational / Methodological Paper
- 1 Complementary Research Paper

Generates structured recommendation explanations (why selected, 3 learning points,
PhD relevance, prerequisite context) and generates ordered reading pathways.
"""
import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy import desc, or_, not_
from sqlalchemy.orm import joinedload
from database.connection import get_db
from database.models import Publication, Recommendation, ReadingRecord, ResearchTopic


class RecommendationEngine:
    def __init__(self):
        pass

    def compute_paper_score(self, pub: Publication, active_topics: List[ResearchTopic], read_pub_ids: set) -> float:
        """
        Calculates recommendation score (0 - 100) based on 9 criteria:
        1. Relevance to PhD primary research (weight 25)
        2. Match with active research topics (weight 20)
        3. Publication recency (weight 15)
        4. Scientific influence / citation velocity (weight 15)
        5. Methodological relevance (weight 10)
        6. Foundational / Landmark importance (weight 10)
        7. Novelty (preprints / current year) (weight 5)
        8. Relation to previously read topics
        9. Exclusion of already completed papers (handled upfront)
        """
        if pub.id in read_pub_ids:
            return -100.0  # Do not recommend completed papers

        score = 0.0
        text_corpus = f"{pub.title} {pub.abstract} {pub.research_topics}".lower()

        # 1 & 2: Topic matching
        for t in active_topics:
            t_keywords = json.loads(t.keywords_json) if t.keywords_json else [t.name.lower()]
            topic_hits = sum(1 for kw in t_keywords if kw.lower() in text_corpus)
            if topic_hits > 0:
                mult = 1.0 if t.category == "Primary" else 0.5
                score += min(topic_hits * 4.0, 25.0) * mult

        # 3: Recency
        current_year = date.today().year
        pub_year = pub.year or (current_year - 5)
        age = max(0, current_year - pub_year)
        if age == 0:
            score += 15.0
        elif age <= 2:
            score += 12.0
        elif age <= 5:
            score += 8.0
        else:
            score += 3.0  # Older papers get points only if foundational/landmark

        # 4: Scientific influence / citations
        cites = pub.citation_count or 0
        if cites > 1000:
            score += 15.0
        elif cites > 250:
            score += 12.0
        elif cites > 50:
            score += 8.0
        elif cites > 5:
            score += 4.0

        # 5: Methodological relevance
        method_terms = ["algorithm", "pipeline", "benchmark", "tool", "workflow", "method", "software", "assembly", "calling"]
        if any(m in text_corpus for m in method_terms):
            score += 10.0

        # 6: Foundational importance
        if pub.paper_category in ["Landmark", "Foundational"]:
            score += 12.0

        # 7: Novelty (Preprints)
        if pub.publication_type == "Preprint":
            score += 5.0

        return round(score, 2)

    def classify_paper(self, pub: Publication) -> str:
        """Classifies paper into category."""
        text = f"{pub.title} {pub.abstract}".lower()
        if pub.citation_count and pub.citation_count > 500:
            return "Landmark"
        if "review" in text or "perspective" in text:
            return "Review"
        if any(w in text for w in ["algorithm", "software", "pipeline", "benchmark", "hifiasm", "mutect2", "tool"]):
            return "Methodological"
        if pub.publication_type == "Preprint" or (pub.year and pub.year >= date.today().year - 1):
            return "Recent"
        if any(w in text for w in ["pathogen", "viral", "phylodynamics", "phylogeography"]):
            return "Complementary"
        return "Core"

    def generate_explanation(self, pub: Publication, category: str) -> Dict[str, Any]:
        """Generates clear, scientifically grounded recommendation rationale."""
        paper_type = self.classify_paper(pub)

        # Learning points tailored to content
        points = []
        text = f"{pub.title} {pub.abstract}".lower()

        if "pangenome" in text or "graph" in text:
            points = [
                "How graph-based references overcome linear reference allele bias in non-European cohorts.",
                "Algorithmic trade-offs between assembly accuracy and graph index computational overhead.",
                "Practical integration into downstream short and long-read variant calling pipelines."
            ]
        elif "somatic" in text or "cancer" in text or "tmb" in text:
            points = [
                "Strategies for distinguishing low-frequency somatic mutations from sequencing artifacts.",
                "Impact of tumor purity and clonal heterogeneity on biomarker quantification.",
                "Translational relevance of mutation signatures and neoantigen prediction in clinical cohorts."
            ]
        elif "assembly" in text or "hifiasm" in text:
            points = [
                "De novo string graph resolution algorithms for diploid and polyploid genomes.",
                "Haplotype phasing methods using parental markers, Hi-C, or long-range linkage.",
                "Evaluating contiguity (N50) and base accuracy benchmarks across sequencing chemistries."
            ]
        elif "pathogen" in text or "phylodynamic" in text:
            points = [
                "Principles of molecular clock rate estimation and Bayesian genealogical reconstruction.",
                "Integrating epidemiological metadata with sequence phylogenies.",
                "Surveillance workflows for tracking transmission dynamics in emerging variants."
            ]
        else:
            points = [
                "Methodological principles, experimental design, and data processing workflows.",
                "Quantitative benchmarks and biological significance of reported findings.",
                "Relevance to your PhD thesis questions and actionable workflow improvements."
            ]

        # Target interest
        interest = pub.research_topics.split(",")[0] if pub.research_topics else "Human Genomics and Cancer"

        why = (
            f"Selected as a high-impact {paper_type.lower()} publication addressing {interest}. "
            f"Published in {pub.journal or 'a peer-reviewed journal'} with {pub.citation_count} citations."
        )

        phd_rel = (
            f"Crucial for establishing solid ground truth and methodology for your dissertation chapters on "
            f"{interest}. Gives you authoritative citations and comparative baselines for your experiments."
        )

        return {
            "why_selected": why,
            "targeted_interest": interest,
            "phd_relevance": phd_rel,
            "three_learnings": points,
            "paper_type": paper_type,
            "prerequisites": "Foundational understanding of high-throughput sequencing and variant calling." if "Methodological" in paper_type else "General human genomics and molecular biology background."
        }

    def generate_weekly_recommendations(self, week_identifier: Optional[str] = None, force_refresh: bool = False) -> List[Recommendation]:
        """
        Selects and stores the 4 papers for the target week:
        - 2 Core papers
        - 1 Computational/Methodological paper
        - 1 Complementary paper
        """
        if not week_identifier:
            today = date.today()
            week_identifier = f"{today.year}-W{today.isocalendar()[1]:02d}"

        with get_db() as db:
            # Check existing for this week
            existing = db.query(Recommendation).options(joinedload(Recommendation.publication)).filter(Recommendation.week_identifier == week_identifier).all()
            if existing and not force_refresh:
                return existing

            if existing and force_refresh:
                for ex in existing:
                    db.delete(ex)
                db.flush()

            # Get completed publication IDs to exclude
            completed_records = db.query(ReadingRecord).filter(ReadingRecord.status == "Completed").all()
            read_ids = {r.publication_id for r in completed_records}

            # Get active topics
            active_topics = db.query(ResearchTopic).filter(ResearchTopic.is_active == True).all()

            # Retrieve eligible publications
            candidates = db.query(Publication).filter(
                not_(Publication.reading_status.in_(["Completed", "Not relevant"]))
            ).all()

            if not candidates:
                return []

            # Score each candidate
            scored_candidates = []
            for pub in candidates:
                sc = self.compute_paper_score(pub, active_topics, read_ids)
                scored_candidates.append((sc, pub))

            scored_candidates.sort(key=lambda x: x[0], reverse=True)

            # Categorize candidates into pools
            core_pool = []
            comp_pool = []
            complem_pool = []

            for sc, pub in scored_candidates:
                text = f"{pub.title} {pub.abstract} {pub.research_topics}".lower()
                is_comp = any(w in text for w in ["algorithm", "pipeline", "tool", "benchmark", "software", "assembly", "method"])
                is_complem = any(w in text for w in ["pathogen", "viral", "bacterial", "phylodynamic", "phylogeography", "surveillance"])

                if is_complem:
                    complem_pool.append((sc, pub))
                elif is_comp:
                    comp_pool.append((sc, pub))
                else:
                    core_pool.append((sc, pub))

            selected_slots = []

            # 2 Core papers
            for sc, pub in core_pool[:2]:
                selected_slots.append(("Core", sc, pub))

            # If core pool had fewer than 2, fill from rest
            while len(selected_slots) < 2 and scored_candidates:
                for sc, pub in scored_candidates:
                    if pub not in [s[2] for s in selected_slots]:
                        selected_slots.append(("Core", sc, pub))
                        break

            # 1 Computational paper
            added_comp = False
            for sc, pub in comp_pool:
                if pub not in [s[2] for s in selected_slots]:
                    selected_slots.append(("Computational", sc, pub))
                    added_comp = True
                    break
            if not added_comp:
                for sc, pub in scored_candidates:
                    if pub not in [s[2] for s in selected_slots]:
                        selected_slots.append(("Computational", sc, pub))
                        break

            # 1 Complementary paper
            added_complem = False
            for sc, pub in complem_pool:
                if pub not in [s[2] for s in selected_slots]:
                    selected_slots.append(("Complementary", sc, pub))
                    added_complem = True
                    break
            if not added_complem:
                for sc, pub in scored_candidates:
                    if pub not in [s[2] for s in selected_slots]:
                        selected_slots.append(("Complementary", sc, pub))
                        break

            # Create recommendation entries
            new_recommendations = []
            for slot_cat, score, pub in selected_slots[:4]:
                exp = self.generate_explanation(pub, slot_cat)
                rec = Recommendation(
                    publication_id=pub.id,
                    week_identifier=week_identifier,
                    category=slot_cat,
                    recommendation_score=max(score, 10.0),
                    selection_reason=exp["why_selected"],
                    targeted_interest=exp["targeted_interest"],
                    phd_relevance=exp["phd_relevance"],
                    key_learnings_json=json.dumps(exp["three_learnings"]),
                    status="Pending"
                )
                db.add(rec)
                # Update pub status
                pub.reading_status = "Recommended"
                new_recommendations.append(rec)

            db.commit()
            return new_recommendations

    def generate_reading_pathway(self, topic_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generates a curated 4-tier reading pathway from introductory / reviews to advanced methods:
        Tier 1: Foundational / Review
        Tier 2: Landmark Discoveries
        Tier 3: Methodological / Computational Benchmarks
        Tier 4: Recent Specialized Advances
        """
        with get_db() as db:
            query = db.query(Publication)
            if topic_name and topic_name != "All Topics":
                query = query.filter(Publication.research_topics.ilike(f"%{topic_name}%"))

            all_pubs = query.all()
            if not all_pubs:
                return []

            tier1 = [p for p in all_pubs if p.paper_category in ["Review", "Foundational"] or "review" in p.title.lower()]
            tier2 = [p for p in all_pubs if p.paper_category == "Landmark" or p.citation_count > 400]
            tier3 = [p for p in all_pubs if p.paper_category in ["Computational", "Methodological"] or "pipeline" in p.title.lower()]
            tier4 = [p for p in all_pubs if p.publication_type == "Preprint" or (p.year and p.year >= 2023)]

            # Fallbacks if tiers are empty
            remaining = [p for p in all_pubs]

            def pick_first(lst, used):
                for item in lst:
                    if item.id not in used:
                        used.add(item.id)
                        return item
                for item in remaining:
                    if item.id not in used:
                        used.add(item.id)
                        return item
                return None

            used_ids = set()
            pathway = []

            p1 = pick_first(tier1, used_ids)
            if p1:
                pathway.append({"tier": 1, "level": "Foundational / Survey", "paper": p1, "focus": "Grasp broad conceptual landscape, terminology, and historical context."})

            p2 = pick_first(tier2, used_ids)
            if p2:
                pathway.append({"tier": 2, "level": "Landmark Groundwork", "paper": p2, "focus": "Examine landmark datasets, empirical discoveries, and established biological findings."})

            p3 = pick_first(tier3, used_ids)
            if p3:
                pathway.append({"tier": 3, "level": "Algorithmic & Computational Methods", "paper": p3, "focus": "Master algorithmic mechanics, pipeline architectures, and comparative benchmarks."})

            p4 = pick_first(tier4, used_ids)
            if p4:
                pathway.append({"tier": 4, "level": "Cutting-Edge Frontiers", "paper": p4, "focus": "Explore state-of-the-art advances, unsolved challenges, and immediate PhD research opportunities."})

            return pathway
