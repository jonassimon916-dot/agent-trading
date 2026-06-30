import streamlit as st
from datetime import datetime, timedelta

IMPACT_CFG = {
    1: {"label": "Haute", "color": "#ef5350", "bg": "rgba(239,83,80,0.15)", "dot": "🔴"},
    0: {"label": "Moyenne", "color": "#ff9800", "bg": "rgba(255,152,0,0.12)", "dot": "🟠"},
    -1: {"label": "Basse", "color": "#78909c", "bg": "rgba(120,144,156,0.08)", "dot": "⚪"},
}

FLAGS = {
    "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "JPY": "🇯🇵",
    "CHF": "🇨🇭", "CAD": "🇨🇦", "AUD": "🇦🇺", "NZD": "🇳🇿", "CNY": "🇨🇳",
}

BG = "#0d1117"
CARD = "#161b22"
BORDER = "#30363d"
TEXT = "#e6edf3"
DIM = "#8b949e"
GREEN = "#3fb950"
RED = "#f85149"
ORANGE = "#d29922"
ACCENT = "#58a6ff"

CSS = f"""
<style>
.cal-wrap {{
  background: {BG}; border-radius: 12px; padding: 16px; margin: 10px 0;
  border: 1px solid {BORDER};
}}
.cal-header {{
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid {BORDER};
}}
.cal-header h3 {{ color: {TEXT}; margin: 0; font-size: 18px; }}
.cal-stats {{ display: flex; gap: 8px; font-size: 13px; }}
.cal-stat {{ background: {CARD}; padding: 4px 10px; border-radius: 6px; border: 1px solid {BORDER}; }}
.cal-stat.high {{ color: {RED}; }}
.cal-stat.med {{ color: {ORANGE}; }}
.cal-stat.total {{ color: {DIM}; }}
.cal-next {{
  background: linear-gradient(135deg, {CARD}, #0d1d3a);
  border: 1px solid {ACCENT}; border-radius: 10px;
  padding: 12px 16px; margin-bottom: 14px;
  display: flex; justify-content: space-between; align-items: center;
}}
.cal-next .nl {{ color: {DIM}; font-size: 12px; }}
.cal-next .nt {{ color: {TEXT}; font-size: 15px; font-weight: 600; }}
.cal-next .nc {{ color: {ACCENT}; font-size: 22px; font-weight: 700; font-family: 'SF Mono', monospace; }}
.cal-day-h {{ color: {ACCENT}; font-size: 14px; font-weight: 600; padding: 8px 0 4px; border-bottom: 1px solid {BORDER}; }}
.cal-empty {{ color: {DIM}; text-align: center; padding: 30px; }}
</style>
"""


def get_day_labels(days=7):
    now = datetime.now()
    labels = {}
    for i in range(days):
        d = now + timedelta(days=i)
        key = d.strftime("%Y-%m-%d")
        if i == 0:
            labels[key] = f"Aujourd'hui {d.strftime('%d %b')}"
        elif i == 1:
            labels[key] = f"Demain {d.strftime('%d %b')}"
        else:
            labels[key] = d.strftime("%A %d %b").capitalize()
    return labels


