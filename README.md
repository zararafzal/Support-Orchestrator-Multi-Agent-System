# 🤖 Multi-Agent Customer Support Orchestration System

> **4 specialised AI agents working in concert — Triage → FAQ → Escalation → CRM — to automate customer support at scale.**

Built by **Zarar Afzal** · AI Product Manager

---

## What It Does

A production-grade multi-agent orchestration system that processes customer support tickets through a pipeline of specialised agents:

| Agent | Role |
|---|---|
| 🔍 **Triage Agent** | Classifies priority (P1/P2/P3), category, sentiment. Flags human-required cases. |
| 📚 **FAQ Agent** | Attempts full resolution from a structured knowledge base. ~60% resolution rate. |
| 🚨 **Escalation Agent** | Routes unresolved tickets to the correct team with SLA, handoff notes, and holding message. |
| 🗃️ **CRM Logger** | Logs every interaction with structured data, tags, and CSAT prediction. |

**Shared orchestration layer** coordinates all agents, enforces fallback policies, and decides human handoff triggers.

---

## Features

- ⚡ Real-time agent trace — see each agent's reasoning as it runs
- 🎯 Priority & category classification with confidence scores
- 📚 Knowledge base-grounded FAQ resolution (no hallucination)
- 🚨 Team-specific escalation routing with SLA assignment
- 🗃️ Full CRM log with CSAT prediction and follow-up flags
- ⬇️ Export CRM log as CSV
- 6 pre-built demo tickets covering billing, technical, security, cancellation scenarios

---

## 🚀 Deploy in 2 Minutes (Free)

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: Multi-Agent Support Orchestrator"
git remote add origin https://github.com/YOUR_USERNAME/support-orchestrator.git
git branch -M main
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"New app"** → connect your GitHub repo
3. Main file: `app.py` → **Deploy**

Live at: `https://YOUR_USERNAME-support-orchestrator.streamlit.app`

---

## 🔑 API Key

Get a free Anthropic API key at **[console.anthropic.com](https://console.anthropic.com)**
Enter it in the sidebar when using the app.

**To pre-fill on Streamlit Cloud:**
- App Settings → Secrets → add:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

---

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| AI Agents | Claude Sonnet (Anthropic) |
| Orchestration | Python — sequential multi-agent pipeline |
| Language | Python 3.10+ |
| Deployment | Streamlit Cloud (free) |

---

## CV / Resume Description

> *"Product-managed the design and phased rollout of a multi-agent customer support system with specialised agents for triage, FAQ resolution, escalation routing, and CRM logging — coordinating across a shared orchestration layer. Defined inter-agent communication contracts, fallback policies, and human handoff triggers. Built in Python with Claude AI. Live demo available."*

**Keywords:** Multi-agent AI · Orchestration · Agentic AI · Customer support automation · LLMs · Python · Streamlit

---

## Agent Architecture

```
Incoming Ticket
      │
      ▼
┌─────────────┐
│ ORCHESTRATOR │  ← shared coordination layer
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ TRIAGE AGENT │  → priority, category, sentiment, human-flag
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FAQ AGENT  │  → attempt KB resolution
└──────┬──────┘
       │
   can_resolve?
   ┌───┴───┐
  YES      NO
   │        │
   ▼        ▼
 Send   ┌──────────────────┐
 Reply  │ ESCALATION AGENT │ → route to team, set SLA
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────┐
        │  CRM LOGGER  │ → structured log, CSAT prediction
        └──────────────┘
```

---

*Made with ☕ by Zarar Afzal · [linkedin.com/in/zararafzal](https://linkedin.com/in/zararafzal) · [github.com/zararafzal](https://github.com/zararafzal)*
