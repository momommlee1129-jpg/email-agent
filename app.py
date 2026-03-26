"""Email Processing Agent — Outlook Mac-style Prototype
4-column layout matching real Outlook for Mac:
  Col1: Icon nav (Mail/Calendar/People)
  Col2: Folder list (Inbox/Drafts/Sent...)
  Col3: Email list (with priority tabs)
  Col4: Reading pane + Agent panel
"""

import streamlit as st
from data.mock_emails import MOCK_EMAILS, LONG_THREAD_EXAMPLE, USER_CONTEXT
from src.agent import classify_priority, extract_action_items, summarize_thread

PRIORITY_CFG = {
    "act_now": {"label": "Act Now", "dot": "#E74C3C", "tag_bg": "#FDEDEC", "tag_fg": "#C0392B"},
    "later":   {"label": "Later",   "dot": "#F39C12", "tag_bg": "#FEF9E7", "tag_fg": "#D68910"},
    "ignore":  {"label": "Ignore",  "dot": "#BDC3C7", "tag_bg": "#F2F3F4", "tag_fg": "#7F8C8D"},
}
URGENCY_ICONS = {"high": "🔴", "medium": "🟡", "low": "🟢"}
AVATAR_COLORS = ["#0078D4", "#107C10", "#D83B01", "#B4009E", "#008272",
                 "#4A154B", "#E74856", "#00B7C3", "#8764B8", "#CA5010"]

def _acolor(n): return AVATAR_COLORS[hash(n) % len(AVATAR_COLORS)]
def _ini(n):
    p = n.replace("(", "").split()
    return (p[0][0] + p[1][0]).upper() if len(p) >= 2 else n[:2].upper()
def _short(n): return n.split("(")[0].strip() if "(" in n else n


