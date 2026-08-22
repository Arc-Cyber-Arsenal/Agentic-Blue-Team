<p align="center">
  <img src="https://raw.githubusercontent.com/Archsec-Emman/Agentic-Blue-Team/master/agentic%20blue%20team.png" alt="Agentic Blue Team Banner" width="400">
</p>

# Agentic Blue Team (ABT)

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com/)

**An agent-centric SOC platform that fuses local-LLM intelligence with a Security Incident Response Platform (SIRP) to automate alert triage, enrichment, and response — inside your own infrastructure.**

> **Credits:** ABT is a maintained fork of [funnywolf's ASP](https://asp.viperrtp.com/asf/ASF/Overview/) (MIT). All core architecture — the Django/LangGraph framework, module & playbook engines, plugin system, and SIRP integration — originates from that project. This fork fixes packaging, adds a one-command Docker deployment, smoke tests with CI, and graceful degradation when optional components are missing.

---

## Overview

Instead of a static dashboard, ABT orchestrates modular AI agents (powered by local LLMs) that continuously ingest alerts from your SIEM, enrich them with threat intelligence, and produce structured security records. A built-in SIRP manages cases, alerts, artifacts, and playbooks so analysts can trigger automated remediation or threat-hunting workflows in one click.

Everything is designed for local deployment: your data, models, and operations never leave your environment.

## Core Features

| Feature | Description |
|---------|-------------|
| **AI-driven analysis** | LangGraph agent templates using local LLMs analyze alerts, enrich data, and decide outcomes. |
| **Built-in SIRP** | Incident response platform for cases, alerts, artifacts, playbooks and knowledge. |
| **Automation pipeline** | Webhook ingestion (Splunk/Kibana) → Redis Streams → agent analysis → SIRP → playbooks. |
| **Extensible plugins** | Python plugins for Splunk, ELK, Qdrant, OTX, LLMs (Ollama/OpenAI-compatible), and more. |
| **Local-first** | Self-hosted; nothing leaves your environment. |

## Architecture

```
SIEM (Splunk/ELK) → Webhook → Redis Stream → AI Agents → SIRP → Playbooks
```

1. **Alert ingestion** — SIEM alerts arrive via the webhook receiver (`PLUGINS/Forwarder`).
2. **Stream processing** — Alerts land in Redis Streams (persistent, replayable queues).
3. **Agent analysis** — Modules in `MODULES/` consume streams; LangGraph agents reason over each alert.
4. **SIRP records** — Results become cases/alerts/artifacts in the SIRP worksheet backend.
5. **Response** — Analysts trigger `PLAYBOOKS/` for hunting, enrichment or remediation.

## Quick Start (Docker)

```bash
git clone https://github.com/Archsec-Emman/Agentic-Blue-Team.git
cd Agentic-Blue-Team

# 1. generate plugin configs from the shipped examples
python bootstrap.py            # or: cp PLUGINS/*/CONFIG.example.py → CONFIG.py

# 2. start redis + qdrant + web
docker compose up -d --build

# 3. open the app
open http://localhost:8000/
```

The web container runs Django migrations automatically. Redis Stack (streams + cache) and Qdrant (vector store) come up as part of the same compose project.

### Download embedding models

Knowledge-base search needs two local models (BM25 sparse + BGE reranker):

```bash
pip install -e .[dev]
python PLUGINS/Huggingface/download_model.py
```

Until they are present, the app boots normally with knowledge sync disabled.

### Configure an LLM

Edit `PLUGINS/LLM/CONFIG.py` (created by `bootstrap.py`) and point it at Ollama or any OpenAI-compatible endpoint. See comments in that file.

### Connect the SIRP backend

ABT stores cases/alerts/artifacts in a HAP/Nocoly-style worksheet platform. Set your instance URL, app key and sign in `PLUGINS/SIRP/CONFIG.py`. Without it, alert analysis runs but records are not persisted.

## Manual Setup (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e .

python bootstrap.py                                 # create CONFIG.py files
# start Redis Stack on localhost:6379 (see Docker/RedisStack/docker-compose.yml)

python manage.py migrate
python manage.py runserver 8000
```

Environment variable `REDIS_URL` overrides the default `redis://localhost:6379/`.

## Ingesting test alerts

Sample alert injectors live in `DATA/` (e.g. `NDR-Rule-05-Suspect-C2-Communication`). Point them at your Forwarder endpoint to watch the full pipeline react.

## Tests

```bash
python bootstrap.py
python manage.py check
python manage.py test tests -v 2     # needs Redis on localhost:6379
```

CI runs the same suite against a real Redis service on every push.

## License

MIT — see [LICENSE](LICENSE). Contains portions Copyright (c) 2025 funnywolf (upstream ASP) and Copyright (c) 2026 Archsec-Emman.
