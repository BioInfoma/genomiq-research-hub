"""
Seed data initialisation for GenomIQ Research Hub.
Pre-populates the 10 specified PhD research profiles, 20 standard bioinformatics
tools, default research projects, milestone tracks, monitored feeds, and landmark publications.
"""
import json
from datetime import datetime, date
from database.connection import get_db
from database.models import (
    SearchProfile, ResearchTopic, BioinformaticsTool, ResearchProject,
    Milestone, Task, MonitoredEntity, Publication, Recommendation, ReadingRecord
)


def seed_all():
    """Seeds default data if database tables are empty."""
    with get_db() as db:
        seed_research_topics(db)
        seed_search_profiles(db)
        seed_bioinformatics_tools(db)
        seed_projects_and_tasks(db)
        seed_monitored_entities(db)
        seed_starter_landmark_publications(db)


def seed_research_topics(db):
    if db.query(ResearchTopic).count() > 0:
        return

    topics = [
        # Primary PhD topics
        {"name": "Human Pangenomics & Graph Genomes", "category": "Primary", "priority_weight": 10,
         "keywords_json": json.dumps(["pangenome", "graph genome", "HPRC", "minigraph", "haplotype", "structural variation"])},
        {"name": "African Population Genomics", "category": "Primary", "priority_weight": 9,
         "keywords_json": json.dumps(["african genomics", "genetic diversity", "population genetics", "admixture", "novel sequences"])},
        {"name": "Cancer Somatic Variant Calling", "category": "Primary", "priority_weight": 10,
         "keywords_json": json.dumps(["somatic variant calling", "mutect2", "strelka2", "tumour heterogeneity", "liquid biopsy"])},
        {"name": "Colorectal Cancer Genomics", "category": "Primary", "priority_weight": 9,
         "keywords_json": json.dumps(["colorectal cancer", "CRC", "microsatellite instability", "MSI", "KRAS", "BRAF", "APC"])},
        {"name": "Tumour Mutational Burden & Biomarkers", "category": "Primary", "priority_weight": 8,
         "keywords_json": json.dumps(["tumour mutational burden", "TMB", "immunotherapy biomarker", "neoantigen", "checkpoint inhibitor"])},
        {"name": "Functional & Single-Cell Genomics", "category": "Primary", "priority_weight": 8,
         "keywords_json": json.dumps(["RNA-seq", "single-cell", "scRNA-seq", "transcriptomics", "gene regulation", "epigenomics"])},
        {"name": "Genome Assembly & Haplotype Phasing", "category": "Primary", "priority_weight": 9,
         "keywords_json": json.dumps(["genome assembly", "hifiasm", "long-read", "PacBio HiFi", "Oxford Nanopore", "phasing"])},
        {"name": "Bioinformatics Pipelines & Benchmarking", "category": "Primary", "priority_weight": 8,
         "keywords_json": json.dumps(["Nextflow", "Snakemake", "variant benchmarking", "reproducible bioinformatics", "GATK"])},

        # Secondary / Complementary topics
        {"name": "Pathogen & Viral Genomics", "category": "Secondary", "priority_weight": 4,
         "keywords_json": json.dumps(["pathogen genomics", "viral surveillance", "SARS-CoV-2", "bacterial genomics", "AMR"])},
        {"name": "Phylodynamics & Molecular Evolution", "category": "Secondary", "priority_weight": 4,
         "keywords_json": json.dumps(["phylodynamics", "phylogeography", "molecular clock", "BEAST", "IQ-TREE", "tree inference"])},
    ]

    for t in topics:
        db.add(ResearchTopic(**t))
    db.flush()


def seed_search_profiles(db):
    if db.query(SearchProfile).count() > 0:
        return

    profiles = [
        {"name": "PROFILE 1: Human Pangenomics",
         "description": "Human reference genome development, graph representations, and population pangenomes.",
         "query_string": "human pangenome graph reference assembly HPRC"},
        {"name": "PROFILE 2: African Population Genomics",
         "description": "Genetic diversity, novel sequence discovery, and population structure across African cohorts.",
         "query_string": "African population genomics genetic diversity novel sequences"},
        {"name": "PROFILE 3: Cancer and Somatic Variant Calling",
         "description": "Somatic mutation discovery, variant calling benchmarks, and cancer precision genetics.",
         "query_string": "somatic variant calling cancer benchmarking mutation detection"},
        {"name": "PROFILE 4: Colorectal Cancer Genomics",
         "description": "Colorectal cancer driver genes, microsatellite instability, and clonal evolution.",
         "query_string": "colorectal cancer somatic mutations MSI clonal evolution"},
        {"name": "PROFILE 5: Tumour Mutational Burden",
         "description": "TMB calculation methods, immunotherapy response prediction, and biomarker validation.",
         "query_string": "tumour mutational burden TMB immunotherapy biomarker"},
        {"name": "PROFILE 6: Functional Genomics",
         "description": "Transcriptomics, single-cell RNA-seq, and regulatory variant annotation.",
         "query_string": "functional genomics transcriptomics single-cell gene regulation"},
        {"name": "PROFILE 7: Genome Assembly and Alignment",
         "description": "Long-read assembly algorithms, graph alignment, and haplotype resolution.",
         "query_string": "genome assembly long-read haplotype resolved minimap2"},
        {"name": "PROFILE 8: Bioinformatics Methods",
         "description": "Reproducible computational pipelines, workflow automation, and benchmarking standards.",
         "query_string": "bioinformatics variant benchmarking reproducible workflow"},
        {"name": "PROFILE 9: Pathogen Genomics",
         "description": "Bacterial and viral molecular surveillance, antimicrobial resistance, and outbreak tracking.",
         "query_string": "pathogen viral bacterial genomics molecular surveillance"},
        {"name": "PROFILE 10: Phylodynamics and Phylogeography",
         "description": "Molecular phylogenetics, Bayesian evolutionary analysis, and transmission dynamics.",
         "query_string": "phylodynamics phylogeography molecular evolution BEAST IQ-TREE"},
    ]

    for p in profiles:
        db.add(SearchProfile(**p, filter_open_access=False, is_active=True))
    db.flush()


