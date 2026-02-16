import streamlit as st
import json
import random
import pandas as pd
import os

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Poker Trainer", layout="wide")

# --- CSS ДЛЯ КРАСОТЫ (КАРТЫ И КНОПКИ) ---
st.markdown("""
<style>
    .card {
        display: inline-block;
        width: 60px;
        height: 85px;
        border: 2px solid #333;
        border-radius: 8px;
        background-color: white;
        color: black;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        line-height: 85px;
        margin: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .card.red { color: #d00; }
    .card.black { color: #000; }
    .big-font { font-size: 30px !important; }
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- ЛОГИКА ПАРСИНГА РЕНДЖЕЙ ---
# Создаем список всех возможных рук (169 стартеров)
ranks = 'AKQJT98765432'
all_hands = []
for i in range(len(ranks)):
    for j in range(len(ranks)):
        card1 = ranks[i]
        card2 = ranks[j]
        if i < j:
            hand = card1 + card2 + 's' # Suited
        elif i > j:
            hand = card2 + card1 + 'o' # Offsuit
        else:
            hand = card1 + card2 # Pair
        all_hands.append(hand)

def parse_range_string(range_str):
    """Превращает строку 'AA,KK:0.5' в словарь {Hand: Weight}"""
    range_dict = {h: 0.0 for h in all_hands} # По умолчанию фолд (0%)
    
    if not range_str:
        return range_dict

    items = [x.strip() for x in range_str.split(',')]
    
    for item in items:
        if not item: continue
        
        weight = 1.0
        hand_code = item
        
        # Проверяем вес (например :0.5)
        if ':' in item:
            parts = item.split(':')
            hand_code = parts[0].strip()
            try:
                weight = float(parts[1])
            except:
                weight = 1.0
        
        # Обработка руки
        # Если рука написана как AK, но без s/o - это обычно ошибка в таких стрингах,
        # но если это пара (AA), то ок. Если не пара (AK), проверим есть ли s/o.
        # В твоем формате:
        # AA - пара
        # AK - часто означает AKo + AKs, но в солверах часто AKo и AKs пишут отдельно.
        # Если написано просто AK и это не пара -> считаем как AKs и AKo (упрощение),
        # но по твоим данным у тебя четко A9s, A8o. 
        # Если написано AK (без суффикса) и это не пара, добавим оба.
        
        target_hands = []
        
        if hand_code in all_hands:
            target_hands.append(hand_code)
        else:
            # Попробуем найти суффиксы, если их нет
            if len(hand_code) == 2 and hand_code[0] != hand_code[1]:
                s = hand_code + 's'
                o = hand_code + 'o'
                if s in all_hands: target_hands.append(s)
                if o in all_hands: target_hands.append(o)
            elif len(hand_code) == 2 and hand_code[0] == hand_code[1]: # Пара
                 if hand_code in all_hands: target_hands.append(hand_code)

        for h in target_hands:
            range_dict[h] = weight

    return range_dict

# --- ЗАГРУЗКА ДАННЫХ ---
@st.cache_data
def load_ranges():
    with open('ranges.json', 'r', encoding='utf-8') as f:
        return json.load(f)

ranges_db = load_ranges()

# --- ИНТЕРФЕЙС ---
st.title("🃏 Preflop GTO Trainer")

# Сайдбар для выбора
with st.sidebar:
    category = st.selectbox("Category", list(ranges_db.keys()))
    subcategory = st.selectbox("Section", list(ranges_db[category].keys()))
    spot_name = st.selectbox("Spot", list(ranges_db[category][subcategory].keys()))
    
    # Кнопка сброса (новой раздачи)
    if st.button("Next Hand ➡️"):
        st.session_state.current_hand = None
        st.session_state.feedback = None

# --- ИГРОВОЙ ПРОЦЕСС ---

# Инициализация состояния
if 'current_hand' not in st.session_state:
    st.session_state.current_hand = None
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'stats' not in st.session_state:
    st.session_state.stats = {'correct': 0, 'total': 0}

# Получаем текущий рендж
range_str = ranges_db[category][subcategory][spot_name]
current_range_dict = parse_range_string(range_str)

# Генерация руки, если нет текущей
if st.session_state.current_hand is None:
    # Генерируем с учетом вероятностей покера (6 комбинаций пар, 4 суйтед, 12 разномаст)
    # Но для тренера лучше равновероятно, чтобы редкие руки тоже падали?
    # Давай просто рандомную руку из 169.
    st.session_state.current_hand = random.choice(all_hands)

hand = st.session_state.current_hand

# Визуализация карты
def render_hand(hand_str):
    rank1, rank2 = hand_str[0], hand_str[1]
    suit_type = hand_str[2] if len(hand_str) > 2 else ''
    
    # Для визуала просто нарисуем масти рандомно, но логично
    suits = ['♠', '♥', '♦', '♣']
    if suit_type == 's':
        s1 = random.choice(suits)
        s2 = s1
    elif suit_type == 'o':
        s1 = random.choice(suits)
        remaining = [s for s in suits if s != s1]
        s2 = random.choice(remaining)
    else: # Pairs
        s1 = random.choice(suits)
        remaining = [s for s in suits if s != s1]
        s2 = random.choice(remaining)
        
    color1 = "red" if s1 in ['♥', '♦'] else "black"
    color2 = "red" if s2 in ['♥', '♦'] else "black"
    
    html = f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <div class="card {color1}">{rank1}{s1}</div>
        <div class="card {color2}">{rank2}{s2}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

st.markdown(f"### Spot: {spot_name}")
render_hand(hand)

# Логика проверки
correct_weight = current_range_dict.get(hand, 0.0)

col1, col2 = st.columns(2)

def check_answer(action):
    is_raise = (action == "Raise")
    
    msg = ""
    # Если вес 1.0 (100% рейз)
    if correct_weight == 1.0:
        if is_raise: msg = "✅ Правильно! (Always Raise)"
        else: msg = "❌ Ошибка. Здесь 100% Raise."
    
    # Если вес 0.0 (100% фолд)
    elif correct_weight == 0.0:
        if not is_raise: msg = "✅ Правильно! (Fold)"
        else: msg = "❌ Ошибка. Здесь Fold."
        
    # Если микс (0 < вес < 1)
    else:
        freq = int(correct_weight * 100)
        msg = f"⚠️ MIX! Raise: {freq}%, Fold: {100-freq}%."
        if is_raise: msg += " Ты сыграл Рейз."
        else: msg += " Ты сыграл Фолд."
    
    st.session_state.feedback = msg
    
    # Запись статы (упрощенно)
    if (correct_weight == 1.0 and is_raise) or (correct_weight == 0.0 and not is_raise):
        st.session_state.stats['correct'] += 1
    st.session_state.stats['total'] += 1

# Кнопки (показываем только если нет ответа)
if st.session_state.feedback is None:
    with col1:
        if st.button("FOLD"):
            check_answer("Fold")
            st.rerun()
    with col2:
        if st.button("RAISE"):
            check_answer("Raise")
            st.rerun()
else:
    # Показываем результат
    if "✅" in st.session_state.feedback:
        st.success(st.session_state.feedback)
    elif "❌" in st.session_state.feedback:
        st.error(st.session_state.feedback)
    else:
        st.warning(st.session_state.feedback)
    
    if st.button("Next Hand ➡️", key="next_btn"):
        st.session_state.current_hand = None
        st.session_state.feedback = None
        st.rerun()

# Статистика сессии
st.divider()
sc = st.session_state.stats['correct']
stt = st.session_state.stats['total']
if stt > 0:
    st.markdown(f"**Session Stats:** {sc}/{stt} ({int(sc/stt*100)}%)")