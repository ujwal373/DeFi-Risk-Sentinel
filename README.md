# DeFi Risk Sentinel 🛡️

A multi-agent AI system for monitoring and evaluating risks in DeFi wallets and transactions using MeTTa-based logic, OpenAI explainability, and real-time interaction through ASI:One chat or Streamlit UI.

### 🔍 Features
- Real-time wallet risk scoring using rule-based reasoning
- Multi-agent architecture (Watcher → Analyzer → Aggregator → Reporter)
- Explainability via LLM (OpenAI GPT-based)
- Streamlit dashboard for live querying
- ASI-compliant `uAgent` with chat commands (`/risk`, `/explain`)
- Designed to integrate with Agentverse and SingularityNET's MeTTa knowledge graph

### 📦 Stack
- Python (FastAPI, uAgents, Streamlit)
- Pydantic, YAML-based MeTTa rule stubs
- OpenAI API (for natural-language reasoning)
- Agentverse-ready metadata + `.agent.toml`

### 🚀 Run Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run services (each in separate terminals)
uvicorn agents.aggregator.app:app --port 8001
uvicorn agents.analyzer.main:app --port 8003
uvicorn agents.reporter.app:app --port 8002
python agents/watcher/main.py
python agents/reporter_agent/reporter_agent.py

# Streamlit dashboard
cd streamlit_app
streamlit run dashboard.py
```

# Project in active development — soon integrating real on-chain data and dynamic user wallet input.