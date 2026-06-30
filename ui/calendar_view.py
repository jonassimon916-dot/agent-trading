import streamlit as st
from datetime import datetime, timedelta

IMPACT_CFG = {
    1: {"label": "HIGH", "color": "#f85149", "dot": "🔴"},
    0: {"label": "MED", "color": "#d29922", "dot": "🟠"},
    -1: {"label": "LOW", "color": "#484858", "dot": "⚪"},
}
FLAGS = {"USD":"🇺🇸","EUR":"🇪🇺","GBP":"🇬🇧","JPY":"🇯🇵","CHF":"🇨🇭","CAD":"🇨🇦","AUD":"🇦🇺","NZD":"🇳🇿","CNY":"🇨🇳"}
TOP_CUR = ["USD","EUR","GBP","JPY","CHF","CAD","AUD","NZD"]


def day_label(days=7):
    now = datetime.now()
    labels = {}
    for i in range(days):
        d = now + timedelta(days=i)
        k = d.strftime("%Y-%m-%d")
        labels[k] = f"{'Aujourdhui' if i==0 else 'Demain' if i==1 else d.strftime('%A %d %b').capitalize()}"
    return labels


def render_calendar(events):
    if "cal_imp" not in st.session_state:
        st.session_state.cal_imp = [1, 0]
    if "cal_cur" not in st.session_state:
        st.session_state.cal_cur = []

    day_labels = day_label(7)
    high_n = sum(1 for e in events if e["impact"] == 1)
    med_n = sum(1 for e in events if e["impact"] == 0)
    important_events = [e for e in events if e["impact"] >= 0]

    st.markdown(f"""<div style="background:linear-gradient(135deg,#15152a,#1a1a35);border:1px solid #2a2a4a;border-radius:12px;padding:12px 16px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;">
<div><span style="color:#f0f0ff;font-weight:600;font-size:14px;">Calendrier Economique</span>
<span style="color:#3a3a5a;font-size:11px;margin-left:8px;">{len(important_events)} evenements</span></div>
<div style="display:flex;gap:12px;">
<span style="color:#f85149;font-size:12px;font-weight:600;">{high_n} HIGH</span>
<span style="color:#d29922;font-size:12px;font-weight:600;">{med_n} MED</span>
</div></div>""", unsafe_allow_html=True)

    imp_sel = st.session_state.cal_imp
    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
    with c1:
        if st.button(f"HIGH ({high_n})", key="fi_h", type="primary" if 1 in imp_sel else "secondary", use_container_width=True):
            st.session_state.cal_imp = [x for x in imp_sel if x != 1] if 1 in imp_sel else sorted(set(imp_sel + [1]))
            st.rerun()
    with c2:
        if st.button(f"MED ({med_n})", key="fi_m", type="primary" if 0 in imp_sel else "secondary", use_container_width=True):
            st.session_state.cal_imp = [x for x in imp_sel if x != 0] if 0 in imp_sel else sorted(set(imp_sel + [0]))
            st.rerun()
    with c3:
        cur = st.session_state.cal_cur
        lbl = f"{len(cur)} devises" if cur else "Toutes"
        if st.button(lbl, key="fi_c", use_container_width=True):
            st.session_state.cal_cur = [] if cur else TOP_CUR
            st.rerun()
    with c4:
        nc = st.multiselect("", TOP_CUR, default=st.session_state.cal_cur, placeholder="Devises", label_visibility="collapsed", key="fs")
        if nc != st.session_state.cal_cur:
            st.session_state.cal_cur = nc
            st.rerun()

    filtered = events
    if st.session_state.cal_imp:
        filtered = [e for e in filtered if e["impact"] in st.session_state.cal_imp]
    if st.session_state.cal_cur:
        filtered = [e for e in filtered if e["currency"] in st.session_state.cal_cur]

    next_h = next((e for e in filtered if e["impact"] == 1), None)
    if next_h and next_h.get("day"):
        try:
            dt = datetime.strptime(f"{next_h['day']} {next_h.get('time','00:00')}", "%Y-%m-%d %H:%M")
            rem = dt - datetime.now()
            if rem.total_seconds() > 0:
                h, m = int(rem.total_seconds() // 3600), int((rem.total_seconds() % 3600) // 60)
                st.markdown(f"""<div style="background:linear-gradient(135deg,#1a1a35,#151540);border:1px solid #7878ff;border-radius:10px;padding:10px 14px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;">
<div><span style="color:#7878a0;font-size:11px;">Prochain HIGH</span><br><span style="color:#f0f0ff;font-size:14px;font-weight:600;">{FLAGS.get(next_h['currency'],'')} {next_h['event'][:40]}</span></div>
<span style="color:#58a6ff;font-size:20px;font-weight:700;font-family:'JetBrains Mono',monospace;">{h}:{m:02d}</span>
</div>""", unsafe_allow_html=True)
        except:
            pass

    prev_day = None
    row_i = 0
    for e in filtered:
        if e["day"] != prev_day:
            st.markdown(f"""<div style="color:#7878ff;font-size:13px;font-weight:600;padding:8px 4px 4px;border-bottom:1px solid #1e1e2e;">{day_labels.get(e['day'], e['day'])}</div>""", unsafe_allow_html=True)
            prev_day = e["day"]

        cfg = IMPACT_CFG.get(e["impact"], IMPACT_CFG[-1])
        flag = FLAGS.get(e.get("currency", ""), "")
        has_data = bool(e.get("actual")) or bool(e.get("forecast"))
        eid = e.get("id", f"r{row_i}")
        rkey = f"res_{eid}"
        shown = rkey in st.session_state

        c = st.columns([0.4, 0.6, 0.3, 2.2, 0.6, 0.8, 0.8, 0.8, 0.5])
        with c[0]:
            st.markdown(f"<span style='font-size:14px'>{cfg['dot']}</span>", unsafe_allow_html=True)
        with c[1]:
            st.markdown(f"<span style='color:#484858;font-size:12px;font-family:monospace'>{e.get('time','--:--')}</span>", unsafe_allow_html=True)
        with c[2]:
            st.markdown(f"<span style='font-size:14px'>{flag}</span>", unsafe_allow_html=True)
        with c[3]:
            w = "600" if e["impact"] == 1 else "400"
            st.markdown(f"<span style='color:#e1e1e6;font-weight:{w};font-size:13px'>{e.get('event','')[:40]}</span>", unsafe_allow_html=True)
        with c[4]:
            bc = cfg["color"]
            st.markdown(f"<span style='color:{bc};font-size:10px;font-weight:700'>{cfg['label']}</span>", unsafe_allow_html=True)
        with c[5]:
            a = e.get("actual","") or "-"
            d = e.get("direction","")
            ac = "#3fb950" if d=="up" else ("#f85149" if d=="down" else "#484858")
            st.markdown(f"<span style='color:{ac};font-size:12px;font-family:monospace'>{a}</span>", unsafe_allow_html=True)
        with c[6]:
            st.markdown(f"<span style='color:#484858;font-size:12px;font-family:monospace'>{e.get('forecast','') or '-'}</span>", unsafe_allow_html=True)
        with c[7]:
            st.markdown(f"<span style='color:#484858;font-size:12px;font-family:monospace'>{e.get('previous','') or '-'}</span>", unsafe_allow_html=True)
        with c[8]:
            if has_data and not shown:
                if st.button("AI", key=f"ca_{eid}_{row_i}", use_container_width=True):
                    from agent.analyst import analyze_calendar_event
                    with st.spinner(""):
                        r = analyze_calendar_event(e)
                    st.session_state[rkey] = r
                    st.rerun()

        if shown:
            r = st.session_state[rkey]
            ics = st.columns(5)
            for ci, (s, v) in enumerate([("XAUUSD", r.get("impact_xauusd","neutral")), ("DXY", r.get("impact_dxy","neutral")), ("EURUSD", r.get("impact_eurusd","neutral")), ("BTCUSD", r.get("impact_btc","neutral")), ("NASDAQ", r.get("impact_nasdaq","neutral"))]):
                ic = "🟢" if v=="bullish" else ("🔴" if v=="bearish" else "⚪")
                ics[ci].markdown(f"<span style='font-size:12px;color:#e1e1e6'>{ic} **{s}**<br><span style='color:{'#3fb950' if v=='bullish' else '#f85149' if v=='bearish' else '#484858'}'>{v}</span></span>", unsafe_allow_html=True)
            st.caption(r.get("raisonnement",""))
            if st.button("x", key=f"cx_{eid}_{row_i}", use_container_width=True):
                del st.session_state[rkey]
                st.rerun()
        row_i += 1

    if not filtered:
        st.markdown("<div style='color:#484858;text-align:center;padding:30px;'>Aucun evenement</div>", unsafe_allow_html=True)