def seed_bioinformatics_tools(db):
    if db.query(BioinformaticsTool).count() > 0:
        return

    tools = [
        {
            "name": "Hifiasm",
            "category": "Genome assembly",
            "description": "De novo haplotype-resolved assembler for PacBio HiFi reads and ultra-long Oxford Nanopore data.",
            "application": "Diploid and polyploid genome assembly, telomere-to-telomere human pangenome assemblies.",
            "input_formats": "FASTQ, FASTA",
            "sequencing_tech": "PacBio HiFi, Oxford Nanopore, Hi-C",
            "algorithms": "String graph, haplotype phasing using heterozygous bubbles and Hi-C links",
            "github_url": "https://github.com/chhylp123/hifiasm",
            "doc_url": "https://hifiasm.readthedocs.io/",
            "associated_doi": "10.1038/s41592-020-01053-z",
            "advantages": "Ultra-fast, produces phased dual assemblies with high contiguity and low switch error.",
            "limitations": "Requires high-accuracy long reads (HiFi >99% accuracy) for optimal phasing.",
            "learning_status": "Proficient",
            "personal_experience": "Standard assembler for constructing phased individual assemblies in pangenome projects."
        },
        {
            "name": "Flye",
            "category": "Genome assembly",
            "description": "De novo assembler for long and noisy reads produced by PacBio and Oxford Nanopore.",
            "application": "Assembly of complex repeat-rich genomes, metagenomes, and viral/bacterial genomes.",
            "input_formats": "FASTQ, FASTA",
            "sequencing_tech": "Oxford Nanopore, PacBio CLR/HiFi",
            "algorithms": "Disjointigs generation and repeat graph resolution",
            "github_url": "https://github.com/fenderglass/Flye",
            "doc_url": "https://github.com/fenderglass/Flye/blob/flye/docs/USAGE.md",
            "associated_doi": "10.1038/s41587-019-0286-x",
            "advantages": "Handles heterogeneous read lengths and uneven coverage exceptionally well.",
            "limitations": "Base error rate in unpolished draft requires subsequent Medaka or Polishing.",
            "learning_status": "Learning",
            "personal_experience": "Utilised for assembling microbial and viral test isolates."
        },
        {
            "name": "Minigraph-Cactus",
            "category": "Graph genome analysis",
            "description": "Pangenome pipeline combining minigraph structural variation graphs with Cactus base-level alignments.",
            "application": "Constructing reference pangenome graphs from multiple phased human assemblies.",
            "input_formats": "FASTA (assemblies), GFA",
            "sequencing_tech": "PacBio HiFi, ONT Assemblies",
            "algorithms": "Minigraph graph mapping followed by progressive cactus whole-genome alignment",
            "github_url": "https://github.com/ComparativeGenomicsToolkit/cactus",
            "doc_url": "https://github.com/ComparativeGenomicsToolkit/cactus/blob/master/doc/pangenome.md",
            "associated_doi": "10.1038/s41587-023-01793-w",
            "advantages": "Retains base-level sequence precision inside graph nodes without combinatorial explosion.",
            "limitations": "Computationally intensive; requires high-memory compute clusters for 90+ human haplotypes.",
            "learning_status": "Learning",
            "personal_experience": "Crucial method for PhD research on population-specific pangenomes."
        },
        {
            "name": "VG (Variation Graph toolkit)",
            "category": "Graph genome analysis",
            "description": "Comprehensive toolkit for creating, manipulating, and mapping to variation graphs.",
            "application": "Graph indexing, read mapping to pangenomes, calling structural variants against graph references.",
            "input_formats": "FASTA, VCF, GFA, GBZ, GAM, BAM",
            "sequencing_tech": "Illumina, PacBio, ONT",
            "algorithms": "Generalized de Bruijn and bidirected sequence graphs, distance index mapping (Giraffe)",
            "github_url": "https://github.com/vgteam/vg",
            "doc_url": "https://github.com/vgteam/vg/wiki",
            "associated_doi": "10.1038/s41587-020-00740-8",
            "advantages": "Removes reference allele bias when aligning short reads to diverse populations.",
            "limitations": "Steep learning curve; substantial memory footprint during index creation.",
            "learning_status": "Learning",
            "personal_experience": "Testing Giraffe for aligning short reads to African pangenome graphs."
        },
        {
            "name": "minimap2",
            "category": "Read alignment",
            "description": "Versatile sequence alignment program for long DNA/RNA reads, short reads, and assembly-to-assembly alignment.",
            "application": "Mapping long reads, full-length cDNA/direct RNA, and whole-genome synteny.",
            "input_formats": "FASTQ, FASTA",
            "sequencing_tech": "PacBio, Oxford Nanopore, Illumina",
            "algorithms": "Minimizer sketching, chaining, and adaptive banded dynamic programming",
            "github_url": "https://github.com/lh3/minimap2",
            "doc_url": "https://lh3.github.io/minimap2/minimap2.html",
            "associated_doi": "10.1093/bioinformatics/bty191",
            "advantages": "De facto standard for long reads; dozens of times faster than older aligners with low memory.",
            "limitations": "Not designed for splicing graph construction without specific annotation options.",
            "learning_status": "Expert",
            "personal_experience": "Daily driver for read alignment and assembly validation."
        },
        {
            "name": "BWA-MEM",
            "category": "Read alignment",
            "description": "Burrows-Wheeler Aligner for mapping low-divergent DNA sequences against large reference genomes.",
            "application": "Standard short-read alignment for germline and somatic variant calling.",
            "input_formats": "FASTQ",
            "sequencing_tech": "Illumina",
            "algorithms": "BWT index, backward search, maximal exact matches (MEM) seeding and extension",
            "github_url": "https://github.com/lh3/bwa",
            "doc_url": "https://bio-bwa.sourceforge.net/bwa.shtml",
            "associated_doi": "10.1093/bioinformatics/btp324",
            "advantages": "Industry benchmark for Illumina sequencing in GATK Best Practices.",
            "limitations": "Suffers from reference bias in divergent or structurally rearranged loci.",
            "learning_status": "Expert",
            "personal_experience": "Foundation of standard cancer exome and whole genome sequencing pipelines."
        },
        {
            "name": "Bowtie2",
            "category": "Read alignment",
            "description": "Ultrafast and memory-efficient tool for aligning sequencing reads to long reference genomes.",
            "application": "Small-RNA alignment, ChIP-seq, ATAC-seq, and metagenomic profiling.",
            "input_formats": "FASTQ, FASTA",
            "sequencing_tech": "Illumina",
            "algorithms": "FM-Index, 2-bit Burrows-Wheeler Transform",
            "github_url": "https://github.com/BenLangmead/bowtie2",
            "doc_url": "https://bowtie-bio.sourceforge.net/bowtie2/manual.shtml",
            "associated_doi": "10.1038/nmeth.1923",
            "advantages": "Very fast for short reads (<100 bp), low RAM requirements.",
            "limitations": "Less effective for split-read structural variant alignment.",
            "learning_status": "Proficient",
            "personal_experience": "Used for functional genomics and epigenomic peak mapping."
        },
        {
            "name": "STAR",
            "category": "RNA-seq analysis",
            "description": "Spliced Transcripts Alignment to a Reference for ultrafast RNA-seq mapping.",
            "application": "Transcriptome alignment, splice junction discovery, chimeric RNA / fusion transcript detection.",
            "input_formats": "FASTQ",
            "sequencing_tech": "Illumina",
            "algorithms": "Sequential Maximum Mappable Seed search via suffix array, stitch alignment",
            "github_url": "https://github.com/alexdobin/STAR",
            "doc_url": "https://github.com/alexdobin/STAR/blob/master/doc/STARmanual.pdf",
            "associated_doi": "10.1093/bioinformatics/bts635",
            "advantages": "Accurately detects canonical and novel splice junctions and cancer fusion events.",
            "limitations": "High RAM footprint (requires ~32 GB RAM for human genome indexing).",
            "learning_status": "Proficient",
            "personal_experience": "Core aligner for RNA-seq and differential expression quantification."
        },
        {
            "name": "HISAT2",
            "category": "RNA-seq analysis",
            "description": "Graph-based alignment system for mapping RNA and DNA sequences.",
            "application": "Genotype-aware RNA-seq alignment and population-informed transcriptomics.",
            "input_formats": "FASTQ",
            "sequencing_tech": "Illumina",
            "algorithms": "Hierarchical Graph FM index (GFM)",
            "github_url": "https://github.com/DaehwanKimLab/hisat2",
            "doc_url": "https://daehwankimlab.github.io/hisat2/manual/",
            "associated_doi": "10.1038/s41587-019-0201-4",
            "advantages": "Significantly smaller index size (~4 GB) than STAR while supporting variant graphs.",
            "limitations": "Slightly slower than STAR on large high-throughput bulk cohorts.",
            "learning_status": "Learning",
            "personal_experience": "Testing for population-specific RNA-seq mapping."
        },
        {
            "name": "GATK (HaplotypeCaller & Mutect2)",
            "category": "Variant calling",
            "description": "Genome Analysis Toolkit for germline (HaplotypeCaller) and somatic (Mutect2) variant discovery.",
            "application": "Gold-standard germline SNV/indel calling and tumor-normal paired somatic variant detection.",
            "input_formats": "BAM, CRAM",
            "sequencing_tech": "Illumina, hybrid capture",
            "algorithms": "Local de novo assembly of haplotypes using active regions and PairHMM",
            "github_url": "https://github.com/broadinstitute/gatk",
            "doc_url": "https://gatk.broadinstitute.org/",
            "associated_doi": "10.1038/ng.806",
            "advantages": "Extensively validated benchmark; comprehensive filtering models and VCF annotation.",
            "limitations": "Computationally demanding; requires careful parameter tuning for low-frequency somatic clones.",
            "learning_status": "Proficient",
            "personal_experience": "Benchmark baseline for comparing colorectal cancer somatic variant callsets."
        },
        {
            "name": "DeepVariant",
            "category": "Variant calling",
            "description": "Deep learning-based variant caller that uses a convolutional neural network (CNN) to call SNVs and small indels.",
            "application": "High-accuracy variant discovery from Illumina, PacBio HiFi, and ONT sequencing.",
            "input_formats": "BAM, CRAM, FASTA",
            "sequencing_tech": "Illumina, PacBio HiFi, Oxford Nanopore, Ultima Genomics",
            "algorithms": "Pileup image generation + Inception-v3 CNN classification",
            "github_url": "https://github.com/google/deepvariant",
            "doc_url": "https://github.com/google/deepvariant/blob/r1.6/docs/README.md",
            "associated_doi": "10.1038/nbt.4235",
            "advantages": "Consistently tops PrecisionFDA challenges; robust across long-read sequencing technologies.",
            "limitations": "GPU acceleration highly recommended; primarily focused on germline calling.",
            "learning_status": "Proficient",
            "personal_experience": "Primary germline caller used for benchmarking HiFi assemblies and sample validation."
        },
        {
            "name": "Strelka2",
            "category": "Variant calling",
            "description": "Fast and accurate somatic and germline small variant caller optimized for WGS and WES.",
            "application": "Tumour-normal matched somatic SNV and indel detection in cancer genomics.",
            "input_formats": "BAM, CRAM",
            "sequencing_tech": "Illumina",
            "algorithms": "Mixture-model indel calling, tiered empirical Bayesian scoring",
            "github_url": "https://github.com/Illumina/strelka",
            "doc_url": "https://github.com/Illumina/strelka/blob/v2.9.x/docs/userGuide/README.md",
            "associated_doi": "10.1038/s41592-018-0051-x",
            "advantages": "Extremely fast runtime (fraction of GATK Mutect2 time) with high precision.",
            "limitations": "Development largely paused; limited native long-read support.",
            "learning_status": "Proficient",
            "personal_experience": "Integrated into cancer variant calling pipeline for rapid somatic profiling."
        },
        {
            "name": "bcftools",
            "category": "Variant annotation",
            "description": "Fast utilities for variant calling and manipulating VCF and BCF files.",
            "application": "Filtering, normalization, merging, consensus generation, and statistical summaries of VCFs.",
            "input_formats": "VCF, BCF, FASTA",
            "sequencing_tech": "Universal",
            "algorithms": "Multiallelic site decomposition, left-alignment of indels, Poisson-binomial likelihood",
            "github_url": "https://github.com/samtools/bcftools",
            "doc_url": "https://samtools.github.io/bcftools/bcftools.html",
            "associated_doi": "10.1093/gigascience/giab008",
            "advantages": "Blazingly fast C implementation; essential command-line utility for any bioinformatics pipeline.",
            "limitations": "Basic variant calling model less sophisticated than deep learning approaches.",
            "learning_status": "Expert",
            "personal_experience": "Used constantly for decomposing, normalizing, and filtering somatic callsets."
        },
        {
            "name": "VEP (Ensembl Variant Effect Predictor)",
            "category": "Variant annotation",
            "description": "Comprehensive functional annotation of genomic variants including coding consequences, regulatory motifs, and clinical impact.",
            "application": "Annotating SNVs, indels, and structural variants with SIFT, PolyPhen, ClinVar, and CADD scores.",
            "input_formats": "VCF, HGVS, variant list",
            "sequencing_tech": "Universal",
            "algorithms": "Transcript overlap mapping, HGVS nomenclature generation, cache-based consequence prediction",
            "github_url": "https://github.com/Ensembl/ensembl-vep",
            "doc_url": "https://www.ensembl.org/info/docs/tools/vep/index.html",
            "associated_doi": "10.1186/s13059-016-1024-5",
            "advantages": "Exhaustive transcript consequence mapping aligned with Ensembl and RefSeq models.",
            "limitations": "Large cache files (20-30 GB); requires optimization for million-variant callsets.",
            "learning_status": "Proficient",
            "personal_experience": "Key annotation engine for identifying deleterious mutations in colorectal cancer cohorts."
        },
        {
            "name": "SnpEff",
            "category": "Variant annotation",
            "description": "Genetic variant annotation and functional effect prediction toolbox.",
            "application": "Annotating VCF files with amino acid changes, codon effects, and loss-of-function predictions.",
            "input_formats": "VCF, BED",
            "sequencing_tech": "Universal",
            "algorithms": "Interval tree searching for transcript and exon coordinate intersections",
            "github_url": "https://github.com/pcingola/SnpEff",
            "doc_url": "https://pcingola.github.io/SnpEff/",
            "associated_doi": "10.4161/fly.19695",
            "advantages": "Faster execution than VEP with minimal disk footprint.",
            "limitations": "Slightly less customizable plugin ecosystem than Ensembl VEP.",
            "learning_status": "Proficient",
            "personal_experience": "Used for quick automated annotation passes during exploratory analysis."
        },
        {
            "name": "samtools",
            "category": "Read alignment",
            "description": "Fundamental suite of programs for interacting with high-throughput sequencing data (SAM, BAM, CRAM).",
            "application": "Sorting, indexing, flagstat calculation, depth calculation, alignment slicing, and CRAM compression.",
            "input_formats": "SAM, BAM, CRAM",
            "sequencing_tech": "Universal",
            "algorithms": "BGZF block compression, coordinate binning index (BAI, CSI)",
            "github_url": "https://github.com/samtools/samtools",
            "doc_url": "http://www.htslib.org/doc/samtools.html",
            "associated_doi": "10.1093/gigascience/giab007",
            "advantages": "Ubiquitous, rock-solid, core dependency of genomic computing.",
            "limitations": "None for standard SAM/BAM manipulation.",
            "learning_status": "Expert",
            "personal_experience": "Indispensable daily toolkit."
        },
        {
            "name": "IQ-TREE",
            "category": "Phylogenetics",
            "description": "Efficient software for phylogenomic inference using maximum likelihood.",
            "application": "Constructing species trees, viral/pathogen strain phylogenies, and testing substitution models.",
            "input_formats": "FASTA, PHYLIP, NEXUS",
            "sequencing_tech": "Universal sequence alignments",
            "algorithms": "ModelFinder automated model selection, ultrafast bootstrap approximation (UFBoot)",
            "github_url": "https://github.com/iqtree/iqtree2",
            "doc_url": "http://www.iqtree.org/doc/",
            "associated_doi": "10.1093/molbev/msaa015",
            "advantages": "Rapid ModelFinder integration; robust UFBoot provides honest branch support values in seconds.",
            "limitations": "Does not perform Bayesian temporal dating (requires TreeTime or BEAST).",
            "learning_status": "Learning",
            "personal_experience": "Applied to complementary phylogenomic tracking of viral cohorts."
        },
        {
            "name": "BEAST2",
            "category": "Phylodynamics",
            "description": "Cross-platform program for Bayesian phylogenetic analysis of molecular sequences using MCMC.",
            "application": "Estimating divergence times, phylodynamic population sizes (Skyline), and spatial spread.",
            "input_formats": "NEXUS, XML",
            "sequencing_tech": "Sequence alignments with temporal sampling metadata",
            "algorithms": "Markov Chain Monte Carlo (MCMC), relaxed molecular clock, coalescent and birth-death models",
            "github_url": "https://github.com/CompEvol/beast2",
            "doc_url": "https://www.beast2.org/",
            "associated_doi": "10.1371/journal.pcbi.1006650",
            "advantages": "Gold standard for estimating viral evolution rates and time to most recent common ancestor (tMRCA).",
            "limitations": "Computationally intensive; long runtimes for large alignments.",
            "learning_status": "To Learn",
            "personal_experience": "Targeted for complementary project examining pathogen transmission chains."
        },
        {
            "name": "Nextstrain",
            "category": "Phylodynamics",
            "description": "Open-source project to harness the scientific and public health potential of pathogen genome data.",
            "application": "Real-time pathogen evolution tracking, interactive web visualization of outbreaks (Auspice).",
            "input_formats": "FASTA sequences, TSV metadata",
            "sequencing_tech": "Illumina, Oxford Nanopore",
            "algorithms": "Augur bioinformatics pipeline (alignment, maximum-likelihood tree, TreeTime dating)",
            "github_url": "https://github.com/nextstrain",
            "doc_url": "https://docs.nextstrain.org/",
            "associated_doi": "10.1093/bioinformatics/bty407",
            "advantages": "Exceptional interactive visualization and automated workflow integration.",
            "limitations": "Requires strict metadata curation for date and location fields.",
            "learning_status": "Learning",
            "personal_experience": "Explored for visualizing pathogen phylodynamics alongside human genomic host variation."
        },
    ]

    for tool in tools:
        db.add(BioinformaticsTool(**tool))
    db.flush()


