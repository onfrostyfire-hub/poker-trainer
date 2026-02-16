Начальник, задача понятна. Мы делаем Spaced Repetition System (SRS) — систему интервальных повторений, как в Anki.
Чтобы адаптировать алгоритм Anki (SM-2) под бесконечную покерную сессию (где нет понятия "приходи завтра", а есть "покажи мне это снова через 5 минут"), мы сделаем систему Весовых Коэффициентов.
Логика работы (Алгоритм):
У каждой руки в каждом споте появляется свой «Вес» (Weight):
 * Новая рука: Вес = 10 (Стандарт).
 * Hard (Сложно): Вес становится 50. Рука будет выпадать в 5 раз чаще.
 * Normal (Норм): Вес становится 10. Обычная частота.
 * Easy (Легко): Вес становится 1. Рука будет выпадать очень редко (в 10 раз реже обычной).
Эти данные будут сохраняться в новый файл srs_data.json, так что история обучения будет копиться вечно (пока ты не удалишь файл).
Инструкция (Версия 16.0 — SRS System):
 * Открывай app.py.
 * Удаляй всё.
 * Вставляй код ниже.
 * Commit Changes.
 * Clear Cache (обязательно).
<!-- end list -->
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
    
    /* КНОПКИ ДЕЙСТВИЙ */
    .action-btn { width: 100%; height: 60px; font-size: 18px; font-weight: bold; border-radius: 12px; border: none; color: white; cursor: pointer; }
    .btn-fold { background-color: #b71c1c; box-shadow: 0 4px #7f0000; }
    .btn-raise { background-color: #2e7d32; box-shadow: 0 4px #1b5e20; }
    
    /* КНОПКИ SRS (ANKI) */
    .srs-btn { width: 100%; height: 50px; font-size: 16px; font-weight: bold; border-radius: 8px; border: none; color: white; margin-top: 10px; cursor: pointer; }
    .srs-hard { background-color: #d32f2f; border: 1px solid #ff5252; } /* RED */
    .srs-normal { background-color: #424242; border: 1px solid #757575; } /* GREY */
    .srs-easy { background-color: #2e7d32; border: 1px solid #66bb6a; } /* GREEN */
    
    div.stButton > button { width: 100%; height: 60px; font-size: 18px; font-weight: bold; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# --- БАЗА ДАННЫХ (ОБЩАЯ) ---
ranks = 'AKQJT98765432'
all_hands = []
for i in range(len(ranks)):
    for j in range(len(ranks)):
        if i < j: all_hands.append(ranks[i] + ranks[j] + 's')
        elif i > j: all_hands.append(ranks[j] + ranks[i] + 'o')
        else: all_hands.append(ranks[i] + ranks[j])

# --- ЗАГРУЗКА РЕНДЖЕЙ ---
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
    # Рейтинг: 1=Hard, 2=Normal, 3=Easy
    data = load_srs_data()
    key = f"{spot_id}_{hand}"
    
    # Получаем текущий вес (по умолчанию 10)
    current_weight = data.get(key, 10)
    
    if rating == 'hard':
        new_weight = 50 # Часто
    elif rating == 'normal':
        new_weight = 10 # Стандарт
    elif rating == 'easy':
        new_weight = 1  # Редко
        
    data[key] = new_weight
    save_srs_data(data)

def get_weighted_hand(hand_list, spot_id):
    # Загружаем веса
    srs_data = load_srs_data()
    weights = []
    
    for h in hand_list:
        key = f"{spot_id}_{h}"
        # Если записи нет - вес 10, если есть - берем из базы
        weights.append(srs_data.get(key, 10))
    
    # Выбираем руку с учетом весов
    # Если список пуст, возвращаем случайную
    if not hand_list: return random.choice(all_hands)
    
    chosen_hand = random.choices(hand_list, weights=weights, k=1)[0]
    return chosen_hand

# --- ПАРСЕРЫ ---
def parse_range_to_list(range_str):
    if not range_str: return []
    hand_list = []
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
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
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
    
    # Уникальный ID спота для базы данных
    SPOT_ID = f"{cat}_{sub}_{spot}".replace(" ", "_")
    
    if st.button("Reset Session Stats"):
        st.session_state.stats = {'correct': 0, 'total': 0}
        st.session_state.history = []
        st.rerun()
        
    st.divider()
    # Кнопка сброса прогресса SRS
    if st.button("Reset SRS Memory"):
        if os.path.exists(SRS_FILE): os.remove(SRS_FILE)
        st.toast("Memory wiped!", icon="🧹")

st.markdown(f"<h3 style='text-align: center; margin: -20px 0 20px 0; color: #aaa;'>{spot}</h3>", unsafe_allow_html=True)

# --- ЗАГРУЗКА РУК ---
spot_data = ranges_db[cat][sub][spot]
if isinstance(spot_data, dict):
    full_range_str = spot_data.get("full", "")
    training_range_str = spot_data.get("training", "")
    if not training_range_str: training_range_str = full_range_str
else:
    full_range_str = str(spot_data)
    training_range_str = str(spot_data)

possible_hands = parse_range_to_list(training_range_str)

# --- СОСТОЯНИЕ ---
if 'hand' not in st.session_state: st.session_state.hand = None
if 'suits' not in st.session_state: st.session_state.suits = None
if 'msg' not in st.session_state: st.session_state.msg = None # Результат (Correct/Error)
if 'srs_mode' not in st.session_state: st.session_state.srs_mode = False # Режим выбора сложности
if 'stats' not in st.session_state: st.session_state.stats = {'correct': 0, 'total': 0}
if 'history' not in st.session_state: st.session_state.history = []

# --- ГЕНЕРАЦИЯ (С УЧЕТОМ SRS) ---
if st.session_state.hand is None:
    # Используем умную функцию с весами
    st.session_state.hand = get_weighted_hand(possible_hands, SPOT_ID)
    st.session_state.suits = None
    st.session_state.srs_mode = False # Сбрасываем режим SRS
    st.session_state.msg = None

if st.session_state.suits is None:
    h_str = st.session_state.hand
    suits_pool = ['♠', '♥', '♦', '♣']
    s1 = random.choice(suits_pool)
    if 's' in h_str: s2 = s1
    elif 'o' in h_str: s2 = random.choice([x for x in suits_pool if x != s1])
    else: s2 = random.choice([x for x in suits_pool if x != s1])
    st.session_state.suits = [s1, s2]

# --- ОТРИСОВКА ---
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

def get_chip_html(seat_label):
    if seat_label == "SB": return '<div class="chip sb-chip">SB</div>'
    elif seat_label == "BB": return '<div class="chip bb-chip">BB</div>'
    return ""

seats = get_seats_labels(spot)
h = st.session_state.hand
r1, r2 = h[0], h[1]
s1, s2 = st.session_state.suits 
c1 = "red" if s1 in ['♥','♦'] else "black"
c2 = "red" if s2 in ['♥','♦'] else "black"

html = ""
html += '<div class="game-area"><div class="table-logo">GTO TRAINER</div>'
for i in range(1, 6):
    pos_label = seats[i]
    chip = get_chip_html(pos_label)
    html += f'<div class="seat pos-{i}">{chip}<span class="seat-label">{pos_label}</span><span class="seat-sub">Fold</span></div>'

hero_label = seats[0]
hero_chip = ""
if hero_label == "SB": hero_chip = '<div class="chip sb-chip" style="top:-15px; right:-10px;">SB</div>'
if hero_label == "BB": hero_chip = '<div class="chip bb-chip" style="top:-15px; right:-10px;">BB</div>'

html += '<div class="hero-panel">' + hero_chip
html += f'<div style="display:flex; flex-direction:column; align-items:center; margin-right:5px;"><span style="color:gold; font-weight:bold; font-size:12px;">HERO</span><span style="color:#555; font-size:10px;">{hero_label}</span></div>'
html += f'<div class="card"><div class="tl {c1}">{r1}<br>{s1}</div><div class="cent {c1}">{s1}</div></div>'
html += f'<div class="card"><div class="tl {c2}">{r2}<br>{s2}</div><div class="cent {c2}">{s2}</div></div>'
html += '</div></div>'
st.markdown(html, unsafe_allow_html=True)

# --- ЛОГИКА ДЕЙСТВИЙ ---
weight = get_weight(st.session_state.hand, full_range_str)

def process_action(action):
    is_correct = False
    if action == "FOLD":
        is_correct = (weight == 0.0)
        corr_act = "Fold" if is_correct else "Raise"
    else: # RAISE
        is_correct = (weight > 0.0)
        corr_act = "Raise" if is_correct else "Fold"
    
    st.session_state.stats['total'] += 1
    if is_correct: st.session_state.stats['correct'] += 1
    
    # Сообщение
    if is_correct:
        txt = f"Pure {corr_act}" if weight in [0.0, 1.0] else f"Mix {corr_act} ({int(weight*100)}%)"
        st.session_state.msg = f"✅ Correct! {txt}"
    else:
        req = f"Raise {int(weight*100)}%" if weight > 0 else "Fold"
        st.session_state.msg = f"❌ Error! Required: {req}"
    
    # Лог
    st.session_state.history.append({
        "Spot": spot, "Hand": st.session_state.hand, "Action": action,
        "Correct": corr_act, "Result": "✅" if is_correct else "❌"
    })
    
    # ВКЛЮЧАЕМ SRS РЕЖИМ (Показываем кнопки сложности)
    st.session_state.srs_mode = True 

# --- КНОПКИ (ДВА РЕЖИМА) ---

# РЕЖИМ 1: ВЫБОР ДЕЙСТВИЯ (ИГРА)
if not st.session_state.srs_mode:
    c1, c2 = st.columns(2, gap="small")
    with c1:
        if st.button("FOLD", key="fold_btn"): process_action("FOLD"); st.rerun()
    with c2:
        if st.button("RAISE", key="raise_btn"): process_action("RAISE"); st.rerun()

# РЕЖИМ 2: ОЦЕНКА СЛОЖНОСТИ (SRS)
else:
    # Показываем результат
    msg = st.session_state.msg
    if "✅" in msg: st.success(msg)
    else: st.error(msg)
    
    st.markdown("<div style='text-align: center; color: #888; margin-bottom: 5px;'>How hard was this hand?</div>", unsafe_allow_html=True)
    
    s1, s2, s3 = st.columns(3, gap="small")
    
    # Кнопки стилизованы через CSS выше, но в Streamlit используем обычные с ключами
    # Для цвета используем type="primary" для Easy, но лучше просто текст
    
    with s1:
        if st.button("HARD (Again)", use_container_width=True):
            update_srs(SPOT_ID, st.session_state.hand, 'hard')
            st.session_state.hand = None
            st.session_state.srs_mode = False
            st.rerun()
    with s2:
        if st.button("NORMAL", use_container_width=True):
            update_srs(SPOT_ID, st.session_state.hand, 'normal')
            st.session_state.hand = None
            st.session_state.srs_mode = False
            st.rerun()
    with s3:
        if st.button("EASY (Skip)", type="primary", use_container_width=True):
            update_srs(SPOT_ID, st.session_state.hand, 'easy')
            st.session_state.hand = None
            st.session_state.srs_mode = False
            st.rerun()

# --- СТАТИСТИКА ---
st.divider()
if len(st.session_state.history) > 0:
    with st.expander("Session Log", expanded=False):
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df.iloc[::-1], hide_index=True, use_container_width=True)

Как это работает теперь:
 * Ты выбираешь Fold или Raise.
 * Кнопки действий исчезают.
 * Появляется результат (Галочка или Крестик).
 * Появляются три кнопки: HARD, NORMAL, EASY.
   * Если нажмешь HARD: Рука запомнится как сложная и будет выпадать постоянно.
   * Если нажмешь EASY: Рука почти исчезнет из выдачи.
 * После нажатия на любую из них — сдается новая карта.
Попробуй и скажи, удобно ли.