def inject_css():
    st.markdown("""<style>
    /* Hide Streamlit chrome */
    #MainMenu,header,footer,div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],div[data-testid="stStatusWidget"]{display:none!important}
    .block-container{padding:0 0.5rem!important; max-width:100%!important}
    section[data-testid="stSidebar"]{display:none!important}

    /* Font */
    *{font-family:'Segoe UI',system-ui,-apple-system,sans-serif}

    /* Top bar */
    .otb{background:linear-gradient(135deg,#0F6CBD 0%,#0E5FA6 100%);color:white;
        padding:7px 14px;display:flex;align-items:center;gap:10px;
        margin:-0.5rem -0.5rem 0 -0.5rem}
    .otb .search{flex:1;max-width:420px;margin:0 auto;background:rgba(255,255,255,.15);
        border-radius:5px;padding:5px 12px;font-size:13px;color:rgba(255,255,255,.7)}
    .otb-right{margin-left:auto;display:flex;gap:6px;align-items:center}

    /* Toolbar */
    .tbar{display:flex;gap:2px;padding:4px 6px;border-bottom:1px solid #E5E5E5;
        background:#FAFAFA;margin:0 -0.5rem;padding-left:0.5rem;flex-wrap:wrap}
    .tbar .tb{font-size:10px;color:#555;padding:3px 7px;cursor:pointer;border-radius:3px;
        display:flex;flex-direction:column;align-items:center;gap:0px}
    .tbar .tb:hover{background:#E8E8E8}
    .tbar .tb .ico{font-size:14px}
    .tbar .sep{width:1px;height:26px;background:#DDD;margin:0 2px}
    .tbar .tb.hi{color:#0F6CBD;font-weight:700}

    /* Icon nav (col1) */
    .nav-icon{width:100%;text-align:center;padding:10px 0;font-size:20px;cursor:pointer;
        border-radius:6px;transition:background .1s;margin-bottom:2px}
    .nav-icon:hover{background:#E0E0E0}
    .nav-icon.active{background:#D6EBFF}

    /* Folder list (col2) */
    .folder-hdr{font-size:13px;font-weight:600;color:#1A1A1A;padding:10px 10px 6px}
    .fi{display:flex;align-items:center;gap:6px;padding:5px 10px;font-size:13px;
        color:#1A1A1A;cursor:pointer;border-radius:4px;transition:background .08s;margin:1px 4px}
    .fi:hover{background:#E8E8E8}
    .fi.sel{background:#D6EBFF;color:#0F6CBD;font-weight:600}
    .fi .badge{margin-left:auto;background:#0F6CBD;color:white;border-radius:10px;
        padding:0 6px;font-size:11px;font-weight:600;line-height:18px}
    .fi .badge.red{background:#E74C3C}

    /* Email list item (col3) */
    .eml{padding:8px 10px;border-bottom:1px solid #F0F0F0;cursor:pointer;transition:background .06s}
    .eml:hover{background:#F5F5F5}
    .eml.sel{background:#E8F2FD;border-left:3px solid #0F6CBD}
    .eml-row{display:flex;gap:8px;align-items:flex-start}
    .eml-av{width:32px;height:32px;border-radius:50%;flex-shrink:0;display:flex;
        align-items:center;justify-content:center;font-size:12px;font-weight:600;color:white}
    .eml-c{flex:1;min-width:0;overflow:hidden}
    .eml-from{font-size:13px;font-weight:600;color:#1A1A1A;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .eml-subj{font-size:12px;color:#1A1A1A;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .eml-prev{font-size:11px;color:#A0A0A0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .eml-meta{flex-shrink:0;text-align:right}
    .eml-time{font-size:11px;color:#A0A0A0}
    .pri-tag{padding:1px 6px;border-radius:3px;font-size:10px;font-weight:700;display:inline-block;margin-top:2px}

    /* Reading pane (col4 top) */
    .rp-subj{font-size:17px;font-weight:600;color:#1A1A1A;margin-bottom:10px}
    .rp-sender{display:flex;align-items:center;gap:8px;padding-bottom:10px;border-bottom:1px solid #F0F0F0}
    .rp-av{width:34px;height:34px;border-radius:50%;flex-shrink:0;display:flex;
        align-items:center;justify-content:center;font-size:13px;font-weight:600;color:white}
    .rp-name{font-size:13px;font-weight:600;color:#1A1A1A}
    .rp-email{font-size:11px;color:#888}
    .rp-to{font-size:11px;color:#888}
    .rp-body{font-size:13.5px;color:#1A1A1A;line-height:1.6;white-space:pre-wrap;padding-top:12px}
    .rp-actions{display:flex;gap:6px;margin-left:auto;font-size:15px;color:#888}

    /* Agent panel */
    .ag-hdr{background:linear-gradient(135deg,#0F6CBD,#0E5FA6);color:white;padding:7px 10px;
        border-radius:5px 5px 0 0;display:flex;align-items:center;gap:6px;margin-top:12px}
    .ag-hdr .t{font-size:13px;font-weight:600}
    .ag-hdr .s{font-size:10px;opacity:.7;margin-left:auto}
    .ag-card{background:#fff;border:1px solid #E8E8E8;border-radius:5px;padding:7px 9px;margin-bottom:5px;font-size:12px}
    .ag-card.act_now{border-left:3px solid #E74C3C}
    .ag-card.later{border-left:3px solid #F39C12}
    .ag-card.ignore{border-left:3px solid #BDC3C7}
    .ag-excerpt{background:#F0F7FF;border-left:2px solid #0F6CBD;padding:4px 8px;
        font-size:11px;color:#333;margin-top:3px;border-radius:0 3px 3px 0;font-style:italic}
    .sum-block{background:#fff;border:1px solid #E8E8E8;border-radius:5px;padding:7px 9px;margin-bottom:5px}
    .sum-block h4{font-size:11px;color:#0F6CBD;margin:0 0 3px;font-weight:700}
    .sum-block p,.sum-block li{font-size:12px;color:#1A1A1A;line-height:1.4;margin:0}
    .sum-block ul{padding-left:14px;margin:2px 0 0}
    .dir-change{background:#FFF8E1;border-left:3px solid #F39C12;padding:4px 8px;
        border-radius:0 3px 3px 0;font-size:11px;color:#7D6608;margin:4px 0}
    </style>""", unsafe_allow_html=True)


def init_state():
    for k, v in {"classifications": {}, "action_items": {}, "thread_summary": None,
                  "confirmed_todos": [], "overrides": {}, "selected_email": None}.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _eff_pri(eid):
    cl = st.session_state.classifications.get(eid)
    if cl and "error" not in cl:
        return st.session_state.overrides.get(eid, cl.get("priority", "later"))
    return None


# ── Top bar + Toolbar ──────────────────────────────────────────────

