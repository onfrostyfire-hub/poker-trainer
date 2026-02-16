import streamlit as st
import json
import random

# --- ВЕРСИЯ 2.0 (ПРОВЕРКА ОБНОВЛЕНИЯ) ---
st.set_page_config(page_title="Poker Trainer v2.0", page_icon="♠️", layout="centered")

# --- СТИЛИ (CSS) ---
st.markdown("""
<style>
    .stApp { background-color: #121212; color: #e0e0e0; }
    
    /* СТОЛ */
    .poker-table {
        background: radial-gradient(ellipse at center, #35654d 0%, #254d39 100%);
        border: 10px solid #4e342e;
        border-radius: 100px;
        padding: 30px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* МЕСТО ХИРО */
    .hero-box {
        background: rgba(0,0,0,0.5);
        border: 2px solid gold;
        border-radius: 15px;
        padding: 10px;
        display: inline-block;
        margin-top: 15px;
    }
    
    /* КАРТА */
    .card-box {
        display: inline-block;
        width: 60px;
        height: 85px;
        background: white;
        border-radius: 5px;
        margin: 5px;
        position: relative;
        color: black;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    
    .rank-tl { position: absolute; top: 2px; left: 4px; font-weight: bold; font-size: 20px; line-height: 1; }
    .suit-center { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 35px; }
    
    .red { color: #d32f2f; }
    .black { color: #212121; }
    
    /* КНОПКИ */
    div.stButton > button { width: 100%; height: 60px; font-size: 18px; border-radius: 10px; font-weight: bold; }
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

@st.cache_data
def load_ranges():
    try:
        with open('ranges.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}

ranges_db = load_ranges()

# --- ИНТЕРФЕЙС ---
st.title("Poker Trainer (v2.0)") # ПРОВЕРКА ВЕРСИИ

if not ranges_db:
    st.error("Файл ranges.json не найден или пуст!")
    st.stop()

# Сайдбар
with st.sidebar:
    st.header("Настройки")
    cat = st.selectbox("Категория", list(ranges_db.keys()))
    sub = st.selectbox("Раздел", list(ranges_db[cat].keys()))
    spot = st.selectbox("Спот", list(ranges_db[cat][sub].keys()))
    if st.button("Сброс статистики"):
        st.session_state.stats = {'correct': 0, 'total': 0}
        st.rerun()

# Состояние
if 'hand' not in st.session_state: st.session_state.hand = random.choice(all_hands)
if 'msg' not in st.session_state: st.session_state.msg = None
if 'stats' not in st.session_state: st.session_state.stats = {'correct': 0, 'total': 0}

# Парсинг ренджа
def get_weight(hand, range_str):
    if not range_str: return 0.0
    # Простой парсер для проверки
    items = [x.strip() for x in range_str.split(',')]
    for item in items:
        w = 1.0
        h = item
        if ':' in item:
            h, w_str = item.split(':')
            try: w = float(w_str)
            except: w = 1.0
        
        # Точное совпадение
        if h == hand: return w
        # Если рука AKs, а в рендже AK (без суффикса - значит оба)
        if len(h) == 2 and h[0] != h[1] and hand.startswith(h): return w
    return 0.0

range_str = ranges_db[cat][sub][spot]
weight = get_weight(st.session_state.hand, range_str)

# --- ОТРИСОВКА (ПРЯМО ЗДЕСЬ, БЕЗ ФУНКЦИЙ) ---
h_str = st.session_state.hand
r1, r2 = h_str[0], h_str[1]
suits = ['♠', '♥', '♦', '♣']
s1 = random.choice(suits)
s2 = s1 if 's' in h_str else random.choice([x for x in suits if x != s1])
c1 = "red" if s1 in ['♥', '♦'] else "black"
c2 = "red" if s2 in ['♥', '♦'] else "black"

# HTML код стола
table_html = f"""
<div class="poker-table">
    <h3>{spot}</h3>
    <div class="hero-box">
        <div style="color:gold; font-weight:bold; margin-bottom:5px;">HERO</div>
        <div class="card-box">
            <div class="rank-tl {c1}">{r1}</div>
            <div class="suit-center {c1}">{s1}</div>
        </div>
        <div class="card-box">
            <div class="rank-tl {c2}">{r2}</div>
            <div class="suit-center {c2}">{s2}</div>
        </div>
    </div>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)

# --- КНОПКИ ---
col1, col2 = st.columns(2)

if st.session_state.msg is None:
    with col1:
        if st.button("FOLD"):
            if weight == 0.0:
                st.session_state.msg = "✅ Fold - Верно!"
                st.session_state.stats['correct'] += 1
            else:
                st.session_state.msg = f"❌ Ошибка. Надо Raise {int(weight*100)}%"
            st.session_state.stats['total'] += 1
            st.rerun()
    with col2:
        if st.button("RAISE"):
            if weight > 0.0:
                st.session_state.msg = f"✅ Raise - Верно! ({int(weight*100)}%)"
                st.session_state.stats['correct'] += 1
            else:
                st.session_state.msg = "❌ Ошибка. Надо Fold."
            st.session_state.stats['total'] += 1
            st.rerun()
else:
    # Результат
    msg = st.session_state.msg
    if "✅" in msg: st.success(msg)
    else: st.error(msg)
    
    if st.button("Next Hand ➡️", type="primary"):
        st.session_state.hand = random.choice(all_hands)
        st.session_state.msg = None
        st.rerun()

# Статистика
cor = st.session_state.stats['correct']
tot = st.session_state.stats['total']
st.caption(f"Stats: {cor}/{tot}")
