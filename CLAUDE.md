# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Evo-Flywheel (进化生物学学术飞轮)** is an AI-driven academic literature analysis system for evolutionary biology researchers. The system automatically collects the latest research papers from multiple sources, intelligently extracts key findings using LLMs, generates daily research reports, and provides semantic search capabilities.

### Current Status

This project is in the **planning/documentation phase**. No code has been written yet. Refer to `docs/` for comprehensive design documentation.

---

## Development Commands

Since this project is not yet implemented, these are the planned commands based on the PRD:

```bash
# Environment setup (planned)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the Streamlit web interface (planned)
streamlit run src/app.py

# Run FastAPI backend (planned)
uvicorn src.main:app --reload

# Manual trigger for RSS collection (planned)
python -m src.tasks.collect

# Run tests (planned)
pytest tests/

# Initialize database (planned)
python -m src.db.init
```

---

## Architecture Overview

### Dual Database Architecture

The system uses two complementary databases:

1. **SQLite** (`evo_flywheel.db`) - Structured data
   - Paper metadata (title, authors, abstract, DOI, journal, source)
   - AI analysis results (importance score, key findings, evolutionary mechanisms)
   - Daily reports, user feedback
   - RSS source configurations

2. **Chroma** (`chroma_db/`) - Vector embeddings
   - Semantic search for paper abstracts
   - Similar paper recommendations
   - Query embeddings for natural language search

Both databases are linked via `paper_id`. Chroma uses the same ID as SQLite for consistency.

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | FastAPI | REST API with auto-documentation |
| Frontend | Streamlit | Quick web interface without frontend expertise |
| Structured Data | SQLite | Zero-config single-file database |
| Vector Data | Chroma | Embedded vector database (duckdb+parquet) |
| Embeddings | sentence-transformers | Free local model (all-MiniLM-L6-v2) |
| LLM | 智谱 GLM-4.7 | Paper analysis (¥0.5/1M input, ¥2/1M output) |
| Scheduler | APScheduler | Daily automated tasks |
| RSS Parsing | feedparser | RSS feed parsing |

### Planned Directory Structure

```
evo-flywheel/
├── src/
│   ├── api/           # FastAPI endpoints
│   ├── db/            # SQLite models and operations
│   ├── vector/        # Chroma integration
│   ├── collectors/    # RSS/API data collection
│   ├── analyzers/     # LLM paper analysis
│   ├── reporters/     # Daily report generation
│   ├── scheduler/     # APScheduler tasks
│   └── app.py         # Streamlit entry point
├── tests/
├── config/
│   └── sources.yaml   # RSS source configurations
├── data/              # Generated data files
├── reports/           # Daily markdown reports
├── chroma_db/         # Vector database storage
└── evo_flywheel.db    # SQLite database
```

---

## Data Flow

```
1. Collection (Daily 09:00)
   RSS feeds + bioRxiv API
   → Deduplication (DOI/title)
   → Metadata extraction
   → Store in SQLite

2. Analysis
   New papers from SQLite
   → LLM (GLM-4.7) analysis
   → Extract: taxa, scale, method, findings, mechanism, score
   → Update SQLite

3. Vectorization
   New papers
   → Generate embeddings (sentence-transformers)
   → Store in Chroma with metadata

4. Search (On-demand)
   User query
   → Query embedding
   → Chroma similarity search
   → Hybrid: SQLite filters + Chroma ranking

5. Reporting
   Daily aggregation
   → Top papers by score
   → Markdown report template
   → Save to reports/
```

---

## Key Configuration Files

### RSS Sources (`config/sources.yaml`)

The system supports 30+ evolutionary biology journals. See `docs/rss.md` for the complete list. The MVP minimum is 7 sources:

**MVP Configuration:**
- arXiv q-bio.PE (Populations & Evolution)
- bioRxiv API (evolutionary_biology category)
- PLOS Computational Biology
- Methods in Ecology & Evolution
- Molecular Ecology
- Nature
- PLOS Biology

### Environment Variables (`.env`)

```bash
ZHIPU_API_KEY=your-zhipu-api-key
DATABASE_URL=sqlite:///evo_flywheel.db
CHROMA_PERSIST_DIR=./chroma_db
```

---

## LLM Analysis Schema

The system uses a structured prompt to extract evolutionary biology insights:

```python
ANALYSIS_SCHEMA = {
    "基础信息": {
        "研究物种": "Involved taxa/classification",
        "进化尺度": "Molecular/Individual/Population/Species",
        "研究方法": "Phylogenetic/Population Genetic/Experimental/Comparative"
    },
    "核心内容": {
        "关键发现": "3-5 key findings",
        "进化机制": "Natural selection/Genetic drift/Gene flow/Mutation",
        "创新性": "Theoretical/Methodological/Discovery innovation"
    },
    "价值评估": {
        "重要性评分": "0-100 score",
        "推荐理由": "1-2 sentences explaining value"
    }
}
```

---

## API Endpoints (Planned)

```
# Papers
GET    /api/papers                    # List papers with filters
GET    /api/papers/{id}               # Paper detail
POST   /api/papers/analyze            # Analyze single paper

# Semantic Search
GET    /api/search/semantic?q={query} # Semantic search
POST   /api/search/similar            # Find similar papers
GET    /api/search/hybrid             # Hybrid search (filters + semantic)

# Reports
GET    /api/reports/today             # Today's report
GET    /api/reports/{date}            # Report by date
POST   /api/reports/generate          # Manual generation

# Feedback
POST   /api/feedback                  # Submit rating/comment

# System
GET    /api/stats/overview            # System statistics
POST   /api/rss/fetch                 # Manual collection trigger
POST   /api/embeddings/rebuild        # Rebuild vector index
```

---

## Development Phases

See `docs/ROADMAP.md` for detailed 6-phase development plan (2-3 weeks MVP):

1. **Phase 0**: Project initialization (0.5d)
2. **Phase 1**: Data layer - SQLite + Chroma setup (2d)
3. **Phase 2**: Collection layer - RSS + bioRxiv API (2d)
4. **Phase 3**: Analysis layer - LLM integration (2d)
5. **Phase 4**: Search layer - Embeddings + semantic search (1.5d)
6. **Phase 5**: Presentation layer - Streamlit UI (3d)
7. **Phase 6**: Testing & optimization (2d)

---

## Performance Targets

| Operation | Target |
|-----------|--------|
| RSS collection | < 2 minutes |
| Single paper analysis | < 10 seconds |
| Batch analysis (30 papers) | < 5 minutes |
| Semantic search | < 1 second |
| Report generation | < 30 seconds |
| UI page load | < 3 seconds |

---

## Key Integration Notes

### bioRxiv API vs RSS

Use the **bioRxiv API** instead of RSS:
- RSS is protected by Cloudflare (requires JavaScript rendering)
- API returns structured JSON, supports date range and category filtering
- Endpoint: `https://api.biorxiv.org/details/biorxiv/{start}/{end}?category=evolutionary_biology`

### Chroma Embedded Mode

```python
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db"
))
```

### Hybrid Search Pattern

1. Use SQLite to filter by metadata (taxa, min_score, journal)
2. Use Chroma to rank by semantic similarity
3. Merge and return top-k results

---

## Reference Documentation

- `docs/PRD.md` - Complete product requirements (v1.2)
- `docs/ROADMAP.md` - Development roadmap with task breakdown
- `docs/rss.md` - 30+ evolutionary biology journal RSS sources
