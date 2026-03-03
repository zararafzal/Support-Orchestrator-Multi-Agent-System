import streamlit as st
import anthropic
import json
import re
import time
import csv
from io import StringIO, BytesIO
from datetime import datetime
import random

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Support Orchestrator · Multi-Agent AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --bg:       #080B10;
  --s1:       #0E1219;
  --s2:       #141922;
  --s3:       #1C2333;
  --border:   #252D3D;
  --borderB:  #2E3A52;
  --text:     #CDD9E5;
  --muted:    #636E7B;
  --dim:      #8B9BB4;

  --triage:   #E8A838;
  --triage-b: #2D2010;
  --faq:      #45B17A;
  --faq-b:    #0D2018;
  --escalate: #E05C5C;
  --escalate-b:#2A0F0F;
  --crm:      #7C6FE0;
  --crm-b:    #1A1630;
  --orch:     #4FA8E8;
  --orch-b:   #0D1E30;
  --resolved: #45B17A;
  --pending:  #E8A838;
  --escalated:#E05C5C;
}

html, body, [class*="css"] {
  font-family: 'IBM Plex Sans', sans-serif !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1300px; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: var(--s1) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container { padding: 1.2rem 1rem; }

/* ── Header ── */
.app-header {
  background: linear-gradient(135deg, var(--s2) 0%, #0D1826 100%);
  border: 1px solid var(--border);
  border-top: 2px solid var(--orch);
  border-radius: 10px;
  padding: 1.6rem 2rem;
  margin-bottom: 1.5rem;
  display: flex; align-items: center; justify-content: space-between;
}
.app-header h1 {
  font-size: 1.5rem !important; font-weight: 700 !important;
  color: var(--text) !important; margin: 0 !important;
  letter-spacing: -0.3px;
}
.app-header p { color: var(--muted) !important; font-size: 0.82rem; margin: 4px 0 0; }
.status-live {
  display: flex; align-items: center; gap: 7px;
  font-size: 0.78rem; font-weight: 600; color: var(--faq);
  background: var(--faq-b); border: 1px solid var(--faq);
  padding: 4px 12px; border-radius: 20px;
}
.dot-live {
  width:7px; height:7px; border-radius:50%;
  background: var(--faq);
  animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ── Agent cards ── */
.agent-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 1.2rem; }
.agent-card {
  border: 1px solid var(--border);
  border-radius: 8px; padding: 12px 14px;
  background: var(--s1);
  transition: all 0.3s ease;
}
.agent-card.active { box-shadow: 0 0 14px rgba(79,168,232,0.15); }
.agent-card.triage  { border-top: 2px solid var(--triage); }
.agent-card.faq     { border-top: 2px solid var(--faq); }
.agent-card.escalate{ border-top: 2px solid var(--escalate); }
.agent-card.crm     { border-top: 2px solid var(--crm); }
.agent-name { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 3px; }
.agent-desc { font-size: 0.75rem; color: var(--muted); line-height: 1.5; }
.agent-status { font-size: 0.7rem; font-weight: 600; margin-top: 7px; display: flex; align-items: center; gap: 5px; }

/* ── Section titles ── */
.sec-title {
  font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1.2px; color: var(--orch); margin-bottom: 8px;
  display: flex; align-items: center; gap: 8px;
}
.sec-title::after { content:""; flex:1; height:1px; background:var(--border); }

/* ── Ticket trace ── */
.trace-item {
  display: flex; gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  align-items: flex-start;
}
.trace-item:last-child { border-bottom: none; }
.trace-icon {
  width: 28px; height: 28px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.85rem; flex-shrink: 0; margin-top: 1px;
}
.trace-body { flex: 1; }
.trace-agent { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px; }
.trace-text { font-size: 0.84rem; color: var(--text); line-height: 1.6; }
.trace-meta { font-size: 0.7rem; color: var(--muted); margin-top: 4px; }
.trace-time { font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; color: var(--muted); flex-shrink:0; margin-top:6px; }

/* ── Outcome box ── */
.outcome-box {
  border-radius: 8px; padding: 1.1rem 1.3rem;
  border: 1px solid; margin-top: 0.5rem;
}
.outcome-resolved  { background: rgba(69,177,122,0.06); border-color: var(--resolved); }
.outcome-escalated { background: rgba(224,92,92,0.06);  border-color: var(--escalated); }
.outcome-pending   { background: rgba(232,168,56,0.06); border-color: var(--pending); }
.outcome-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px; }
.outcome-response { font-size: 0.88rem; line-height: 1.7; color: var(--text); }

/* ── CRM table ── */
.crm-row {
  display: grid;
  grid-template-columns: 90px 80px 80px 100px 1fr;
  gap: 8px; padding: 8px 10px;
  background: var(--s2); border: 1px solid var(--border);
  border-radius: 6px; margin-bottom: 4px;
  font-size: 0.78rem; align-items: center;
}
.crm-row.header { background: var(--s3); font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--muted); }

