---
title: Lumina Intelligent University Advisor
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Lumina: The Intelligent University Advisor
A production-grade Self-RAG advisory system built with LangGraph, Groq, and React.

## Features
- **Self-RAG Architecture**: Real-time reflection on retrieval relevance and hallucination detection.
- **High Performance**: Powered by Groq Llama 3.3 70B for near-instant reasoning.
- **Glassmorphic UI**: Transparent pipeline visualization showing the agent's internal reasoning steps.
- **Robust Knowledge Base**: Grounded in official university catalogs and policies.

## Environment Variables
To run this Space, you need to set the following secrets in your Space settings:
- `GROQ_API_KEY`: Your Groq API key.
- `TAVILY_API_KEY`: Your Tavily API key for web search fallback.
- `GOOGLE_API_KEY`: (Optional) If using Google Generative AI components.

## Local Development
```bash
# Install dependencies
pip install -r requirements.txt
cd university-advisor-ui && npm install && npm run build
cd ..

# Run the backend (it will serve the built UI from /static)
python self_rag_agent.py
```
