import streamlit as st
import json
import random

# --- ВЕРСИЯ 14.0 (DEBUG MODE) ---
st.set_page_config(page_title="Poker Trainer Pro", page_icon="♠️", layout="centered")

# --- CSS СТИЛИ ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    .game-area { position: relative; width: 100%; max-width: 500px; height: 340px; margin: 0 auto 40px auto; background: radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%); border: 10px solid #3e2723; border-radius: 170px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .table-logo { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); color: rgba(255,255,255,0.1); font-weight: bold; font-size: 24px; pointer-events: none; }
    .seat { position: absolute; width: 55px; height: 55px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.4); z-index: 5; }
    .seat-label { color: #fff; font-weight: bold; font-size: 13px; }
    .seat-sub { color: #888; font-size: 9px; }
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
    div.stButton > button { width: 100%; height: 60px; font-size: 18px; font-weight: bold; border-radius: 12px; border: none; }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button { background: #b71c1c; color: white; }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { background: #2e7d32; color: white; }
</style>
""", unsafe_allow_html=True)

# --- ЛОГИКА ---
ranks = 'AKQJT98765432'
all_hands = []
for i in range(len(ranks)):
    for j in range(len(ranks)):
        if i < j: all_hands.append(ranks[i] + ranks[j] + 's')
        elif i > j: all_hands.append(ranks[j] + ranks[i] + 'o')
        else: all_hands.append(ranks[i] + ranks[j])

# ОТКЛЮЧИЛ КЭШ ДЛЯ ОТЛАДКИ (ttl=0)
@st.cache_data(ttl=0)
def load_ranges():
    try:
        with open('ranges.json', 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

ranges_db = load_ranges()
if not ranges_db: st.error("Файл ranges.json не найден!"); st.stop()

# --- ПАРСЕРЫ ---
def parse_range_to_list(range_str):
    if not range_str: return []
    hand_list = []
    # Удаляем переносы строк
    cleaned_str = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned_str.split(',')]
    for item in items:
        if not item: continue
        hand_code = item.split(':')[0]
        targets = []
        if hand_code in all_hands: targets.append(hand_code)
        else:
            if len(hand_code) == 2 and hand_code[0] != hand_code[1]:
                s, o = hand_code + 's', hand_code + 'o'
                if s in all_hands: targets.append(s)
                if o in all_hands: targets.append(o)
            elif len(hand_code) == 2 and hand_code[0] == hand_code[1]: 
                 if hand_code in all_hands: targets.append(hand_code)
        hand_list.extend(targets)
    return list(set(hand_list))

def get_weight(hand, range_str):
    if not range_str: return 0.0
    # Исправление парсинга весов
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        w = 1.0; h = item
        if ':' in item: h, w_str = item.split(':'); w = float(w_str)
        if h == hand: return w
        if len(h) == 2 and h[0] != h[1] and hand.startswith(h): return w
    return 0.0

# --- САЙДБАР ---
with st.sidebar:
    st.title("Settings")
    cat = st.selectbox("Category", list(ranges_db.keys()))
    sub = st.selectbox("Section", list(ranges_db[cat].keys()))
    spot = st.selectbox("Spot", list(ranges_db[cat][sub].keys()))
    if st.button("Reset Stats"):
        st.session_state.stats = {'correct': 0, 'total': 0}
        st.rerun()

st.markdown(f"<h3 style='text-align: center; margin: -20px 0 20px 0; color: #aaa;'>{spot}</h3>", unsafe_allow_html=True)

# --- ДИАГНОСТИКА ДАННЫХ ---
spot_data = ranges_db[cat][sub][spot]

# Проверка типа данных
data_type = "Dict (New)" if isinstance(spot_data, dict) else "String (Old)"

if isinstance(spot_data, dict):
    full_range_str = spot_data.get("full", "")
    training_range_str = spot_data.get("training", "")
    
    # Фолбек, если тренинг пустой
    if not training_range_str:
        training_range_str = full_range_str
        st.sidebar.error("Warning: 'training' field is empty! Using full range.")
else:
    full_range_str = str(spot_data)
    training_range_str = str(spot_data)
    st.sidebar.warning("Warning: Using OLD format (String). Please update ranges.json!")

# --- СОСТОЯНИЕ ---
if 'hand' not in st.session_state: st.session_state.hand = None
if 'suits' not in st.session_state: st.session_state.suits = None
if 'msg' not in st.session_state: st.session_state.msg = None
if 'stats' not in st.session_state: st.session_state.stats = {'correct': 0, 'total': 0}

# --- ШАГ 1: ГЕНЕРАЦИЯ ---
possible_hands = parse_range_to_list(training_range_str)

# ВЫВОД ДИАГНОСТИКИ В САЙДБАР
st.sidebar.divider()
st.sidebar.markdown(f"**Data Format:** {data_type}")
st.sidebar.markdown(f"**Hands in Training Pool:** {len(possible_hands)}")
if len(possible_hands) > 0 and len(possible_hands) < 169:
    st.sidebar.success("✅ Training Mode Active")
    st.sidebar.code(f"Examples: {', '.join(possible_hands[:3])}...")
elif len(possible_hands) == 169:
    st.sidebar.error("❌ Pool is FULL (169 hands). Range not loaded?")
else:
    st.sidebar.warning("Pool seems suspicious.")

if st.session_state.hand is None:
    if not possible_hands: possible_hands = all_hands
    st.session_state.hand = random.choice(possible_hands)
    st.session_state.suits = None

# --- ШАГ 2: МАСТИ ---
if st.session_state.suits is None:
    h_str = st.session_state.hand
    suits_pool = ['♠', '♥', '♦', '♣']
    s1 = random.choice(suits_pool)
    if 's' in h_str: s2 = s1
    elif 'o' in h_str: s2 = random.choice([x for x in suits_pool if x != s1])
    else: s2 = random.choice([x for x in suits_pool if x != s1])
    st.session_state.suits = [s1, s2]

# --- ПОЗИЦИИ ---
def get_seats_labels(spot_name):
    order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
    spot_upper = spot_name.upper()
    hero_idx = 0 
    if "EP" in spot_upper or "UTG" in spot_upper: hero_idx = 0
    elif "MP" in spot_upper: hero_idx = 1
    elif "CO" in spot_upper: hero_idx = 2
    elif "BTN" in spot_upper or "BU" in spot_upper: hero_idx = 3
    elif "SB" in spot_upper: hero_idx = 4
    elif "BB" in spot_upper: hero_idx = 5
    return order[hero_idx:] + order[:hero_idx]

seats = get_seats_labels(spot)

# --- ОТРИСОВКА ---
h = st.session_state.hand
r1, r2 = h[0], h[1]
s1, s2 = st.session_state.suits 
c1 = "red" if s1 in ['♥','♦'] else "black"
c2 = "red" if s2 in ['♥','♦'] else "black"

html = ""
html += '<div class="game-area">'
html += '<div class="table-logo">GTO TRAINER</div>'
html += f'<div class="seat pos-1"><span class="seat-label">{seats[1]}</span><span class="seat-sub">Fold</span></div>'
html += f'<div class="seat pos-2"><span class="seat-label">{seats[2]}</span><span class="seat-sub">Fold</span></div>'
html += f'<div class="seat pos-3"><span class="seat-label">{seats[3]}</span><span class="seat-sub">Fold</span></div>'
html += f'<div class="seat pos-4"><span class="seat-label">{seats[4]}</span><span class="seat-sub">Fold</span></div>'
html += f'<div class="seat pos-5"><span class="seat-label">{seats[5]}</span><span class="seat-sub">Fold</span></div>'
html += '<div class="hero-panel">'
html += '<div style="display:flex; flex-direction:column; align-items:center; margin-right:5px;">'
html += f'<span style="color:gold; font-weight:bold; font-size:12px;">HERO</span>'
html += f'<span style="color:#555; font-size:10px;">{seats[0]}</span>'
html += '</div>'
html += f'<div class="card"><div class="tl {c1}">{r1}<br>{s1}</div><div class="cent {c1}">{s1}</div></div>'
html += f'<div class="card"><div class="tl {c2}">{r2}<br>{s2}</div><div class="cent {c2}">{s2}</div></div>'
html += '</div></div>'

st.markdown(html, unsafe_allow_html=True)

# --- КНОПКИ ---
weight = get_weight(st.session_state.hand, full_range_str)

c1, c2 = st.columns(2, gap="small")
if st.session_state.msg is None:
    with c1:
        if st.button("FOLD"):
            if weight == 0.0: st.session_state.msg = "✅ Correct! (Fold)"; st.session_state.stats['correct']+=1
            else: st.session_state.msg = f"❌ Error! Raise {int(weight*100)}%"; 
            st.session_state.stats['total']+=1; st.rerun()
    with c2:
        if st.button("RAISE"):
            if weight > 0.0: 
                txt = "Pure" if weight==1.0 else f"Mix {int(weight*100)}%"
                st.session_state.msg = f"✅ Correct! ({txt})"; st.session_state.stats['correct']+=1
            else: st.session_state.msg = "❌ Error! Fold"; 
            st.session_state.stats['total']+=1; st.rerun()
else:
    msg = st.session_state.msg
    if "✅" in msg: st.success(msg)
    else: st.error(msg)
    if st.button("Next Hand ➡️"):
        st.session_state.hand = None; st.session_state.suits = None; st.session_state.msg = None; st.rerun()

st.markdown(f"<div style='text-align:center; color:#666; font-family:monospace;'>Session: {st.session_state.stats['correct']}/{st.session_state.stats['total']}</div>", unsafe_allow_html=True)
