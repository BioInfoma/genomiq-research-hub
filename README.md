# GenomIQ Research Hub 🧬
### Personal PhD Research Intelligence and Management Platform

**GenomIQ Research Hub** is a modular, local-first research intelligence and workflow management platform specifically tailored for a PhD researcher in **Bioinformatics, Human Genomics, and Cancer Genomics**. 

It runs 100% locally with free, open-source academic APIs and tools—no mandatory subscriptions, paid APIs, or external dependencies required.

---

## 🌟 Key Features

### 1. Automated Academic Literature Discovery
- **Multi-API Integration:** Real-time query integration across:
  - **OpenAlex REST API**
  - **NCBI PubMed (E-utilities)**
  - **Europe PMC REST API**
  - **Crossref REST API**
  - **bioRxiv / medRxiv Preprint API**
- **10 Configured PhD Search Profiles:**
  - `PROFILE 1: Human Pangenomics`
  - `PROFILE 2: African Population Genomics`
  - `PROFILE 3: Cancer and Somatic Variant Calling`
  - `PROFILE 4: Colorectal Cancer Genomics`
  - `PROFILE 5: Tumour Mutational Burden`
  - `PROFILE 6: Functional Genomics`
  - `PROFILE 7: Genome Assembly and Alignment`
  - `PROFILE 8: Bioinformatics Methods`
  - `PROFILE 9: Pathogen Genomics`
  - `PROFILE 10: Phylodynamics and Phylogeography`
- **Deduplication Engine:** Canonical DOI normalization, PMID matching, and Jaccard title similarity check to prevent duplicate entries.

### 2. Intelligent Paper Recommendation Engine
- **Supervisor Target:** Automatically schedules the expected **4 weekly papers**:
  - **2 Papers:** Core Research Topics (Pangenomics, Somatic Variation, Colorectal Cancer)
  - **1 Paper:** Computational & Methodological Topics (Algorithms, Aligners, Variant Callers)
  - **1 Paper:** Complementary Research Topics (Pathogen Genomics, Phylodynamics)
- **9-Parameter Weighted Scoring Algorithm:** Evaluates topic relevance, publication recency, citation velocity, methodology, and excludes already-read papers.
- **Scientifically Grounded Explanations:** Explains *why* each paper was selected, addressed research interests, thesis relevance, and 3 essential takeaways.
- **4-Tier Guided Reading Pathways:** Generates curated reading trajectories from foundational reviews to cutting-edge frontiers.

### 3. Four-Paper Weekly Reading Tracker
- Real-time progress bar against the supervisor's 4-paper target.
- Status management: `Recommended`, `Accepted`, `Reading`, `Completed`, `Revisit`, `Not relevant`.
- Structured PhD reflection capture:
  - Main biological and computational findings
  - Key algorithms and datasets
  - Methodological limitations
  - Direct applications to PhD dissertation chapters
  - Accumulated reading duration and star ratings

### 4. Research Documentation Management
- Dedicated markdown repository for:
  - 💡 **Research Ideas & Hypotheses**
  - ⚙️ **Bioinformatics Methods & Workflows**
  - 📋 **Meeting Notes & Supervisor Feedback**
  - 🔬 **Experimental Activities & Benchmarking Logs**
- Direct linking between notes and publications.
- One-click Markdown export.

### 5. Bioinformatics Software & Methods Database
- Pre-populated with **20 foundational tools**:
  - *Assemblers & Graph Tools:* Hifiasm, Flye, Minigraph-Cactus, VG
  - *Aligners:* Minimap2, BWA-MEM, Bowtie2, STAR, HISAT2, Samtools
  - *Variant Callers:* GATK (HaplotypeCaller & Mutect2), DeepVariant, Strelka2, Bcftools
  - *Variant Annotators:* Ensembl VEP, SnpEff
  - *Phylogenetics & Phylodynamics:* IQ-TREE, BEAST2, Nextstrain
- Tracks supported sequencing technologies, input formats, underlying algorithms, documentation links, GitHub URLs, and personal learning status (`To Learn` ➔ `Learning` ➔ `Proficient` ➔ `Expert`).

### 6. Authors and Citation Tracking
- Citation count analytics and network exploration.
- Track followed Principal Investigators and research groups.
- One-click export to **BibTeX** and **RIS** (Zotero, EndNote, Mendeley).