def render_topbar():
    st.markdown(
        '<div class="otb">'
        '<span style="font-size:16px">🌐</span>'
        '<span style="font-size:14px;font-weight:600;background:#0E5FA6;padding:3px 10px;border-radius:4px">✏ 新邮件</span>'
        '<div class="search">🔍 搜索</div>'
        '<div class="otb-right"><span>🔔</span> <span>⚙️</span></div>'
        '</div>', unsafe_allow_html=True)

def render_toolbar():
    st.markdown(
        '<div class="tbar">'
        '<div class="tb"><span class="ico">🗑</span>删除</div>'
        '<div class="tb"><span class="ico">📦</span>存档</div>'
        '<div class="tb"><span class="ico">⚠</span>报告</div>'
        '<div class="sep"></div>'
        '<div class="tb"><span class="ico">📂</span>移动</div>'
        '<div class="tb"><span class="ico">🚩</span>标记</div>'
        '<div class="sep"></div>'
        '<div class="tb"><span class="ico">✉</span>标为未读</div>'
        '<div class="tb"><span class="ico">🔄</span>同步</div>'
        '<div class="sep"></div>'
        '<div class="tb hi"><span class="ico">🤖</span>AI Agent</div>'
        '</div>', unsafe_allow_html=True)


# ── Col 1: Icon nav ───────────────────────────────────────────────

def render_icon_nav(col):
    with col:
        st.markdown('<div class="nav-icon active">✉️</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-icon">📅</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-icon">👥</div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-icon">✅</div>', unsafe_allow_html=True)
        st.markdown('<div style="flex:1"></div>', unsafe_allow_html=True)
        st.markdown('<div class="nav-icon">⚙️</div>', unsafe_allow_html=True)


# ── Col 2: Folder list ────────────────────────────────────────────

def render_folders(col):
    with col:
        st.markdown('<div class="folder-hdr">momo@techcorp.com</div>', unsafe_allow_html=True)

        classified = bool(st.session_state.classifications)
        act_n = sum(1 for e in MOCK_EMAILS if _eff_pri(e["id"]) == "act_now") if classified else 0
        badge_html = f'<span class="badge red">{act_n}</span>' if act_n else f'<span class="badge">{len(MOCK_EMAILS)}</span>'

        st.markdown(f'<div class="fi sel">📥 收件箱 {badge_html}</div>', unsafe_allow_html=True)
        st.markdown('<div class="fi">📝 草稿</div>', unsafe_allow_html=True)
        st.markdown('<div class="fi">📦 存档</div>', unsafe_allow_html=True)
        st.markdown('<div class="fi">📤 已发送</div>', unsafe_allow_html=True)
        st.markdown('<div class="fi">🗑 已删除邮件</div>', unsafe_allow_html=True)
        st.markdown('<div class="fi">⚠️ 垃圾邮件</div>', unsafe_allow_html=True)
        st.markdown('<div class="fi">📰 订阅邮件</div>', unsafe_allow_html=True)
        st.markdown('<div class="fi">💬 对话历史</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div style="font-size:11px;color:#888;font-weight:600;padding:0 10px">📅 TODAY</div>', unsafe_allow_html=True)
        for evt in USER_CONTEXT["calendar_today"]:
            st.markdown(f'<div style="font-size:11px;color:#555;padding:2px 10px">'
                        f'<span style="color:#0F6CBD;font-weight:600">{evt["time"]}</span> '
                        f'{evt["title"]}</div>', unsafe_allow_html=True)

        st.markdown('<div style="font-size:11px;color:#888;font-weight:600;padding:6px 10px 0">✅ TO DO</div>', unsafe_allow_html=True)
        for t in USER_CONTEXT["active_todos"]:
            st.markdown(f'<div style="font-size:11px;color:#555;padding:2px 10px">☐ {t}</div>', unsafe_allow_html=True)


# ── Col 3: Email list ─────────────────────────────────────────────

