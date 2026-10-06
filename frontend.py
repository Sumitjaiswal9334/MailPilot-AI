"""MailPilot AI — redesigned Streamlit dashboard for the existing FastAPI backend.

Run with:
    streamlit run frontend.py

Optional environment variable:
    MAILPILOT_API_URL=http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import os
from html import escape
from typing import Any

import requests
import streamlit as st

API = os.getenv("MAILPILOT_API_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = (5, 30)

st.set_page_config(
    page_title="MailPilot AI · Smart Inbox",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Design system
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --mp-ink:#172033; --mp-muted:#778198; --mp-blue:#3867f4; --mp-blue-soft:#edf2ff;
            --mp-border:#e8ecf4; --mp-bg:#f6f8fc; --mp-green:#159b72; --mp-red:#d94452; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    .stApp { background:var(--mp-bg); color:var(--mp-ink); }
    [data-testid="stHeader"] { background:var(--mp-bg); z-index:1000; }
    [data-testid="stSidebar"] { background:#111a2e; border-right:1px solid #202b43; }
    [data-testid="stSidebar"] * { color:#e6ebf6; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#aeb9d0; }
    [data-testid="stSidebar"] .stButton button { width:100%; border-radius:10px; border:1px solid #34405a;
       background:#1b2740; color:#f5f7ff; text-align:left; }
    [data-testid="stSidebar"] .stButton button:hover { border-color:#708cf9; background:#243454; }
    [data-testid="stSidebar"] [data-testid="stRadio"] > div { gap:8px; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
      min-height:42px; padding:10px 12px; margin:0; border-radius:12px;
      color:#d9e2f3; font-weight:700; transition:background .15s ease, color .15s ease;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#1b2943; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
      background:#203657; color:#ffffff; box-shadow:0 5px 14px rgba(4,12,29,.2);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
      color:#ffffff;
    }
    .block-container { padding-top:3.15rem; padding-bottom:3rem; max-width:1600px; }
    h1,h2,h3,h4 { font-family:'Manrope',sans-serif; letter-spacing:-.035em; color:var(--mp-ink); }
    .brand-row { display:flex; align-items:center; gap:11px; padding:.45rem .1rem 1.35rem; }
    .brand-mark { width:42px;height:42px;border-radius:13px;display:flex;align-items:center;justify-content:center;
      color:white;font-size:21px;background:linear-gradient(135deg,#527bff,#3156dc);box-shadow:0 8px 22px #385ff044; }
    .brand-name { font:800 20px 'Manrope',sans-serif;color:#fff;letter-spacing:-.7px; }
    .brand-sub { font-size:11px;color:#8d9ab4;margin-top:1px; }
    .side-label { font-size:10px; font-weight:700; color:#7f8ba5; letter-spacing:1.5px; margin:1.2rem 0 .8rem; }
    .side-status { border:1px solid #2d3a53; background:#18243a; padding:12px;border-radius:12px;margin:.6rem 0 1rem; }
    .status-dot { display:inline-block;width:7px;height:7px;border-radius:50%;background:#30c99a;margin-right:7px; }
    .muted { color:var(--mp-muted); }
    .eyebrow { display:block; position:relative; z-index:2; color:var(--mp-blue);font-size:11px;
      font-weight:800;letter-spacing:1.3px;text-transform:uppercase;line-height:1.5;
      margin:0 0 7px; padding-top:2px; }
    .page-title { position:relative; z-index:2; font:800 29px 'Manrope',sans-serif;
      letter-spacing:-1.1px;color:#182238;margin:0;line-height:1.2; }
    .page-subtitle { color:#7c879c;font-size:13px;margin-top:4px; }
    .top-chip { display:inline-block;padding:6px 10px;border-radius:999px;background:#e8f8f1;color:#087c5b;font-size:11px;font-weight:700; }
    .metric-card { background:white;border:1px solid var(--mp-border);border-radius:15px;padding:17px 18px;min-height:112px;
      box-shadow:0 3px 12px rgba(28,44,77,.025); }
    .metric-label { color:#7d879b;font-size:12px;font-weight:600; }
    .metric-value { font:800 27px 'Manrope',sans-serif;color:#1c2740;margin-top:7px;letter-spacing:-.8px; }
    .metric-foot { color:#8a94a8;font-size:11px;margin-top:2px; }
    .panel { background:#fff;border:1px solid var(--mp-border);border-radius:16px;padding:18px 19px;box-shadow:0 3px 12px rgba(28,44,77,.025); }
    .panel-title { font:800 16px 'Manrope',sans-serif;color:#202b42; }
    .panel-note { color:#8791a5;font-size:12px;margin-top:3px; }
    .email-tile { background:#fff;border:1px solid var(--mp-border);border-left:4px solid #5b7cfa;border-radius:12px;padding:13px 14px;margin:8px 0; }
    .email-tile.spam { border-left-color:#e34d5b;background:#fff8f8;border-color:#f5dfe1; }
    .email-subject { font-weight:700;color:#222d43;font-size:13px;line-height:1.45; }
    .email-meta { color:#8791a4;font-size:11px;margin-top:5px; }
    .pill { display:inline-block;border-radius:6px;padding:3px 7px;font-size:10px;font-weight:800;letter-spacing:.2px; }
    .pill-blue { background:#edf2ff;color:#365ce1; }
    .pill-green { background:#e8f8f1;color:#11845f; }
    .pill-red { background:#ffebed;color:#c43242; }
    .pill-amber { background:#fff4dd;color:#9a6900; }
    .draft-box { background:#f5f8ff;border:1px solid #dce6ff;border-left:4px solid #4a70f5;border-radius:11px;padding:14px 16px;
      color:#34415e;white-space:pre-wrap;line-height:1.65;font-size:13px; }
    .risk-box { background:#fff5e8;border:1px solid #ffe0b5;border-radius:10px;padding:11px 13px;color:#8c5a0b;font-size:12px; }
    .empty-state { text-align:center;background:white;border:1px dashed #d9dfeb;border-radius:15px;padding:35px 18px;color:#7e899e; }
    .empty-icon { font-size:30px;margin-bottom:7px; }
    div.stButton > button { border-radius:10px;font-weight:700;min-height:2.55rem;border:1px solid #dfe5ef; }
    div.stButton > button[kind="primary"] { background:#3867f4;border-color:#3867f4;color:#fff; }
    div.stButton > button[kind="primary"]:hover { background:#2e56d7;border-color:#2e56d7; }
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stSelectbox"] div[data-baseweb="select"] { border-radius:10px; }
    div[data-testid="stForm"] { background:white;border:1px solid var(--mp-border);padding:18px;border-radius:15px; }
    hr { border-color:#e8ecf4; }
    .small-caption { font-size:11px;color:#8791a5; }
    @media (max-width: 900px) { .page-title{font-size:24px;} .block-container{padding:2.8rem 1rem 3rem;} }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# API helpers
# -----------------------------------------------------------------------------
def api_request(method: str, path: str, *, timeout: int = 30, **kwargs: Any) -> requests.Response:
    return requests.request(method, f"{API}{path}", timeout=timeout, **kwargs)


def response_detail(response: requests.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            return str(payload.get("detail") or payload.get("message") or payload.get("error") or payload)
        return str(payload)
    except (ValueError, requests.exceptions.JSONDecodeError):
        return response.text[:500] or f"HTTP {response.status_code}"


def get_json(path: str, *, timeout: int = 15, default: Any = None) -> Any:
    try:
        response = api_request("GET", path, timeout=timeout)
        if response.ok:
            return response.json()
        st.session_state["api_warning"] = f"Backend returned {response.status_code}: {response_detail(response)}"
    except requests.RequestException:
        st.session_state["api_warning"] = "Backend unavailable. Start FastAPI and refresh this page."
    return default


def post_json(path: str, *, timeout: int = 30, json_body: dict | None = None) -> tuple[bool, Any]:
    try:
        response = api_request("POST", path, timeout=timeout, json=json_body)
        if response.ok:
            try:
                return True, response.json()
            except ValueError:
                return True, {"message": response.text}
        return False, response_detail(response)
    except requests.RequestException as exc:
        return False, f"Could not reach backend: {exc}"


def parse_result(email: dict[str, Any]) -> dict[str, Any]:
    raw = email.get("result", {})
    if isinstance(raw, str):
        try:
            raw = json.loads(raw or "{}")
        except (ValueError, TypeError):
            raw = {}
    if not isinstance(raw, dict):
        raw = {}
    result = dict(raw)
    result["draft"] = email.get("draft") or result.get("draft") or ""
    result["status"] = email.get("status") or result.get("status") or "pending_review"
    return result


def is_spam(email: dict[str, Any]) -> bool:
    return bool(parse_result(email).get("is_spam", False))


def label(value: Any) -> str:
    return str(value or "—").replace("_", " ").title()


def pill(text: str, color: str = "blue") -> str:
    return f'<span class="pill pill-{color}">{escape(text.upper())}</span>'


def show_notice(kind: str, message: str) -> None:
    getattr(st, kind, st.info)(message)


def refresh_data() -> None:
    st.session_state.pop("api_warning", None)
    st.rerun()

def go_to_process() -> None:
    st.session_state["navigation_page"] = "Process email"

def go_to_inbox(email_id: Any) -> None:
    st.session_state["selected_email_id"] = email_id
    st.session_state["navigation_page"] = "Inbox"

# -----------------------------------------------------------------------------
# Sidebar / navigation
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand-row"><div class="brand-mark">✉</div><div><div class="brand-name">MailPilot AI</div>'
        '<div class="brand-sub">Your intelligent inbox</div></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-label">WORKSPACE</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["Overview", "Inbox", "Spam center", "Process email"],
        label_visibility="collapsed",
        key="navigation_page",
    )
    st.markdown('<div class="side-label">GMAIL ACCOUNT</div>', unsafe_allow_html=True)
    gmail_status = get_json("/auth/gmail/status", timeout=10, default={}) or {}
    connected = bool(gmail_status.get("connected"))
    account = gmail_status.get("email") or "Gmail account"
    if connected:
        st.markdown(
            f'<div class="side-status"><div><span class="status-dot"></span><b>Connected</b></div>'
            f'<div style="font-size:11px;color:#aeb9d0;margin:6px 0 0 14px;overflow-wrap:anywhere">{escape(account)}</div></div>',
            unsafe_allow_html=True,
        )
    elif gmail_status.get("state") == "expired_or_revoked":
        st.warning("Gmail session expired. Reconnect to continue.")
    elif gmail_status.get("state") == "configuration_missing":
        st.error("Gmail OAuth is not configured in the backend.")
    else:
        st.markdown('<div class="side-status"><span style="color:#f2c46d">●</span> <b>Not connected</b><div style="font-size:11px;color:#aeb9d0;margin-top:5px">Connect to sync your inbox</div></div>', unsafe_allow_html=True)

    if connected:
        if st.button("↻  Sync Gmail inbox", use_container_width=True, type="primary"):
            with st.spinner("Syncing Gmail and processing new messages…"):
                ok, payload = post_json("/gmail/sync?limit=5", timeout=100)
            if ok:
                st.success(f"Sync complete · {payload.get('imported', 0)} new email(s) imported")
                st.rerun()
            else:
                st.error(str(payload))
        if st.button("Disconnect Gmail", use_container_width=True):
            ok, payload = post_json("/auth/gmail/disconnect", timeout=20)
            if ok:
                st.success("Gmail disconnected.")
                st.rerun()
            st.error(str(payload))
    else:
        if st.button("Connect Gmail", use_container_width=True, type="primary"):
            # The existing backend exposes the OAuth login URL through GET.
            try:
                response = api_request("GET", "/auth/gmail/login", timeout=10)
                if response.ok:
                    url = response.json().get("authorization_url")
                    if url:
                        st.link_button("Continue with Google ↗", url, use_container_width=True)
                        st.caption("After granting access, return here and refresh the page.")
                    else:
                        st.error("Backend did not return an authorization URL.")
                else:
                    st.error(response_detail(response))
            except requests.RequestException as exc:
                st.error(f"Could not start Gmail OAuth: {exc}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="small-caption">Powered by Gemini · LangGraph</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Load emails and derived counts
# -----------------------------------------------------------------------------
emails = get_json("/emails", timeout=15, default=[])
if not isinstance(emails, list):
    emails = []
normal_emails = [e for e in emails if not is_spam(e)]
spam_emails = [e for e in emails if is_spam(e)]
pending_emails = [e for e in emails if str(e.get("status", "pending_review")) == "pending_review"]
urgent_emails = [e for e in normal_emails if str(parse_result(e).get("urgency", "normal")).lower() in {"high", "critical"}]
sent_emails = [e for e in emails if str(e.get("status", "")).lower() == "sent"]

# Top-level header
header_left, header_right = st.columns([4, 1.25], vertical_alignment="center")
with header_left:
    st.markdown('<div class="eyebrow">AI-POWERED EMAIL WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{escape(page)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Triage smarter. Respond faster. Stay in control.</div>', unsafe_allow_html=True)
with header_right:
    st.markdown('<div style="text-align:right"><span class="top-chip">● Human approval enabled</span></div>', unsafe_allow_html=True)

if st.session_state.get("api_warning"):
    st.warning(st.session_state.pop("api_warning"))

# -----------------------------------------------------------------------------
# Shared components
# -----------------------------------------------------------------------------
def metric_card(col: Any, title: str, value: Any, foot: str, icon: str) -> None:
    col.markdown(
        f'<div class="metric-card"><div class="metric-label">{icon} &nbsp; {escape(title)}</div>'
        f'<div class="metric-value">{escape(str(value))}</div><div class="metric-foot">{escape(foot)}</div></div>',
        unsafe_allow_html=True,
    )


def email_tile(email: dict[str, Any], selected: bool = False) -> None:
    result = parse_result(email)
    spam = bool(result.get("is_spam"))
    category = label(result.get("category", "other"))
    urgency = label(result.get("urgency", "normal"))
    status = label(email.get("status", "pending_review"))
    sender = str(email.get("sender", "Unknown sender"))
    subject = str(email.get("subject", "No subject"))
    css = "email-tile spam" if spam else "email-tile"
    status_color = "red" if spam else ("green" if status in {"Approved", "Sent", "Gmail Draft"} else "blue")
    st.markdown(
        f'<div class="{css}"><div style="display:flex;justify-content:space-between;gap:8px;align-items:flex-start">'
        f'<div class="email-subject">{("🚨 " if spam else "✉️ ")}{escape(subject[:110])}</div>'
        f'{pill("SPAM · AVOID OPENING" if spam else status, status_color)}</div>'
        f'<div class="email-meta">{escape(sender)} &nbsp;·&nbsp; {pill(category, "red" if spam else "blue")} '
        f'&nbsp; {pill(urgency, "amber" if urgency.lower() in {"high", "critical"} else "blue")} '
        f'&nbsp; <span style="color:#a0a8b8">ID #{escape(str(email.get("id", "?")))}</span></div></div>',
        unsafe_allow_html=True,
    )


def render_email_detail(email: dict[str, Any], *, allow_actions: bool = True) -> None:
    result = parse_result(email)
    spam = bool(result.get("is_spam"))
    status = str(email.get("status", "pending_review"))
    confidence = result.get("confidence", 0)
    try:
        confidence_pct = max(0, min(100, round(float(confidence) * 100)))
    except (TypeError, ValueError):
        confidence_pct = 0
    category = label(result.get("category", "other"))
    urgency = label(result.get("urgency", "normal"))
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="panel-title">{"🚨 Spam review" if spam else "✦ AI email assessment"}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel-note">Email #{escape(str(email.get("id", "?")))} · {escape(label(status))}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Category", category)
    c2.metric("Urgency", urgency)
    c3.metric("Confidence", f"{confidence_pct}%")
    st.progress(confidence_pct / 100, text="AI classification confidence")
    st.markdown("**Why this result**")
    st.write(str(result.get("reason") or "No explanation provided."))
    flags = result.get("risk_flags") or []
    if flags:
        st.markdown(f'<div class="risk-box">⚠️ <b>Risk flags</b><br>{escape(", ".join(label(x) for x in flags))}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#14815e;font-size:12px">✓ No risk flags reported by the classifier</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Original email</div>', unsafe_allow_html=True)
    st.markdown(f'**From:** {escape(str(email.get("sender", "Unknown sender")))}')
    st.markdown(f'**Subject:** {escape(str(email.get("subject", "No subject")))}')
    st.text(str(email.get("body") or "No body available."))

    draft = str(email.get("draft") or result.get("draft") or "")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="panel-title">✍️ Suggested reply</div>', unsafe_allow_html=True)
    if spam:
        st.warning("This message was classified as spam. MailPilot does not provide a normal reply draft.")
    elif draft:
        st.markdown(f'<div class="draft-box">{escape(draft)}</div>', unsafe_allow_html=True)
    else:
        st.info("No reply draft is available for this email.")

    if allow_actions:
        st.markdown("<br>", unsafe_allow_html=True)
        if status == "pending_review":
            if spam:
                st.warning("Approval and sending are disabled for messages classified as spam.")
            elif st.button("✓  Approve for sending", type="primary", key=f"approve_{email.get('id')}", use_container_width=True):
                ok, payload = post_json(f"/emails/{email['id']}/approve", timeout=15)
                if ok:
                    st.success("Draft approved. Sending remains a separate action.")
                    st.rerun()
                st.error(str(payload))
        elif status == "approved":
            st.markdown('<span class="top-chip">✓ Approved for sending</span>', unsafe_allow_html=True)
        elif status == "sent":
            st.markdown('<span class="top-chip">✓ Already sent</span>', unsafe_allow_html=True)

        # Gmail-specific actions are shown only for Gmail-imported messages.
        gmail_id = email.get("gmail_id")
        action_cols = st.columns(2)
        if gmail_id and status in {"approved", "gmail_draft"}:
            with action_cols[0]:
                if st.button("Create Gmail draft", key=f"draft_{email['id']}", use_container_width=True):
                    ok, payload = post_json(f"/gmail/emails/{email['id']}/create-draft", timeout=30)
                    if ok:
                        st.success("Gmail draft created.")
                        st.rerun()
                    st.error(str(payload))
        can_send = (not spam) and ((gmail_id and status in {"approved", "gmail_draft"}) or (not gmail_id and status == "approved"))
        with action_cols[1]:
            if can_send:
                confirm_key = f"confirm_send_{email['id']}"
                confirmed = st.checkbox("I confirm this reply is ready to send", key=confirm_key)
                if st.button("Send email", key=f"send_{email['id']}", type="primary", disabled=not confirmed, use_container_width=True):
                    path = f"/gmail/emails/{email['id']}/send" if gmail_id else f"/emails/{email['id']}/send"
                    ok, payload = post_json(path, timeout=35)
                    if ok:
                        st.success("Email sent." if gmail_id else "Simulated send completed (mock/local mode).")
                        st.rerun()
                    st.error(str(payload))
        if not gmail_id and status == "approved":
            st.caption("This is a manually submitted email; the backend's non-Gmail send endpoint may simulate sending.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
if page == "Overview":
    st.markdown("<br>", unsafe_allow_html=True)
    metrics = st.columns(4, gap="medium")
    metric_card(metrics[0], "Total processed", len(emails), "Emails in local history", "✉")
    metric_card(metrics[1], "Needs review", len(pending_emails), "Awaiting your decision", "◷")
    metric_card(metrics[2], "Urgent", len(urgent_emails), "High or critical urgency", "⚡")
    metric_card(metrics[3], "Spam detected", len(spam_emails), "Separated for safer review", "⚑")

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        st.markdown('<div class="panel-title">Recent inbox activity</div><div class="panel-note">Latest messages processed by MailPilot</div>', unsafe_allow_html=True)
        if not emails:
            st.markdown('<div class="empty-state"><div class="empty-icon">✉️</div><b>Your inbox is ready</b><br>Connect Gmail and sync, or process a sample email to get started.</div>', unsafe_allow_html=True)
        else:
            for email in sorted(emails, key=lambda e: int(e.get("id", 0) or 0), reverse=True)[:6]:
                email_tile(email)
                st.button("Open email details", key=f"overview_open_{email.get('id')}",
                          on_click=go_to_inbox, args=(email.get("id"),))
    with right:
        st.markdown('<div class="panel-title">Your workflow</div><div class="panel-note">AI assists; you stay in control</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        for number, title, desc in [
            ("01", "Analyze", "Gemini classifies the email and highlights urgency and risks."),
            ("02", "Review", "Check the explanation and suggested response before approving."),
            ("03", "Send safely", "Create a Gmail draft or explicitly confirm sending."),
        ]:
            st.markdown(f'<div style="display:flex;gap:12px;margin:15px 0"><div style="min-width:35px;height:35px;background:#edf2ff;color:#3867f4;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:12px">{number}</div><div><b style="color:#253149">{title}</b><div style="font-size:12px;color:#818ba0;line-height:1.55;margin-top:3px">{desc}</div></div></div>', unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("**Quick action**")
        st.button("＋  Process a new email", type="primary", use_container_width=True, on_click=go_to_process)

elif page in {"Inbox", "Spam center"}:
    st.markdown("<br>", unsafe_allow_html=True)
    search_col, category_col, status_col = st.columns([2, 1, 1])
    with search_col:
        query = st.text_input("Search", placeholder="Search sender, subject, or email text…", label_visibility="collapsed", key="inbox_search")
    with category_col:
        category_filter = st.selectbox("Category", ["All categories", "Work", "Personal", "Finance", "Newsletter", "Urgent", "Other", "Spam"], label_visibility="collapsed")
    with status_col:
        status_filter = st.selectbox("Status", ["All statuses", "Pending Review", "Approved", "Gmail Draft", "Sent"], label_visibility="collapsed")

    source_emails = spam_emails if page == "Spam center" else normal_emails
    filtered = []
    for email in source_emails:
        result = parse_result(email)
        haystack = " ".join(str(email.get(k, "")) for k in ("sender", "subject", "body")).lower()
        if query and query.lower() not in haystack:
            continue
        if category_filter != "All categories" and label(result.get("category", "other")) != category_filter:
            continue
        if status_filter != "All statuses" and label(email.get("status", "pending_review")) != status_filter:
            continue
        filtered.append(email)

    if page == "Spam center":
        st.markdown('<div class="risk-box">🚨 <b>Spam center</b> — treat these messages as untrusted. Avoid clicking links or replying unless you have independently verified the sender.</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel-note">Showing {len(filtered)} message(s)</div>', unsafe_allow_html=True)
    if not filtered:
        st.markdown('<div class="empty-state"><div class="empty-icon">⌕</div><b>No matching emails</b><br>Try changing your search or filters.</div>', unsafe_allow_html=True)
    else:
        list_col, detail_col = st.columns([1.03, 1.35], gap="large")
        email_ids = [str(e.get("id")) for e in filtered]
        selected_id = str(st.session_state.get("selected_email_id", email_ids[0]))
        if selected_id not in email_ids:
            selected_id = email_ids[0]
        with list_col:
            st.markdown('<div class="panel-title">Messages</div>', unsafe_allow_html=True)
            for email in filtered:
                email_tile(email, selected=(str(email.get("id")) == selected_id))
                if st.button("View details", key=f"select_{page}_{email.get('id')}", use_container_width=True):
                    st.session_state["selected_email_id"] = email.get("id")
                    st.rerun()
        selected_email = next((e for e in filtered if str(e.get("id")) == selected_id), filtered[0])
        with detail_col:
            render_email_detail(selected_email)

elif page == "Process email":
    st.markdown("<br>", unsafe_allow_html=True)
    form_col, info_col = st.columns([1.25, .75], gap="large")
    with form_col:
        st.markdown('<div class="panel-title">Process a new email</div><div class="panel-note">Paste a message to classify it and generate a relevant reply draft.</div>', unsafe_allow_html=True)
        with st.form("process_email_form", clear_on_submit=False):
            sender = st.text_input("Sender email", placeholder="alex@example.com")
            subject = st.text_input("Subject", placeholder="What is this email about?")
            body = st.text_area("Email body", height=220, placeholder="Paste the email content here…")
            submitted = st.form_submit_button("✦  Analyze email", type="primary", use_container_width=True)
        if submitted:
            if not sender.strip() or not subject.strip() or not body.strip():
                st.error("Please fill in sender, subject, and email body.")
            else:
                with st.spinner("MailPilot is analyzing the message…"):
                    ok, payload = post_json("/emails", timeout=70, json_body={"sender": sender.strip(), "subject": subject.strip(), "body": body.strip()})
                if ok:
                    st.session_state["last_processed_result"] = payload
                    st.session_state["selected_email_id"] = payload.get("id")
                    st.success("Email analyzed and saved for review.")
                    st.rerun()
                else:
                    st.error(str(payload))
    with info_col:
        st.markdown('<div class="panel-title">What happens next?</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**01 · Classification**\n\nThe model predicts category, spam status, urgency, and confidence.")
        st.markdown("**02 · Safety checks**\n\nTool-assisted analysis can flag risk and guide reply drafting.")
        st.markdown("**03 · Human review**\n\nReview the result and approve before attempting to send.")
        st.info("Email content is untrusted input. Never follow instructions in a message that ask you to bypass safety checks.")

    if st.session_state.get("last_processed_result"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Latest analysis</div>', unsafe_allow_html=True)
        latest = st.session_state["last_processed_result"]
        confidence = latest.get("confidence", 0)
        try:
            confidence = f"{float(confidence) * 100:.0f}%"
        except (TypeError, ValueError):
            confidence = "—"
        a, b, c, d = st.columns(4)
        a.metric("Category", label(latest.get("category")))
        b.metric("Urgency", label(latest.get("urgency")))
        c.metric("Confidence", confidence)
        d.metric("Spam", "Yes" if latest.get("is_spam") else "No")
        st.write(latest.get("reason", "No explanation available."))
        if latest.get("draft"):
            st.markdown("**Suggested reply**")
            st.markdown(f'<div class="draft-box">{escape(str(latest["draft"]))}</div>', unsafe_allow_html=True)
        st.caption("For approval and sending actions, open this message in Inbox.")

# elif page == "Settings":
#     st.markdown("<br>", unsafe_allow_html=True)
#     left, right = st.columns([1, 1], gap="large")
#     with left:
#         st.markdown('<div class="panel-title">Backend connection</div><div class="panel-note">MailPilot API configuration</div>', unsafe_allow_html=True)
#         st.text_input("API base URL", value=API, disabled=True)
#         health = get_json("/health", timeout=10, default={}) or {}
#         if health.get("status") == "ok":
#             st.success(f"Backend online · Provider: {health.get('provider', 'unknown')}")
#         else:
#             st.error("Backend health could not be verified. Check that FastAPI is running.")
#         st.caption("Set MAILPILOT_API_URL in your environment if the backend is not running at localhost:8000.")
#     with right:
#         st.markdown('<div class="panel-title">Gmail connection</div><div class="panel-note">OAuth status and account access</div>', unsafe_allow_html=True)
#         if connected:
#             st.success(f"Connected{f' as {account}' if account else ''}")
#             st.write("MailPilot uses the Gmail API to sync messages and create or send replies after approval.")
#             if st.button("Disconnect and revoke Gmail access", type="secondary"):
#                 ok, payload = post_json("/auth/gmail/disconnect", timeout=20)
#                 if ok:
#                     st.success("Gmail disconnected.")
#                     st.rerun()
#                 st.error(str(payload))
#         else:
#             st.warning("Gmail is not connected.")
#             st.write("Use Connect Gmail in the sidebar after configuring OAuth credentials in the backend environment.")
#     st.markdown("<br>", unsafe_allow_html=True)
#     st.markdown('<div class="panel-title">Privacy and safety</div>', unsafe_allow_html=True)
#     st.markdown("- Gmail credentials should remain on the backend and must never be placed in frontend code.\n- Email bodies are untrusted content and may contain malicious instructions.\n- Sending should only occur after explicit user review and backend approval.\n- This build is designed for local, single-user use; it is not a multi-user production deployment.")

st.markdown("<br><div style='text-align:center;color:#9aa3b4;font-size:11px'>MailPilot AI · Agentic email triage with human approval · Keep the final decision in your hands</div>", unsafe_allow_html=True)