### 7. PhD Tasks & Kanban Board
- Visual Kanban workflow: `To do`, `In progress`, `Completed`, `On hold`.
- Priority levels (`Low`, `Medium`, `High`, `Urgent`), deadline tracking, and task linking to specific publications and projects.

### 8. Web & Software Release Monitoring
- Automated monitoring of GitHub repository releases (e.g. `lh3/minimap2`, `vgteam/vg`, `broadinstitute/gatk`).
- RSS feed tracking for bioRxiv genomics/bioinformatics preprints.

### 9. Automated Weekly Research Digest & Reports
- Generates a weekly research digest synthesizing recommendations, newly discovered papers, preprints, software updates, and task deadlines.
- Exportable to Markdown and HTML.
- Domain saturation analytics by topic.

### 10. Data Safety & Persistence
- Local persistent SQLite database at `data/genomiq.db`.
- Automatic one-click timestamped database backups.
- Background task scheduler using APScheduler.

---

## 🚀 Quickstart & Execution

### Prerequisites
- Python 3.10+ (Recommended Python 3.12)
- Git (optional)

### Installation
1. Clone or navigate to the project directory:
   ```bash
   cd c:\Users\USER\Documents\Phd\Web_app
   ```

2. Activate the virtual environment:
   - **Windows:**
     ```powershell
     .venv\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     source .venv/bin/activate
     ```

3. (If not already installed) Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
Launch the Streamlit web application:
```bash
streamlit run app.py
```
Open your browser to:
👉 **`http://localhost:8501`**

---

## 🧪 Running the Automated Test Suite

Run pytest to verify database persistence, deduplication, recommendation logic, and API connectors:
```bash
pytest -v
```

---

## 📁 Project Architecture

```
Web_app/
├── app.py                     # Streamlit application entry point
├── config.py                  # Settings, paths, environment configuration
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Pytest test configuration
├── README.md                  # Comprehensive user and developer manual
├── .env.example               # Example optional API credentials
├── data/
│   ├── genomiq.db             # Local persistent SQLite database
│   └── backups/               # Automated timestamped database backups
├── database/
│   ├── __init__.py
│   ├── models.py              # SQLAlchemy 2.0 ORM models
│   ├── connection.py          # Engine, sessionmaker, and DB backup utility
│   └── seed_data.py           # 10 search profiles, 20 bioinformatics tools, landmark papers
├── core/
│   ├── __init__.py
│   ├── discovery.py           # Multi-API literature discovery (OpenAlex, PubMed, Europe PMC, bioRxiv)
│   ├── deduplication.py       # DOI / PMID normalization and title similarity check
│   ├── recommendation.py      # 9-parameter recommendation algorithm & weekly 4-paper selector
│   ├── reading_tracker.py     # Reading tracker service, KPIs, status transitions
│   ├── monitoring.py          # GitHub API releases & RSS monitoring
│   ├── digest.py              # Weekly digest and report generator
│   ├── export.py              # BibTeX & RIS citation export utilities
│   └── scheduler.py           # APScheduler background tasks manager
├── ui/
│   ├── __init__.py
│   ├── components.py          # Reusable scientific UI cards, badges, and metrics
│   └── pages/
│       ├── overview.py        # 1. Overview Dashboard
│       ├── discovery.py       # 2. Automated Literature Discovery
│       ├── recommendations.py # 3. Recommended Reading (Weekly 4 papers)
│       ├── reading_tracker.py # 4. Four-Paper Reading Tracker
│       ├── library.py         # 5. Central Literature Library
│       ├── notes.py           # 6. Research Documentation Management
│       ├── tools.py           # 7. Bioinformatics Software & Methods
│       ├── citations.py       # 8. Authors and Citations
│       ├── projects.py        # 9. Research Projects & Objectives
│       ├── tasks.py           # 10. Tasks & Milestones (Kanban Board)
│       ├── monitoring.py      # 11. Web & Research Monitoring
│       ├── reports.py         # 12. Reports & Weekly Digest
│       └── settings.py        # 13. Settings & Research Profile
└── tests/
    ├── test_deduplication.py
    ├── test_models.py
    ├── test_recommendations.py
    └── test_discovery.py
```
