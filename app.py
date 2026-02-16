import streamlit as st
import json
import random

# --- ВЕРСИЯ 4.0 (FIXED HTML RENDERING) ---
st.set_page_config(page_title="Poker Trainer Pro", page_icon="♠️", layout="centered")

# --- CSS СТИЛИ ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    
    /* Игровое поле */
    .game-area {
        position: relative;
        width: 100%;
        max-width: 500px;
        height: 320px;
        margin: 0 auto 50px auto;
        background: radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%);
        border: 10px solid #3e2723;
        border-radius: 150px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* Лого */
    .table-logo {
        position: absolute;
        top: 45%; left: 50%;
        transform: translate(-50%, -50%);
        color: rgba(255,255,255,0.1);
        font-weight: bold;
        font-size: 20px;
        pointer-events: none;
    }
    
    /* Оппоненты */
    .seat {
        position: absolute;
        width: 60px; height: 60px;
        background: rgba(0,0,0,0.7);
        border: 2px solid #555;
        border-radius: 50%;
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        font-size: 10px; color: #aaa;
    }
    .seat-1 { top: -10px; left: 20%; }
    .seat-2 { top: -10px; right: 20%; }
    .seat-3 { top: 40%; right: -20px; }
    .seat-4 { bottom: 15%; right: 5%; }
    .seat-5 { bottom: 15%; left: 5%; }
    
    /* Хиро */
    .hero-panel {
        position: absolute;
        bottom: -40px; left: 50%;
        transform: translateX(-50%);
        background: #222;
        border: 2px solid #ffd700;
        border-radius: 15px;
        padding: 8px 15px;
        display: flex; gap: 5px;
        box-shadow: 0 0 15px rgba(255,215,0,0.2);
        z-index: 10;
    }
    
    /* Карты */
    .card {
        width: 50px; height: 75px;
        background: white; border-radius: 4px;
        position: relative; color: black;
    }
    .tl { position: absolute; top: 2px; left: 3px; font-weight: bold; font-size: 16px; line-height: 1; }
    .cent { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); font-size: 28px; }
    .red { color: #d32f2f; } .black { color: #111; }
    
    /* Кнопки */
    div.stButton > button { width: 100%; height: 60px; font-size: 18px; font-weight: bold; border-radius: 10px; border: none; }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button { background: #c62828; color: white; }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { background: #2e7d32; color: white; }
</style>
""", unsafe_allow_html=True)

# --- ДАННЫЕ И ЛОГИКА ---
ranks = 'AKQJT98765432'
all_hands = []
for i in range(len(ranks)):
    for j in range(len(ranks)):
        if i < j: all_hands.append(ranks[i] + ranks[j] + 's')
        elif i > j: all_hands.append(ranks[j] + ranks[i] + 'o')
        else: all_hands.append(ranks[i] + ranks[j])

@st.cache_data
def load_ranges():
    try:
        with open('ranges.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

ranges_db = load_ranges()

# --- ИНТЕРФЕЙС ---
if not ranges_db:
    st.error("Файл ranges.json не найден!")
    st.stop()

# Сайдбар
with st.sidebar:
    st.title("Settings")
    cat = st.selectbox("Category", list(ranges_db.keys()))
    sub = st.selectbox("Subcategory", list(ranges_db[cat].keys()))
    spot = st.selectbox("Spot", list(ranges_db[cat][sub].keys()))
    if st.button("Reset Stats"):
        st.session_state.stats = {'correct': 0, 'total': 0}
        st.rerun()

st.markdown(f"<h3 style='text-align: center; margin: 0 0 20px 0;'>{spot}</h3>", unsafe_allow_html=True)

# Состояние
if 'hand' not in st.session_state: st.session_state.hand = random.choice(all_hands)
if 'msg' not in st.session_state: st.session_state.msg = None
if 'stats' not in st.session_state: st.session_state.stats = {'correct': 0, 'total': 0}

# Вес руки
def get_weight(hand, range_str):
    if not range_str: return 0.0
    items = [x.strip() for x in range_str.split(',')]
    for item in items:
        w = 1.0; h = item
        if ':' in item: h, w_str = item.split(':'); w = float(w_str)
        if h == hand: return w
        if len(h) == 2 and h[0] != h[1] and hand.startswith(h): return w
    return 0.0

weight = get_weight(st.session_state.hand, ranges_db[cat][sub][spot])

# --- ОТРИСОВКА СТОЛА ---
h = st.session_state.hand
r1, r2 = h[0], h[1]
suits = ['♠', '♥', '♦', '♣']; s1 = random.choice(suits)
s2 = s1 if 's' in h else random.choice([x for x in suits if x != s1])
c1 = "red" if s1 in ['♥','♦'] else "black"
c2 = "red" if s2 in ['♥','♦'] else "black"

# Генерируем HTML без лишних отступов в начале строк!
html = f"""
<div class="game-area">
<div class="table-logo">POKER TRAINER</div>
<div class="seat seat-1"><span>V1</span></div>
<div class="seat seat-2"><span>V2</span></div>
<div class="seat seat-3"><span>V3</span></div>
<div class="seat seat-4"><span>V4</span></div>
<div class="seat seat-5"><span>V5</span></div>
<div class="hero-panel">
<div style="position:absolute; top:-20px; left:0; width:100%; text-align:center; color:gold; font-size:12px; font-weight:bold;">HERO</div>
<div class="card"><div class="tl {c1}">{r1}<br>{s1}</div><div class="cent {c1}">{s1}</div></div>
<div class="card"><div class="tl {c2}">{r2}<br>{s2}</div><div class="cent {c2}">{s2}</div></div>
</div>
</div>
"""
st.markdown(html, unsafe_allow_html=True)

# --- КНОПКИ ---
c_1, c_2 = st.columns(2, gap="medium")
if st.session_state.msg is None:
    with c_1:
        if st.button("FOLD"):
            if weight == 0.0: st.session_state.msg = "✅ Fold - OK!"; st.session_state.stats['correct']+=1
            else: st.session_state.msg = f"❌ Raise {int(weight*100)}%!"; 
            st.session_state.stats['total']+=1; st.rerun()
    with c_2:
        if st.button("RAISE"):
            if weight > 0.0: st.session_state.msg = f"✅ Raise ({int(weight*100)}%)"; st.session_state.stats['correct']+=1
            else: st.session_state.msg = "❌ Fold!"; 
            st.session_state.stats['total']+=1; st.rerun()
else:
    msg = st.session_state.msg
    if "✅" in msg: st.success(msg)
    else: st.error(msg)
    if st.button("Next Hand ➡️"):
        st.session_state.hand = random.choice(all_hands); st.session_state.msg = None; st.rerun()

st.caption(f"Stats: {st.session_state.stats['correct']}/{st.session_state.stats['total']}")