def seed_projects_and_tasks(db):
    if db.query(ResearchProject).count() > 0:
        return

    project = ResearchProject(
        title="PhD: Structural Variation and Pangenomic Architecture in Diverse Human Populations & Colorectal Cancer",
        description="Comprehensive PhD thesis investigating graph-based human pangenome representations to eliminate reference allele bias, resolve African population genetic diversity, and characterize somatic structural rearrangements in colorectal cancer.",
        status="Active",
        start_date=date(2025, 9, 1),
        target_end_date=date(2028, 8, 31)
    )
    db.add(project)
    db.flush()

    milestones = [
        Milestone(project_id=project.id, title="M1: Comprehensive Literature Review on Graph Pangenomes & Cancer Genomics", due_date=date(2026, 12, 15), status="In Progress"),
        Milestone(project_id=project.id, title="M2: Benchmarking Long-Read Assemblers & Graph Aligners (Hifiasm vs VG Giraffe)", due_date=date(2027, 4, 30), status="Pending"),
        Milestone(project_id=project.id, title="M3: Somatic Mutation Calling & TMB Quantification in Colorectal Cancer Cohort", due_date=date(2027, 10, 31), status="Pending"),
        Milestone(project_id=project.id, title="M4: Dissertation Submission & Final Defense", due_date=date(2028, 7, 31), status="Pending"),
    ]
    for m in milestones:
        db.add(m)

    tasks = [
        Task(project_id=project.id, title="Read 4 supervisor-assigned weekly papers on pangenomes and variant calling", description="Weekly literature review commitment; summarize methods and findings in GenomIQ reading tracker.", status="In progress", priority="High", due_date=date(2026, 11, 15)),
        Task(project_id=project.id, title="Benchmark Mutect2 vs Strelka2 on simulated cancer WGS reads", description="Assess sensitivity and specificity for low-frequency somatic SNVs (<5% allele fraction).", status="To do", priority="High", due_date=date(2026, 11, 25)),
        Task(project_id=project.id, title="Configure Minigraph-Cactus test pipeline on 5 African haplotypes", description="Evaluate structural variant discovery rate compared to linear GRCh38 alignment.", status="To do", priority="Medium", due_date=date(2026, 12, 5)),
        Task(project_id=project.id, title="Prepare progress presentation for supervisor committee meeting", description="Compile reading log, TMB benchmark preliminary results, and timeline updates.", status="To do", priority="Urgent", due_date=date(2026, 11, 20)),
        Task(project_id=project.id, title="Audit GATK Somatic Best Practices pipeline documentation", description="Document exact parameter flags used for tumor-normal filtering.", status="Completed", priority="Low", due_date=date(2026, 11, 5), completed_at=datetime(2026, 11, 5, 16, 0)),
    ]
    for t in tasks:
        db.add(t)
    db.flush()


