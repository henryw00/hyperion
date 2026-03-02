# Hyperion: AI-Powered Claims Similarity Engine

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Framework: Gradio](https://img.shields.io/badge/UI-Gradio-ff69b4.svg)](https://gradio.app/)

This project aligns unstructured insurance data with dense vector embeddings to construct a **semantic claims search engine**. By comparing incoming First Notice of Loss (FNOL) descriptions against a massive historical database, we discover the most contextually relevant precedents—with immediate implications for reserve accuracy, fraud detection, and investigation speed.

---

## Core Value Proposition

**Semantic context, not exact keyword matching, predicts claim relevance.**

| Search Modality | Handling of "Tenant fell on wet floor" vs "Customer slipped on spill" |
|-----------------|:---------------------------------------------------------------------|
| Legacy Keyword Search | **Missed Match** (Requires exact vocabulary overlap)           |
| Hyperion Vector Search | **Good Match** (Understands underlying semantic concept)      |

This allows adjusters to find relevant precedents without using exact phrasing or legacy systems. 
Hyperion reduces hours of manual database querying into a sub-second operation, standardizing claim outcomes across varying jurisdictions.

---

## The Problem & Our Approach

The industry standard evaluates new claims by looking at past cases. However, traditional searches using exact keywords or strict policy codes return either zero results or thousands of irrelevant false positives and requires a significant amount of manual work.  

Our approach: systematically map **n (default 1000)historical claims** into a dense vector space using NLP (`all-MiniLM-L6-v2`). 

We then combine this vector search with **dynamic metadata post-filtering** (Jurisdiction and Policy Type) to surface exact precedents. Finally, an **Opt-In Synthesis panel** generates an actionable investigation plan based strictly on the financial baselines and key factors of the user's selected matches.

---

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone [https://github.com/YOUR-USERNAME/hyperion.git](https://github.com/YOUR-USERNAME/hyperion.git)
cd hyperion

# Create and activate a virtual environment
python -m venv venv

# On macOS:
python3 -m venv venv

# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install core NLP and UI frameworks
pip install pandas gradio sentence-transformers scikit-learn
```

### 3. Generate the Dataset

Hyperion requires a foundational dataset to run. We use a local generator to create n (default 1000) synthetic historical claims, allowing you to stress-test the local embedding logic without needing external database credentials. Using the sample dataset also works fine. 

```bash
# Generates large_claims_data.json (~30MB)
python generate_data.py
```

### 4. Run the Pipeline

```bash
# Start the Hyperion Server
python app/app.py
```

> **Note:** Upon startup, the backend will load the JSON dataset and compute the vector embeddings in memory. A progress bar will display in the terminal. Once complete, it will output a local `127.0.0.1` URL.

---

## Technical Features

| Feature | Implementation | Notes |
|:--------|:---------------|:------|
| **Vector Search** | `sentence-transformers` | Sub-second latency via cosine similarity. |
| **Multi-Select Filters** | `pandas` `.isin()` | Post-filtering maintains vector index integrity. |
| **Data Synthesis** | Procedural Aggregation | Calculates min/max/mean exposures instantly. |
| **Adaptive UI** | `gradio` + Custom CSS | Full support for Light and Dark system modes. |

---

## Pipeline Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                            HYPERION ENGINE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1: DATA INGESTION & EMBEDDING                                        │
│  ───────────────────────────────────                                        │
│  • Load n (default = 1000) unstructured historical claims (JSON → Pandas)   │
│  • Concatenate descriptions + key factors for maximum context               │
│  • Encode text using all-MiniLM-L6-v2 transformer model                     │
│  → Output: In-memory dense vector matrix                                    │
│                                                                             │
│  Phase 2: SEMANTIC SEARCH & FILTERING                                       │
│  ────────────────────────────────────                                       │
│  • Encode new incoming First Notice of Loss (FNOL)                          │
│  • Compute cosine similarity against historical vector space                │
│  • Apply Pandas multi-select post-filters (Jurisdiction, Policy Type)       │
│  → Output: Top N semantically aligned historical precedents                 │
│                                                                             │
│  Phase 3: OPT-IN SYNTHESIS                                                  │
│  ─────────────────────────                                                  │
│  • Adjuster manually selects highly relevant cases from matches             │
│  • Engine aggregates financial baselines (minimum, maximum, mean)           │
│  • Procedural synthesis extracts common factors for investigation plan      │
│  → Output: Actionable Next-Steps Report & Recommendation                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```text
hyperion/
├── app.py                      # Core application: search backend + Gradio UI
├── generate_data.py            # Script to generate synthetic historical precedents
├── large_claims_data.json      # Output dataset (generated locally, do not commit)
├── README.md                   # Project documentation
└── .gitignore                  # Git tracking exclusions
```

---

## Usage Workflow

1. **Input:** Type or paste an unstructured claim description into the *New Claim (FNOL)* box.
2. **Filter:** (Optional) Apply parameters using the multi-select *Jurisdiction* and *Policy Type* dropdowns.
3. **Search:** Click **Find Contextual Precedents**.
4. **Expand:** Review the top matches. Click **Show More Cases** to load additional precedents.
5. **Synthesize:** Expand the **Advanced Synthesis Panel**, select the checkboxes for the most relevant precedents, and click **Generate Investigation Plan** to view aggregate financials and next steps.
