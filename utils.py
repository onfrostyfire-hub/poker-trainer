import streamlit as st
import json
import pandas as pd
import os
import random

# Константы
HISTORY_FILE = 'history_log.csv'
SRS_FILE = 'srs_data.json'
RANGES_FILE = 'ranges.json'
SETTINGS_FILE = 'user_settings.json'
RANKS = 'AKQJT98765432'
ALL_HANDS = [r1+r2+s for r1 in RANKS for r2 in RANKS for s in ('s','o') if (r1<r2 and s=='s') or (r1>r2 and s=='o')] + [r+r for r in RANKS]

# --- ФУНКЦИИ ЗАГРУЗКИ ---
@st.cache_data(ttl=0)
def load_ranges():
    if not os.path.exists(RANGES_FILE):
        return {}
    with open(RANGES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_srs_data():
    if not os.path.exists(SRS_FILE):
        return {}
    with open(SRS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_srs_data(data):
    with open(SRS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def load_user_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_user_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f)

def load_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)
    return pd.DataFrame(columns=["Date", "Spot", "Hand", "Result", "CorrectAction"])

def save_to_history(record):
    df_new = pd.DataFrame([record])
    if not os.path.exists(HISTORY_FILE):
        df_new.to_csv(HISTORY_FILE, index=False)
    else:
        df_new.to_csv(HISTORY_FILE, mode='a', header=False, index=False)

# --- ЛОГИКА ---
def update_srs_smart(spot_id, hand, rating):
    data = load_srs_data()
    key = f"{spot_id}_{hand}"
    w = data.get(key, 100)
    if rating == 'hard':
        w *= 2.5
    elif rating == 'normal':
        w = w / 1.5 if w > 100 else w * 1.2
    elif rating == 'easy':
        w /= 4.0
    data[key] = int(max(1, min(w, 2000)))
    save_srs_data(data)

def get_weight(hand, range_str):
    if not range_str:
        return 0.0
    items = [x.strip() for x in range_str.replace('\n', ' ').split(',')]
    for item in items:
        w = 1.0
        h = item
        if ':' in item:
            h, w_str = item.split(':')
            w = float(w_str)
        if h == hand:
            return w
        if len(h) == 2 and h[0] != h[1] and hand.startswith(h):
            return w
    return 0.0

def parse_range_to_list(range_str):
    if not range_str:
        return []
    hand_list = []
    cleaned = range_str.replace('\n', ' ').replace('\r', '')
    items = [x.strip() for x in cleaned.split(',')]
    for item in items:
        if not item:
            continue
        h = item.split(':')[0]
        if h in ALL_HANDS:
            hand_list.append(h)
        elif len(h) == 2:
            if h[0] == h[1]:
                hand_list.append(h)
            else:
                hand_list.extend([h+'s', h+'o'])
    return list(set(hand_list))

def format_hand_colored(hand_str):
    if "♠" not in hand_str and "♥" not in hand_str:
        return hand_str
    h = hand_str
    h = h.replace('♠', '<span style="color:#e0e0e0">♠</span>')
    h = h.replace('♥', '<span style="color:#ff6b6b">♥</span>')
    h = h.replace('♦', '<span style="color:#4dabf7">♦</span>')
    h = h.replace('♣', '<span style="color:#69db7c">♣</span>')
    return h

def get_chip_style(seat_index):
    if seat_index == 0: return "bottom: 28%; left: 48%;"
    if seat_index == 1: return "bottom: 30%; left: 28%;"
    if seat_index == 2: return "top: 30%; left: 28%;"
    if seat_index == 3: return "top: 18%; left: 48%;"
    if seat_index == 4: return "top: 30%; right: 28%;"
    if seat_index == 5: return "bottom: 30%; right: 28%;"
    return ""

def render_range_matrix(range_str, target_hand=None):
    ranks_seq = "AKQJT98765432"
    grid_html = '<div style="display:grid;grid-template-columns:repeat(13,1fr);gap:1px;background:#111;padding:2px;border:1px solid #444;">'
    for r1 in ranks_seq:
        for r2 in ranks_seq:
            if ranks_seq.index(r1) == ranks_seq.index(r2):
                h = r1 + r2
            elif ranks_seq.index(r1) < ranks_seq.index(r2):
                h = r1 + r2 + 's'
            else:
                h = r2 + r1 + 'o'
            
            w = get_weight(h, range_str)
            style = "aspect-ratio:1;display:flex;justify-content:center;align-items:center;font-size:9px;cursor:default;"
            
            if target_hand and h == target_hand:
                style += "border:2px solid #ffc107;z-index:10;color:#fff;font-weight:bold;background:rgba(255,193,7,0.2);"
            elif w > 0:
                op = 0.4 + (0.6 * w)
                bg = f"rgba(102, 16, 242, {op})" if w < 1 else f"rgba(40, 167, 69, {op})"
                style += f"background:{bg};color:#fff;"
            else:
                style += "background:#2c3034;color:#495057;"
                
            grid_html += f'<div style="{style}">{h}</div>'
    grid_html += '</div>'
    return grid_html