/* ── Priority & status pills ── */
.pill { display:inline-block; padding:2px 8px; border-radius:20px; font-size:0.68rem; font-weight:700; }
.pill-p1  { background:rgba(224,92,92,0.15);  color:var(--escalate); border:1px solid var(--escalate); }
.pill-p2  { background:rgba(232,168,56,0.15); color:var(--triage);   border:1px solid var(--triage); }
.pill-p3  { background:rgba(69,177,122,0.15); color:var(--faq);      border:1px solid var(--faq); }
.pill-res { background:rgba(69,177,122,0.15); color:var(--faq);      border:1px solid var(--faq); }
.pill-esc { background:rgba(224,92,92,0.15);  color:var(--escalate); border:1px solid var(--escalate); }
.pill-pen { background:rgba(232,168,56,0.15); color:var(--triage);   border:1px solid var(--triage); }

/* ── Stats ── */
.stat-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:1.2rem; }
.stat-card {
  background:var(--s1); border:1px solid var(--border); border-radius:8px;
  padding:12px 14px; text-align:center;
}
.stat-num { font-size:1.6rem; font-weight:700; color:var(--text); line-height:1.2; }
.stat-label { font-size:0.7rem; color:var(--muted); margin-top:3px; text-transform:uppercase; letter-spacing:0.5px; }

/* ── Inputs ── */
[data-testid="stTextArea"] textarea {
  background:var(--s2) !important; border:1px solid var(--border) !important;
  border-radius:8px !important; color:var(--text) !important;
  font-family:'IBM Plex Sans',sans-serif !important;
}
[data-testid="stTextArea"] textarea:focus { border-color:var(--orch) !important; }
[data-testid="stSelectbox"] > div > div {
  background:var(--s2) !important; border:1px solid var(--border) !important; color:var(--text) !important;
}
label, p { color:var(--dim) !important; }

/* ── Buttons ── */
[data-testid="stButton"] > button {
  background: linear-gradient(135deg, #1A4A7A, #2563A8) !important;
  color: #E8F0FA !important; border: 1px solid var(--orch) !important;
  border-radius: 8px !important; font-weight: 600 !important;
  font-family: 'IBM Plex Sans', sans-serif !important;
}
[data-testid="stButton"] > button:hover { filter: brightness(1.15) !important; }
[data-testid="stDownloadButton"] > button {
  background: var(--s2) !important; color: var(--text) !important;
  border: 1px solid var(--border) !important; border-radius: 8px !important;
}
[data-testid="stDownloadButton"] > button:hover { border-color: var(--orch) !important; color: var(--orch) !important; }

/* ── Sidebar labels ── */
.slabel { font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--muted); margin-bottom:4px; }
</style>
""", unsafe_allow_html=True)


# ── Knowledge base (FAQ Agent's context) ─────────────────────────────────
KNOWLEDGE_BASE = """
=== PRODUCT KNOWLEDGE BASE ===

