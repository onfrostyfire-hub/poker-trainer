import streamlit as st
import json
import random
import pandas as pd
import os
from datetime import datetime, timedelta

# --- ВЕРСИЯ 21.1 (SYNTAX FIX & MOBILE UI) ---
st.set_page_config(page_title="Poker Trainer Pro", page_icon="♠️", layout="centered")

# --- CSS СТИЛИ ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    
    /* УВЕЛИЧЕННЫЙ СТОЛ */
    .game-area { 
        position: relative; width: 100%; max-width: 550px; height: 380px; 
        margin: 0 auto 20px auto; 
        background: radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%); 
        border: 12px solid #3e2723; border-radius: 200px; 
        box-shadow: 0 10px 40px rgba(0,0,0,0.6); 
    }
    .table-logo { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); color: rgba(255,255,255,0.08); font-weight: bold; font-size: 28px; pointer-events: none; }
    
    /* МЕСТА */
    .seat { 
        position: absolute; width: 65px; height: 65px; 
        background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 50%; 
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
        box-shadow: 0 5px 10px rgba(0,0,0,0.5); z-index: 5; 
    }
    .seat-active { border-color: #ffd700; background: rgba(20,20,20,0.95); }
    .seat-folded { opacity: 0.5; border-color: #333; }
    
    .seat-label { color: #fff; font-weight: bold; font-size: 14px; }
    .seat-sub { color: #888; font-size: 10px; }
    
    /* РУБАШКИ КАРТ */
    .opp-cards { position: absolute; top: -15px; width: 30px; height: 40px; background: #fff; border-radius: 3px; border: 1px solid #ccc; background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); box-shadow: 2px 2px 5px rgba(0,0,0,0.5); z-index: 4; }
    .opp-c1 { transform: rotate(-10deg); left: 10px; }
    .opp-c2 { transform: rotate(10deg); left: 25px; }

    /* ФИШКИ */
    .chip { position: absolute; width: 24px; height: 24px; border-radius: 50%; font-size: 10px; color: #000; font-weight: bold; display: flex; justify-content: center; align-items: center; box-shadow: 2px 2px 4px rgba(0,0,0,0.6); z-index: 20; }
    .sb-chip { background: #ffd700; border: 1px solid #e6c200; }
    .bb-chip { background: #ff5722; border: 1px solid #e64a19; }
    
    /* ПОЗИЦИИ */
    .pos-1 { bottom: 20%; left: 6%; } 
    .pos-2 { top: 20%; left: 6%; } 
    .pos-3 { top: -25px; left: 50%; transform: translateX(-50%); } 
    .pos-4 { top: 20%; right: 6%; } 
    .pos-5 { bottom: 20%; right: 6%; }
    
    /* HERO */
    .hero-panel { position: absolute; bottom: -50px; left: 50%; transform: translateX(-50%); background: #1a1a1a; border: 3px solid #ffd700; border-radius: 16px; padding: 8px 20px; display: flex; gap: 10px; box-shadow: 0 0 25px rgba(255,215,0,0.25); z-index: 10; align-items: center; }
    .card { width: 55px; height: 80px; background: white; border-radius: 5px; position: relative; color: black; font-family: 'Arial', sans-serif; }
    .tl { position: absolute; top: 2px; left: 4px; font-weight: bold; font-size: 18px; line-height: 1.1; }
    .cent { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 32px; }
    .suit-red { color: #d32f2f; } .suit-blue { color: #1e88e5; } .suit-black { color: #111; }

    /* MOBILE-FIRST КНОПКИ (В РЯД) */
    div[data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; min-width: 50% !important; }
    
    /* Стили кнопок */
    div.stButton > button { width: 100%; height: 75px; font-size: 22px; font-weight: 800; border-radius: 14px; border: none; text-transform: uppercase; letter-spacing: 1px; transition: transform 0.1s; }
    div.stButton > button:active { transform: scale(0.96); }
    
    /* Цвета */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button { 
        background-color: #c62828 !important; color: white !important; 
        box-shadow: 0 6px 0 #8e0000; margin-bottom: 6px;
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { 
        background-color: #2e7d32 !important; color: white !important; 
        box-shadow: 0 6px 0 #1b5e20; margin-bottom: 6px;
    }

</style>
""", unsafe_allow_html=True)

# --- ФАЙЛЫ ---
HISTORY_FILE = 'history_log.csv'
SRS_FILE = 'srs_data.json'
RANGES_FILE = 'ranges.json'

# --- ИНИЦИАЛИЗАЦИЯ ---
ranks = 'AKQJT98765432'
all_hands = [r1+r2+s for r1 in ranks for r2 in ranks for s in ('s','o') if (r1<r2 and s=='s') or (r1>r2 and s=='o')] + [r+r for r in ranks]

@st.cache_data(ttl=0)
def load_ranges():
    try:
        with open(RANGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

ranges_db = load_ranges()

# --- ФУНКЦИИ ИСТОРИИ ---
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

# --- SRS ЛОГИКА ---
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

# --- ВКЛАДКИ ---
tab_trainer, tab_stats = st.tabs(["🎮 Trainer", "📈 Statistics"])

# ==========================================
# ВКЛАДКА 1: ТРЕНАЖЕР
# ==========================================
with tab_trainer:
    # --- НАСТРОЙКИ ---
    with st.expander("⚙️ Settings", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            if ranges_db:
                cat = st.selectbox("Category", list(ranges_db.keys()))
                sub = st.selectbox("Section", list(ranges_db[cat].keys()))
            else:
                st.error("No ranges loaded.")
                st.stop()
        with c2:
            train_mode = st.radio("Mode", ["Manual", "Early (EP/MP)", "Late (CO/BU/SB)"], horizontal=True)

        all_spots = list(ranges_db[cat][sub].keys())
        if train_mode == "Early (EP/MP)":
            target_spots = [s for s in all_spots if any(p in s.upper() for p in ["EP", "UTG", "MP"])]
        elif train_mode == "Late (CO/BU/SB)":
            target_spots = [s for s in all_spots if any(p in s.upper() for p in ["CO", "BU", "BTN", "SB"])]
        else:
            target_spots = all_spots
        
        if not target_spots: target_spots = all_spots
        
        if train_mode == "Manual":
            selected_spot = st.selectbox("Spot", target_spots)
        
        if st.button("Reset SRS Memory"):
            if os.path.exists(SRS_FILE): os.remove(SRS_FILE)
            st.toast("Memory wiped!")

    # --- СОСТОЯНИЕ ---
    if 'hand' not in st.session_state: st.session_state.hand = None
    if 'active_spot' not in st.session_state: st.session_state.active_spot = None
    if 'suits' not in st.session_state: st.session_state.suits = None
    if 'msg' not in st.session_state: st.session_state.msg = None
    if 'srs_mode' not in st.session_state: st.session_state.srs_mode = False

    # --- ЛОГИКА РАЗДАЧИ ---
    if st.session_state.hand is None:
        if train_mode == "Manual": st.session_state.active_spot = selected_spot
        else: st.session_state.active_spot = random.choice(target_spots)
        
        if st.session_state.active_spot not in ranges_db[cat][sub]:
            st.session_state.active_spot = list(ranges_db[cat][sub].keys())[0]

        spot_id = st.session_state.active_spot
        data = ranges_db[cat][sub][spot_id]
        
        full_r = data.get("full", "") if isinstance(data, dict) else str(data)
        train_r = data.get("training", full_r) if isinstance(data, dict) else str(data)
        
        poss = parse_range_to_list(train_r)
        if not poss: poss = all_hands
        
        srs = load_srs_data()
        srs_k = f"{cat}_{sub}_{spot_id}".replace(" ", "_")
        w = [srs.get(f"{srs_k}_{h}", 100) for h in poss]
        
        st.session_state.hand = random.choices(poss, weights=w, k=1)[0]
        
        pool = ['♠', '♥', '♦', '♣']
        s1 = random.choice(pool)
        s2 = s1 if 's' in st.session_state.hand else random.choice([x for x in pool if x != s1])
        st.session_state.suits = [s1, s2]
        st.session_state.srs_mode = False

    # --- ОТРИСОВКА ---
    curr_spot = st.session_state.active_spot
    st.markdown(f"<h3 style='text-align:center; color:#888; margin-bottom:10px;'>{curr_spot}</h3>", unsafe_allow_html=True)
    
    order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
    hero_idx = 0
    u = curr_spot.upper()
    if any(p in u for p in ["EP", "UTG"]): hero_idx = 0
    elif "MP" in u: hero_idx = 1
    elif "CO" in u: hero_idx = 2
    elif any(p in u for p in ["BTN", "BU"]): hero_idx = 3
    elif "SB" in u: hero_idx = 4
    elif "BB" in u: hero_idx = 5
    
    rotated_seats = order[hero_idx:] + order[:hero_idx]
    
    h_val = st.session_state.hand
    s1, s2 = st.session_state.suits
    c1 = "suit-red" if s1 in '♥' else "suit-blue" if s1 in '♦' else "suit-black"
    c2 = "suit-red" if s2 in '♥' else "suit-blue" if s2 in '♦' else "suit-black"

    html = '<div class="game-area"><div class="table-logo">GTO PRO</div>'
    
    for i in range(1, 6):
        pos_name = rotated_seats[i]
        std_idx_pos = order.index(pos_name)
        std_idx_hero = order.index(rotated_seats[0])
        
        is_folded = False
        has_cards = False
        
        if std_idx_pos < std_idx_hero:
            is_folded = True; status_text = "Fold"
        else:
            has_cards = True; status_text = "Wait"

        if rotated_seats[0] == "SB" and pos_name == "BB": has_cards = True; is_folded = False
        
        seat_cls = "seat-folded" if is_folded else "seat-active"
        cards_html = '<div class="opp-cards"><div class="opp-c1"></div><div class="opp-c2"></div></div>' if has_cards else ""
        
        chip_html = ""
        if pos_name == "SB": chip_html = '<div class="chip sb-chip" style="top:-10px; right:-10px;">SB</div>'
        if pos_name == "BB": chip_html = '<div class="chip bb-chip" style="top:-10px; right:-10px;">BB</div>'

        html += f"""<div class="seat pos-{i} {seat_cls}">{cards_html}{chip_html}<span class="seat-label">{pos_name}</span><span class="seat-sub">{status_text}</span></div>"""

    hero_pos = rotated_seats[0]
    hero_chip = ""
    if hero_pos == "SB": hero_chip = '<div class="chip sb-chip" style="top:-15px; right:-10px;">SB</div>'
    if hero_pos == "BB": hero_chip = '<div class="chip bb-chip" style="top:-15px; right:-10px;">BB</div>'

    html += f"""
    <div class="hero-panel">{hero_chip}
        <div style="display:flex; flex-direction:column; align-items:center;"><span style="color:gold; font-weight:bold; font-size:12px;">HERO</span><span style="color:#777; font-size:10px;">{hero_pos}</span></div>
        <div class="card"><div class="tl {c1}">{h_val[0]}<br>{s1}</div><div class="cent {c1}">{s1}</div></div>
        <div class="card"><div class="tl {c2}">{h_val[1]}<br>{s2}</div><div class="cent {c2}">{s2}</div></div>
    </div></div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # --- КНОПКИ ---
    spot_data = ranges_db[cat][sub][curr_spot]
    full_r = spot_data.get("full", "") if isinstance(spot_data, dict) else str(spot_data)
    ans_weight = get_weight(st.session_state.hand, full_r)
    srs_k = f"{cat}_{sub}_{curr_spot}".replace(" ", "_")

    if not st.session_state.srs_mode:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("FOLD"):
                is_correct = (ans_weight == 0.0)
                st.session_state.msg = "✅ Correct!" if is_correct else f"❌ Error! Raise {int(ans_weight*100)}%"
                save_to_history({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Spot": curr_spot, "Hand": st.session_state.hand,
                    "Result": 1 if is_correct else 0, "CorrectAction": "Fold" if ans_weight == 0 else "Raise"
                })
                st.session_state.srs_mode = True; st.rerun()
        with c2:
            if st.button("RAISE"):
                is_correct = (ans_weight > 0.0)
                st.session_state.msg = f"✅ Correct! ({int(ans_weight*100)}%)" if is_correct else "❌ Error! Fold"
                save_to_history({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Spot": curr_spot, "Hand": st.session_state.hand,
                    "Result": 1 if is_correct else 0, "CorrectAction": "Raise" if ans_weight > 0 else "Fold"
                })
                st.session_state.srs_mode = True; st.rerun()
    else:
        if "✅" in st.session_state.msg: st.success(st.session_state.msg)
        else: st.error(st.session_state.msg)
        
        st.markdown("<div style='text-align:center; margin-bottom:10px; color:#666;'>Rate difficulty:</div>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("HARD (x2.5)"): update_srs_smart(srs_k, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
        with b2:
            if st.button("NORMAL"): update_srs_smart(srs_k, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
        with b3:
            if st.button("EASY (/4)"): update_srs_smart(srs_k, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()

# ==========================================
# ВКЛАДКА 2: СТАТИСТИКА
# ==========================================
with tab_stats:
    st.header("📊 Statistics Dashboard")
    df = load_history()
    if df.empty:
        st.info("No stats yet. Play some hands!")
    else:
        df["Date"] = pd.to_datetime(df["Date"])
        time_filter = st.selectbox("Period", ["Today", "Last 7 Days", "Last 30 Days", "All Time"])
        now = datetime.now()
        
        if time_filter == "Today": df_filtered = df[df["Date"].dt.date == now.date()]
        elif time_filter == "Last 7 Days": df_filtered = df[df["Date"] >= (now - timedelta(days=7))]
        elif time_filter == "Last 30 Days": df_filtered = df[df["Date"] >= (now - timedelta(days=30))]
        else: df_filtered = df
            
        total_hands = len(df_filtered)
        if total_hands > 0:
            correct_hands = df_filtered["Result"].sum()
            accuracy = int((correct_hands / total_hands) * 100)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Hands Played", total_hands)
            c2.metric("Accuracy", f"{accuracy}%")
            c3.metric("Errors", total_hands - correct_hands)
            
            st.subheader("Performance by Spot")
            spot_stats = df_filtered.groupby("Spot")["Result"].mean() * 100
            st.bar_chart(spot_stats)
            
            st.subheader("Recent Errors")
            errors_df = df_filtered[df_filtered["Result"] == 0].sort_values("Date", ascending=False).head(10)
            st.dataframe(errors_df[["Date", "Spot", "Hand", "CorrectAction"]], hide_index=True, use_container_width=True)
        else:
            st.warning("No data for this period.")
