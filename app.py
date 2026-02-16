import streamlit as st
import json
import random
import pandas as pd
import os
from datetime import datetime, timedelta

# --- ВЕРСИЯ 27.0 (SIDEBAR SETTINGS, PERSISTENT CONFIG, SMART MATRIX) ---
st.set_page_config(page_title="Poker Trainer Pro", page_icon="♠️", layout="wide") # Layout wide для сайдбара

# --- CSS СТИЛИ ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    
    /* СТОЛ (Центрируем на широком экране) */
    .game-area { 
        position: relative; width: 100%; max-width: 500px; height: 320px; 
        margin: 20px auto; 
        background: radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%); 
        border: 10px solid #3e2723; border-radius: 160px; 
        box-shadow: 0 5px 20px rgba(0,0,0,0.6); 
    }
    .table-logo { position: absolute; top: 35%; left: 50%; transform: translate(-50%, -50%); color: rgba(255,255,255,0.08); font-weight: bold; font-size: 24px; pointer-events: none; }
    
    /* МЕСТА */
    .seat { position: absolute; width: 55px; height: 55px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 3px 6px rgba(0,0,0,0.5); z-index: 5; }
    .seat-active { border-color: #ffd700; background: rgba(20,20,20,0.95); }
    .seat-folded { opacity: 0.5; border-color: #333; }
    .seat-label { color: #fff; font-weight: bold; font-size: 12px; }
    .opp-cards { position: absolute; top: -12px; width: 26px; height: 36px; background: #fff; border-radius: 3px; border: 1px solid #ccc; background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); box-shadow: 2px 2px 4px rgba(0,0,0,0.5); z-index: 4; }
    .opp-c1 { transform: rotate(-10deg); left: 8px; } .opp-c2 { transform: rotate(10deg); left: 20px; }
    .dealer-button { position: absolute; width: 22px; height: 22px; background: #ffd700; border: 2px solid #e6c200; border-radius: 50%; color: #000; font-weight: bold; font-size: 11px; display: flex; justify-content: center; align-items: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.5); z-index: 15; }
    .poker-chip { width: 24px; height: 24px; background: #111; border: 3px dashed #d32f2f; border-radius: 50%; box-shadow: 1px 1px 4px rgba(0,0,0,0.7); }
    .blind-stack { position: absolute; z-index: 15; display: flex; flex-direction: column; align-items: center; }
    .chip-stacked { margin-top: -18px; }
    .pos-1 { bottom: 20%; left: 4%; } .pos-2 { top: 20%; left: 4%; } .pos-3 { top: -20px; left: 50%; transform: translateX(-50%); } .pos-4 { top: 20%; right: 4%; } .pos-5 { bottom: 20%; right: 4%; }
    .hero-panel { position: absolute; bottom: -40px; left: 50%; transform: translateX(-50%); background: #1a1a1a; border: 3px solid #ffd700; border-radius: 14px; padding: 6px 15px; display: flex; gap: 8px; box-shadow: 0 0 20px rgba(255,215,0,0.25); z-index: 10; align-items: center; }
    .card { width: 50px; height: 75px; background: white; border-radius: 4px; position: relative; color: black; font-family: 'Arial', sans-serif; }
    .tl { position: absolute; top: 2px; left: 3px; font-weight: bold; font-size: 16px; line-height: 1.1; }
    .cent { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 28px; }
    .suit-red { color: #d32f2f; } .suit-blue { color: #1e88e5; } .suit-black { color: #111; }
    div.stButton > button { width: 100%; height: 60px !important; font-size: 18px !important; font-weight: 800; border-radius: 12px; border: none; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 5px; }
    div[data-testid="column"] div.stButton > button { width: 100%; }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button { background-color: #c62828 !important; color: white !important; box-shadow: 0 4px 0 #8e0000; }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { background-color: #2e7d32 !important; color: white !important; box-shadow: 0 4px 0 #1b5e20; }
    .range-grid { display: grid; grid-template-columns: repeat(13, 1fr); gap: 2px; margin-top: 10px; font-family: monospace; max-width: 500px; margin: 10px auto; }
    .grid-cell { aspect-ratio: 1; display: flex; justify-content: center; align-items: center; font-size: 10px; color: #ddd; border-radius: 2px; cursor: default; position: relative; }
    .current-hand-highlight { border: 2px solid #ffeb3b !important; box-shadow: 0 0 8px #ffeb3b; z-index: 10; transform: scale(1.1); font-weight: bold; color: #fff !important; }
</style>
""", unsafe_allow_html=True)

# --- ФАЙЛЫ ---
HISTORY_FILE = 'history_log.csv'
SRS_FILE = 'srs_data.json'
RANGES_FILE = 'ranges.json'
SETTINGS_FILE = 'user_settings.json' # Файл для сохранения настроек
ranks = 'AKQJT98765432'
all_hands = [r1+r2+s for r1 in ranks for r2 in ranks for s in ('s','o') if (r1<r2 and s=='s') or (r1>r2 and s=='o')] + [r+r for r in ranks]

# --- ЗАГРУЗЧИКИ ---
@st.cache_data(ttl=0)
def load_ranges():
    try:
        with open(RANGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

ranges_db = load_ranges()

def load_srs_data():
    if os.path.exists(SRS_FILE):
        try:
            with open(SRS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_srs_data(data):
    with open(SRS_FILE, 'w') as f:
        json.dump(data, f)

# --- СОХРАНЕНИЕ НАСТРОЕК (PERSISTENCE) ---
def load_user_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def save_to_history(record):
    df_new = pd.DataFrame([record])
    if not os.path.exists(HISTORY_FILE):
        df_new.to_csv(HISTORY_FILE, index=False)
    else:
        df_new.to_csv(HISTORY_FILE, mode='a', header=False, index=False)

def load_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)
    return pd.DataFrame(columns=["Date", "Spot", "Hand", "Result", "CorrectAction"])

# --- ЛОГИКА ---
def update_srs_smart(spot_id, hand, rating):
    data = load_srs_data()
    key = f"{spot_id}_{hand}"
    w = data.get(key, 100)
    if rating == 'hard': w *= 2.5
    elif rating == 'normal': w = w / 1.5 if w > 100 else w * 1.2
    elif rating == 'easy': w /= 4.0
    data[key] = int(max(1, min(w, 2000)))
    save_srs_data(data)

def get_weight(hand, range_str):
    if not range_str: return 0.0
    items = [x.strip() for x in range_str.replace('\n', ' ').split(',')]
    for item in items:
        w = 1.0; h = item
        if ':' in item: h, w_str = item.split(':'); w = float(w_str)
        if h == hand: return w
        if len(h) == 2 and h[0] != h[1] and hand.startswith(h): return w
    return 0.0

def parse_range_to_list(range_str):
    if not range_str: return []
    hand_list = []
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        if not item: continue
        h = item.split(':')[0]
        if h in all_hands: hand_list.append(h)
        elif len(h) == 2:
            if h[0] == h[1]: hand_list.append(h)
            else: hand_list.extend([h+'s', h+'o'])
    return list(set(hand_list))

def get_chip_style(seat_index):
    if seat_index == 0: return "bottom: 22%; left: 47%;"
    if seat_index == 1: return "bottom: 25%; left: 22%;"
    if seat_index == 2: return "top: 25%; left: 22%;"
    if seat_index == 3: return "top: 12%; left: 47%;"
    if seat_index == 4: return "top: 25%; right: 22%;"
    if seat_index == 5: return "bottom: 25%; right: 22%;"
    return ""

def render_range_matrix(range_str, target_hand=None):
    ranks_seq = "AKQJT98765432"
    html = '<div class="range-grid">'
    for r1 in ranks_seq:
        for r2 in ranks_seq:
            if ranks_seq.index(r1) == ranks_seq.index(r2): hand = r1 + r2
            elif ranks_seq.index(r1) < ranks_seq.index(r2): hand = r1 + r2 + 's'
            else: hand = r2 + r1 + 'o'
            w = get_weight(hand, range_str)
            
            css_class = "grid-cell"
            if target_hand and hand == target_hand:
                css_class += " current-hand-highlight"
            
            if w > 0:
                opacity = 0.3 + (0.7 * w)
                bg = f"rgba(46, 125, 50, {opacity})"
                style = f"background: {bg}; color: #fff;"
            else:
                style = "background: #222; color: #555;"
                
            html += f'<div class="{css_class}" style="{style}">{hand}</div>'
    return html + '</div>'

# --- ИНТЕРФЕЙС (SIDEBAR SETTINGS) ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    if not ranges_db:
        st.error("Ranges.json not found.")
        st.stop()

    # Загружаем сохраненные настройки
    saved_config = load_user_settings()
    
    # 1. Source
    st.subheader("1. Source")
    all_sources = list(ranges_db.keys())
    
    # Восстанавливаем галочки
    default_sources = saved_config.get("sources", [all_sources[0]]) if all_sources else []
    # Фильтруем на случай если файл изменился
    default_sources = [s for s in default_sources if s in all_sources]
    
    selected_sources = []
    for src in all_sources:
        if st.checkbox(src, value=(src in default_sources)):
            selected_sources.append(src)
            
    if not selected_sources:
        st.warning("Select source.")
        st.stop()

    # 2. Scenario
    st.subheader("2. Scenario")
    avail_scenarios = set()
    for src in selected_sources:
        if isinstance(ranges_db[src], dict):
            avail_scenarios.update(ranges_db[src].keys())
    avail_scenarios = list(avail_scenarios)
    
    saved_scenarios = saved_config.get("scenarios", [])
    default_scenarios = [s for s in saved_scenarios if s in avail_scenarios]
    if not default_scenarios and avail_scenarios: default_scenarios = [avail_scenarios[0]]
    
    selected_scenarios = []
    for sc in avail_scenarios:
        if st.checkbox(sc, value=(sc in default_scenarios)):
            selected_scenarios.append(sc)
            
    if not selected_scenarios:
        st.warning("Select scenario.")
        st.stop()

    # 3. Position Filter
    st.subheader("3. Positions")
    saved_mode = saved_config.get("mode", "All")
    mode_options = ["All", "Early (EP/MP)", "Late (CO/BU/SB)", "Manual"]
    if saved_mode not in mode_options: saved_mode = "All"
    
    train_mode = st.radio("Filter", mode_options, index=mode_options.index(saved_mode))
    
    # Сохраняем текущие настройки в файл при каждом реране
    current_conf = {
        "sources": selected_sources,
        "scenarios": selected_scenarios,
        "mode": train_mode
    }
    save_user_settings(current_conf)

    # Логика пула спотов
    final_spot_pool = []
    for src in selected_sources:
        for sc in selected_scenarios:
            if sc in ranges_db[src]:
                spots = list(ranges_db[src][sc].keys())
                for sp in spots:
                    u = sp.upper()
                    match = False
                    if train_mode == "All": match = True
                    elif train_mode == "Early (EP/MP)": match = any(x in u for x in ["EP", "UTG", "MP"])
                    elif train_mode == "Late (CO/BU/SB)": match = any(x in u for x in ["CO", "BU", "BTN", "SB"])
                    
                    if match or train_mode == "Manual":
                        final_spot_pool.append(f"{src}|{sc}|{sp}")

    if not final_spot_pool:
        st.error("No spots found.")
        st.stop()

    if train_mode == "Manual":
        manual_choice = st.selectbox("Select Spot", final_spot_pool)
        final_spot_pool = [manual_choice]

    st.divider()
    if st.button("Reset Learning Data"):
        if os.path.exists(SRS_FILE): os.remove(SRS_FILE)
        st.toast("Brain Wiped!")

# --- ОСНОВНОЕ ОКНО ---
tab_trainer, tab_stats = st.tabs(["🎮 Trainer", "📈 Statistics"])

with tab_trainer:
    if 'hand' not in st.session_state: st.session_state.hand = None
    if 'current_spot_key' not in st.session_state: st.session_state.current_spot_key = None
    if 'suits' not in st.session_state: st.session_state.suits = None
    if 'msg' not in st.session_state: st.session_state.msg = None
    if 'srs_mode' not in st.session_state: st.session_state.srs_mode = False
    if 'last_result_was_error' not in st.session_state: st.session_state.last_result_was_error = False

    # Генерация руки
    if st.session_state.hand is None:
        chosen = random.choice(final_spot_pool)
        st.session_state.current_spot_key = chosen
        src, sc, sp = chosen.split('|')
        data = ranges_db[src][sc][sp]
        f_r = data.get("full", "") if isinstance(data, dict) else str(data)
        t_r = data.get("training", f_r) if isinstance(data, dict) else str(data)
        poss = parse_range_to_list(t_r)
        if not poss: poss = all_hands
        srs = load_srs_data()
        srs_key = f"{src}_{sc}_{sp}".replace(" ", "_")
        w = [srs.get(f"{srs_key}_{h}", 100) for h in poss]
        st.session_state.hand = random.choices(poss, weights=w, k=1)[0]
        pool = ['♠', '♥', '♦', '♣']
        s1 = random.choice(pool)
        s2 = s1 if 's' in st.session_state.hand else random.choice([x for x in pool if x != s1])
        st.session_state.suits = [s1, s2]
        st.session_state.srs_mode = False
        st.session_state.last_result_was_error = False

    # Отрисовка
    if st.session_state.current_spot_key:
        src, sc, sp = st.session_state.current_spot_key.split('|')
        st.markdown(f"<div style='text-align:center;color:#666;font-size:12px;'>{src} • {sc}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;color:#ddd;font-weight:bold;font-size:20px;margin-bottom:10px;'>{sp}</div>", unsafe_allow_html=True)
        
        order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
        hero_idx = 0
        u = sp.upper()
        if any(p in u for p in ["EP", "UTG"]): hero_idx = 0
        elif "MP" in u: hero_idx = 1
        elif "CO" in u: hero_idx = 2
        elif any(p in u for p in ["BTN", "BU"]): hero_idx = 3
        elif "SB" in u: hero_idx = 4
        elif "BB" in u: hero_idx = 5
        
        rot = order[hero_idx:] + order[:hero_idx]
        h_val = st.session_state.hand
        s1, s2 = st.session_state.suits
        c1 = "suit-red" if s1 in '♥' else "suit-blue" if s1 in '♦' else "suit-black"
        c2 = "suit-red" if s2 in '♥' else "suit-blue" if s2 in '♦' else "suit-black"

        html = '<div class="game-area"><div class="table-logo">GTO PRO</div>'
        chips_html = ""

        for i in range(1, 6):
            pos = rot[i]
            std_i = order.index(pos)
            hero_i = order.index(rot[0])
            is_fold = std_i < hero_i
            if rot[0] == "SB" and pos == "BB": is_fold = False
            cls = "seat-folded" if is_fold else "seat-active"
            cards = '<div class="opp-cards"><div class="opp-c1"></div><div class="opp-c2"></div></div>' if not is_fold else ""
            html += f'<div class="seat pos-{i} {cls}">{cards}<span class="seat-label">{pos}</span></div>'
            sty = get_chip_style(i)
            if pos == "BTN": chips_html += f'<div class="dealer-button" style="{sty}">D</div>'
            elif pos == "SB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div></div>'
            elif pos == "BB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div><div class="poker-chip chip-stacked"></div></div>'

        hero = rot[0]
        sty = get_chip_style(0)
        if hero == "BTN": chips_html += f'<div class="dealer-button" style="{sty}">D</div>'
        elif hero == "SB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div></div>'
        elif hero == "BB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div><div class="poker-chip chip-stacked"></div></div>'

        html += f'<div class="hero-panel"><div style="display:flex;flex-direction:column;align-items:center;"><span style="color:gold;font-weight:bold;font-size:12px;">HERO</span><span style="color:#777;font-size:10px;">{hero}</span></div><div class="card"><div class="tl {c1}">{h_val[0]}<br>{s1}</div><div class="cent {c1}">{s1}</div></div><div class="card"><div class="tl {c2}">{h_val[1]}<br>{s2}</div><div class="cent {c2}">{s2}</div></div></div>'
        html += chips_html + "</div>"
        st.markdown(html, unsafe_allow_html=True)

        data = ranges_db[src][sc][sp]
        full_r = data.get("full", "") if isinstance(data, dict) else str(data)
        ans_w = get_weight(st.session_state.hand, full_r)
        srs_key = f"{src}_{sc}_{sp}".replace(" ", "_")

        if not st.session_state.srs_mode:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("FOLD", use_container_width=True):
                    corr = (ans_w == 0.0)
                    st.session_state.last_result_was_error = not corr
                    st.session_state.msg = "✅ Correct!" if corr else f"❌ Error! Raise {int(ans_w*100)}%"
                    save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": f"{sp} ({src})", "Hand": st.session_state.hand, "Result": 1 if corr else 0, "CorrectAction": "Fold" if ans_w == 0 else "Raise"})
                    st.session_state.srs_mode = True; st.rerun()
            with c2:
                if st.button("RAISE", use_container_width=True):
                    corr = (ans_w > 0.0)
                    st.session_state.last_result_was_error = not corr
                    st.session_state.msg = f"✅ Correct! ({int(ans_w*100)}%)" if corr else "❌ Error! Fold"
                    save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": f"{sp} ({src})", "Hand": st.session_state.hand, "Result": 1 if corr else 0, "CorrectAction": "Raise" if ans_w > 0 else "Fold"})
                    st.session_state.srs_mode = True; st.rerun()
        else:
            if "✅" in st.session_state.msg: st.success(st.session_state.msg)
            else: st.error(st.session_state.msg)
            
            # --- ВИЗУАЛИЗАТОР (ТОЛЬКО ЕСЛИ ОШИБКА) ---
            if st.session_state.last_result_was_error:
                st.markdown(f"**Incorrect!** Hand: {st.session_state.hand}. Spot: {sp}")
                st.markdown(render_range_matrix(full_r, target_hand=st.session_state.hand), unsafe_allow_html=True)
            # ------------------------------------------

            st.caption("Rate Difficulty:")
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("HARD", use_container_width=True): update_srs_smart(srs_key, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
            with b2:
                if st.button("NORMAL", use_container_width=True): update_srs_smart(srs_key, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
            with b3:
                if st.button("EASY", use_container_width=True): update_srs_smart(srs_key, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()

with tab_stats:
    st.header("📊 Stats")
    df = load_history()
    if df.empty: st.info("No data.")
    else:
        df["Date"] = pd.to_datetime(df["Date"])
        tf = st.selectbox("Time", ["Today", "Last 7 Days", "All Time"])
        now = datetime.now()
        if tf == "Today": df_f = df[df["Date"].dt.date == now.date()]
        elif tf == "Last 7 Days": df_f = df[df["Date"] >= (now - timedelta(days=7))]
        else: df_f = df
        
        if len(df_f) > 0:
            acc = int((df_f["Result"].sum() / len(df_f)) * 100)
            st.metric("Accuracy", f"{acc}%", f"{len(df_f)} hands")
            st.bar_chart(df_f.groupby("Spot")["Result"].mean() * 100)
            st.dataframe(df_f[df_f["Result"]==0].sort_values("Date", ascending=False).head(10)[["Spot","Hand","CorrectAction"]], hide_index=True, use_container_width=True)
        else: st.warning("No hands in this period.")
