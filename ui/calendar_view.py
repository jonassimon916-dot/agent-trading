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

COLORS = {
    "bg": "#1a1a2e", "card": "#16213e", "border": "#2a2a4a",
    "text": "#e0e0e0", "text_dim": "#8892a4", "accent": "#00d4aa",
    "green": "#00c853", "red": "#ff1744",
}

CSS = """
<style>
.cal-container {
  background: """ + COLORS["bg"] + """;
  border-radius: 12px;
  padding: 16px;
  margin: 8px 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
.cal-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid """ + COLORS["border"] + """;
}
.cal-header h3 {
  color: """ + COLORS["text"] + """;
  margin: 0; font-size: 18px; font-weight: 600;
}
.cal-stats {
  display: flex; gap: 12px; color: """ + COLORS["text_dim"] + """;
  font-size: 13px;
}
.cal-stats span { background: """ + COLORS["card"] + """; padding: 4px 10px; border-radius: 6px; }
.cal-stats .high { color: """ + COLORS["red"] + """; font-weight: 600; }
.cal-stats .med { color: #ff9800; font-weight: 600; }
.cal-filter-bar {
  display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px;
}
.filter-btn {
  padding: 3px 12px; border-radius: 14px; border: 1px solid """ + COLORS["border"] + """;
  background: """ + COLORS["card"] + """; color: """ + COLORS["text_dim"] + """;
  cursor: pointer; font-size: 12px; transition: all 0.2s;
}
.filter-btn.active {
  background: """ + COLORS["accent"] + """; color: #fff; border-color: """ + COLORS["accent"] + """;
}
.filter-btn.high.active { background: """ + COLORS["red"] + """; border-color: """ + COLORS["red"] + """; }
.filter-btn.med.active { background: #ff9800; border-color: #ff9800; }
.cal-day-group { margin-bottom: 16px; }
.cal-day-header {
  color: """ + COLORS["accent"] + """;
  font-size: 14px; font-weight: 600;
  padding: 6px 0; margin-bottom: 4px;
  border-bottom: 1px solid """ + COLORS["border"] + """;
}
.cal-row {
  display: flex; align-items: center; padding: 7px 8px;
  border-radius: 6px; font-size: 13px; gap: 8px;
  transition: background 0.15s;
  border-bottom: 1px solid rgba(255,255,255,0.03);
}
.cal-row:hover { background: rgba(255,255,255,0.05); }
.cal-row .dot { font-size: 14px; width: 20px; text-align: center; }
.cal-row .time {
  color: """ + COLORS["text_dim"] + """; width: 50px; font-size: 12px;
  font-family: 'SF Mono', 'Courier New', monospace;
}
.cal-row .flag { font-size: 16px; width: 28px; text-align: center; }
.cal-row .name {
  flex: 1; color: """ + COLORS["text"] + """;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.cal-row .name.high { font-weight: 600; }
.cal-row .val {
  width: 72px; text-align: right; font-family: 'SF Mono', 'Courier New', monospace;
  font-size: 12px;
}
.cal-row .val.green { color: """ + COLORS["green"] + """; }
.cal-row .val.red { color: """ + COLORS["red"] + """; }
.cal-row .val.dim { color: """ + COLORS["text_dim"] + """; }
.cal-row .badge {
  font-size: 10px; padding: 1px 7px; border-radius: 10px;
  font-weight: 600; width: 55px; text-align: center;
}
.badge-high { background: rgba(239,83,80,0.2); color: """ + COLORS["red"] + """; }
.badge-med { background: rgba(255,152,0,0.2); color: #ff9800; }
.badge-low { background: rgba(120,144,156,0.15); color: #78909c; }
.next-event {
  background: linear-gradient(135deg, """ + COLORS["card"] + """, #1a1a3e);
  border: 1px solid """ + COLORS["accent"] + """;
  border-radius: 10px; padding: 12px 16px; margin-bottom: 14px;
  display: flex; align-items: center; justify-content: space-between;
}
.next-event .label { color: """ + COLORS["text_dim"] + """; font-size: 12px; }
.next-event .title { color: """ + COLORS["text"] + """; font-size: 15px; font-weight: 600; }
.next-event .countdown { color: """ + COLORS["accent"] + """; font-size: 20px; font-weight: 700; font-family: 'SF Mono', monospace; }
</style>
"""


def get_day_labels(days=7):
    now = datetime.now()
    labels = {}
    for i in range(days):
        d = now + timedelta(days=i)
        key = d.strftime("%Y-%m-%d")
        if i == 0:
            labels[key] = f"Aujourd'hui · {d.strftime('%d %b')}"
        elif i == 1:
            labels[key] = f"Demain · {d.strftime('%d %b')}"
        else:
            labels[key] = d.strftime("%A %d %b").capitalize()
    return labels