BILLING & PAYMENTS:
- Refund Policy: Full refunds within 14 days of purchase, no questions asked. After 14 days, pro-rated refunds only.
- Payment Methods: Visa, Mastercard, Amex, PayPal, bank transfer (enterprise only).
- Invoice Requests: Go to Account > Billing > Download Invoice. Can take 24h to generate.
- Failed Payments: Usually auto-retry within 24h. If persists, update card at Account > Billing.
- Subscription Cancellation: Can cancel anytime. Access continues until end of billing period.
- Pricing Plans: Starter ($29/mo), Pro ($79/mo), Enterprise (custom). Annual = 20% discount.

TECHNICAL ISSUES:
- Login Problems: Try password reset first. If SSO user, contact your IT admin.
- Slow Performance: Clear browser cache, try incognito mode. Check status.ourapp.com.
- Data Export: Settings > Data > Export. CSV/JSON available. Enterprise: SFTP available.
- API Rate Limits: Starter=100 req/min, Pro=1000 req/min, Enterprise=unlimited.
- Integrations: Slack, Jira, Salesforce, HubSpot natively. Zapier for others.
- Mobile App: iOS 14+ and Android 10+ supported. Download from respective app stores.

ACCOUNT MANAGEMENT:
- Password Reset: Login page > Forgot Password. Link valid 1 hour.
- 2FA Setup: Account > Security > Enable 2FA. Supports authenticator apps and SMS.
- Team Seats: Manage at Account > Team. Starter=1, Pro=5, Enterprise=unlimited.
- Data Privacy / GDPR: Data deletion request at Privacy > Delete My Data. Processed in 30 days.
- Single Sign-On: SAML 2.0 supported on Enterprise plan only.

ONBOARDING & USAGE:
- Getting Started: docs.ourapp.com/quickstart — takes ~15 minutes.
- Training / Webinars: Free weekly onboarding calls every Tuesday 2PM EST. Register at ourapp.com/webinars.
- Dedicated Support: Enterprise customers get a dedicated Customer Success Manager.
- SLA: Pro=99.9% uptime, response in 4h. Enterprise=99.99%, response in 1h. Starter=best effort.

ESCALATION TEAMS:
- Billing disputes > Billing Team
- Security incidents, data breaches > Security Team (URGENT)
- Enterprise account issues > Enterprise Success Team
- Technical bugs / outages > Engineering Tier-2
- Legal / compliance > Legal Team
- Abuse / ToS violations > Trust & Safety Team
"""


# ── Agent system prompts ──────────────────────────────────────────────────
TRIAGE_PROMPT = """You are the Triage Agent in a multi-agent customer support system.

Your ONLY job: analyse an incoming support ticket and output a structured triage assessment.

Return ONLY valid JSON, no preamble:
{
  "priority": "P1|P2|P3",
  "category": "Billing|Technical|Account|Onboarding|Security|Other",
  "sentiment": "Frustrated|Neutral|Positive|Urgent",
  "summary": "One sentence summary of the issue",
  "requires_human": true|false,
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of your triage decision"
}

Priority guide:
- P1: Service down, data loss, security incident, major billing error, very angry customer
- P2: Feature broken, billing question, account locked, moderate frustration
- P3: General question, how-to, minor issue, positive sentiment"""

FAQ_PROMPT = """You are the FAQ Agent in a multi-agent customer support system.

You have access to the product knowledge base. Your job: determine if you can FULLY resolve the ticket from the knowledge base, and if so, write the response.

Knowledge Base:
{kb}

Return ONLY valid JSON:
{{
  "can_resolve": true|false,
  "confidence": 0.0-1.0,
  "response": "Full customer-facing response if can_resolve=true, else empty string",
  "reason_cannot_resolve": "If can_resolve=false, explain why",
  "kb_sections_used": ["section names used"]
}}

Rules:
- Only set can_resolve=true if you can FULLY answer from the KB
- Response must be warm, professional, and actionable
- If any part of the question is outside the KB, set can_resolve=false"""

ESCALATION_PROMPT = """You are the Escalation Routing Agent in a multi-agent customer support system.

