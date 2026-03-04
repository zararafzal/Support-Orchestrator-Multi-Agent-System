import streamlit as st
import anthropic
import json
import re
import time
import csv
import math
from io import StringIO
from datetime import datetime
import random
from collections import Counter

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AutoLeaps · AI Support Orchestrator",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --bg:       #07090F;
  --s1:       #0C0F18;
  --s2:       #111520;
  --s3:       #181D2E;
  --border:   #1E2638;
  --text:     #CDD9E5;
  --muted:    #536070;
  --dim:      #7A8FA8;
  --brand:    #2563EB;
  --brand-b:  #0A1529;
  --triage:   #F59E0B;
  --triage-b: #201500;
  --faq:      #10B981;
  --faq-b:    #061A10;
  --escalate: #EF4444;
  --escalate-b:#200A0A;
  --crm:      #8B5CF6;
  --crm-b:    #130D24;
  --orch:     #3B82F6;
  --orch-b:   #091529;
  --resolved: #10B981;
  --pending:  #F59E0B;
  --escalated:#EF4444;
}

html, body, [class*="css"] {
  font-family: 'IBM Plex Sans', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1340px; }
[data-testid="stSidebar"] {
  background: var(--s1) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.2rem 1rem; }

.app-header {
  background: linear-gradient(135deg, #0C1020 0%, #0A1428 60%, #0D1525 100%);
  border: 1px solid var(--border);
  border-top: 2px solid var(--brand);
  border-radius: 12px;
  padding: 1.6rem 2rem;
  margin-bottom: 1rem;
  display: flex; align-items: center; justify-content: space-between;
}
.brand-logo { font-size: 1.6rem; font-weight: 800; color: #fff; letter-spacing: -0.5px; }
.brand-logo span { color: var(--brand); }
.brand-sub { font-size: 0.78rem; color: var(--muted); margin-top: 3px; }
.status-live {
  display: flex; align-items: center; gap: 7px;
  font-size: 0.75rem; font-weight: 600; color: var(--faq);
  background: var(--faq-b); border: 1px solid rgba(16,185,129,0.3);
  padding: 5px 14px; border-radius: 20px;
}
.dot-live { width:7px; height:7px; border-radius:50%; background:var(--faq); animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

.sys-desc {
  background: var(--s2);
  border: 1px solid var(--border);
  border-left: 3px solid var(--brand);
  border-radius: 10px;
  padding: 1.2rem 1.6rem;
  margin-bottom: 1.2rem;
}
.sys-desc-title { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--brand); margin-bottom: 10px; }
.sys-desc-body { font-size: 0.84rem; color: var(--dim); line-height: 1.75; }
.sys-desc-body strong { color: var(--text); }
.pipeline-flow { display: flex; align-items: center; gap: 6px; margin-top: 12px; flex-wrap: wrap; }
.pipe-step {
  display: flex; align-items: center; gap: 5px;
  background: var(--s3); border: 1px solid var(--border);
  border-radius: 6px; padding: 5px 10px;
  font-size: 0.72rem; font-weight: 600;
}
.pipe-arrow { color: var(--muted); font-size: 0.8rem; }

.agent-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 1.2rem; }
.agent-card { border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; background: var(--s1); }
.agent-card.triage  { border-top: 2px solid var(--triage); }
.agent-card.rag     { border-top: 2px solid var(--orch); }
.agent-card.escalate{ border-top: 2px solid var(--escalate); }
.agent-card.crm     { border-top: 2px solid var(--crm); }
.agent-name { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 3px; }
.agent-desc { font-size: 0.75rem; color: var(--muted); line-height: 1.5; }
.agent-status { font-size: 0.7rem; font-weight: 600; margin-top: 7px; display: flex; align-items: center; gap: 5px; }

.rag-badge {
  display: inline-flex; align-items: center; gap: 5px;
  background: var(--brand-b); border: 1px solid rgba(37,99,235,0.4);
  border-radius: 20px; padding: 3px 10px;
  font-size: 0.68rem; font-weight: 700; color: var(--orch);
  text-transform: uppercase; letter-spacing: 0.5px;
}
.rag-doc-item {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--s3); border: 1px solid var(--border); border-radius: 6px;
  padding: 6px 10px; margin-bottom: 4px; font-size: 0.75rem;
}

.sec-title {
  font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1.2px; color: var(--orch); margin-bottom: 8px;
  display: flex; align-items: center; gap: 8px;
}
.sec-title::after { content:""; flex:1; height:1px; background:var(--border); }

.trace-item { display:flex; gap:12px; padding:10px 0; border-bottom:1px solid var(--border); align-items:flex-start; }
.trace-item:last-child { border-bottom:none; }
.trace-icon { width:28px; height:28px; border-radius:6px; display:flex; align-items:center; justify-content:center; font-size:0.85rem; flex-shrink:0; margin-top:1px; }
.trace-body { flex:1; }
.trace-agent { font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:3px; }
.trace-text { font-size:0.84rem; color:var(--text); line-height:1.6; }
.trace-meta { font-size:0.7rem; color:var(--muted); margin-top:4px; }
.trace-time { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:var(--muted); flex-shrink:0; margin-top:6px; }

.outcome-box { border-radius:8px; padding:1.1rem 1.3rem; border:1px solid; margin-top:0.5rem; }
.outcome-resolved  { background:rgba(16,185,129,0.05); border-color:var(--resolved); }
.outcome-escalated { background:rgba(239,68,68,0.05);  border-color:var(--escalated); }
.outcome-pending   { background:rgba(245,158,11,0.05); border-color:var(--pending); }
.outcome-label { font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px; }
.outcome-response { font-size:0.88rem; line-height:1.75; color:var(--text); }

.crm-row { display:grid; grid-template-columns:90px 80px 80px 100px 1fr; gap:8px; padding:8px 10px; background:var(--s2); border:1px solid var(--border); border-radius:6px; margin-bottom:4px; font-size:0.78rem; align-items:center; }
.crm-row.header { background:var(--s3); font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:var(--muted); }

