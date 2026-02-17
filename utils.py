import streamlit as st
import json
import pandas as pd
import os
import random

# ФАЙЛЫ
HISTORY_FILE = 'history_log.csv'
SRS_FILE = 'srs_data.json'
RANGES_FILE = 'ranges.json'
SETTINGS_FILE = 'user_settings.json'
RANKS = 'AKQJT98765432'
ALL_HANDS = [r1+r2+s for r1 in RANKS for r2 in RANKS for s in ('s','o') if (r1<r2 and s=='s') or (r1>r2 and s=='o')] + [r+r for r in RANKS]

# --- ЗАГРУЗКА ДАННЫХ ---
@st.cache_data(ttl=0)
def load_ranges():
    try:
        with open(RANGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_srs_data():
    if os.path.exists(SRS_FILE):
        try:
            with open(SRS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_srs_data(data):
    with open(SRS_FILE, 'w') as f:
        json.dump(data, f)

def load_user_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
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
    if rating == 'hard': w *= 2.5
    elif rating == 'normal': w = w / 1.5 if w > 100 else w * 1.2
    elif rating == 'easy': w /= 4.0
    data[key] = int(max(1, min(w, 2000)))
    save_srs_data(data)

def get_weight(hand, range_str):
    if not range_str: return 0.0
    items = [x.strip() for x in range_str.replace('\n', ' ').split(',')]
    for item in items:
        w = 1.0; h = item
        if ':' in item: h, w_str = item.split(':'); w = float(w_str)
        if h == hand: return w
        if len(h) == 2 and h[0] != h[1] and hand.startswith(h): return w
    return 0.0

def parse_range_to_list(range_str):
    if not range_str: return []
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
    if "♠" not in hand_str and "♥" not in hand_str: return hand_str
    h = hand_str
    h = h.replace('♠', '<span style="color:#e0e0e0">♠</span>')
    h = h.replace('♥', '<span style="color:#ff6b6b">♥</span>')
    h = h.replace('♦', '<span style="color:#4dabf7">♦</span>')
    h = h.replace('♣', '<span style="color:#69db7c">♣</span>')
    return h