Your job: determine the correct team to escalate to, set priority/SLA, and write a structured internal handoff note.

Return ONLY valid JSON:
{
  "escalate_to": "Team name",
  "internal_priority": "P1|P2|P3",
  "sla_hours": 1|4|24|48,
  "handoff_note": "Internal note for the receiving team — include context, what was tried, and recommended action",
  "customer_holding_message": "Warm, professional message to send to customer explaining they'll be followed up",
  "tags": ["tag1", "tag2"]
}"""

CRM_PROMPT = """You are the CRM Logger Agent in a multi-agent customer support system.

Your job: create a structured CRM log entry for this ticket interaction.

Return ONLY valid JSON:
{
  "ticket_id": "TKT-{id}",
  "customer_intent": "One phrase describing what customer wanted",
  "resolution_type": "Resolved|Escalated|Pending",
  "resolution_summary": "1-2 sentence summary of outcome",
  "follow_up_required": true|false,
  "follow_up_action": "What follow-up is needed, if any",
  "csat_prediction": "Positive|Neutral|Negative",
  "tags": ["tag1", "tag2"],
  "internal_notes": "Any notes useful for future agents"
}"""


# ── Agent caller ──────────────────────────────────────────────────────────
def run_agent(client, agent_name, system_prompt, user_content, max_tokens=800):
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    raw = msg.content[0].text
    raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
    return json.loads(raw)


def orchestrate(ticket: str, customer_name: str, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    result = {"ticket": ticket, "customer": customer_name, "trace": [], "timestamp": datetime.now().isoformat()}
    t0 = time.time()

    # ── Step 1: Triage ──
    triage = run_agent(client, "Triage", TRIAGE_PROMPT, f"Ticket: {ticket}")
    result["triage"] = triage
    result["trace"].append({
        "agent": "TRIAGE AGENT",
        "color": "#E8A838", "bg": "#2D2010",
        "icon": "🔍",
        "output": f"Priority: {triage['priority']}  ·  Category: {triage['category']}  ·  Sentiment: {triage['sentiment']}",
        "detail": triage.get("reasoning",""),
        "ms": int((time.time()-t0)*1000),
    })

    # ── Step 2: FAQ attempt ──
    faq_system = FAQ_PROMPT.format(kb=KNOWLEDGE_BASE)
    faq_user   = f"Ticket: {ticket}\n\nTriage context: Category={triage['category']}, Priority={triage['priority']}"
    faq = run_agent(client, "FAQ", faq_system, faq_user, max_tokens=1000)
    result["faq"] = faq
    if faq["can_resolve"]:
        result["trace"].append({
            "agent": "FAQ AGENT",
            "color": "#45B17A", "bg": "#0D2018",
            "icon": "📚",
            "output": f"✓ Resolved from knowledge base (confidence: {int(faq['confidence']*100)}%)",
            "detail": f"KB sections used: {', '.join(faq.get('kb_sections_used',[]))}",
            "ms": int((time.time()-t0)*1000),
        })
    else:
        result["trace"].append({
            "agent": "FAQ AGENT",
            "color": "#45B17A", "bg": "#0D2018",
            "icon": "📚",
            "output": f"✗ Cannot resolve from KB — triggering escalation",
            "detail": faq.get("reason_cannot_resolve",""),
            "ms": int((time.time()-t0)*1000),
        })

    # ── Step 3: Escalation (if FAQ can't resolve or requires human) ──
    if not faq["can_resolve"] or triage.get("requires_human"):
        esc_user = f"""Ticket: {ticket}
