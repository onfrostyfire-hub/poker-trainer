import streamlit as st
import json
import random
import pandas as pd
import os

# --- ВЕРСИЯ 16.0 (ANKI STYLE SRS ALGORITHM) ---
st.set_page_config(page_title="Poker Trainer Pro", page_icon="♠️", layout="centered")

# --- CSS СТИЛИ ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    .game-area { position: relative; width: 100%; max-width: 500px; height: 340px; margin: 0 auto 30px auto; background: radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%); border: 10px solid #3e2723; border-radius: 170px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .table-logo { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); color: rgba(255,255,255,0.1); font-weight: bold; font-size: 24px; pointer-events: none; }
    
    .seat { position: absolute; width: 55px; height: 55px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.4); z-index: 5; }
    .seat-label { color: #fff; font-weight: bold; font-size: 13px; }
    .seat-sub { color: #888; font-size: 9px; }
    
    .chip { position: absolute; width: 20px; height: 20px; border-radius: 50%; font-size: 9px; color: #000; font-weight: bold; display: flex; justify-content: center; align-items: center; box-shadow: 1px 1px 3px rgba(0,0,0,0.5); z-index: 20; }
    .sb-chip { background: #ffd700; top: -5px; right: -5px; border: 1px solid #e6c200; }
    .bb-chip { background: #ff5722; top: -5px; right: -5px; border: 1px solid #e64a19; }
    
    .pos-1 { bottom: 18%; left: 8%; }
    .pos-2 { top: 18%; left: 8%; }
    .pos-3 { top: -15px; left: 50%; transform: translateX(-50%); }
    .pos-4 { top: 18%; right: 8%; }
    .pos-5 { bottom: 18%; right: 8%; }
    
    .hero-panel { position: absolute; bottom: -45px; left: 50%; transform: translateX(-50%); background: #1a1a1a; border: 2px solid #ffd700; border-radius: 12px; padding: 5px 15px; display: flex; gap: 8px; box-shadow: 0 0 20px rgba(255,215,0,0.2); z-index: 10; align-items: center; }
    .card { width: 50px; height: 75px; background: white; border-radius: 4px; position: relative; color: black; }
    .tl { position: absolute; top: 0px; left: 3px; font-weight: bold; font-size: 16px; line-height: 1.2; }
    .cent { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 26px; }
    .red { color: #d32f2f; } .black { color: #111; }
    
    div.stButton > button { width: 100%; height: 60px; font-size: 18px; font-weight: bold; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# --- ДАННЫЕ ---
ranks = 'AKQJT98765432'
all_hands = []
for i in range(len(ranks)):
    for j in range(len(ranks)):
        if i < j: all_hands.append(ranks[i] + ranks[j] + 's')
        elif i > j: all_hands.append(ranks[j] + ranks[i] + 'o')
        else: all_hands.append(ranks[i] + ranks[j])

@st.cache_data(ttl=0)
def load_ranges():
    try:
        with open('ranges.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

ranges_db = load_ranges()
if not ranges_db: st.error("Ranges not found!"); st.stop()

# --- СИСТЕМА SRS (ANKI) ---
SRS_FILE = 'srs_data.json'

def load_srs_data():
    if os.path.exists(SRS_FILE):
        try:
            with open(SRS_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_srs_data(data):
    with open(SRS_FILE, 'w') as f:
        json.dump(data, f)

def update_srs(spot_id, hand, rating):
    data = load_srs_data()
    key = f"{spot_id}_{hand}"
    if rating == 'hard': new_weight = 50
    elif rating == 'normal': new_weight = 10
    elif rating == 'easy': new_weight = 1
    data[key] = new_weight
    save_srs_data(data)

def get_weighted_hand(hand_list, spot_id):
    srs_data = load_srs_data()
    weights = [srs_data.get(f"{spot_id}_{h}", 10) for h in hand_list]
    if not hand_list: return random.choice(all_hands)
    return random.choices(hand_list, weights=weights, k=1)[0]

# --- ПАРСЕРЫ ---
def parse_range_to_list(range_str):
    if not range_str: return []
    hand_list = []
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        if not item: continue
        h_code = item.split(':')[0]
        targets = []
        if h_code in all_hands: targets.append(h_code)
        else:
            if len(h_code) == 2 and h_code[0] != h_code[1]:
                s, o = h_code + 's', h_code + 'o'
                if s in all_hands: targets.append(s)
                if o in all_hands: targets.append(o)
            elif len(h_code) == 2 and h_code[0] == h_code[1]:
                if h_code in all_hands: targets.append(h_code)
        hand_list.extend(targets)
    return list(set(hand_list))

def get_weight(hand, range_str):
    if not range_str: return 0.0
    items = [x.strip() for x in range_str.replace('\n', ' ').split(',')]
    for item in items:
        w = 1.0; h = item
        if ':' in item: h, w_str = item.split(':'); w = float(w_str)
        if h == hand: return w
        if len(h) == 2 and h[0] != h[1] and hand.startswith(h): return w
    return 0.0

# --- ИНТЕРФЕЙС ---
with st.sidebar:
    st.title("Settings")
    cat = st.selectbox("Category", list(ranges_db.keys()))
    sub = st.selectbox("Section", list(ranges_db[cat].keys()))
    spot = st.selectbox("Spot", list(ranges_db[cat][sub].keys()))
    SPOT_ID = f"{cat}_{sub}_{spot}".replace(" ", "_")
    if st.button("Reset Session Stats"):
        st.session_state.stats = {'correct': 0, 'total': 0}
        st.session_state.history = []
        st.rerun()
    st.divider()
    if st.button("Reset SRS Memory"):
        if os.path.exists(SRS_FILE): os.remove(SRS_FILE)
        st.toast("Memory wiped!", icon="🧹")

st.markdown(f"<h3 style='text-align: center; margin: -20px 0 20px 0; color: #aaa;'>{spot}</h3>", unsafe_allow_html=True)

# --- ДАННЫЕ СПОТА ---
spot_data = ranges_db[cat][sub][spot]
if isinstance(spot_data, dict):
    full_range_str = spot_data.get("full", "")
    training_range_str = spot_data.get("training", full_range_str)
else:
    full_range_str = str(spot_data)
    training_range_str = str(spot_data)

possible_hands = parse_range_to_list(training_range_str)

# --- СОСТОЯНИЕ ---
if 'hand' not in st.session_state: st.session_state.hand = None
if 'suits' not in st.session_state: st.session_state.suits = None
if 'msg' not in st.session_state: st.session_state.msg = None
if 'srs_mode' not in st.session_state: st.session_state.srs_mode = False
if 'stats' not in st.session_state: st.session_state.stats = {'correct': 0, 'total': 0}
if 'history' not in st.session_state: st.session_state.history = []

if st.session_state.hand is None:
    st.session_state.hand = get_weighted_hand(possible_hands, SPOT_ID)
    st.session_state.suits = None
    st.session_state.srs_mode = False
    st.session_state.msg = None

if st.session_state.suits is None:
    h_str = st.session_state.hand
    pool = ['♠', '♥', '♦', '♣']
    s1 = random.choice(pool)
    if 's' in h_str: s2 = s1
    else: s2 = random.choice([x for x in pool if x != s1])
    st.session_state.suits = [s1, s2]

# --- ОТРИСОВКА ---
def get_seats_labels(spot_name):
    order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
    u = spot_name.upper()
    idx = 0
    if "EP" in u or "UTG" in u: idx = 0
    elif "MP" in u: idx = 1
    elif "CO" in u: idx = 2
    elif "BTN" in u or "BU" in u: idx = 3
    elif "SB" in u: idx = 4
    elif "BB" in u: idx = 5
    return order[idx:] + order[:idx]

seats = get_seats_labels(spot)
h = st.session_state.hand
r1, r2 = h[0], h[1]
s1, s2 = st.session_state.suits 
c1 = "red" if s1 in ['♥','♦'] else "black"
c2 = "red" if s2 in ['♥','♦'] else "black"

html = f'<div class="game-area"><div class="table-logo">GTO TRAINER</div>'
for i in range(1, 6):
    lbl = seats[i]
    chip = f'<div class="chip {"sb-chip" if lbl=="SB" else "bb-chip"}">{lbl}</div>' if lbl in ["SB", "BB"] else ""
    html += f'<div class="seat pos-{i}">{chip}<span class="seat-label">{lbl}</span><span class="seat-sub">Fold</span></div>'

hero_lbl = seats[0]
hero_chip = f'<div class="chip {"sb-chip" if hero_lbl=="SB" else "bb-chip"}" style="top:-15px; right:-10px;">{hero_lbl}</div>' if hero_lbl in ["SB", "BB"] else ""
html += f'<div class="hero-panel">{hero_chip}<div style="display:flex; flex-direction:column; align-items:center; margin-right:5px;"><span style="color:gold; font-weight:bold; font-size:12px;">HERO</span><span style="color:#555; font-size:10px;">{hero_lbl}</span></div><div class="card"><div class="tl {c1}">{r1}<br>{s1}</div><div class="cent {c1}">{s1}</div></div><div class="card"><div class="tl {c2}">{r2}<br>{s2}</div><div class="cent {c2}">{s2}</div></div></div></div>'
st.markdown(html, unsafe_allow_html=True)

# --- КНОПКИ ---
weight = get_weight(st.session_state.hand, full_range_str)

if not st.session_state.srs_mode:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("FOLD"):
            corr = (weight == 0.0)
            st.session_state.stats['total'] += 1
            if corr: st.session_state.stats['correct'] += 1
            st.session_state.msg = "✅ Correct! Fold" if corr else f"❌ Error! Raise {int(weight*100)}%"
            st.session_state.history.append({"Spot": spot, "Hand": st.session_state.hand, "Result": "✅" if corr else "❌"})
            st.session_state.srs_mode = True; st.rerun()
    with c2:
        if st.button("RAISE"):
            corr = (weight > 0.0)
            st.session_state.stats['total'] += 1
            if corr: st.session_state.stats['correct'] += 1
            st.session_state.msg = f"✅ Correct! Raise ({int(weight*100)}%)" if corr else "❌ Error! Fold"
            st.session_state.history.append({"Spot": spot, "Hand": st.session_state.hand, "Result": "✅" if corr else "❌"})
            st.session_state.srs_mode = True; st.rerun()
else:
    if "✅" in st.session_state.msg: st.success(st.session_state.msg)
    else: st.error(st.session_state.msg)
    s1, s2, s3 = st.columns(3)
    with s1:
        if st.button("HARD (Again)"): update_srs(SPOT_ID, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
    with s2:
        if st.button("NORMAL"): update_srs(SPOT_ID, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
    with s3:
        if st.button("EASY (Skip)", type="primary"): update_srs(SPOT_ID, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()

st.divider()
if st.session_state.history:
    st.subheader("Session Log")
    st.dataframe(pd.DataFrame(st.session_state.history).iloc[::-1], hide_index=True, use_container_width=True)