def seed_monitored_entities(db):
    if db.query(MonitoredEntity).count() > 0:
        return

    entities = [
        MonitoredEntity(name="Hifiasm GitHub Releases", entity_type="github_repo", url="https://api.github.com/repos/chhylp123/hifiasm/releases", feed_or_repo="chhylp123/hifiasm", is_active=True),
        MonitoredEntity(name="VG Variation Graph Releases", entity_type="github_repo", url="https://api.github.com/repos/vgteam/vg/releases", feed_or_repo="vgteam/vg", is_active=True),
        MonitoredEntity(name="Minimap2 GitHub Releases", entity_type="github_repo", url="https://api.github.com/repos/lh3/minimap2/releases", feed_or_repo="lh3/minimap2", is_active=True),
        MonitoredEntity(name="Broad Institute GATK Releases", entity_type="github_repo", url="https://api.github.com/repos/broadinstitute/gatk/releases", feed_or_repo="broadinstitute/gatk", is_active=True),
        MonitoredEntity(name="bioRxiv Genomics RSS", entity_type="rss_feed", url="https://connect.biorxiv.org/biorxiv_xml.php?subject=genomics", feed_or_repo="biorxiv_genomics", is_active=True),
        MonitoredEntity(name="bioRxiv Bioinformatics RSS", entity_type="rss_feed", url="https://connect.biorxiv.org/biorxiv_xml.php?subject=bioinformatics", feed_or_repo="biorxiv_bioinformatics", is_active=True),
    ]
    for e in entities:
        db.add(e)
    db.flush()