Triage: priority={triage['priority']}, category={triage['category']}, sentiment={triage['sentiment']}
FAQ result: could not resolve — {faq.get('reason_cannot_resolve','')}"""
        esc = run_agent(client, "Escalation", ESCALATION_PROMPT, esc_user)
        result["escalation"] = esc
        result["trace"].append({
            "agent": "ESCALATION AGENT",
            "color": "#E05C5C", "bg": "#2A0F0F",
            "icon": "🚨",
            "output": f"→ Routing to: {esc['escalate_to']}  ·  SLA: {esc['sla_hours']}h",
            "detail": esc.get("handoff_note",""),
            "ms": int((time.time()-t0)*1000),
        })
        result["final_response"]    = esc["customer_holding_message"]
        result["resolution_status"] = "Escalated"
    else:
        result["final_response"]    = faq["response"]
        result["resolution_status"] = "Resolved"

    # ── Step 4: CRM Logger ──
    ticket_id = f"TKT-{random.randint(10000,99999)}"
    crm_user = f"""Ticket ID: {ticket_id}
Customer: {customer_name}
Ticket: {ticket}
Triage: {json.dumps(triage)}
Resolution status: {result['resolution_status']}
Final response given: {result['final_response'][:200]}"""
    crm = run_agent(client, "CRM", CRM_PROMPT.replace("{id}", str(random.randint(10000,99999))), crm_user)
    crm["ticket_id"] = ticket_id
    result["crm"] = crm
    result["trace"].append({
        "agent": "CRM LOGGER",
        "color": "#7C6FE0", "bg": "#1A1630",
        "icon": "🗃️",
        "output": f"Logged: {ticket_id}  ·  CSAT prediction: {crm['csat_prediction']}  ·  Follow-up: {'Yes' if crm['follow_up_required'] else 'No'}",
        "detail": crm.get("resolution_summary",""),
        "ms": int((time.time()-t0)*1000),
    })

    result["total_ms"] = int((time.time()-t0)*1000)
    return result


# ── Session state init ────────────────────────────────────────────────────
if "crm_log" not in st.session_state:
    st.session_state.crm_log = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:1.2rem;">
      <div style="font-size:1.2rem;font-weight:800;color:#CDD9E5;letter-spacing:-0.3px;">🤖 Support Orchestrator</div>
      <div style="font-size:0.75rem;color:#636E7B;margin-top:2px;">Multi-Agent AI System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="slabel">🔑 Anthropic API Key</div>', unsafe_allow_html=True)
    api_key = st.text_input("", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
    if not api_key:
        st.warning("Add your API key to activate agents.")

    st.markdown("---")
    st.markdown('<div class="slabel">🎭 Demo Tickets</div>', unsafe_allow_html=True)

    DEMOS = {
        "😡 Billing Dispute": "I was charged twice for my subscription this month! $79 was taken on the 3rd and again on the 5th. This is completely unacceptable and I need an immediate refund. I've been a customer for 2 years and this is the third billing error.",
        "🔧 API Issue": "Our production integration is throwing 429 errors on every request since this morning. We're on the Pro plan and this is breaking our entire pipeline. 50k requests are queued. Need urgent help.",
        "❓ Simple FAQ": "Hi, can you tell me what payment methods you accept? Also, do you offer annual billing discounts?",
        "🔐 Security Alert": "I think my account has been compromised. I received a login notification from a location I don't recognise (Singapore) and I'm based in Dublin. I haven't travelled. Please help immediately.",
        "📊 Data Export": "How do I export all my data? I need to do a backup before our company audit next week.",
        "🔄 Cancellation": "I need to cancel my subscription. Can you explain what happens to my data after I cancel? And will I get a refund for the remaining days?",
    }

    demo_choice = st.selectbox("Load a demo ticket", ["(none)"] + list(DEMOS.keys()))
    if demo_choice != "(none)":
        st.session_state["demo_ticket"] = DEMOS[demo_choice]

    st.markdown("---")
    st.markdown("""
    <div style="background:var(--s2);border:1px solid var(--border);border-radius:8px;padding:10px 12px;">
      <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#636E7B;margin-bottom:8px;">Agent Pipeline</div>
      <div style="font-size:0.78rem;color:#8B9BB4;line-height:1.8;">
        <span style="color:#E8A838;">①</span> Triage — classify &amp; prioritise<br>
        <span style="color:#45B17A;">②</span> FAQ — attempt KB resolution<br>
        <span style="color:#E05C5C;">③</span> Escalation — route if needed<br>
        <span style="color:#7C6FE0;">④</span> CRM — log everything
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:0.68rem;color:#3D4A5C;text-align:center;">Built by Zarar Afzal<br>AI Product Manager</div>', unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div>
    <h1>Multi-Agent Customer Support Orchestration</h1>
    <p>4 specialised AI agents · Triage → FAQ → Escalation → CRM · Real-time pipeline</p>
  </div>
  <div class="status-live"><div class="dot-live"></div>AGENTS ONLINE</div>
