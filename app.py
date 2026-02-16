import streamlit as st
import json
import random

# --- ВЕРСИЯ 3.0 (APP STYLE INTERFACE) ---
st.set_page_config(page_title="Poker Trainer Pro", page_icon="♠️", layout="centered")

# --- CSS СТИЛИ (ВИЗУАЛ КАК В ПРИЛОЖЕНИИ) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0a0a0a; /* Очень темный фон приложения */
        color: #e0e0e0;
    }
    
    /* Контейнер для всего игрового поля */
    .game-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 20px;
    }

    /* ОСНОВНОЙ СТОЛ */
    .poker-table-container {
        position: relative;
        width: 95%;
        max-width: 600px;
        height: 350px; /* Фиксированная высота для позиционирования */
        background: radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%); /* Глубокий зеленый */
        border: 12px solid #3e2723; /* Деревянный борт */
        border-radius: 180px; /* Овальная форма */
        box-shadow: inset 0 0 50px rgba(0,0,0,0.8), 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 60px; /* Место для Хиро снизу */
    }

    /* ЛОГОТИП ПО ЦЕНТРУ СТОЛА */
    .table-center-logo {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 24px;
        color: rgba(255,255,255,0.1);
        font-weight: bold;
        pointer-events: none;
    }

    /* ОБЩИЙ СТИЛЬ МЕСТ ОППОНЕНТОВ */
    .villain-seat {
        position: absolute;
        width: 70px;
        height: 70px;
        background: rgba(0,0,0,0.6);
        border: 3px solid #555;
        border-radius: 50%; /* Круглые аватарки */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: #aaa;
        font-size: 12px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
    }
    .villain-seat span { font-weight: bold; color: #ddd; }

    /* ПОЗИЦИИ ОППОНЕНТОВ (6-max) */
    .seat-1 { top: -20px; left: 25%; } /* Top Left */
    .seat-2 { top: -20px; right: 25%; } /* Top Right */
    .seat-3 { top: 40%; right: -25px; } /* Right */
    .seat-4 { bottom: 20%; right: 5%; } /* Bottom Right */
    .seat-5 { bottom: 20%; left: 5%; } /* Bottom Left */
    
    /* МЕСТО ХИРО (ОСОБОЕ) */
    .hero-seat-container {
        position: absolute;
        bottom: -50px; /* Свисает с края стола */
        left: 50%;
        transform: translateX(-50%);
        
        background: linear-gradient(to bottom, #2c2c2c, #1a1a1a);
        border: 3px solid #ffd700; /* Золотая обводка */
        border-radius: 20px;
        padding: 10px 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.3); /* Золотое свечение */
        z-index: 10;
    }

    /* КОНТЕЙНЕР ДЛЯ КАРТ ХИРО */
    .hero-cards-row {
        display: flex;
        gap: 5px;
    }

    /* САМА КАРТА */
    .card-box {
        width: 55px;
        height: 80px;
        background: white;
        border-radius: 5px;
        position: relative;
        color: black;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.3);
    }
    
    .rank-tl { position: absolute; top: 2px; left: 4px; font-weight: bold; font-size: 18px; line-height: 1; }
    .suit-center { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 32px; }
    
    .red { color: #d32f2f; }
    .black { color: #212121; }
    
    /* КНОПКИ ДЕЙСТВИЙ */
    div.stButton > button { 
        width: 100%; height: 65px; 
        font-size: 20px; border-radius: 14px; 
        font-weight: bold; text-transform: uppercase;
        border: none;
    }
    /* Цвета кнопок через хак (nth-of-type) - Fold красный, Raise зеленый */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button { background-color: #d32f2f; color: white; }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { background-color: #2e7d32; color: white; }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover { background-color: #b71c1c; }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover { background-color: #1b5e20; }

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
# Заголовок спота крупно
st.markdown(f"<h2 style='text-align: center; margin-bottom: 0;'>{st.session_state.get('spot_name_title', 'Poker Trainer')}</h2>", unsafe_allow_html=True)

if not ranges_db:
    st.error("Файл ranges.json не найден!")
    st.stop()

# Сайдбар
with st.sidebar:
    st.header("Настройки")
    cat = st.selectbox("Категория", list(ranges_db.keys()))
    sub = st.selectbox("Раздел", list(ranges_db[cat].keys()))
    spot = st.selectbox("Спот", list(ranges_db[cat][sub].keys()))
    st.session_state['spot_name_title'] = spot # Сохраняем для заголовка
    if st.button("Сброс статистики"):
        st.session_state.stats = {'correct': 0, 'total': 0}
        st.rerun()

# Состояние
if 'hand' not in st.session_state: st.session_state.hand = random.choice(all_hands)
if 'msg' not in st.session_state: st.session_state.msg = None
if 'stats' not in st.session_state: st.session_state.stats = {'correct': 0, 'total': 0}

# Парсинг ренджа (упрощенный)
def get_weight(hand, range_str):
    if not range_str: return 0.0
    items = [x.strip() for x in range_str.split(',')]
    for item in items:
        w = 1.0
        h = item
        if ':' in item:
            h, w_str = item.split(':')
            try: w = float(w_str)
            except: w = 1.0
        if h == hand: return w
        if len(h) == 2 and h[0] != h[1] and hand.startswith(h): return w
    return 0.0

range_str = ranges_db[cat][sub][spot]
weight = get_weight(st.session_state.hand, range_str)

# --- ОТРИСОВКА ИГРОВОГО ПОЛЯ ---
h_str = st.session_state.hand
r1, r2 = h_str[0], h_str[1]
suits = ['♠', '♥', '♦', '♣']
s1 = random.choice(suits)
s2 = s1 if 's' in h_str else random.choice([x for x in suits if x != s1])
c1 = "red" if s1 in ['♥', '♦'] else "black"
c2 = "red" if s2 in ['♥', '♦'] else "black"

# HTML СТРУКТУРА СТОЛА
table_html = f"""
<div class="game-container">
    <div class="poker-table-container">
        <div class="table-center-logo">GTO TRAINER</div>
        
        <div class="villain-seat seat-1"><span>Villain 1</span>Customer</div>
        <div class="villain-seat seat-2"><span>Villain 2</span>Customer</div>
        <div class="villain-seat seat-3"><span>Villain 3</span>Customer</div>
        <div class="villain-seat seat-4"><span>Villain 4</span>Customer</div>
        <div class="villain-seat seat-5"><span>Villain 5</span>Customer</div>
        
        <div class="hero-seat-container">
            <div style="color:gold; font-weight:bold; margin-bottom:5px; font-size: 14px;">⭐️ HERO (You)</div>
            <div class="hero-cards-row">
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
    </div>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)

# --- КНОПКИ ---
col1, col2 = st.columns(2, gap="medium") # Добавил отступ между кнопками

if st.session_state.msg is None:
    with col1:
        if st.button("FOLD"):
            if weight == 0.0:
                st.session_state.msg = "✅ Fold - Верно!"
                st.session_state.stats['correct'] += 1
            else:
                freq = int(weight*100)
                st.session_state.msg = f"❌ Ошибка. Нужно Raise {freq}%"
            st.session_state.stats['total'] += 1
            st.rerun()
    with col2:
        if st.button("RAISE"):
            if weight > 0.0:
                freq = int(weight*100)
                if weight == 1.0: st.session_state.msg = "✅ Raise - Верно! (100%)"
                else: st.session_state.msg = f"✅ Raise - Верно! (Mix {freq}%)"
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
    
    # Кнопка Next (обычная серая, чтобы не отвлекала)
    if st.button("Next Hand ➡️"):
        st.session_state.hand = random.choice(all_hands)
        st.session_state.msg = None
        st.rerun()

# Статистика
cor = st.session_state.stats['correct']
tot = st.session_state.stats['total']
perc = int(cor/tot*100) if tot > 0 else 0
st.markdown(f"<div style='text-align:center; color:#888; margin-top:10px;'>Session Stats: {cor}/{tot} ({perc}%)</div>", unsafe_allow_html=True)
