import streamlit as st
import json
import random
import pandas as pd # Подключаем панд для красивых таблиц

# --- ВЕРСИЯ 15.0 (CHIPS & ANALYTICS) ---
st.set_page_config(page_title="Poker Trainer Pro", page_icon="♠️", layout="centered")

# --- CSS СТИЛИ ---
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    .game-area { position: relative; width: 100%; max-width: 500px; height: 340px; margin: 0 auto 30px auto; background: radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%); border: 10px solid #3e2723; border-radius: 170px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .table-logo { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); color: rgba(255,255,255,0.1); font-weight: bold; font-size: 24px; pointer-events: none; }
    
    /* МЕСТА */
    .seat { position: absolute; width: 55px; height: 55px; background: rgba(0,0,0,0.85); border: 2px solid #555; border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.4); z-index: 5; }
    .seat-label { color: #fff; font-weight: bold; font-size: 13px; }
    .seat-sub { color: #888; font-size: 9px; }
    
    /* ФИШКИ БЛАЙНДОВ */
    .chip { position: absolute; width: 20px; height: 20px; border-radius: 50%; font-size: 9px; color: #000; font-weight: bold; display: flex; justify-content: center; align-items: center; box-shadow: 1px 1px 3px rgba(0,0,0,0.5); z-index: 20; }
    .sb-chip { background: #ffd700; top: -5px; right: -5px; border: 1px solid #e6c200; } /* Желтая */
    .bb-chip { background: #ff5722; top: -5px; right: -5px; border: 1px solid #e64a19; } /* Оранжевая */
    
    /* РАССТАНОВКА */
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

# --- САЙДБАР ---
with st.sidebar:
    st.title("Settings")
    cat = st.selectbox("Category", list(ranges_db.keys()))
    sub = st.selectbox("Section", list(ranges_db[cat].keys()))
    spot = st.selectbox("Spot", list(ranges_db[cat][sub].keys()))
    if st.button("Reset Session Stats"):
        st.session_state.stats = {'correct': 0, 'total': 0}
        st.session_state.history = [] # Очищаем историю ошибок
        st.rerun()

st.markdown(f"<h3 style='text-align: center; margin: -20px 0 20px 0; color: #aaa;'>{spot}</h3>", unsafe_allow_html=True)

# --- ИНИЦИАЛИЗАЦИЯ ДАННЫХ ---
spot_data = ranges_db[cat][sub][spot]
if isinstance(spot_data, dict):
    full_range_str = spot_data.get("full", "")
    training_range_str = spot_data.get("training", "")
    if not training_range_str: training_range_str = full_range_str
else:
    full_range_str = str(spot_data)
    training_range_str = str(spot_data)

# --- СОСТОЯНИЕ ---
if 'hand' not in st.session_state: st.session_state.hand = None
if 'suits' not in st.session_state: st.session_state.suits = None
if 'msg' not in st.session_state: st.session_state.msg = None
if 'stats' not in st.session_state: st.session_state.stats = {'correct': 0, 'total': 0}
if 'history' not in st.session_state: st.session_state.history = [] # Список для лога ошибок

# --- ГЕНЕРАЦИЯ ---
possible_hands = parse_range_to_list(training_range_str)

# Индикатор пула рук (для проверки)
if len(possible_hands) < 169:
    st.sidebar.success(f"🎯 Training Mode: {len(possible_hands)} hands")
else:
    st.sidebar.warning(f"⚠️ Full Pool: {len(possible_hands)} hands")

if st.session_state.hand is None:
    if not possible_hands: possible_hands = all_hands
    st.session_state.hand = random.choice(possible_hands)
    st.session_state.suits = None

if st.session_state.suits is None:
    h_str = st.session_state.hand
    suits_pool = ['♠', '♥', '♦', '♣']
    s1 = random.choice(suits_pool)
    if 's' in h_str: s2 = s1
    elif 'o' in h_str: s2 = random.choice([x for x in suits_pool if x != s1])
    else: s2 = random.choice([x for x in suits_pool if x != s1])
    st.session_state.suits = [s1, s2]

# --- ПОЗИЦИИ И ФИШКИ ---
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

# Функция для генерации HTML фишки
def get_chip_html(seat_label):
    if seat_label == "SB":
        return '<div class="chip sb-chip">SB</div>'
    elif seat_label == "BB":
        return '<div class="chip bb-chip">BB</div>'
    return ""

# --- ОТРИСОВКА ---
h = st.session_state.hand
r1, r2 = h[0], h[1]
s1, s2 = st.session_state.suits 
c1 = "red" if s1 in ['♥','♦'] else "black"
c2 = "red" if s2 in ['♥','♦'] else "black"

html = ""
html += '<div class="game-area">'
html += '<div class="table-logo">GTO TRAINER</div>'

# Отрисовка мест оппонентов с фишками
for i in range(1, 6):
    pos_label = seats[i]
    chip = get_chip_html(pos_label)
    html += f'<div class="seat pos-{i}">{chip}<span class="seat-label">{pos_label}</span><span class="seat-sub">Fold</span></div>'

# Отрисовка Хиро с фишкой (если Хиро на SB/BB)
hero_label = seats[0]
hero_chip = ""
if hero_label == "SB": hero_chip = '<div class="chip sb-chip" style="top:-15px; right:-10px;">SB</div>'
if hero_label == "BB": hero_chip = '<div class="chip bb-chip" style="top:-15px; right:-10px;">BB</div>'

html += '<div class="hero-panel">'
html += hero_chip
html += '<div style="display:flex; flex-direction:column; align-items:center; margin-right:5px;">'
html += f'<span style="color:gold; font-weight:bold; font-size:12px;">HERO</span>'
html += f'<span style="color:#555; font-size:10px;">{hero_label}</span>'
html += '</div>'
html += f'<div class="card"><div class="tl {c1}">{r1}<br>{s1}</div><div class="cent {c1}">{s1}</div></div>'
html += f'<div class="card"><div class="tl {c2}">{r2}<br>{s2}</div><div class="cent {c2}">{s2}</div></div>'
html += '</div></div>'

st.markdown(html, unsafe_allow_html=True)

# --- ЛОГИКА ---
weight = get_weight(st.session_state.hand, full_range_str)

# Функция записи результата
def log_result(is_correct, action_taken, correct_action, hand_played, spot_played):
    st.session_state.stats['total'] += 1
    if is_correct:
        st.session_state.stats['correct'] += 1
    
    # Записываем в историю (только ошибки, или все - давай все, фильтранем потом)
    st.session_state.history.append({
        "Spot": spot_played,
        "Hand": hand_played,
        "My Action": action_taken,
        "Correct Action": correct_action,
        "Result": "✅" if is_correct else "❌"
    })

c1, c2 = st.columns(2, gap="small")

if st.session_state.msg is None:
    with c1:
        if st.button("FOLD"):
            if weight == 0.0:
                st.session_state.msg = "✅ Correct! (Fold)"
                log_result(True, "Fold", "Fold", st.session_state.hand, spot)
            else:
                st.session_state.msg = f"❌ Error! Raise {int(weight*100)}%"
                log_result(False, "Fold", "Raise", st.session_state.hand, spot)
            st.rerun()
    with c2:
        if st.button("RAISE"):
            if weight > 0.0: 
                txt = "Pure" if weight==1.0 else f"Mix {int(weight*100)}%"
                st.session_state.msg = f"✅ Correct! ({txt})"
                log_result(True, "Raise", "Raise", st.session_state.hand, spot)
            else:
                st.session_state.msg = "❌ Error! Fold"
                log_result(False, "Raise", "Fold", st.session_state.hand, spot)
            st.rerun()
else:
    msg = st.session_state.msg
    if "✅" in msg: st.success(msg)
    else: st.error(msg)
    if st.button("Next Hand ➡️"):
        st.session_state.hand = None
        st.session_state.suits = None
        st.session_state.msg = None
        st.rerun()

# --- СТАТИСТИКА И ТАБЛИЦА ---
st.divider()
st.subheader("📊 Session Statistics")

# Общая стата
cor = st.session_state.stats['correct']
tot = st.session_state.stats['total']
perc = int(cor/tot*100) if tot > 0 else 0
st.progress(perc)
st.caption(f"Total Accuracy: {cor}/{tot} ({perc}%)")

# Таблица ошибок
if len(st.session_state.history) > 0:
    df = pd.DataFrame(st.session_state.history)
    
    # Фильтр "Показывать только ошибки"
    show_errors = st.checkbox("Show only errors", value=True)
    
    if show_errors:
        df_display = df[df["Result"] == "❌"]
    else:
        df_display = df
    
    if not df_display.empty:
        # Отображаем таблицу (перевернув, чтобы новые были сверху)
        st.dataframe(df_display.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.info("No errors yet! Great job!")
else:
    st.info("Play some hands to see statistics.")