</div>
""", unsafe_allow_html=True)

# ── Stats ──────────────────────────────────────────────────────────────────
total  = len(st.session_state.crm_log)
resolved  = sum(1 for t in st.session_state.crm_log if t.get("resolution_status")=="Resolved")
escalated = sum(1 for t in st.session_state.crm_log if t.get("resolution_status")=="Escalated")
avg_ms = int(sum(t.get("total_ms",0) for t in st.session_state.crm_log) / max(total,1))

st.markdown(f"""
<div class="stat-grid">
  <div class="stat-card">
    <div class="stat-num">{total}</div>
    <div class="stat-label">Total Tickets</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" style="color:var(--faq);">{resolved}</div>
    <div class="stat-label">Auto-Resolved</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" style="color:var(--escalate);">{escalated}</div>
    <div class="stat-label">Escalated</div>
  </div>
  <div class="stat-card">
    <div class="stat-num" style="color:var(--orch);">{avg_ms if total else "—"}{'ms' if total else ''}</div>
    <div class="stat-label">Avg. Process Time</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Agent status cards ─────────────────────────────────────────────────────
st.markdown("""
<div class="agent-grid">
  <div class="agent-card triage">
    <div class="agent-name" style="color:var(--triage);">🔍 Triage Agent</div>
    <div class="agent-desc">Classifies priority, category, sentiment. Flags human-required cases.</div>
    <div class="agent-status" style="color:var(--triage);">● Ready</div>
  </div>
  <div class="agent-card faq">
    <div class="agent-name" style="color:var(--faq);">📚 FAQ Agent</div>
    <div class="agent-desc">Resolves tickets from the product knowledge base. ~60% resolution rate.</div>
    <div class="agent-status" style="color:var(--faq);">● Ready</div>
  </div>
  <div class="agent-card escalate">
    <div class="agent-name" style="color:var(--escalate);">🚨 Escalation Agent</div>
    <div class="agent-desc">Routes unresolved tickets to correct team with SLA and handoff notes.</div>
    <div class="agent-status" style="color:var(--escalate);">● Ready</div>
  </div>
  <div class="agent-card crm">
    <div class="agent-name" style="color:var(--crm);">🗃️ CRM Logger</div>
    <div class="agent-desc">Logs every interaction with structured data, tags, and CSAT prediction.</div>
    <div class="agent-status" style="color:var(--crm);">● Ready</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">📨 Submit Ticket</div>', unsafe_allow_html=True)

col_inp, col_name = st.columns([3, 1])
with col_inp:
    default_ticket = st.session_state.pop("demo_ticket", "")
    ticket_text = st.text_area(
        "", value=default_ticket,
        placeholder="Paste a customer support ticket here — or load a demo from the sidebar...",
        height=110, label_visibility="collapsed"
    )
with col_name:
    customer_name = st.text_input("", placeholder="Customer name", label_visibility="collapsed")
    if not customer_name:
        customer_name = "Customer"
    submit_btn = st.button("⚡ Run Agent Pipeline", use_container_width=True)

# ── Run orchestration ──────────────────────────────────────────────────────
if submit_btn:
    if not api_key:
        st.error("⚠️ Enter your Anthropic API key in the sidebar.")
    elif not ticket_text.strip():
        st.error("⚠️ Please enter a ticket.")
    else:
        with st.spinner("🤖 Agents processing..."):
            try:
                result = orchestrate(ticket_text.strip(), customer_name, api_key)
                st.session_state.last_result = result
                st.session_state.crm_log.append(result)
                st.rerun()
            except anthropic.AuthenticationError:
                st.error("❌ Invalid API key.")
            except anthropic.RateLimitError:
                st.error("❌ Rate limit. Wait a moment.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ── Display last result ────────────────────────────────────────────────────
if st.session_state.last_result:
    r = st.session_state.last_result
    st.markdown("---")

    col_trace, col_out = st.columns([1, 1])

    with col_trace:
        st.markdown('<div class="sec-title">⚡ Agent Trace</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="background:var(--s2);border:1px solid var(--border);border-radius:8px;padding:4px 12px 4px;margin-bottom:8px;">', unsafe_allow_html=True)
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
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f'<div style="padding:8px 0 4px;text-align:right;font-size:0.72rem;color:var(--muted);">Total: {r.get("total_ms",0)}ms</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_out:
        st.markdown('<div class="sec-title">💬 Outcome</div>', unsafe_allow_html=True)

        # Triage summary
        triage = r.get("triage", {})
        crm    = r.get("crm", {})
        status = r.get("resolution_status", "Pending")
        prio   = triage.get("priority","P2")
        prio_cls = {"P1":"pill-p1","P2":"pill-p2","P3":"pill-p3"}.get(prio,"pill-p2")
        stat_cls = {"Resolved":"pill-res","Escalated":"pill-esc"}.get(status,"pill-pen")
        out_cls  = {"Resolved":"outcome-resolved","Escalated":"outcome-escalated"}.get(status,"outcome-pending")

        st.markdown(f"""
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;">
          <span class="pill {prio_cls}">{prio}</span>
          <span class="pill {stat_cls}">{status}</span>
          <span class="pill" style="background:var(--s3);color:var(--dim);border:1px solid var(--border);">{triage.get('category','')}</span>
          <span class="pill" style="background:var(--s3);color:var(--dim);border:1px solid var(--border);">{triage.get('sentiment','')}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="outcome-box {out_cls}">
          <div class="outcome-label" style="color:{'var(--resolved)' if status=='Resolved' else 'var(--escalated)'};">
            {'✓ Auto-Resolved by FAQ Agent' if status=='Resolved' else '→ Escalated to Human Agent'}
          </div>
          <div class="outcome-response">{r.get('final_response','')}</div>
        </div>
        """, unsafe_allow_html=True)

        # CRM summary
        if crm:
            st.markdown(f"""
            <div style="margin-top:10px;background:var(--s2);border:1px solid var(--border);border-radius:8px;padding:10px 12px;">
              <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--crm);margin-bottom:6px;">🗃️ CRM Entry</div>
              <div style="font-size:0.78rem;color:var(--dim);line-height:1.7;">
                <b style="color:var(--text);">ID:</b> {crm.get('ticket_id','')} &nbsp;·&nbsp;
                <b style="color:var(--text);">CSAT:</b> {crm.get('csat_prediction','')} &nbsp;·&nbsp;
                <b style="color:var(--text);">Follow-up:</b> {'Required' if crm.get('follow_up_required') else 'None'}<br>
                <b style="color:var(--text);">Summary:</b> {crm.get('resolution_summary','')}<br>
                {'<b style="color:var(--text);">Action:</b> ' + crm.get('follow_up_action','') if crm.get('follow_up_required') else ''}
              </div>
              <div style="margin-top:6px;">
                {''.join(f'<span class="pill" style="background:var(--crm-b);color:var(--crm);border:1px solid var(--crm);margin:2px;">{t}</span>' for t in crm.get('tags',[]))}
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Escalation details if escalated
        if status == "Escalated" and r.get("escalation"):
            esc = r["escalation"]
            st.markdown(f"""
            <div style="margin-top:10px;background:var(--escalate-b);border:1px solid var(--escalate);border-radius:8px;padding:10px 12px;">
              <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--escalate);margin-bottom:6px;">🚨 Escalation Details</div>
              <div style="font-size:0.78rem;color:var(--dim);line-height:1.7;">
                <b style="color:var(--text);">Team:</b> {esc.get('escalate_to','')} &nbsp;·&nbsp;
                <b style="color:var(--text);">SLA:</b> {esc.get('sla_hours','')}h<br>
                <b style="color:var(--text);">Handoff:</b> {esc.get('handoff_note','')}
              </div>
            </div>
            """, unsafe_allow_html=True)


