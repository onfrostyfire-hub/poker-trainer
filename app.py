import streamlit as st
import json
import random

# --- НАСТРОЙКИ СТРАНИЦЫ (Скрываем лишнее, ставим иконку) ---
st.set_page_config(page_title="GTO Trainer", page_icon="♠️", layout="centered")

# --- CSS СТИЛИ (ВИЗУАЛ) ---
# Рисуем стол, карты и кнопки через CSS
st.markdown("""
<style>
    /* Темная тема и фон */
    .stApp {
        background-color: #1e1e1e;
    }
    
    /* Покерный стол (овал) */
    .poker-table {
        background: radial-gradient(ellipse at center, #35654d 0%, #254d39 100%);
        border: 15px solid #3e2723; /* Бортик стола */
        border-radius: 150px;
        padding: 40px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        text-align: center;
        position: relative;
        min-height: 300px;
    }
    
    /* Позиция Хиро */
    .hero-seat {
        background-color: rgba(0,0,0,0.6);
        border-radius: 15px;
        padding: 10px;
        display: inline-block;
        margin-top: 20px;
        border: 2px solid #daa520; /* Золотая обводка */
    }
    
    /* Карты */
    .card {
        display: inline-block;
        width: 70px;
        height: 100px;
        background-color: white;
        border-radius: 8px;
        margin: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.4);
        position: relative;
    }
    
    .card-rank {
        position: absolute;
        top: 5px;
        left: 5px;
        font-size: 24px;
        font-weight: bold;
    }
    
    .card-suit {
        position: absolute;
        bottom: 5px;
        right: 5px;
        font-size: 36px;
    }
    
    .red { color: #d32f2f; }
    .black { color: #212121; }
    
    /* Кнопки действий */
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        color: white;
        transition: transform 0.1s;
    }
    
    /* Цвета кнопок (через nth-child, т.к. Streamlit не дает ставить классы на кнопки напрямую) */
    /* Это хак, но для начала сойдет. */
    
    /* Текст статистики */
    .stats-box {
        background-color: #333;
        color: #eee;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-top: 10px;
        font-family: monospace;
    }
    
</style>
""", unsafe_allow_html=True)

# --- ЛОГИКА (БЕЗ ИЗМЕНЕНИЙ) ---
ranks = 'AKQJT98765432'
all_hands = []
for i in range(len(ranks)):
    for j in range(len(ranks)):
        card1 = ranks[i]
        card2 = ranks[j]
        if i < j: all_hands.append(card1 + card2 + 's')
        elif i > j: all_hands.append(card2 + card1 + 'o')
        else: all_hands.append(card1 + card2)

def parse_range_string(range_str):
    range_dict = {h: 0.0 for h in all_hands}
    if not range_str: return range_dict
    items = [x.strip() for x in range_str.split(',')]
    for item in items:
        if not item: continue
        weight = 1.0
        hand_code = item
        if ':' in item:
            parts = item.split(':')
            hand_code = parts[0].strip()
            try: weight = float(parts[1])
            except: weight = 1.0
        
        target_hands = []
        if hand_code in all_hands:
            target_hands.append(hand_code)
        else:
            if len(hand_code) == 2 and hand_code[0] != hand_code[1]:
                s, o = hand_code + 's', hand_code + 'o'
                if s in all_hands: target_hands.append(s)
                if o in all_hands: target_hands.append(o)
            elif len(hand_code) == 2 and hand_code[0] == hand_code[1]:
                 if hand_code in all_hands: target_hands.append(hand_code)

        for h in target_hands: range_dict[h] = weight
    return range_dict

@st.cache_data
def load_ranges():
    with open('ranges.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# --- ИНТЕРФЕЙС ---

# Сайдбар
ranges_db = load_ranges()
with st.sidebar:
    st.header("⚙️ Настройки")
    category = st.selectbox("Пак", list(ranges_db.keys()))
    subcategory = st.selectbox("Раздел", list(ranges_db[category].keys()))
    spot_name = st.selectbox("Ситуация (Spot)", list(ranges_db[category][subcategory].keys()))
    
    st.divider()
    if st.button("Сбросить статистику"):
        st.session_state.stats = {'correct': 0, 'total': 0}
        st.rerun()

# Состояние
if 'current_hand' not in st.session_state: st.session_state.current_hand = None
if 'feedback' not in st.session_state: st.session_state.feedback = None
if 'stats' not in st.session_state: st.session_state.stats = {'correct': 0, 'total': 0}

# Загрузка
range_str = ranges_db[category][subcategory][spot_name]
current_range_dict = parse_range_string(range_str)

if st.session_state.current_hand is None:
    st.session_state.current_hand = random.choice(all_hands)

hand = st.session_state.current_hand

# --- ВИЗУАЛИЗАЦИЯ (ФУНКЦИЯ) ---
def render_game(hand_str, spot_title):
    # Разбор руки
    rank1, rank2 = hand_str[0], hand_str[1]
    suit_type = hand_str[2] if len(hand_str) > 2 else ''
    
    suits = ['♠', '♥', '♦', '♣']
    s1 = random.choice(suits)
    if suit_type == 's': s2 = s1
    elif suit_type == 'o': 
        s2 = random.choice([s for s in suits if s != s1])
    else: 
        s2 = random.choice([s for s in suits if s != s1])
        
    c1_class = "red" if s1 in ['♥