def render_calendar(events):
    st.markdown(CSS, unsafe_allow_html=True)

    if "cal_impact_filter" not in st.session_state:
        st.session_state.cal_impact_filter = [1, 0]
    if "cal_currency_filter" not in st.session_state:
        st.session_state.cal_currency_filter = []

    today = datetime.now().strftime("%Y-%m-%d")
    day_labels = get_day_labels(7)

    high_count = sum(1 for e in events if e["impact"] == 1)
    med_count = sum(1 for e in events if e["impact"] == 0)
    total = len(events)

    next_high = next((e for e in events if e["impact"] == 1), None)

    st.markdown('<div class="cal-container">', unsafe_allow_html=True)

    st.markdown('<div class="cal-header"><h3>📅 Calendrier Economique</h3>', unsafe_allow_html=True)
    st.markdown(f'<div class="cal-stats">'
                f'<span class="high">{high_count} haute{"s" if high_count > 1 else ""}</span>'
                f'<span class="med">{med_count} moyenne{"s" if med_count > 1 else ""}</span>'
                f'<span>{total} total</span>'
                f'</div></div>', unsafe_allow_html=True)

    filtered = events
    if st.session_state.cal_impact_filter:
        filtered = [e for e in filtered if e["impact"] in st.session_state.cal_impact_filter]

    top_currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]
    cur_filter = st.session_state.cal_currency_filter
    if cur_filter:
        filtered = [e for e in filtered if e["currency"] in cur_filter]

    imp_c = st.session_state.cal_impact_filter
    col_filters = st.columns([1, 1, 1, 2])
    with col_filters[0]:
        all_h = len([e for e in events if e["impact"] == 1]) > 0
        if st.button(f"🔴 Haute ({high_count})", key="filt_high",
                     type="primary" if 1 in imp_c else "secondary",
                     use_container_width=True):
            if 1 in imp_c:
                st.session_state.cal_impact_filter.remove(1)
            else:
                st.session_state.cal_impact_filter.append(1)
            st.rerun()
    with col_filters[1]:
        if st.button(f"🟠 Moyenne ({med_count})", key="filt_med",
                     type="primary" if 0 in imp_c else "secondary",
                     use_container_width=True):
            if 0 in imp_c:
                st.session_state.cal_impact_filter.remove(0)
            else:
                st.session_state.cal_impact_filter.append(0)
            st.rerun()
    with col_filters[2]:
        if cur_filter:
            label = f"Filtres ({len(cur_filter)})"
        else:
            label = "Toutes devises"
        if st.button(label, key="filt_cur", use_container_width=True):
            if cur_filter:
                st.session_state.cal_currency_filter = []
            else:
                st.session_state.cal_currency_filter = top_currencies
            st.rerun()
    with col_filters[3]:
        currency_opts = st.multiselect(
            "", top_currencies,
            default=cur_filter,
            placeholder="Devises...",
            label_visibility="collapsed",
            key="cur_sel",
        )
        if currency_opts != cur_filter:
            st.session_state.cal_currency_filter = currency_opts
            st.rerun()

    if next_high and next_high["day"]:
        now = datetime.now()
        try:
            dt_str = f"{next_high['day']} {next_high['time'] or '00:00'}"
            event_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            remaining = event_dt - now
            if remaining.total_seconds() > 0:
                hours = int(remaining.total_seconds() // 3600)
                mins = int((remaining.total_seconds() % 3600) // 60)
                cd = f"{hours}h {mins:02d}min"
                st.markdown(
                    f'<div class="next-event">'
                    f'<div><div class="label">Prochain evenement haute importance</div>'
                    f'<div class="title">{FLAGS.get(next_high["currency"], "")} {next_high["event"][:45]}</div></div>'
                    f'<div class="countdown">{cd}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        except:
            pass

    prev_day = None
    grouped = []
    for e in filtered:
        if e["day"] != prev_day:
            grouped.append({"day": e["day"], "events": []})
            prev_day = e["day"]
        grouped[-1]["events"].append(e)

    for group in grouped:
        day_str = group["day"]
        label = day_labels.get(day_str, day_str)
        st.markdown(f'<div class="cal-day-header">{label}</div>', unsafe_allow_html=True)

        for e in group["events"]:
            imp = e["impact"]
            cfg = IMPACT_CFG.get(imp, IMPACT_CFG[-1])
            currency = e.get("currency", "")
            flag = FLAGS.get(currency, "")
            time_str = e.get("time", "") or "--:--"
            event_name = e.get("event", "")[:45]
            actual = e.get("actual", "") or "-"
            forecast = e.get("forecast", "") or "-"
            previous = e.get("previous", "") or "-"

            dirn = e.get("direction", "")
            act_cls = "green" if dirn == "up" else ("red" if dirn == "down" else "dim")
            badge_cls = "badge-high" if imp == 1 else ("badge-med" if imp == 0 else "badge-low")
            name_cls = "high" if imp == 1 else ""

            st.markdown(
                f'<div class="cal-row">'
                f'<span class="dot">{cfg["dot"]}</span>'
                f'<span class="time">{time_str}</span>'
                f'<span class="flag">{flag}</span>'
                f'<span class="name {name_cls}">{event_name}</span>'
                f'<span class="badge {badge_cls}">{cfg["label"]}</span>'
                f'<span class="val {act_cls}">{actual}</span>'
                f'<span class="val dim">{forecast}</span>'
                f'<span class="val dim">{previous}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if not filtered:
        st.markdown(
            f'<div style="color:{COLORS["text_dim"]};text-align:center;padding:24px;">'
            f'Aucun evenement avec les filtres actuels</div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