# ── CRM Log Table ─────────────────────────────────────────────────────────
if st.session_state.crm_log:
    st.markdown("---")
    st.markdown('<div class="sec-title">🗃️ CRM Log</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="crm-row header">
      <div>Ticket ID</div><div>Priority</div><div>Status</div><div>CSAT</div><div>Summary</div>
    </div>
    """, unsafe_allow_html=True)

    for entry in reversed(st.session_state.crm_log):
        crm    = entry.get("crm", {})
        triage = entry.get("triage", {})
        status = entry.get("resolution_status","Pending")
        prio   = triage.get("priority","P2")
        pc = {"P1":"pill-p1","P2":"pill-p2","P3":"pill-p3"}.get(prio,"pill-p2")
        sc = {"Resolved":"pill-res","Escalated":"pill-esc"}.get(status,"pill-pen")
        cc = {"Positive":"pill-res","Neutral":"pill-pen","Negative":"pill-esc"}.get(crm.get("csat_prediction",""),"pill-pen")

        st.markdown(f"""
        <div class="crm-row">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:var(--muted);">{crm.get('ticket_id','—')}</div>
          <div><span class="pill {pc}">{prio}</span></div>
          <div><span class="pill {sc}">{status}</span></div>
          <div><span class="pill {cc}">{crm.get('csat_prediction','—')}</span></div>
          <div style="font-size:0.78rem;color:var(--dim);">{crm.get('resolution_summary','')[:80]}{'...' if len(crm.get('resolution_summary',''))>80 else ''}</div>
        </div>
        """, unsafe_allow_html=True)

    # Export
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 2, 5])
    with c1:
        # CSV export
        out = StringIO()
        w = csv.writer(out)
        w.writerow(["Ticket ID","Customer","Priority","Category","Sentiment","Status","CSAT","Follow-up","Summary","Timestamp"])
        for e in st.session_state.crm_log:
            c = e.get("crm",{}); t = e.get("triage",{})
            w.writerow([c.get("ticket_id",""), e.get("customer",""), t.get("priority",""),
                        t.get("category",""), t.get("sentiment",""), e.get("resolution_status",""),
                        c.get("csat_prediction",""), c.get("follow_up_required",""),
                        c.get("resolution_summary",""), e.get("timestamp","")])
        st.download_button("⬇️ Export CRM as CSV", out.getvalue().encode(),
                           file_name=f"crm_log_{datetime.now().strftime('%Y%m%d')}.csv",
                           mime="text/csv", use_container_width=True)
    with c2:
        if st.button("🗑️ Clear Log", use_container_width=True):
            st.session_state.crm_log = []
            st.session_state.last_result = None
            st.rerun()


# ── Empty state ────────────────────────────────────────────────────────────
elif not st.session_state.last_result:
    st.markdown("""
    <div style="text-align:center;padding:3rem 2rem;color:#3D4A5C;">
      <div style="font-size:2.5rem;margin-bottom:0.8rem;">🤖</div>
      <div style="font-size:0.95rem;font-weight:600;color:#636E7B;margin-bottom:0.4rem;">Pipeline ready — no tickets processed yet</div>
      <div style="font-size:0.82rem;">Submit a ticket above or load a demo from the sidebar</div>
    </div>
    """, unsafe_allow_html=True)
