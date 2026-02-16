import streamlit as st
import json
import random

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Poker Trainer", page_icon="♠️", layout="centered")

# --- 2. CSS СТИЛИ (ЭТО ОТВЕЧАЕТ ЗА КРАСОТУ) ---
st.markdown("""
<style>
    /* Темный фон всего приложения */
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }
    
    /* СУКНО СТОЛА */
    .poker-table {
        background: radial-gradient(ellipse at center, #35654d 0%, #254d39 100%);
        border: 12px solid #3e2723;
        border-radius: 120px;
        padding: 40px;
        margin: 0 auto 30px auto;
        box-shadow: inset 0 0 30px #000, 0 10px 20px rgba(0,0,0,0.5);
        text-align: center;
        max-width: 600px;
    }
    
    /* МЕСТО ХИРО */
    .hero-seat {
        background-color: rgba(0, 0, 0, 0.6);
        border: 2px solid #ffd700;
        border-radius: 16px;
        padding: 15px;
        display: inline-block;
        margin-top: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    
    /* КАРТЫ */
    .poker-card {
        display: inline-block;
        width: 60px;
        height: 88px;
        background-color: white;
        border-radius: 6px;
        margin: 0 5px;
        position: relative;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.4);
        text-align: left;
    }
    
    /* Шрифт на картах */
    .card-rank {
        position: absolute;
        top: 2px;
        left: 4px;
        font-size: 20px;
        font-weight: bold;
        line-height: 1;
        font-family: Arial, sans-serif;
    }
    
    .card-suit-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 32px;
    }

    /* Цвета мастей */
    .suit-red { color: #d32f2f; }
    .suit-black { color: #212121; }

    /* КНОПКИ */
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        font-weight: bold;
        border-radius: 12px;
    }
    
    /* Текст статистики */
    .stats-text {
        text-align: center;
        color: #888;
        margin-top: 20px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ЛОГИКА ПОКЕРА ---
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
            # Обработка пар, суйтед, разномастных без суффиксов
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
    # Пытаемся загрузить JSON
    try:
        with open('ranges.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"Error": {"Error": {"No ranges.json found": ""}}}

# --- 4. ИНТЕРФЕЙС И СОСТОЯНИЕ ---
ranges_db = load_ranges()

# Сайдбар
with st.sidebar:
    st.header("Настройки")
    
    # Защита от пустого файла
    if "Error" in ranges_db:
        st.error("Файл ranges.json не найден!")
        st.stop()
        
    category = st.selectbox("Категория", list(ranges_db.keys()))
    subcategory = st.selectbox("Раздел", list(ranges_db[category].keys()))
    spot_name = st.selectbox("Спот", list(ranges_db[category][subcategory].keys()))
    
    st.divider()
    if st.button("Сброс статистики"):
        st.session_state.stats = {'correct': 0, 'total': 0}
        st.rerun()

# Инициализация переменных
if 'current_hand' not in st.session_state: st.session_state.current_hand = None
if 'feedback' not in st.session_state: st.session_state.feedback = None
if 'stats' not in st.session_state: st.session_state.stats = {'correct': 0, 'total': 0}

# Получаем рендж
range_str = ranges_db[category][subcategory][spot_name]
current_range_dict = parse_range_string(range_str)

# Генерация руки
if st.session_state.current_hand is None:
    st.session_state.current_hand = random.choice(all_hands)

hand = st.session_state.current_hand

# --- 5. ОТРИСОВКА СТОЛА (ГЛАВНАЯ ФУНКЦИЯ) ---
def render_game_visuals(hand_str, title):
    rank1, rank2 = hand_str[0], hand_str[1]
    
    # Генерация мастей
    suits = ['♠', '♥', '♦', '♣']
    s1 = random.choice(suits)
    
    is_suited = (len(hand_str) > 2 and hand_str[2] == 's')
    is_pair = (len(hand_str) == 2)
    
    if is_suited:
        s2 = s1
    elif is_pair:
        s2 = random.choice([s for s in suits if s != s1])
    else:
        s2 = random.choice([s for s in suits if s != s1])
    
    # Определение цвета
    reds = ['♥', '♦']
    c1 = "suit-red" if s1 in reds else "suit-black"
    c2 = "suit-red" if s2 in reds else "suit-black"
    
    # HTML Строка
    html = f"""
    <div class="poker-table">
        <h3 style="color: #ddd; margin-bottom: 30px;">{title}</h3>
        
        <div class="hero-seat">
            <div style="color: gold; font-weight: bold; font-size: 14px; margin-bottom: 8px;">HERO</div>
            
            <div class="poker-card">
                <div class="card-rank {c1}">{rank1}<br>{s1}</div>
                <div class="card-suit-center {c1}">{s1}</div>
            </div>
            
            <div class="poker-card">
                <div class="card-rank {c2}">{rank2}<br>{s2}</div>
                <div class="card-suit-center {c2}">{s2}</div>
            </div>
        </div>
    </div>
    """
    
    # ВЫВОД НА ЭКРАН
    st.markdown(html, unsafe_allow_html=True)

# Вызываем отрисовку
render_game_visuals(hand, spot_name)

# --- 6. КНОПКИ И ПРОВЕРКА ---
correct_weight = current_range_dict.get(hand, 0.0)

col1, col2 = st.columns(2)

# Если пользователь еще не ответил
if st.session_state.feedback is None:
    with col1:
        if st.button("FOLD"):
            if correct_weight == 0.0:
                st.session_state.feedback = "✅ Верно! (Fold)"
                st.session_state.stats['correct'] += 1
            else:
                freq = int(correct_weight * 100)
                st.session_state.feedback = f"❌ Ошибка. Нужно Raise {freq}%"
            st.session_state.stats['total'] += 1
            st.rerun()
            
    with col2:
        if st.button("RAISE"):
            if correct_weight > 0.0:
                if correct_weight == 1.0:
                    st.session_state.feedback = "✅ Верно! (Raise)"
                else:
                    freq = int(correct_weight * 100)
                    st.session_state.feedback = f"⚠️ Верно (Mix). Raise {freq}%"
                st.session_state.stats['correct'] += 1
            else:
                st.session_state.feedback = "❌ Ошибка. Здесь Fold."
            st.session_state.stats['total'] += 1
            st.rerun()

# Если пользователь ответил (показываем результат)
else:
    msg = st.session_state.feedback
    if "✅" in msg:
        st.success(msg)
    elif "❌" in msg:
        st.error(msg)
    else:
        st.warning(msg)
    
    # Кнопка Next
    if st.button("Следующая раздача ➡️", type="primary"):
        st.session_state.current_hand = None
        st.session_state.feedback = None
        st.rerun()

# --- 7. СТАТИСТИКА ---
correct = st.session_state.stats['correct']
total = st.session_state.stats['total']
percent = int(correct/total*100) if total > 0 else 0

st.markdown(
    f"<div class='stats-text'>Статистика сессии: {correct} / {total} ({percent}%)</div>", 
    unsafe_allow_html=True
)