.pill { display:inline-block; padding:2px 8px; border-radius:20px; font-size:0.68rem; font-weight:700; }
.pill-p1  { background:rgba(239,68,68,0.12);  color:var(--escalate); border:1px solid rgba(239,68,68,0.4); }
.pill-p2  { background:rgba(245,158,11,0.12); color:var(--triage);   border:1px solid rgba(245,158,11,0.4); }
.pill-p3  { background:rgba(16,185,129,0.12); color:var(--faq);      border:1px solid rgba(16,185,129,0.4); }
.pill-res { background:rgba(16,185,129,0.12); color:var(--faq);      border:1px solid rgba(16,185,129,0.4); }
.pill-esc { background:rgba(239,68,68,0.12);  color:var(--escalate); border:1px solid rgba(239,68,68,0.4); }
.pill-pen { background:rgba(245,158,11,0.12); color:var(--triage);   border:1px solid rgba(245,158,11,0.4); }

.stat-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin-bottom:1.2rem; }
.stat-card { background:var(--s1); border:1px solid var(--border); border-radius:8px; padding:12px 14px; text-align:center; }
.stat-num { font-size:1.5rem; font-weight:700; color:var(--text); line-height:1.2; }
.stat-label { font-size:0.68rem; color:var(--muted); margin-top:3px; text-transform:uppercase; letter-spacing:0.5px; }