def seed_starter_landmark_publications(db):
    """Seeds verified landmark publications in human pangenomics and cancer genomics."""
    if db.query(Publication).count() > 0:
        return

    papers = [
        {
            "title": "A draft human pangenome reference",
            "authors": "Liao, W. W., Asri, M., Ebler, J., Doerr, D., Haukness, M., et al. (Human Pangenome Reference Consortium)",
            "abstract": "Here the Human Pangenome Reference Consortium presents a first draft of the human pangenome reference. The pangenome reference includes 47 phased, diploid assemblies from a cohort of genetically diverse individuals (94 distinct haploid genomes). It adds 119 million base pairs of euchromatic polymorphic sequence and 1,115 gene duplications relative to the linear reference GRCh38, drastically decreasing reference allele bias in short-read alignment and variant discovery.",
            "doi": "10.1038/s41586-023-05896-x",
            "pmid": "37165242",
            "year": 2023,
            "publication_date": "2023-05-10",
            "journal": "Nature",
            "publication_type": "Journal Article",
            "keywords": "pangenome, graph genome, HPRC, structural variation, reference bias",
            "research_topics": "Human Pangenomics & Graph Genomes, Genome Assembly & Haplotype Phasing",
            "citation_count": 850,
            "is_open_access": True,
            "pdf_url": "https://www.nature.com/articles/s41586-023-05896-x.pdf",
            "publisher_url": "https://doi.org/10.1038/s41586-023-05896-x",
            "source_database": "Nature / Crossref",
            "relevance_score": 9.9,
            "reading_status": "Completed",
            "paper_category": "Landmark",
            "is_bookmarked": True
        },
        {
            "title": "Haplotype-resolved de novo assembly using phased assembly graphs with hifiasm",
            "authors": "Cheng, H., Concepcion, G. T., Feng, X., Zhang, H., Li, H.",
            "abstract": "We present hifiasm, an algorithm that generates haplotype-resolved de novo genome assemblies from PacBio high-fidelity (HiFi) reads and parental or chromosome-conformation (Hi-C) data. On benchmark human datasets, hifiasm produces contig N50s exceeding 50 Mb and resolves both maternal and paternal haplotypes with high accuracy, enabling routine reference-grade individual genome assembly.",
            "doi": "10.1038/s41592-020-01053-z",
            "pmid": "33526884",
            "year": 2021,
            "publication_date": "2021-02-01",
            "journal": "Nature Methods",
            "publication_type": "Journal Article",
            "keywords": "genome assembly, hifiasm, PacBio HiFi, haplotype phasing, algorithms",
            "research_topics": "Genome Assembly & Haplotype Phasing, Bioinformatics Pipelines & Benchmarking",
            "citation_count": 1250,
            "is_open_access": True,
            "pdf_url": "https://www.nature.com/articles/s41592-020-01053-z.pdf",
            "publisher_url": "https://doi.org/10.1038/s41592-020-01053-z",
            "source_database": "Nature Methods",
            "relevance_score": 9.7,
            "reading_status": "Reading",
            "paper_category": "Computational",
            "is_bookmarked": True
        },
        {
            "title": "A universal SNP and small-indel variant caller using deep neural networks",
            "authors": "Poplin, R., Chang, P. C., Alexander, D., Schwartz, S., Colthurst, T., et al.",
            "abstract": "Calling genetic variants with high accuracy is fundamental to sequencing studies. Here we present DeepVariant, a variant caller based on a deep convolutional neural network that calls single nucleotide polymorphisms and small insertions and deletions in aligned high-throughput sequencing reads by treating the task as image classification. DeepVariant outperforms standard state-of-the-art tools across multiple independent benchmarks.",
            "doi": "10.1038/nbt.4235",
            "pmid": "30247488",
            "year": 2018,
            "publication_date": "2018-09-24",
            "journal": "Nature Biotechnology",
            "publication_type": "Journal Article",
            "keywords": "DeepVariant, machine learning, deep learning, variant calling, CNN",
            "research_topics": "Bioinformatics Pipelines & Benchmarking, Cancer Somatic Variant Calling",
            "citation_count": 1400,
            "is_open_access": True,
            "pdf_url": "https://www.nature.com/articles/nbt.4235.pdf",
            "publisher_url": "https://doi.org/10.1038/nbt.4235",
            "source_database": "Nature Biotechnology",
            "relevance_score": 9.5,
            "reading_status": "Recommended",
            "paper_category": "Methodological",
            "is_bookmarked": True
        },
        {
            "title": "The somatic mutation landscape and genomic classifications of colorectal cancer",
            "authors": "Cancer Genome Atlas Network",
            "abstract": "We present comprehensive molecular characterisation of human colorectal carcinoma. Genome-scale analysis of 276 samples demonstrates that 16% of colorectal carcinomas are hypermutated, associated with either microsatellite instability (MSI) or somatic POLE exonuclease domain mutations. We identify recurrent somatic alterations in APC, TP53, SMAD4, PIK3CA, KRAS, ARID1A, SOX9, and FAM123B, and provide a framework for targeted therapeutic interventions.",
            "doi": "10.1038/nature11252",
            "pmid": "22810696",
            "year": 2012,
            "publication_date": "2012-07-18",
            "journal": "Nature",
            "publication_type": "Journal Article",
            "keywords": "colorectal cancer, TCGA, somatic mutations, hypermutation, MSI, driver genes",
            "research_topics": "Colorectal Cancer Genomics, Cancer Somatic Variant Calling",
            "citation_count": 5200,
            "is_open_access": True,
            "pdf_url": "https://www.nature.com/articles/nature11252.pdf",
            "publisher_url": "https://doi.org/10.1038/nature11252",
            "source_database": "Nature / TCGA",
            "relevance_score": 9.8,
            "reading_status": "Recommended",
            "paper_category": "Landmark",
            "is_bookmarked": True
        },
        {
            "title": "Tumor mutational burden as a biomarker for immunotherapy response across multiple cancer types",
            "authors": "Samstein, R. M., Lee, C. H., Shoushtari, A. N., Hellmann, M. D., Shen, R., et al.",
            "abstract": "Tumor mutational burden (TMB) has emerged as a potential predictive biomarker of response to immune checkpoint inhibitor (ICI) therapy. In this study of 1,662 patients with advanced cancer treated with ICI, higher somatic TMB (top 10% within each histology) was associated with improved overall survival across diverse cancer types including colorectal and lung adenocarcinoma.",
            "doi": "10.1038/s41588-018-0312-8",
            "pmid": "30643254",
            "year": 2019,
            "publication_date": "2019-01-14",
            "journal": "Nature Genetics",
            "publication_type": "Journal Article",
            "keywords": "tumour mutational burden, TMB, immune checkpoint inhibitor, overall survival, biomarkers",
            "research_topics": "Tumour Mutational Burden & Biomarkers, Colorectal Cancer Genomics",
            "citation_count": 2100,
            "is_open_access": True,
            "pdf_url": "https://www.nature.com/articles/s41588-018-0312-8.pdf",
            "publisher_url": "https://doi.org/10.1038/s41588-018-0312-8",
            "source_database": "Nature Genetics",
            "relevance_score": 9.4,
            "reading_status": "Recommended",
            "paper_category": "Core",
            "is_bookmarked": False
        },
        {
            "title": "The African Genome Variation Project shapes medical genetics in Africa",
            "authors": "Gurdasani, D., Carstensen, T., Tekola-Ayele, F., Pagani, L., Tachmazidou, I., et al.",
            "abstract": "We present the African Genome Variation Project (AGVP), which examined dense genotypic data and whole-genome sequences across sub-Saharan Africa. We discovered millions of previously unrecorded variants, high levels of genetic diversity, and variable patterns of linkage disequilibrium that demonstrate the necessity of African-specific reference panels and pangenomes for equitable genomic medicine.",
            "doi": "10.1038/nature13997",
            "pmid": "25470054",
            "year": 2015,
            "publication_date": "2015-01-15",
            "journal": "Nature",
            "publication_type": "Journal Article",
            "keywords": "African genomics, AGVP, genetic diversity, population genetics, linkage disequilibrium",
            "research_topics": "African Population Genomics, Human Pangenomics & Graph Genomes",
            "citation_count": 680,
            "is_open_access": True,
            "pdf_url": "https://www.nature.com/articles/nature13997.pdf",
            "publisher_url": "https://doi.org/10.1038/nature13997",
            "source_database": "Nature",
            "relevance_score": 9.6,
            "reading_status": "Accepted",
            "paper_category": "Foundational",
            "is_bookmarked": True
        }
    ]

    current_week = f"{date.today().year}-W{date.today().isocalendar()[1]:02d}"

    for p_data in papers:
        pub = Publication(**p_data)
        db.add(pub)
        db.flush()

        # Add reading record
        rec_status = pub.reading_status
        rr = ReadingRecord(
            publication_id=pub.id,
            status=rec_status,
            date_started=date.today() if rec_status in ["Reading", "Completed"] else None,
            date_completed=date.today() if rec_status == "Completed" else None,
            reading_duration_minutes=90 if rec_status == "Completed" else 30 if rec_status == "Reading" else 0,
            personal_notes="Seminal paper for PhD foundation. High priority methodological reference." if rec_status == "Completed" else "",
            main_findings="Outlines essential algorithmic and biological principles." if rec_status == "Completed" else "",
            important_methods="Graph genome indexing and haplotype-phased assembly." if "pangenome" in pub.title.lower() else "Somatic variant calling and filtering.",
            phd_relevance="Directly foundational to thesis chapters 1 and 2.",
            rating=5 if rec_status == "Completed" else 0
        )
        db.add(rr)

        # Seed weekly recommendation for the first 4 active items
        if pub.id in [1, 2, 3, 4]:
            rec = Recommendation(
                publication_id=pub.id,
                week_identifier=current_week,
                category="Core" if pub.id in [1, 4] else "Computational" if pub.id == 2 else "Methodological",
                recommendation_score=pub.relevance_score,
                selection_reason=f"Selected as a {pub.paper_category.lower()} reference directly aligning with your PhD focus on {pub.research_topics.split(',')[0]}.",
                targeted_interest=pub.research_topics.split(",")[0],
                phd_relevance=f"Provides critical benchmark evidence and biological ground truth for your dissertation analyses.",
                key_learnings_json=json.dumps([
                    "Understand algorithmic workflow and design choices.",
                    "Analyze benchmarking metrics and performance compared to previous baselines.",
                    "Identify limitations and potential extensions for your own PhD research questions."
                ]),
                status="Accepted" if rec_status in ["Accepted", "Reading", "Completed"] else "Pending"
            )
            db.add(rec)

    db.flush()