def _render_one_email(email):
    eid = email["id"]
    short = _short(email["from_name"])
    ini = _ini(short)
    ac = _acolor(short)
    ts = email["timestamp"].split(" ")[1][:5]
    prev = email["body"][:60].replace("\n", " ")
    sel = st.session_state.selected_email == eid

    cl = st.session_state.classifications.get(eid)
    pri_html = ""
    if cl and "error" not in cl:
        p = st.session_state.overrides.get(eid, cl.get("priority", "later"))
        c = PRIORITY_CFG[p]
        pri_html = f'<span class="pri-tag" style="background:{c["tag_bg"]};color:{c["tag_fg"]}">{c["label"]}</span>'

    sel_cls = "sel" if sel else ""
    st.markdown(
        f'<div class="eml {sel_cls}"><div class="eml-row">'
        f'<div class="eml-av" style="background:{ac}">{ini}</div>'
        f'<div class="eml-c">'
        f'<div class="eml-from">{short}</div>'
        f'<div class="eml-subj">{email["subject"][:45]}</div>'
        f'<div class="eml-prev">{prev}</div>'
        f'</div>'
        f'<div class="eml-meta"><div class="eml-time">{ts}</div>{pri_html}</div>'
        f'</div></div>', unsafe_allow_html=True)

    btn_label = f"→ {short[:10]}" if sel else f"{short[:10]}"
    if st.button(btn_label, key=f"s_{eid}", use_container_width=True):
        st.session_state.selected_email = eid
        st.rerun()


def render_email_list(col):
    with col:
        classified = bool(st.session_state.classifications)
        counts = {"act_now": 0, "later": 0, "ignore": 0}
        if classified:
            for e in MOCK_EMAILS:
                p = _eff_pri(e["id"])
                if p:
                    counts[p] = counts.get(p, 0) + 1

        tab_all, tab_now, tab_later, tab_other = st.tabs([
            f"全部 ({len(MOCK_EMAILS)})",
            f"🔴 重要 ({counts['act_now']})" if classified else "🔴 重要",
            f"🟡 稍后 ({counts['later']})" if classified else "🟡 稍后",
            f"⚪ 其他 ({counts['ignore']})" if classified else "⚪ 其他",
        ])

        with tab_all:
            for email in MOCK_EMAILS:
                _render_one_email(email)

        with tab_now:
            if not classified:
                st.caption("运行 AI Triage 后显示")
            else:
                matched = [e for e in MOCK_EMAILS if _eff_pri(e["id"]) == "act_now"]
                if matched:
                    for e in matched:
                        _render_one_email(e)
                else:
                    st.caption("没有重要邮件 🎉")

        with tab_later:
            if not classified:
                st.caption("运行 AI Triage 后显示")
            else:
                matched = [e for e in MOCK_EMAILS if _eff_pri(e["id"]) == "later"]
                if matched:
                    for e in matched:
                        _render_one_email(e)
                else:
                    st.caption("没有稍后处理的邮件")

        with tab_other:
            if not classified:
                st.caption("运行 AI Triage 后显示")
            else:
                matched = [e for e in MOCK_EMAILS if _eff_pri(e["id"]) == "ignore"]
                if matched:
                    for e in matched:
                        _render_one_email(e)
                else:
                    st.caption("没有可忽略的邮件")


# ── Col 4: Reading pane + Agent panel ─────────────────────────────

def render_reading_and_agent(col):
    with col:
        eid = st.session_state.selected_email
        email = next((e for e in MOCK_EMAILS if e["id"] == eid), None) if eid else None

        if not email:
            st.markdown('<div style="text-align:center;color:#C0C0C0;padding-top:80px;font-size:14px">'
                        '← 选择一封邮件以阅读</div>', unsafe_allow_html=True)
            _render_agent_panel(None)
            return

        # Reading pane
        short = _short(email["from_name"])
        ini = _ini(short)
        ac = _acolor(short)
        to_str = ", ".join(email["to"])
        cc_str = ", ".join(email["cc"]) if email["cc"] else ""
        body = email["body"].replace("<", "&lt;").replace(">", "&gt;")

        st.markdown(f'<div class="rp-subj">{email["subject"]}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="rp-sender">'
            f'<div class="rp-av" style="background:{ac}">{ini}</div>'
            f'<div>'
            f'<div class="rp-name">{email["from_name"]}</div>'
            f'<div class="rp-email">{email["from"]}</div>'
            f'<div class="rp-to">收件人: {to_str}{"  |  CC: "+cc_str if cc_str else ""}</div>'
            f'</div>'
            f'<div style="margin-left:auto;font-size:11px;color:#A0A0A0">{email["timestamp"]}</div>'
            f'<div class="rp-actions">↩ ↩↩ ↪</div>'
            f'</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="rp-body">{body}</div>', unsafe_allow_html=True)

        if email.get("thread_length", 1) > 4:
            with st.expander(f"💬 Full thread ({len(LONG_THREAD_EXAMPLE['messages'])} msgs)"):
                for msg in LONG_THREAD_EXAMPLE["messages"]:
                    sn = msg["from"].split("@")[0].replace(".", " ").title()
                    st.markdown(f"**{sn}** · {msg['timestamp']}")
                    st.text(msg["body"])
                    st.divider()

        # Agent panel below reading pane
        _render_agent_panel(email)