[data-testid="stTextArea"] textarea { background:var(--s2) !important; border:1px solid var(--border) !important; border-radius:8px !important; color:var(--text) !important; font-family:'IBM Plex Sans',sans-serif !important; }
[data-testid="stTextArea"] textarea:focus { border-color:var(--orch) !important; }
[data-testid="stSelectbox"] > div > div { background:var(--s2) !important; border:1px solid var(--border) !important; color:var(--text) !important; }
label, p { color:var(--dim) !important; }
[data-testid="stButton"] > button { background:linear-gradient(135deg,#1A3A7A,#2563EB) !important; color:#E8F0FA !important; border:1px solid rgba(59,130,246,0.5) !important; border-radius:8px !important; font-weight:600 !important; font-family:'IBM Plex Sans',sans-serif !important; }
[data-testid="stButton"] > button:hover { filter:brightness(1.15) !important; }
[data-testid="stDownloadButton"] > button { background:var(--s2) !important; color:var(--text) !important; border:1px solid var(--border) !important; border-radius:8px !important; }
[data-testid="stDownloadButton"] > button:hover { border-color:var(--orch) !important; color:var(--orch) !important; }
.slabel { font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--muted); margin-bottom:4px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# RAG ENGINE  —  pure-Python TF-IDF (no external vector DB required)
# ══════════════════════════════════════════════════════════════════════════════

def tokenize(text: str) -> list:
    tokens = re.findall(r"[a-z0-9']+", text.lower())
    return [t for t in tokens if len(t) > 2]

def build_tfidf_index(chunks: list) -> dict:
    N = len(chunks)
    if N == 0:
        return {"chunks": [], "vecs": [], "idf": {}}
    tf_list, df = [], Counter()
    for chunk in chunks:
        toks = tokenize(chunk)
        tf = Counter(toks)
        tf_list.append(tf)
        for term in set(toks):
            df[term] += 1
    idf = {t: math.log((N + 1) / (c + 1)) + 1 for t, c in df.items()}
    vecs = []
    for tf in tf_list:
        vec = {t: freq * idf.get(t, 1) for t, freq in tf.items()}
        norm = math.sqrt(sum(v ** 2 for v in vec.values())) or 1
        vecs.append({t: v / norm for t, v in vec.items()})
    return {"chunks": chunks, "vecs": vecs, "idf": idf}

def retrieve_chunks(query: str, index: dict, top_k: int = 5) -> list:
    if not index or not index.get("chunks"):
        return []
    q_tf = Counter(tokenize(query))
    q_vec = {t: freq * index["idf"].get(t, 1) for t, freq in q_tf.items()}
    q_norm = math.sqrt(sum(v ** 2 for v in q_vec.values())) or 1
    q_vec_n = {t: v / q_norm for t, v in q_vec.items()}
    scores = []
    for i, vec in enumerate(index["vecs"]):
        score = sum(q_vec_n.get(t, 0) * val for t, val in vec.items())
        scores.append((score, index["chunks"][i]))
    scores.sort(reverse=True, key=lambda x: x[0])
    return [s for s in scores[:top_k] if s[0] > 0.01]

def chunk_text(text: str, size: int = 400, overlap: int = 80) -> list:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        c = " ".join(words[i:i + size])
        if c.strip():
            chunks.append(c)
        i += size - overlap
    return chunks

def parse_file(uf) -> str:
    name = uf.name.lower()
    raw = uf.read()
    if name.endswith((".txt", ".md")):
        return raw.decode("utf-8", errors="ignore")
    elif name.endswith(".csv"):
        return raw.decode("utf-8", errors="ignore")
    elif name.endswith(".json"):
        try:
            return json.dumps(json.loads(raw.decode("utf-8", errors="ignore")), indent=2)
        except Exception:
            return raw.decode("utf-8", errors="ignore")
    elif name.endswith(".pdf"):
        text = raw.decode("latin-1", errors="ignore")
        return " ".join(re.findall(r"\(([^\)]{3,200})\)", text))
    return raw.decode("utf-8", errors="ignore")


# ══════════════════════════════════════════════════════════════════════════════
# AUTOLEAPS DEFAULT KNOWLEDGE BASE
# ══════════════════════════════════════════════════════════════════════════════

AUTOLEAPS_KB = """
=== AUTOLEAPS KNOWLEDGE BASE ===

ABOUT AUTOLEAPS:
AutoLeaps is an online automotive marketplace connecting private car buyers, sellers, lease holders, and dealerships across the UK and Ireland.

LISTINGS & VEHICLE SEARCH:
- Searching: Use filters on autoleaps.com — make, model, year, mileage, fuel type, price range, postcode radius.
- Listing a Car: Create a free account > My Garage > Add Listing. Include reg number, mileage, condition, photos (min 5). Takes up to 2 hours to go live.
- Featured Listings: £9.99/month. Appear at top of search results. Manage in My Listings > Upgrade.
- Expired Listings: Auto-expire after 90 days. Renew free in My Listings > Renew.
- Photo Requirements: Minimum 5 photos. Max 10MB per image. JPEG or PNG only.
- Vehicle History Check: Free basic HPI check included. Full HPI report £9.99.

BUYING A CAR:
- Making an Offer: Use "Make Offer" button. Seller notified by email and has 48h to respond.
- Buyer Protection: AutoLeaps Buyer Protection covers purchases via our secure payment portal up to £50,000.
- Financing / PCP: Available through partner lenders. Min deposit 10%, subject to credit check. APR from 6.9%.
- Secure Payment / Escrow: Recommended for all transactions. Funds held until buyer confirms vehicle received.

LEASING:
- Lease Transfers: AutoLeaps Lease Swap allows listing and taking over existing lease agreements. My Account > Lease Swap > Add.
- Lease Eligibility: New lease taker must pass credit check with original finance provider. AutoLeaps facilitates but does not guarantee approval.
- Lease Payments: Outstanding lease payments must be up to date to list for swap.
- Early Termination: Contact your finance provider directly.

ACCOUNT & BILLING:
- Subscription Plans: Free (3 listings/month), Standard (£4.99/mo, 10 listings), Pro Dealer (£49.99/mo, unlimited + analytics).
- Refund Policy: Subscription fees non-refundable once billing cycle begins. Listing upgrades refundable within 48h.
- Payment Methods: Visa, Mastercard, Amex, PayPal. Bank transfer for Pro Dealer accounts only.
- Invoice / VAT: Download at Account > Billing > Invoices. VAT receipts available for Pro Dealer accounts.
- Cancelling a Plan: Cancel anytime at Account > Subscription > Cancel. Access continues until end of billing period.

DEALERS & FLEET:
- Dealer Onboarding: Apply at autoleaps.com/dealers. Requires FCA number and proof of trading address. Approval 2–5 business days.
- Fleet Listings: Bulk upload up to 500 vehicles via CSV at Account > Fleet > Bulk Upload.
- Dealer Analytics: Available on Pro Dealer plan — views, leads, conversion data.
- Lead Management: Enquiries route to dealer CRM via email or webhook integration.

TRUST & SAFETY:
- Scam Prevention: AutoLeaps never asks for payment outside the platform. Report suspicious listings at autoleaps.com/report.
- ID Verification: All sellers must verify identity (driving licence or passport) before first sale completes.
- GDPR & Data: Data deletion requests at Account > Privacy > Delete My Data. Processed within 30 days.
- Fraud / Disputed Transactions: Contact trust@autoleaps.com immediately. Transaction frozen pending investigation.

TECHNICAL:
- App: Available on iOS 14+ and Android 10+. Download from App Store / Google Play.
- Listing Not Showing: Check My Listings. If "Under Review" allow up to 2h. Contact support if stuck.
- Notifications Not Working: Check app permissions > Settings > Notifications > AutoLeaps must be enabled.

ESCALATION TEAMS:
- Billing disputes, refund requests → Billing Team (response: 1 business day)
- Fraud, scam, disputed transactions → Trust & Safety Team (URGENT — response: 2h)
- Dealer onboarding, FCA verification → Dealer Success Team (response: 2 business days)
- Technical bugs, listing errors → Engineering Support (response: 4h)
- Legal, GDPR → Legal & Compliance Team (response: 5 business days)
- Lease transfer issues → Leasing Specialist Team (response: 1 business day)
"""


# ══════════════════════════════════════════════════════════════════════════════
# AGENT PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

TRIAGE_PROMPT = """You are the Triage Agent for AutoLeaps — an online automotive marketplace in the UK and Ireland.

Your ONLY job: analyse an incoming support ticket and output a structured triage assessment.

Return ONLY valid JSON, no preamble:
{
  "priority": "P1|P2|P3",
  "category": "Billing|Listing|Buying|Leasing|Dealer|Trust & Safety|Technical|Account|Other",
  "sentiment": "Frustrated|Neutral|Positive|Urgent",
  "customer_type": "Private Buyer|Private Seller|Dealer|Fleet Manager|Lease Holder|Unknown",
  "summary": "One sentence summary of the issue",
  "requires_human": true|false,
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of your triage decision"
}

Priority guide:
- P1: Fraud/scam suspected, disputed transaction, account compromised, money at risk, very angry customer
- P2: Listing not live, offer not received, billing error, lease swap blocked, dealer onboarding delayed
- P3: General how-to question, feature query, minor issue, positive or neutral sentiment"""

FAQ_PROMPT = """You are the FAQ Agent for AutoLeaps — an online automotive marketplace in the UK and Ireland.

You have access to the AutoLeaps knowledge base AND additional context retrieved from AutoLeaps' internal documents via RAG retrieval. Your job: determine if you can FULLY resolve the ticket and write a helpful response.

Retrieved Knowledge Base Context:
{kb}

Return ONLY valid JSON:
{{
  "can_resolve": true|false,
  "confidence": 0.0-1.0,
  "response": "Full customer-facing response if can_resolve=true, else empty string",
  "reason_cannot_resolve": "If can_resolve=false, explain why",
  "kb_sections_used": ["section names used"],
  "rag_used": true|false
}}

Rules:
- Only set can_resolve=true if you can FULLY answer from the provided context
- Response must be warm, professional, AutoLeaps-branded, and actionable
- Address customer by name if provided
- If any part requires account-level access, set can_resolve=false
- rag_used=true if you drew on the retrieved document chunks"""

ESCALATION_PROMPT = """You are the Escalation Routing Agent for AutoLeaps — an online automotive marketplace.

Route to the correct team, set SLA, and write a structured handoff note.

AutoLeaps Teams: Billing Team | Trust & Safety Team | Dealer Success Team | Engineering Support | Legal & Compliance Team | Leasing Specialist Team | Senior Customer Success

Return ONLY valid JSON:
{
  "escalate_to": "Team name",
  "internal_priority": "P1|P2|P3",
  "sla_hours": 2|4|24|48,
  "handoff_note": "Internal note — include context, what was attempted, recommended action",
  "customer_holding_message": "Warm, professional AutoLeaps-branded message to customer with next steps and timeline",
  "tags": ["tag1", "tag2"]
}"""

CRM_PROMPT = """You are the CRM Logger Agent for AutoLeaps — an online automotive marketplace.

Create a structured CRM log entry.

Return ONLY valid JSON:
{
  "ticket_id": "AL-{id}",
  "customer_intent": "One phrase describing what the customer wanted",
  "customer_type": "Private Buyer|Private Seller|Dealer|Fleet Manager|Lease Holder|Unknown",
  "resolution_type": "Resolved|Escalated|Pending",
  "resolution_summary": "1-2 sentence summary of outcome",
  "follow_up_required": true|false,
  "follow_up_action": "What follow-up is needed, if any",
  "csat_prediction": "Positive|Neutral|Negative",
  "tags": ["tag1", "tag2"],
  "internal_notes": "Notes useful for future agents or account managers"
}"""


# ══════════════════════════════════════════════════════════════════════════════
# AGENT RUNNER + ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

def run_agent(client, system_prompt: str, user_content: str, max_tokens: int = 900) -> dict:
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    raw = msg.content[0].text
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    return json.loads(raw)


def orchestrate(ticket: str, customer_name: str, api_key: str, rag_index: dict) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    result = {"ticket": ticket, "customer": customer_name, "trace": [], "timestamp": datetime.now().isoformat()}
    t0 = time.time()

    # Step 1 — Triage
    triage = run_agent(client, TRIAGE_PROMPT, f"Customer: {customer_name}\nTicket: {ticket}")
    result["triage"] = triage
    result["trace"].append({
        "agent": "TRIAGE AGENT", "color": "#F59E0B", "bg": "#201500", "icon": "🔍",
        "output": f"Priority: {triage['priority']}  ·  Category: {triage['category']}  ·  Customer type: {triage.get('customer_type','Unknown')}",
        "detail": triage.get("reasoning", ""),
        "ms": int((time.time() - t0) * 1000),
    })

    # Step 2 — RAG Retrieval
    rag_chunks_used, rag_used = [], False
    kb_context = AUTOLEAPS_KB
    if rag_index and rag_index.get("chunks"):
        query = f"{ticket} {triage.get('category','')} {triage.get('summary','')}"
        top_chunks = retrieve_chunks(query, rag_index, top_k=5)
        if top_chunks:
            rag_used = True
            rag_chunks_used = [c for _, c in top_chunks]
            kb_context = AUTOLEAPS_KB + "\n\n=== RETRIEVED FROM UPLOADED DOCUMENTS ===\n" + "\n\n---\n".join(rag_chunks_used)
    rag_detail = f"Retrieved {len(rag_chunks_used)} chunks from uploaded documents" if rag_used else "No uploaded documents — using default AutoLeaps KB"
    result["trace"].append({
        "agent": "RAG RETRIEVAL", "color": "#3B82F6", "bg": "#091529", "icon": "✦",
        "output": f"{'✓ ' + str(len(rag_chunks_used)) + ' relevant chunks retrieved from your knowledge base' if rag_used else '○ Using default AutoLeaps knowledge base'}",
        "detail": rag_detail,
        "ms": int((time.time() - t0) * 1000),
    })

    # Step 3 — FAQ Agent
    faq = run_agent(
        client,
        FAQ_PROMPT.format(kb=kb_context),
        f"Customer: {customer_name}\nTicket: {ticket}\nTriage: Category={triage['category']}, Priority={triage['priority']}, Customer type={triage.get('customer_type','Unknown')}",
        max_tokens=1200,
    )
    result["faq"] = faq
    if faq["can_resolve"]:
        result["trace"].append({
            "agent": "FAQ AGENT", "color": "#10B981", "bg": "#061A10", "icon": "📚",
            "output": f"✓ Resolved (confidence: {int(faq['confidence']*100)}%){' · RAG ✦' if rag_used else ''}",
            "detail": f"KB sections: {', '.join(faq.get('kb_sections_used', []))}",
            "ms": int((time.time() - t0) * 1000),
        })
    else:
        result["trace"].append({
            "agent": "FAQ AGENT", "color": "#10B981", "bg": "#061A10", "icon": "📚",
            "output": "✗ Cannot fully resolve — triggering escalation",
            "detail": faq.get("reason_cannot_resolve", ""),
            "ms": int((time.time() - t0) * 1000),
        })

    # Step 4 — Escalation
    if not faq["can_resolve"] or triage.get("requires_human"):
        esc = run_agent(
            client, ESCALATION_PROMPT,
            f"Customer: {customer_name}\nTicket: {ticket}\nTriage: priority={triage['priority']}, category={triage['category']}, sentiment={triage['sentiment']}, customer_type={triage.get('customer_type','Unknown')}\nFAQ result: could not resolve — {faq.get('reason_cannot_resolve','')}",
        )
        result["escalation"] = esc
        result["trace"].append({
            "agent": "ESCALATION AGENT", "color": "#EF4444", "bg": "#200A0A", "icon": "🚨",
            "output": f"→ Routing to: {esc['escalate_to']}  ·  SLA: {esc['sla_hours']}h",
            "detail": esc.get("handoff_note", ""),
            "ms": int((time.time() - t0) * 1000),
        })
        result["final_response"] = esc["customer_holding_message"]
        result["resolution_status"] = "Escalated"
    else:
        result["final_response"] = faq["response"]
        result["resolution_status"] = "Resolved"

    # Step 5 — CRM Logger
    ticket_id = f"AL-{random.randint(10000,99999)}"
    crm = run_agent(
        client,
        CRM_PROMPT.replace("{id}", str(random.randint(10000,99999))),
        f"Ticket ID: {ticket_id}\nCustomer: {customer_name}\nTicket: {ticket}\nTriage: {json.dumps(triage)}\nResolution status: {result['resolution_status']}\nFinal response: {result['final_response'][:200]}",
    )
    crm["ticket_id"] = ticket_id
    result["crm"] = crm
    result["trace"].append({
        "agent": "CRM LOGGER", "color": "#8B5CF6", "bg": "#130D24", "icon": "🗃️",
        "output": f"Logged: {ticket_id}  ·  CSAT: {crm['csat_prediction']}  ·  Follow-up: {'Yes' if crm['follow_up_required'] else 'No'}",
        "detail": crm.get("resolution_summary", ""),
        "ms": int((time.time() - t0) * 1000),
    })

    result["total_ms"] = int((time.time() - t0) * 1000)
    result["rag_used"] = rag_used
    result["rag_chunks_count"] = len(rag_chunks_used)
    return result


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

for key, default in [("crm_log", []), ("last_result", None), ("rag_index", {}), ("rag_docs", [])]:
    if key not in st.session_state:
        st.session_state[key] = default


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:1.2rem;">
      <div style="font-size:1.2rem;font-weight:800;color:#CDD9E5;letter-spacing:-0.3px;">🚗 AutoLeaps</div>
      <div style="font-size:0.72rem;color:#536070;margin-top:2px;">AI Support Orchestrator</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="slabel">🔑 Anthropic API Key</div>', unsafe_allow_html=True)
    api_key = st.text_input("", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
    if not api_key:
        st.warning("Add your API key to activate agents.")

    # RAG Upload
    st.markdown("---")
    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
      <span style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#536070;">📂 Knowledge Base</span>
      <span class="rag-badge">RAG</span>
    </div>
    <div style="font-size:0.74rem;color:#536070;margin-bottom:8px;line-height:1.5;">Upload your AutoLeaps SOPs, pricing docs, dealer policies, or any support runbooks. The FAQ agent will retrieve and use them automatically.</div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "", accept_multiple_files=True,
        type=["txt", "md", "csv", "json", "pdf"],
        label_visibility="collapsed",
    )

    if uploaded_files:
        existing = {d["name"] for d in st.session_state.rag_docs}
        added = 0
        for uf in uploaded_files:
            if uf.name not in existing:
                try:
                    text = parse_file(uf)
                    chunks = chunk_text(text)
                    st.session_state.rag_docs.append({"name": uf.name, "chunks": chunks})
                    added += 1
                except Exception as e:
                    st.error(f"Error: {uf.name} — {e}")
        if added:
            all_chunks = [c for d in st.session_state.rag_docs for c in d["chunks"]]
            st.session_state.rag_index = build_tfidf_index(all_chunks)
            st.success(f"✓ {added} doc(s) indexed into RAG")

    if st.session_state.rag_docs:
        total_chunks = sum(len(d["chunks"]) for d in st.session_state.rag_docs)
        st.markdown(f"""
        <div style="background:var(--brand-b);border:1px solid rgba(37,99,235,0.3);border-radius:8px;padding:8px 10px;margin-bottom:6px;">
          <div style="font-size:0.68rem;color:var(--orch);font-weight:700;margin-bottom:5px;">✦ RAG INDEX ACTIVE — {total_chunks} chunks</div>
        """, unsafe_allow_html=True)
        for doc in st.session_state.rag_docs:
            st.markdown(f"""
          <div class="rag-doc-item">
            <span style="color:var(--text);font-size:0.75rem;">📄 {doc['name'][:24]}{'…' if len(doc['name'])>24 else ''}</span>
            <span style="color:var(--muted);font-size:0.68rem;">{len(doc['chunks'])} chunks</span>
          </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear Knowledge Base", use_container_width=True):
            st.session_state.rag_docs = []
            st.session_state.rag_index = {}
            st.rerun()
    else:
        st.markdown("""
        <div style="background:var(--s2);border:1px dashed var(--border);border-radius:8px;padding:10px;text-align:center;">
          <div style="font-size:0.72rem;color:#3D4A5C;">No docs uploaded<br><span style="font-size:0.68rem;">Default AutoLeaps KB active</span></div>
        </div>""", unsafe_allow_html=True)

    # Demo tickets
    st.markdown("---")
    st.markdown('<div class="slabel">🎭 Demo Tickets</div>', unsafe_allow_html=True)
    DEMOS = {
        "😡 Double-Charged": "I was charged £49.99 twice this month for my Pro Dealer subscription — once on the 1st and again on the 3rd. I need the duplicate refunded immediately. I manage 30 listings and this is the second billing issue I've had.",
        "🚗 Listing Not Live": "I submitted my 2021 BMW 3 Series listing 6 hours ago with all required photos and it's still 'Under Review'. I have a serious buyer waiting and need this live today. What is causing the delay?",
        "❓ New Seller": "Hi, I'm new and want to sell my car privately. How do I create a listing? What photos do I need? Do I need to arrange the HPI check or does AutoLeaps do that?",
        "🔐 Fraud Suspected": "Someone made an offer on my car and is now asking me to proceed via a bank transfer outside AutoLeaps. They claim to be a verified AutoLeaps buyer. Is this legitimate? I haven't sent any money yet.",
        "🔄 Lease Transfer": "I want to swap my remaining 14-month Audi A3 lease. I found someone to take it over. How does the credit check work and what happens if they're declined? Who bears the cost?",
        "🏢 Dealer Approval": "I applied to become a verified dealer 4 days ago and uploaded my FCA registration and trading address. No response. We have 35 vehicles ready to list. How long does approval actually take?",
    }
    demo_choice = st.selectbox("Load a demo", ["(none)"] + list(DEMOS.keys()), label_visibility="collapsed")
    if demo_choice != "(none)":
        st.session_state["demo_ticket"] = DEMOS[demo_choice]

    st.markdown("---")
    st.markdown("""
    <div style="background:var(--s2);border:1px solid var(--border);border-radius:8px;padding:10px 12px;">
      <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#536070;margin-bottom:8px;">Pipeline</div>
      <div style="font-size:0.77rem;color:#7A8FA8;line-height:1.9;">
        <span style="color:#F59E0B;">①</span> Triage — classify &amp; prioritise<br>
        <span style="color:#3B82F6;">✦</span> RAG — retrieve relevant docs<br>
        <span style="color:#10B981;">②</span> FAQ — attempt resolution<br>
        <span style="color:#EF4444;">③</span> Escalation — route if needed<br>
        <span style="color:#8B5CF6;">④</span> CRM — log everything
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="font-size:0.68rem;color:#2A3347;text-align:center;">Built by Zarar Afzal · AI Product Manager</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN PAGE
# ══════════════════════════════════════════════════════════════════════════════

# Header
st.markdown("""
<div class="app-header">
  <div>
    <div class="brand-logo">Auto<span>Leaps</span> <span style="font-size:0.9rem;font-weight:400;color:#536070;">Support Intelligence</span></div>
    <div class="brand-sub">Multi-agent AI · Triage → RAG Retrieval → FAQ → Escalation → CRM · Real-time pipeline</div>
  </div>
  <div class="status-live"><div class="dot-live"></div>AGENTS ONLINE</div>
</div>
""", unsafe_allow_html=True)

# System description
rag_docs_count = len(st.session_state.rag_docs)
total_chunks_count = sum(len(d["chunks"]) for d in st.session_state.rag_docs)
rag_status_html = (
    f'<span class="rag-badge">✦ RAG ACTIVE — {total_chunks_count} chunks from {rag_docs_count} doc(s)</span>'
    if rag_docs_count else
    '<span style="font-size:0.72rem;color:#536070;background:var(--s3);border:1px solid var(--border);padding:3px 10px;border-radius:20px;font-weight:600;">Default AutoLeaps KB</span>'
)

st.markdown(f"""
<div class="sys-desc">
  <div class="sys-desc-title">⚙️ How This System Works</div>
  <div class="sys-desc-body">
    This is <strong>AutoLeaps' multi-agent AI support orchestration system</strong> — purpose-built for the UK and Ireland automotive marketplace. Every customer ticket is automatically processed through a <strong>5-stage intelligent pipeline</strong> powered by Claude, designed around AutoLeaps' specific customer types: private buyers, private sellers, dealers, fleet managers, and lease holders.
    <br><br>
    <strong>① Triage Agent</strong> — Reads the ticket and classifies priority (P1 critical / P2 standard / P3 low), support category (Billing, Listing, Leasing, Dealer, Trust &amp; Safety, etc.), customer sentiment, and customer type. Every ticket is understood in AutoLeaps context before any action is taken.
    <br><br>
    <strong>✦ RAG Retrieval</strong> — Searches your uploaded AutoLeaps documents — SOPs, pricing guides, dealer policies, escalation runbooks — using TF-IDF semantic matching to retrieve the most relevant content for each specific ticket. This grounds every response in <em>your actual policies and data</em>, not generic answers. Upload your docs in the sidebar to activate. {rag_status_html}
    <br><br>
    <strong>② FAQ Agent</strong> — Attempts to fully resolve the ticket using the retrieved knowledge. Tickets resolved automatically receive an instant, accurate, AutoLeaps-branded response — targeting ~60% deflection rate and removing routine tickets from the human queue entirely.
    <br><br>
    <strong>③ Escalation Agent</strong> — Routes unresolved or complex tickets to the correct AutoLeaps team (Billing, Trust &amp; Safety, Dealer Success, Leasing Specialists, Engineering, Legal) with a structured internal handoff note and a warm customer-facing holding message with realistic SLA timelines.
    <br><br>
    <strong>④ CRM Logger</strong> — Records every interaction with structured metadata including customer type, resolution outcome, CSAT prediction, follow-up flags, and tags — exportable as CSV for your CRM system.
  </div>
  <div class="pipeline-flow">
    <span class="pipe-step" style="color:#F59E0B;border-color:rgba(245,158,11,0.3);">🔍 Triage</span>
    <span class="pipe-arrow">→</span>
    <span class="pipe-step" style="color:#3B82F6;border-color:rgba(59,130,246,0.3);">✦ RAG Retrieval</span>
    <span class="pipe-arrow">→</span>
    <span class="pipe-step" style="color:#10B981;border-color:rgba(16,185,129,0.3);">📚 FAQ Resolution</span>
    <span class="pipe-arrow">→</span>
    <span class="pipe-step" style="color:#EF4444;border-color:rgba(239,68,68,0.3);">🚨 Escalation</span>
    <span class="pipe-arrow">→</span>
    <span class="pipe-step" style="color:#8B5CF6;border-color:rgba(139,92,246,0.3);">🗃️ CRM Logger</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Stats
total     = len(st.session_state.crm_log)
resolved  = sum(1 for t in st.session_state.crm_log if t.get("resolution_status") == "Resolved")
escalated = sum(1 for t in st.session_state.crm_log if t.get("resolution_status") == "Escalated")
rag_count = sum(1 for t in st.session_state.crm_log if t.get("rag_used"))
avg_ms    = int(sum(t.get("total_ms", 0) for t in st.session_state.crm_log) / max(total, 1))

st.markdown(f"""
<div class="stat-grid">
  <div class="stat-card"><div class="stat-num">{total}</div><div class="stat-label">Total Tickets</div></div>
  <div class="stat-card"><div class="stat-num" style="color:var(--faq);">{resolved}</div><div class="stat-label">Auto-Resolved</div></div>
  <div class="stat-card"><div class="stat-num" style="color:var(--escalate);">{escalated}</div><div class="stat-label">Escalated</div></div>
  <div class="stat-card"><div class="stat-num" style="color:var(--orch);">{rag_count}</div><div class="stat-label">RAG-Assisted</div></div>
  <div class="stat-card"><div class="stat-num" style="color:var(--dim);">{avg_ms if total else "—"}{'ms' if total else ''}</div><div class="stat-label">Avg. Process Time</div></div>
</div>
""", unsafe_allow_html=True)

# Agent cards
rag_active = bool(st.session_state.rag_docs)
rag_label = f"● Active — {total_chunks_count} chunks" if rag_active else "● Default AutoLeaps KB"
rag_color = "var(--orch)" if rag_active else "var(--muted)"

st.markdown(f"""
<div class="agent-grid">
  <div class="agent-card triage">
    <div class="agent-name" style="color:var(--triage);">🔍 Triage Agent</div>
    <div class="agent-desc">Classifies priority, category, sentiment, and customer type (buyer, seller, dealer, fleet, lease holder).</div>
    <div class="agent-status" style="color:var(--triage);">● Ready</div>
  </div>
  <div class="agent-card rag">
    <div class="agent-name" style="color:var(--orch);">✦ RAG + FAQ Agent</div>
    <div class="agent-desc">Retrieves relevant chunks from your uploaded docs via TF-IDF, then attempts full ticket resolution.</div>
    <div class="agent-status" style="color:{rag_color};">{rag_label}</div>
  </div>
  <div class="agent-card escalate">
    <div class="agent-name" style="color:var(--escalate);">🚨 Escalation Agent</div>
    <div class="agent-desc">Routes to the correct AutoLeaps team: Billing, Trust & Safety, Dealer, Leasing, Engineering, Legal.</div>
    <div class="agent-status" style="color:var(--escalate);">● Ready</div>
  </div>
  <div class="agent-card crm">
    <div class="agent-name" style="color:var(--crm);">🗃️ CRM Logger</div>
    <div class="agent-desc">Logs every interaction with customer type, CSAT prediction, follow-up flags, and exportable tags.</div>
    <div class="agent-status" style="color:var(--crm);">● Ready</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Ticket input
st.markdown('<div class="sec-title">📨 Submit Support Ticket</div>', unsafe_allow_html=True)
col_inp, col_meta = st.columns([3, 1])
with col_inp:
    default_ticket = st.session_state.pop("demo_ticket", "")
    ticket_text = st.text_area(
        "", value=default_ticket,
        placeholder="Paste a customer support ticket — or load a demo from the sidebar…",
        height=120, label_visibility="collapsed",
    )
with col_meta:
    customer_name = st.text_input("", placeholder="Customer name", label_visibility="collapsed")
    if not customer_name:
        customer_name = "Customer"
    submit_btn = st.button("⚡ Run Agent Pipeline", use_container_width=True)

# Run
if submit_btn:
    if not api_key:
        st.error("⚠️ Enter your Anthropic API key in the sidebar.")
    elif not ticket_text.strip():
        st.error("⚠️ Please enter a support ticket.")
    else:
        with st.spinner("🤖 AutoLeaps agents processing…"):
            try:
                result = orchestrate(ticket_text.strip(), customer_name, api_key, st.session_state.rag_index)
                st.session_state.last_result = result
                st.session_state.crm_log.append(result)
                st.rerun()
            except anthropic.AuthenticationError:
                st.error("❌ Invalid API key.")
            except anthropic.RateLimitError:
                st.error("❌ Rate limit hit. Wait a moment and retry.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# Result display
if st.session_state.last_result:
    r = st.session_state.last_result
    st.markdown("---")
    if r.get("rag_used"):
        st.markdown(f"""
        <div style="background:var(--brand-b);border:1px solid rgba(37,99,235,0.3);border-radius:8px;padding:8px 14px;margin-bottom:10px;display:flex;align-items:center;gap:10px;">
          <span class="rag-badge">✦ RAG</span>
          <span style="font-size:0.78rem;color:var(--dim);">FAQ agent used <strong style="color:var(--orch);">{r.get('rag_chunks_count',0)} retrieved chunks</strong> from your uploaded documents to answer this ticket.</span>
        </div>
        """, unsafe_allow_html=True)

    col_trace, col_out = st.columns([1, 1])
    with col_trace:
        st.markdown('<div class="sec-title">⚡ Agent Trace</div>', unsafe_allow_html=True)
        st.markdown('<div style="background:var(--s2);border:1px solid var(--border);border-radius:8px;padding:4px 12px;">', unsafe_allow_html=True)
        for step in r.get("trace", []):
            st.markdown(f"""
            <div class="trace-item">
              <div class="trace-icon" style="background:{step['bg']};color:{step['color']};">{step['icon']}</div>
              <div class="trace-body">
                <div class="trace-agent" style="color:{step['color']};">{step['agent']}</div>
                <div class="trace-text">{step['output']}</div>
                <div class="trace-meta">{step['detail']}</div>
              </div>
              <div class="trace-time">{step['ms']}ms</div>
            </div>""", unsafe_allow_html=True)
        st.markdown(f'<div style="padding:8px 0 4px;text-align:right;font-size:0.72rem;color:var(--muted);">Total: {r.get("total_ms",0)}ms</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_out:
        st.markdown('<div class="sec-title">💬 Outcome</div>', unsafe_allow_html=True)
        triage = r.get("triage", {})
        crm    = r.get("crm", {})
        status = r.get("resolution_status", "Pending")
        prio   = triage.get("priority", "P2")
        prio_cls = {"P1":"pill-p1","P2":"pill-p2","P3":"pill-p3"}.get(prio,"pill-p2")
        stat_cls = {"Resolved":"pill-res","Escalated":"pill-esc"}.get(status,"pill-pen")
        out_cls  = {"Resolved":"outcome-resolved","Escalated":"outcome-escalated"}.get(status,"outcome-pending")

        st.markdown(f"""
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;">
          <span class="pill {prio_cls}">{prio}</span>
          <span class="pill {stat_cls}">{status}</span>
          <span class="pill" style="background:var(--s3);color:var(--dim);border:1px solid var(--border);">{triage.get('category','')}</span>
          <span class="pill" style="background:var(--s3);color:var(--dim);border:1px solid var(--border);">{triage.get('customer_type','')}</span>
          <span class="pill" style="background:var(--s3);color:var(--dim);border:1px solid var(--border);">{triage.get('sentiment','')}</span>
        </div>
        <div class="outcome-box {out_cls}">
          <div class="outcome-label" style="color:{'var(--resolved)' if status=='Resolved' else 'var(--escalated)'};">
            {'✓ Auto-Resolved by FAQ Agent' if status=='Resolved' else '→ Escalated to Human Agent'}
          </div>
          <div class="outcome-response">{r.get('final_response','')}</div>
        </div>
        """, unsafe_allow_html=True)

        if crm:
            st.markdown(f"""
            <div style="margin-top:10px;background:var(--s2);border:1px solid var(--border);border-radius:8px;padding:10px 12px;">
              <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--crm);margin-bottom:6px;">🗃️ CRM Entry</div>
              <div style="font-size:0.78rem;color:var(--dim);line-height:1.8;">
                <b style="color:var(--text);">ID:</b> {crm.get('ticket_id','')} &nbsp;·&nbsp;
                <b style="color:var(--text);">CSAT:</b> {crm.get('csat_prediction','')} &nbsp;·&nbsp;
                <b style="color:var(--text);">Follow-up:</b> {'Required' if crm.get('follow_up_required') else 'None'}<br>
                <b style="color:var(--text);">Summary:</b> {crm.get('resolution_summary','')}<br>
                {'<b style="color:var(--text);">Action:</b> ' + crm.get('follow_up_action','') if crm.get('follow_up_required') else ''}
              </div>
              <div style="margin-top:6px;">{''.join(f'<span class="pill" style="background:var(--crm-b);color:var(--crm);border:1px solid rgba(139,92,246,0.3);margin:2px;">{t}</span>' for t in crm.get('tags',[]))}</div>
            </div>
            """, unsafe_allow_html=True)

        if status == "Escalated" and r.get("escalation"):
            esc = r["escalation"]
            st.markdown(f"""
            <div style="margin-top:10px;background:var(--escalate-b);border:1px solid rgba(239,68,68,0.3);border-radius:8px;padding:10px 12px;">
              <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--escalate);margin-bottom:6px;">🚨 Escalation Details</div>
              <div style="font-size:0.78rem;color:var(--dim);line-height:1.8;">
                <b style="color:var(--text);">Team:</b> {esc.get('escalate_to','')} &nbsp;·&nbsp;
                <b style="color:var(--text);">SLA:</b> {esc.get('sla_hours','')}h<br>
                <b style="color:var(--text);">Handoff:</b> {esc.get('handoff_note','')}
              </div>
            </div>
            """, unsafe_allow_html=True)

# CRM Log
if st.session_state.crm_log:
    st.markdown("---")
    st.markdown('<div class="sec-title">🗃️ CRM Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="crm-row header"><div>Ticket ID</div><div>Priority</div><div>Status</div><div>CSAT</div><div>Summary</div></div>', unsafe_allow_html=True)
    for entry in reversed(st.session_state.crm_log):
        crm_e  = entry.get("crm", {})
        tri_e  = entry.get("triage", {})
        st_e   = entry.get("resolution_status", "Pending")
        pr_e   = tri_e.get("priority", "P2")
        pc = {"P1":"pill-p1","P2":"pill-p2","P3":"pill-p3"}.get(pr_e,"pill-p2")
        sc = {"Resolved":"pill-res","Escalated":"pill-esc"}.get(st_e,"pill-pen")
        cc = {"Positive":"pill-res","Neutral":"pill-pen","Negative":"pill-esc"}.get(crm_e.get("csat_prediction",""),"pill-pen")
        rag_f = ' <span class="rag-badge" style="font-size:0.58rem;padding:1px 5px;">RAG</span>' if entry.get("rag_used") else ""
        st.markdown(f"""
        <div class="crm-row">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:var(--muted);">{crm_e.get('ticket_id','—')}{rag_f}</div>
          <div><span class="pill {pc}">{pr_e}</span></div>
          <div><span class="pill {sc}">{st_e}</span></div>
          <div><span class="pill {cc}">{crm_e.get('csat_prediction','—')}</span></div>
          <div style="font-size:0.77rem;color:var(--dim);">{crm_e.get('resolution_summary','')[:80]}{'…' if len(crm_e.get('resolution_summary',''))>80 else ''}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([2, 2, 5])
    with c1:
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(["Ticket ID","Customer","Priority","Category","Customer Type","Sentiment","Status","CSAT","RAG Used","Follow-up","Summary","Timestamp"])
        for e in st.session_state.crm_log:
            ce = e.get("crm",{}); te = e.get("triage",{})
            w.writerow([ce.get("ticket_id",""), e.get("customer",""), te.get("priority",""), te.get("category",""),
                        te.get("customer_type",""), te.get("sentiment",""), e.get("resolution_status",""),
                        ce.get("csat_prediction",""), "Yes" if e.get("rag_used") else "No",
                        ce.get("follow_up_required",""), ce.get("resolution_summary",""), e.get("timestamp","")])
        st.download_button("⬇️ Export CRM as CSV", buf.getvalue().encode(),
                           file_name=f"autoleaps_crm_{datetime.now().strftime('%Y%m%d')}.csv",
                           mime="text/csv", use_container_width=True)
    with c2:
        if st.button("🗑️ Clear Log", use_container_width=True):
            st.session_state.crm_log = []
            st.session_state.last_result = None
            st.rerun()

elif not st.session_state.last_result:
    st.markdown("""
    <div style="text-align:center;padding:3rem 2rem;">
      <div style="font-size:2.5rem;margin-bottom:0.8rem;">🚗</div>
      <div style="font-size:0.95rem;font-weight:600;color:#536070;margin-bottom:0.4rem;">AutoLeaps pipeline ready — no tickets processed yet</div>
      <div style="font-size:0.82rem;color:#2A3347;">Submit a ticket above or load a demo · Upload your docs in the sidebar to activate RAG</div>
    </div>
    """, unsafe_allow_html=True)
