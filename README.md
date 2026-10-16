# Deep Search Engine

A powerful AI Agent-based research system that leverages Claude AI for automated, intelligent information gathering and recursive self-improvement.

## Overview

Deep Search Engine is designed to enable AI agents to conduct comprehensive research through intelligent querying, multi-source analysis, and continuous refinement of search strategies. It implements a recursive feedback loop that improves search quality and relevance over iterations.

## Features

### 🤖 AI Agent-Based Research
- Leverages Claude AI agents for intelligent research coordination
- Multi-step reasoning and analysis capabilities
- Context-aware search strategy optimization

### 🔄 Recursive Self-Improvement
- Feedback loop mechanism for continuous enhancement
- Learns from previous search results
- Adapts search strategies based on relevance metrics
- Improves result quality with each iteration

### 📊 Comprehensive Analysis
- Multi-source information gathering
- Intelligent result filtering and ranking
- Evidence-based conclusion generation
- Detailed research reports with source citations

### ⚙️ Flexible Configuration
- Modular architecture for easy extension
- Configurable search parameters
- Customizable improvement strategies
- Support for multiple AI models

## Getting Started

### Prerequisites

- Python 3.9+
- Claude API key
- Dependencies listed in `requirements.txt`

### Installation

```bash
# Clone the repository
git clone https://github.com/hongkyukim/deep-search-engine.git
cd deep-search-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Claude API key
```

### Basic Usage

```python
from deep_search_engine import SearchAgent

# Initialize the agent
agent = SearchAgent(
    api_key="your-claude-api-key",
    model="claude-opus-4-1"
)

# Perform a search
results = agent.search(
    query="What are the latest developments in AI safety?",
    iterations=3,
    depth="comprehensive"
)

# Access results
print(results.summary)
print(results.sources)
print(results.confidence_score)
```

## Project Structure

```
deep-search-engine/
├── README.md
├── requirements.txt
├── .env.example
├── setup.py
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   └── search_agent.py
│   ├── search/
│   │   ├── __init__.py
│   │   ├── query_engine.py
│   │   └── result_processor.py
│   ├── improvement/
│   │   ├── __init__.py
│   │   ├── feedback_loop.py
│   │   └── strategy_optimizer.py
│   └── utils/
│       ├── __init__.py
│       └── config.py
└── tests/
    ├── __init__.py
    ├── test_agent.py
    └── test_search.py
```

## How It Works

### 1. Initial Query Processing
The agent receives a research query and breaks it down into sub-questions for more targeted searching.

### 2. Multi-Source Search
The search engine queries multiple sources and aggregates relevant information with quality scoring.

### 3. Analysis & Synthesis
Claude AI analyzes gathered information, identifies patterns, and synthesizes coherent findings.

### 4. Feedback & Improvement
The system evaluates result quality and automatically refines search strategies for the next iteration.

### 5. Report Generation
Comprehensive research reports are generated with citations, confidence scores, and recommendations.

## Configuration

Edit `.env` file to customize:

```env
# API Configuration
CLAUDE_API_KEY=your-api-key
CLAUDE_MODEL=claude-opus-4-1

# Search Configuration
MAX_SEARCH_ITERATIONS=5
SEARCH_TIMEOUT=300
RESULT_LIMIT=20

# Improvement Strategy
FEEDBACK_WEIGHT=0.7
NOVELTY_THRESHOLD=0.5
QUALITY_THRESHOLD=0.6
```

## Performance Metrics

The system tracks and reports:
- **Relevance Score**: How well results match the query
- **Novelty Score**: Uniqueness of findings
- **Confidence Score**: Reliability of conclusions
- **Coverage Score**: Breadth of sources considered
- **Iteration Improvement**: Quality enhancement over iterations

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: hongkyukim.kim@gmail.com

---

**Latest Update**: October 2026  
**Version**: 1.0.0  
**Status**: Active Development