def render_calendar(events):
    st.markdown(CSS, unsafe_allow_html=True)

    if "cal_impact" not in st.session_state:
        st.session_state.cal_impact = [1, 0]
    if "cal_cur" not in st.session_state:
        st.session_state.cal_cur = []

    today = datetime.now().strftime("%Y-%m-%d")
    day_labels = get_day_labels(7)
    top_cur = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]

    high_n = sum(1 for e in events if e["impact"] == 1)
    med_n = sum(1 for e in events if e["impact"] == 0)
    low_n = sum(1 for e in events if e["impact"] == -1)

    next_high = next((e for e in events if e["impact"] == 1), None)

    st.markdown('<div class="cal-wrap">', unsafe_allow_html=True)

    st.markdown(f"""<div class="cal-header"><h3>Calendrier Economique</h3>
    <div class="cal-stats">
      <span class="cal-stat high">Red {high_n}</span>
      <span class="cal-stat med">Orange {med_n}</span>
      <span class="cal-stat total">{high_n+med_n+low_n} total</span>
    </div></div>""", unsafe_allow_html=True)

    imp_sel = st.session_state.cal_impact
    cols_f = st.columns([1, 1, 1, 2])
    with cols_f[0]:
        if st.button(f"Haute ({high_n})", key="cf_h",
                     type="primary" if 1 in imp_sel else "secondary",
                     use_container_width=True):
            st.session_state.cal_impact = [x for x in imp_sel if x != 1] if 1 in imp_sel else sorted(set(imp_sel + [1]))
            st.rerun()
    with cols_f[1]:
        if st.button(f"Moyenne ({med_n})", key="cf_m",
                     type="primary" if 0 in imp_sel else "secondary",
                     use_container_width=True):
            st.session_state.cal_impact = [x for x in imp_sel if x != 0] if 0 in imp_sel else sorted(set(imp_sel + [0]))
            st.rerun()
    with cols_f[2]:
        cur_sel = st.session_state.cal_cur
        lbl = f"Devises ({len(cur_sel)})" if cur_sel else "Toutes"
        if st.button(lbl, key="cf_c", use_container_width=True):
            st.session_state.cal_cur = [] if cur_sel else top_cur
            st.rerun()
    with cols_f[3]:
        new_cur = st.multiselect("", top_cur, default=st.session_state.cal_cur,
                                  placeholder="Devises...", label_visibility="collapsed", key="cf_sel")
        if new_cur != st.session_state.cal_cur:
            st.session_state.cal_cur = new_cur
            st.rerun()

    filtered = events
    if st.session_state.cal_impact:
        filtered = [e for e in filtered if e["impact"] in st.session_state.cal_impact]
    if st.session_state.cal_cur:
        filtered = [e for e in filtered if e["currency"] in st.session_state.cal_cur]

    if next_high and next_high.get("day"):
        try:
            dt_s = f"{next_high['day']} {next_high.get('time', '00:00')}"
            dt = datetime.strptime(dt_s, "%Y-%m-%d %H:%M")
            rem = dt - datetime.now()
            if rem.total_seconds() > 0:
                h, m = int(rem.total_seconds() // 3600), int((rem.total_seconds() % 3600) // 60)
                st.markdown(f"""<div class="cal-next">
                <div><div class="nl">Prochain evenement haute importance</div>
                <div class="nt">{FLAGS.get(next_high['currency'],'')} {next_high['event'][:45]}</div></div>
                <div class="nc">{h}h {m:02d}min</div></div>""", unsafe_allow_html=True)
        except:
            pass

    prev_day = None
    row_idx = 0
    for e in filtered:
        if e["day"] != prev_day:
            st.markdown(f'<div class="cal-day-h">{day_labels.get(e["day"], e["day"])}</div>', unsafe_allow_html=True)
            prev_day = e["day"]

        imp = e["impact"]
        cfg = IMPACT_CFG.get(imp, IMPACT_CFG[-1])
        flag = FLAGS.get(e.get("currency", ""), "")
        has_data = bool(e.get("actual")) or bool(e.get("forecast"))
        eid = e.get("id", f"r{row_idx}")
        res_key = f"cal_res_{eid}"
        show_analysis = res_key in st.session_state

        cols = st.columns([0.5, 0.8, 0.4, 2.5, 0.7, 0.9, 0.9, 0.9, 0.6])
        with cols[0]:
            st.markdown(f"<span style='font-size:16px'>{cfg['dot']}</span>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"<span style='color:{DIM};font-size:12px'>{e.get('time','--:--')}</span>", unsafe_allow_html=True)
        with cols[2]:
            st.markdown(f"<span style='font-size:15px'>{flag}</span>", unsafe_allow_html=True)
        with cols[3]:
            name = e.get("event", "")[:45]
            w = "600" if imp == 1 else "400"
            st.markdown(f"<span style='color:{TEXT};font-weight:{w};font-size:13px'>{name}</span>", unsafe_allow_html=True)
        with cols[4]:
            badge = cfg["label"]
            bc = RED if imp == 1 else (ORANGE if imp == 0 else DIM)
            st.markdown(f"<span style='color:{bc};font-size:11px;font-weight:600'>{badge}</span>", unsafe_allow_html=True)
        with cols[5]:
            a = e.get("actual", "") or "-"
            d = e.get("direction", "")
            ac = GREEN if d == "up" else (RED if d == "down" else DIM)
            st.markdown(f"<span style='color:{ac};font-size:12px;font-family:monospace'>{a}</span>", unsafe_allow_html=True)
        with cols[6]:
            fv = e.get("forecast", "") or "-"
            st.markdown(f"<span style='color:{DIM};font-size:12px;font-family:monospace'>{fv}</span>", unsafe_allow_html=True)
        with cols[7]:
            pv = e.get("previous", "") or "-"
            st.markdown(f"<span style='color:{DIM};font-size:12px;font-family:monospace'>{pv}</span>", unsafe_allow_html=True)
        with cols[8]:
            if has_data and not show_analysis:
                if st.button("AI", key=f"cai_{eid}_{row_idx}", help="Analyser avec IA", use_container_width=True):
                    from agent.analyst import analyze_calendar_event
                    with st.spinner("Analyse IA en cours..."):
                        analysis = analyze_calendar_event(e)
                    st.session_state[res_key] = analysis
                    st.rerun()

        if show_analysis:
            analysis = st.session_state[res_key]
            impact_cols = st.columns(5)
            impacts = [
                ("XAUUSD", analysis.get("impact_xauusd", "neutral")),
                ("DXY", analysis.get("impact_dxy", "neutral")),
                ("EURUSD", analysis.get("impact_eurusd", "neutral")),
                ("BTCUSD", analysis.get("impact_btc", "neutral")),
                ("NASDAQ", analysis.get("impact_nasdaq", "neutral")),
            ]
            for ci, (sym, imp_act) in enumerate(impacts):
                icon = "🟢" if imp_act == "bullish" else ("🔴" if imp_act == "bearish" else "⚪")
                with impact_cols[ci]:
                    st.markdown(f"<span style='font-size:12px'>{icon} **{sym}**: {imp_act}</span>", unsafe_allow_html=True)
            st.caption(analysis.get("raisonnement", ""))
            if st.button("Fermer", key=f"clo_{eid}_{row_idx}"):
                del st.session_state[res_key]
                st.rerun()

        row_idx += 1

    if not filtered:
        st.markdown(f'<div class="cal-empty">Aucun evenement avec ces filtres</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
