# GAVEL — Generative AI for Virtual Evaluation and Legal Assistance

**Accelerate legal workflows with AI-powered document intelligence, forensic verification, automated drafting, and precedent discovery.**

---

## Overview

GAVEL is a comprehensive AI toolkit built to transform how legal professionals handle document review, drafting, and research. By combining advanced language models with specialized legal agents, GAVEL automates time-consuming tasks while maintaining the rigor and precision required in legal practice.

### What GAVEL Does

- **Accelerates case review** by distilling lengthy judgments into structured summaries
- **Validates document authenticity** through forensic content analysis
- **Automates legal drafting** using multi-agent collaboration and templates
- **Discovers relevant precedents** by grounding searches in actual case law 

---

## Core Features

### 📄 Intelligent Summarizer
Transform verbose legal documents into actionable insights without losing critical details.

- **Structured Extraction:** Automatically identifies key facts, legal issues, holdings, and judicial reasoning
- **Entity Recognition:** Detects and normalizes parties, judges, courts, statutes, and legal concepts
- **Executive Summaries:** Generates concise overviews tailored for busy practitioners
- **Precedent Highlighting:** Surfaces citation-worthy principles and rulings

### 🔍 Forensic Verifier
Detect document tampering and assess authenticity through deep digital analysis.

- **Alteration Detection:** Identifies suspicious edits, metadata inconsistencies, and content modifications
- **Integrity Scoring:** Provides quantitative confidence ratings to prioritize manual review

### ✍️ Agentic Drafting
Convert requirements into polished legal documents through collaborative AI agents.

- **Multi-Agent Pipeline:** Coordinates specialized agents for drafting, reviewing, and validating
- **Compliance Checking:** Ensures adherence to procedural and substantive requirements

### 📚 Precedent Discovery
Find relevant case law through intelligent search grounding and citation matching.

- **Factual Similarity Matching:** Identifies cases with analogous fact patterns
- **Citation Verification:** Links results directly to source documents
- **Argument Anchoring:** Suggests citation placements for drafted briefs

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 16+ and npm (for frontend)
- API keys for Gemini and Serper (see Environment Variables section)

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/gavel.git
cd gavel
```

#### 2. Set Up Python Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

#### 4. Configure Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your preferred text editor and add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

**Important:** Never commit your `.env` file to version control. Verify it's listed in `.gitignore`.

---

## Running GAVEL

### Backend Agent Services

Each agent runs as an independent service. Start them in separate terminal windows:

**Summarizer Agent:**
```bash
cd agents/summarizer_workflow
python main.py
```

**Drafting Agent:**
```bash
cd agents/draft_helper
python main.py
```

**Forensic Verifier:**
```bash
cd agents/forgery_evidence_checker
python main.py
```

**Precedent Search Agent:**
```bash
cd agents/precedent_searcher
python main.py
```

### Frontend Application

Launch the development server:

```bash
cd frontend
npx vite
```

The application will be available at `http://localhost:3000` (default Vite port).

---

## Project Structure

```
gavel/
├── agents/
│   ├── draft_helper/           # Automated legal drafting agent
│   ├── forgery_evidence_checker/  # Document forensics and verification
│   ├── precedent_searcher/     # Case law discovery and matching
│   └── summarizer_workflow/    # Document summarization orchestration
├── frontend/                    # Web interface (React + Vite)
├── .env.example                 # Template for environment variables
├── .gitignore                   # Excludes sensitive files from git
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## API Keys and Services

### Gemini API (Google AI)
Used for core language model capabilities including summarization, entity extraction, and drafting.

**Get your key:** [Google AI Studio](https://makersuite.google.com/app/apikey)

### Serper API
Powers search grounding for precedent discovery and case law retrieval.

**Get your key:** [Serper.dev](https://serper.dev/)

---


## Security Notice

**Never commit sensitive information:**
- API keys and credentials belong in `.env` only
- Client data and case files should not be uploaded to public repositories
- Review `.gitignore` to ensure proper exclusions

---

## Developed by 
1. Anuradha Krishnan (Developer Frontend and Summarization Engine)
2. Gayathri Venkatesan (Developer Infrastructure and Agentic Drafting)
3. Sarath Rajan Senthilkumar (Team Lead and Precedent Copilot)
4. Vidhula Ganesh (Developer Infrastructure, ML and Forensic Verifier)


Built with care for the legal community. GAVEL is designed to augment, not replace, human legal expertise.
