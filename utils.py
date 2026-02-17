import streamlit as st
import json
import pandas as pd
import os
import random

# КОНСТАНТЫ
HISTORY_FILE = 'history_log.csv'
SRS_FILE = 'srs_data.json'
RANGES_FILE = 'ranges.json'
SETTINGS_FILE = 'user_settings.json'
RANKS = 'AKQJT98765432'
ALL_HANDS = []
for i, r1 in enumerate(RANKS):
    for j, r2 in enumerate(RANKS):
        if i < j: ALL_HANDS.append(r1 + r2 + 's'); ALL_HANDS.append(r1 + r2 + 'o')
        elif i == j: ALL_HANDS.append(r1 + r2)

# ЗАГРУЗКА ДАННЫХ
@st.cache_data(ttl=0)
def load_ranges():
    if not os.path.exists(RANGES_FILE): return {}
    with open(RANGES_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def load_srs_data():
    if not os.path.exists(SRS_FILE): return {}
    with open(SRS_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def save_srs_data(data):
    with open(SRS_FILE, 'w', encoding='utf-8') as f: json.dump(data, f)

def load_user_settings():
    if not os.path.exists(SETTINGS_FILE): return {}
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def save_user_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f: json.dump(settings, f)

def load_history():
    if os.path.exists(HISTORY_FILE): return pd.read_csv(HISTORY_FILE)
    return pd.DataFrame(columns=["Date", "Spot", "Hand", "Result", "CorrectAction"])

def save_to_history(record):
    df_new = pd.DataFrame([record])
    if not os.path.exists(HISTORY_FILE): df_new.to_csv(HISTORY_FILE, index=False)
    else: df_new.to_csv(HISTORY_FILE, mode='a', header=False, index=False)

def update_srs_smart(spot_id, hand, rating):
    data = load_srs_data()
    key = f"{spot_id}_{hand}"
    w = data.get(key, 100)
    if rating == 'hard': w *= 2.5
    elif rating == 'normal': w = w / 1.5 if w > 100 else w * 1.2
    elif rating == 'easy': w /= 4.0
    data[key] = int(max(1, min(w, 2000)))
    save_srs_data(data)

# ЛОГИКА ВЕСОВ
def get_weight(hand, range_str):
    # ЗАЩИТА ОТ ОШИБКИ: Если range_str не строка (например None или словарь), возвращаем 0
    if not range_str or not isinstance(range_str, str): return 0.0
    
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        if ':' in item:
            h_part, w_part = item.split(':')
            weight = float(w_part)
            if weight <= 1.0: weight *= 100
        else:
            h_part = item
            weight = 100.0
            
        if h_part == hand: return weight
        if len(h_part) == 2 and h_part[0] != h_part[1] and hand.startswith(h_part): return weight
    return 0.0

def parse_range_to_list(range_str):
    if not range_str or not isinstance(range_str, str): return []
    hand_list = []
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        if not item: continue
        h = item.split(':')[0]
        if h in ALL_HANDS: hand_list.append(h)
        elif len(h) == 2:
            if h[0] == h[1]: hand_list.append(h)
            else: hand_list.extend([h+'s', h+'o'])
    return list(set(hand_list))

def format_hand_colored(hand_str):
    if not any(s in hand_str for s in ['♠','♥','♦','♣']): return hand_str
    h = hand_str.replace('♠', '<span style="color:#e0e0e0">♠</span>')
    h = h.replace('♥', '<span style="color:#ff6b6b">♥</span>')
    h = h.replace('♦', '<span style="color:#4dabf7">♦</span>')
    h = h.replace('♣', '<span style="color:#69db7c">♣</span>')
    return h

def get_chip_style(seat_index):
    # Координаты для фишек (универсальные)
    pos = {0: "bottom:25%;left:47%;", 1: "bottom:25%;left:22%;", 2: "top:25%;left:22%;", 3: "top:10%;left:47%;", 4: "top:25%;right:22%;", 5: "bottom:25%;right:22%;"}
    return pos.get(seat_index, "")

# ОТРИСОВКА МАТРИЦЫ (С УЧЕТОМ ЦВЕТОВ)
def render_range_matrix(spot_data, target_hand=None):
    # Если вдруг передали строку по старинке - превращаем её в словарь
    if isinstance(spot_data, str):
        spot_data = {"full": spot_data}
    if not isinstance(spot_data, dict):
        spot_data = {}

    r_call = spot_data.get("call", "")
    r_4bet = spot_data.get("4bet", "")
    r_full = spot_data.get("full", "") # Fallback для Open Raise
    
    grid_html = '<div style="display:grid;grid-template-columns:repeat(13,1fr);gap:1px;background:#111;padding:1px;border:1px solid #444;">'
    
    for r1 in RANKS:
        for r2 in RANKS:
            if RANKS.index(r1) == RANKS.index(r2): h = r1 + r2
            elif RANKS.index(r1) < RANKS.index(r2): h = r1 + r2 + 's'
            else: h = r2 + r1 + 'o'
            
            w_c = get_weight(h, r_call)
            w_4 = get_weight(h, r_4bet)
            w_f = get_weight(h, r_full)
            
            style = "aspect-ratio:1;display:flex;justify-content:center;align-items:center;font-size:7px;cursor:default;color:#fff;"
            bg = "#2c3034" # Fold (Серый)
            
            # Приоритет цветов: 3-Bet/Call Mix -> Pure 4Bet -> Pure Call -> Open Raise
            if w_4 > 0 or w_c > 0:
                if w_4 > 0 and w_c > 0:
                    bg = "linear-gradient(135deg, #d63384 50%, #28a745 50%)" # Mix 4B/Call
                elif w_4 > 0 and w_4 < 100:
                    bg = "linear-gradient(135deg, #d63384 50%, #2c3034 50%)" # Mix 4B/Fold
                elif w_c > 0 and w_c < 100:
                    bg = "linear-gradient(135deg, #28a745 50%, #2c3034 50%)" # Mix Call/Fold
                elif w_4 >= 100:
                    bg = "#d63384" # Pure 4Bet
                elif w_c >= 100:
                    bg = "#28a745" # Pure Call
            elif w_f > 0:
                if w_f < 100: bg = "linear-gradient(135deg, #28a745 50%, #2c3034 50%)"
                else: bg = "#28a745"
            else:
                style += "color:#495057;"
            
            style += f"background:{bg};"
            if target_hand and h == target_hand:
                style += "border:1.5px solid #ffc107;z-index:10;box-shadow: 0 0 4px #ffc107;"
            
            grid_html += f'<div style="{style}">{h}</div>'
            
    return grid_html + '</div>'
