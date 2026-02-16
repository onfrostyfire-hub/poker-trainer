import streamlit as st
import json
import random

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="GTO Trainer", page_icon="♠️", layout="centered")

# --- CSS СТИЛИ (ВИЗУАЛ) ---
st.markdown("""
<style>
    /* Темная тема для всего приложения */
    .stApp {
        background-color: #1e1e1e;
        color: white;
    }
    
    /* Зеленый покерный стол */
    .poker-table {
        background: radial-gradient(ellipse at center, #35654d 0%, #254d39 100%);
        border: 15px solid #3e2723;
        border-radius: 100px; /* Более овальный */
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: inset 0 0 20px #000;
        text-align: center;
    }
    
    /* Место героя */
    .hero-seat {
        background-color: rgba(0,0,0,0.5);
        border: 2px solid #ffd700;
        border-radius: 15px;
        padding: 10px;
        display: inline-block;
        margin-top: 20px;
    }
    
    /* Сами карты */
    .playing-card {
        display: inline-block;
        width: 60px;
        height: 90px;
        background-color: #fdfdfd;
        border-radius: 6px;
        margin: 4px;
        position: relative;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.5);
    }
    
    .card-top-left {
        position: absolute;
        top: 2px;
        left: 4px;
        font-size: 20px;
        font-weight: bold;
        line-height: 1;
    }
    
    .card-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 30px;
    }

    .red-suit { color: #d32f2f; }
    .black-suit { color: #212121; }
    
    /* Стиль кнопок */
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        border-radius: 12px;
        border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# --- ЛОГИКА ---
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
try:
    ranges_db = load_ranges()
except:
    st.error("Ошибка загрузки ranges.json. Проверь, что файл существует и там правильный JSON.")
    st.stop()

with st.sidebar:
    st.title("Settings")
    category = st.selectbox("Category", list(ranges_db.keys()))
    subcategory = st.selectbox("Section", list(ranges_db[category].keys()))
    spot_name = st.selectbox("Spot", list(ranges_db[category][subcategory].keys()))
    
    if st.button("Reset Stats"):
        st.session_state.stats = {'correct': 0, 'total': 0}
        st.rerun()

# Инициализация
if 'current_hand' not in st.session_state: st.session_state.current_hand = None
if 'feedback' not in st.session_state: st.session_state.feedback = None
if 'stats' not in st.session_state: st.session_state.stats = {'correct': 0, 'total': 0}

# Получаем рендж
range_str = ranges_db[category][subcategory][spot_name]
current_range_dict = parse_range_string(range_str)

# Новая рука
if st.session_state.current_hand is None:
    st.session_state.current_hand = random.choice(all_hands)

hand = st.session_state.current_hand

# --- ФУНКЦИЯ ОТРИСОВКИ (Исправленная) ---
def render_game(hand_str, spot_title):
    rank1 = hand_str[0]
    rank2 = hand_str[1]
    
    # Определяем масти
    suits_list = ['♠', '♥', '♦', '♣']
    s1 = random.choice(suits_list)
    
    is_suited = (len(hand_str) > 2 and hand_str[2] == 's')
    is_offsuit = (len(hand_str) > 2 and hand_str[2] == 'o')
    is_pair = (len(hand_str) == 2)

    if is_suited:
        s2 = s1
    elif is_pair:
        # Для пары масть второй карты любая, кроме первой
        available = [s for s in suits_list if s != s1]
        s2 = random.choice(available)
    else: 
        # Для разномастных (offsuit) тоже любая другая
        available = [s for s in suits_list if s != s1]
        s2 = random.choice(available)
    
    # Определяем цвет (для CSS)
    # Червы и Бубны - красные
    red_suits = ['♥', '♦']
    c1_css = "red-suit" if s1 in red_suits else "black-suit"
    c2_css = "red-suit" if s2 in red_suits else "black-suit"

    # HTML код стола
    html_code = f"""
    <div class="poker-table">
        <h3 style="margin:0; color:#eee;">{spot_title}</h3>
        <div style="height: 30px;"></div>
        
        <div class="hero-seat">
            <div style="color: gold; font-weight: bold; font-size: 14px; margin-bottom: 5px;">HERO</div>
            
            <div class="playing-card">
                <div class="card-top-left {c1_css}">{rank1}<br>{s1}</div>
                <div class="card-center {c1_css}">{s1}</div>
            </div>
            
            <div class="playing-card">
                <div class="card-top-left {c2_css}">{rank2}<br>{s2}</div>
                <div class="card-center {c2_css}">{s2}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# Рисуем стол
render_game(hand, spot_name)

# Логика весов
correct_weight = current_range_dict.get(hand, 0.0)

# Кнопки управления
col1, col2 = st.columns(2)

if st.session_state.feedback is None:
    with col1:
        if st.button("FOLD"):
            # Если вес 0, значит фолд правильный
            is_correct = (correct_weight == 0.0)
            if is_correct:
                msg = "✅ Верно! (Fold)"
                st.session_state.stats['correct'] += 1
            else:
                freq = int(correct_weight * 100)
                msg = f"❌ Ошибка. Нужно Raise {freq}%"
            
            st.session_state.feedback = msg
            st.session_state.stats['total'] += 1
            st.rerun()
            
    with col2:
        if st.button("RAISE"):
            # Если вес > 0, значит рейз (или микс) правильный
            is_correct = (correct_weight > 0.0)
            if is_correct:
                if correct_weight == 1.0:
                    msg = "✅ Верно! (Pure Raise)"
                else:
                    freq = int(correct_weight * 100)
                    msg = f"⚠️ Верно (Mix). Raise {freq}%"
                st.session_state.stats['correct'] += 1
            else:
                msg = "❌ Ошибка. Здесь Fold."
            
            st.session_state.feedback = msg
            st.session_state.stats['total'] += 1
            st.rerun()

else:
    # Отображение результата
    if "✅" in st.session_state.feedback:
        st.success(st.session_state.feedback)
    elif "❌" in st.session_state.feedback:
        st.error(st.session_state.feedback)
    else:
        st.warning(st.session_state.feedback)
    
    # Кнопка Next
    if st.button("Next Hand ➡️", type="primary"):
        st.session_state.current_hand = None
        st.session_state.feedback = None
        st.rerun()

# Статистика
cor = st.session_state.stats['correct']
tot = st.session_state.stats['total']
perc = int(cor/tot*100) if tot > 0 else 0
st.markdown(f"<div style='text-align:center; color:grey; margin-top:20px;'>Stats: {cor}/{tot} ({perc}%)</div>", unsafe_allow_html=True)