def _render_agent_panel(email):
    st.markdown(
        '<div class="ag-hdr"><span>🤖</span><span class="t">AI Email Agent</span>'
        '<span class="s">Add-in</span></div>', unsafe_allow_html=True)

    view = st.radio("m", ["triage", "actions", "summary", "eval"],
                    format_func=lambda x: {"triage":"📊 Triage","actions":"✅ Actions",
                                            "summary":"📜 Summary","eval":"📈 Eval"}[x],
                    horizontal=True, label_visibility="collapsed")

    if view == "triage":
        _ag_triage(email)
    elif view == "actions":
        _ag_actions(email)
    elif view == "summary":
        _ag_summary()
    elif view == "eval":
        _ag_eval()


def _ag_triage(email):
    if st.button("⚡ Classify Inbox", type="primary", use_container_width=True):
        bar = st.progress(0)
        for i, e in enumerate(MOCK_EMAILS):
            bar.progress((i+1)/len(MOCK_EMAILS), text=f"{i+1}/{len(MOCK_EMAILS)}")
            st.session_state.classifications[e["id"]] = classify_priority(e, USER_CONTEXT)
        bar.empty()
        st.rerun()

    if not st.session_state.classifications:
        st.caption("点击上方按钮对收件箱智能分类")
        return

    counts = {"act_now":0,"later":0,"ignore":0}
    for e in MOCK_EMAILS:
        p = _eff_pri(e["id"])
        if p: counts[p] = counts.get(p,0)+1
    c1,c2,c3 = st.columns(3)
    c1.metric("🔴",counts["act_now"])
    c2.metric("🟡",counts["later"])
    c3.metric("⚪",counts["ignore"])

    if not email:
        st.caption("← 选择邮件查看分类详情")
        return
    eid = email["id"]
    cl = st.session_state.classifications.get(eid)
    if not cl or "error" in cl:
        return

    p = st.session_state.overrides.get(eid, cl.get("priority","later"))
    cfg = PRIORITY_CFG[p]
    st.markdown("---")
    st.markdown(
        f'<div class="ag-card {p}">'
        f'<div style="display:flex;justify-content:space-between;align-items:center">'
        f'<strong>{_short(email["from_name"])}</strong>'
        f'<span class="pri-tag" style="background:{cfg["tag_bg"]};color:{cfg["tag_fg"]}">{cfg["label"]}</span>'
        f'</div>'
        f'<div style="font-size:11px;color:#888;margin-top:2px">Confidence: {cl.get("confidence","N/A")}</div>'
        f'</div>', unsafe_allow_html=True)

    for r in cl.get("reasons",[]):
        st.markdown(f"<div style='font-size:11px;color:#666;padding:1px 0'>• {r}</div>", unsafe_allow_html=True)
    excerpt = cl.get("key_excerpt","")
    if excerpt:
        st.markdown(f'<div class="ag-excerpt">"{excerpt}"</div>', unsafe_allow_html=True)
    action = cl.get("action_suggestion","none")
    if action != "none":
        st.caption(f"Suggested: **{action}**")

    options = ["act_now","later","ignore"]
    idx = options.index(p) if p in options else 1
    new_p = st.selectbox("Override", options, index=idx, key=f"ov_{eid}",
                         format_func=lambda x: PRIORITY_CFG[x]["label"])
    raw_p = cl.get("priority","later")
    if new_p != raw_p:
        st.session_state.overrides[eid] = new_p
    elif eid in st.session_state.overrides:
        del st.session_state.overrides[eid]


def _ag_actions(email):
    if not email:
        st.caption("← 选择邮件提取待办")
        return
    eid = email["id"]
    st.caption(f"**{_short(email['from_name'])}** — {email['subject'][:35]}")

    if st.button("📝 Extract", type="primary", use_container_width=True, key="ext"):
        with st.spinner("分析中..."):
            st.session_state.action_items[eid] = extract_action_items(email, USER_CONTEXT)

    ai = st.session_state.action_items.get(eid)
    if ai and "error" not in ai:
        items = ai.get("action_items",[])
        for j,item in enumerate(items):
            urg = item.get("urgency","medium")
            icon = URGENCY_ICONS.get(urg,"🟡")
            ti = "📅" if item.get("type")=="calendar_event" else "☑️"
            st.markdown(
                f'<div class="ag-card">{icon}{ti} <strong>{item["task"]}</strong><br/>'
                f'<span style="font-size:10px;color:#888">Due: {item.get("due","unspecified")}</span></div>',
                unsafe_allow_html=True)
            if st.button("✅ Add to To Do", key=f"c_{eid}_{j}", use_container_width=True):
                st.session_state.confirmed_todos.append(item)
                st.toast(f"✅ {item['task']}")
        if not items:
            st.info("未发现待办")
    elif ai and "error" in ai:
        st.error(ai["error"])

    if st.session_state.confirmed_todos:
        st.markdown("---")
        for it in st.session_state.confirmed_todos:
            st.markdown(f"☑️ {it['task']}")


def _ag_summary():
    thread = LONG_THREAD_EXAMPLE
    st.caption(f"**{thread['subject'][:35]}** · {len(thread['messages'])} msgs")
    if st.button("📜 Summarize", type="primary", use_container_width=True, key="sum"):
        with st.spinner("生成摘要..."):
            st.session_state.thread_summary = summarize_thread(thread, USER_CONTEXT)

    s = st.session_state.thread_summary
    if not s: return
    if "error" in s:
        st.error(s["error"]); return

    st.markdown(f'<div class="sum-block"><h4>📌 Topic</h4><p>{s.get("topic","")}</p></div>', unsafe_allow_html=True)
    kp = "".join(f"<li>{p}</li>" for p in s.get("key_points",[]))
    st.markdown(f'<div class="sum-block"><h4>🔑 Key Points</h4><ul>{kp}</ul></div>', unsafe_allow_html=True)
    for c in s.get("direction_changes",[]):
        st.markdown(f'<div class="dir-change">⚠️ {c}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sum-block"><h4>📍 Status</h4><p>{s.get("current_status","")}</p></div>', unsafe_allow_html=True)
    acts = s.get("action_required",[])
    if acts:
        a = "".join(f"<li><strong>{a}</strong></li>" for a in acts)
        st.markdown(f'<div class="sum-block"><h4>🎯 Actions</h4><ul>{a}</ul></div>', unsafe_allow_html=True)


def _ag_eval():
    if not st.session_state.classifications:
        st.caption("先运行 Triage"); return
    results = []
    for e in MOCK_EMAILS:
        cl = st.session_state.classifications.get(e["id"])
        if cl and "error" not in cl:
            pred = cl.get("priority","N/A"); exp = e.get("expected_priority","?")
            results.append({"ok":pred==exp,"pred":pred,"exp":exp,
                            "subj":e["subject"][:25],"conf":cl.get("confidence","")})
    ok = sum(r["ok"] for r in results); total = len(results)
    c1,c2 = st.columns(2)
    c1.metric("Accuracy", f"{ok/total:.0%}" if total else "—")
    c2.metric("Score", f"{ok}/{total}")
    misses = sum(1 for e in MOCK_EMAILS if e.get("expected_priority")=="act_now"
                 and st.session_state.classifications.get(e["id"],{}).get("priority")=="ignore")
    exp_an = sum(1 for e in MOCK_EMAILS if e.get("expected_priority")=="act_now")
    st.metric("Critical Miss", f"{misses}/{exp_an}",
              delta="Safe" if misses==0 else "DANGER",
              delta_color="normal" if misses==0 else "inverse")
    st.markdown("---")
    for r in results:
        st.markdown(f"{'✅' if r['ok'] else '❌'} **{r['subj']}** `{r['exp']}`→`{r['pred']}`")


# ── Main ──────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="Outlook · AI Agent", page_icon="✉️",
                       layout="wide", initial_sidebar_state="collapsed")
    init_state()
    inject_css()
    render_topbar()
    render_toolbar()

    # 4-column Outlook layout
    col_nav, col_folders, col_list, col_read = st.columns([0.4, 1.5, 2.5, 5])

    render_icon_nav(col_nav)
    render_folders(col_folders)
    render_email_list(col_list)
    render_reading_and_agent(col_read)


if __name__ == "__main__":
    main()
