import streamlit as st
import json
import random
import pandas as pd
import os
from datetime import datetime, timedelta

# --- ВЕРСИЯ 28.0 (FREEBETRANGE STYLE UI) ---
st.set_page_config(page_title="GTO Pro", page_icon="♠️", layout="wide")

# --- CSS СТИЛИ (THEME: FREEBETRANGE) ---
st.markdown("""
<style>
    /* ОБЩИЙ ФОН */
    .stApp { background-color: #212529; color: #e9ecef; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    
    /* УБИРАЕМ ОТСТУПЫ */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    /* === СТОЛ (RACETRACK SHAPE) === */
    .game-area { 
        position: relative; 
        width: 100%; max-width: 600px; height: 340px; 
        margin: 0 auto 20px auto; 
        /* Зеленое сукно + Темно-красный борт */
        background: radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%); 
        border: 15px solid #4a1c1c; /* Борт */
        border-radius: 170px; /* Овальная форма */
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
    }
    .table-logo { 
        position: absolute; top: 45%; left: 50%; transform: translate(-50%, -50%); 
        color: rgba(255,255,255,0.1); font-weight: 700; font-size: 32px; pointer-events: none; 
    }
    
    /* МЕСТА ИГРОКОВ (Квадратные скругленные, как на скрине) */
    .seat { 
        position: absolute; width: 60px; height: 60px; 
        background: #343a40; border: 2px solid #495057; border-radius: 8px; 
        display: flex; flex-direction: column; justify-content: center; align-items: center; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.4); z-index: 5; 
    }
    .seat-active { border-color: #ffc107; background: #343a40; }
    .seat-folded { opacity: 0.4; border-color: #212529; }
    .seat-label { color: #fff; font-weight: bold; font-size: 11px; margin-top: 15px; }
    
    /* АВАТАРКИ/РУБАШКИ КАРТ ОППОНЕНТОВ */
    .opp-cards { 
        position: absolute; top: -10px; 
        width: 30px; height: 42px; 
        background: #fff; border-radius: 4px; border: 1px solid #ccc; 
        background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); 
        box-shadow: 1px 1px 3px rgba(0,0,0,0.5); z-index: 4; 
    }
    
    /* ФИШКИ */
    .dealer-button { 
        position: absolute; width: 20px; height: 20px; 
        background: #ffc107; border: 1px solid #e0a800; border-radius: 50%; 
        color: #000; font-weight: bold; font-size: 10px; 
        display: flex; justify-content: center; align-items: center; 
        box-shadow: 1px 1px 3px rgba(0,0,0,0.5); z-index: 15; 
    }
    .poker-chip { 
        width: 18px; height: 18px; 
        background: #222; border: 3px dashed #d32f2f; border-radius: 50%; 
        box-shadow: 1px 1px 2px rgba(0,0,0,0.7); 
    }
    .blind-stack { position: absolute; z-index: 15; display: flex; flex-direction: column; align-items: center; }
    .chip-stacked { margin-top: -14px; }

    /* ПОЗИЦИОНИРОВАНИЕ (Адаптировано под овал) */
    .pos-1 { bottom: 20%; left: 8%; } 
    .pos-2 { top: 20%; left: 8%; } 
    .pos-3 { top: -25px; left: 50%; transform: translateX(-50%); } 
    .pos-4 { top: 20%; right: 8%; } 
    .pos-5 { bottom: 20%; right: 8%; }
    
    /* HERO (Главный игрок) */
    .hero-panel { 
        position: absolute; bottom: -30px; left: 50%; transform: translateX(-50%); 
        background: #212529; border: 2px solid #ffc107; border-radius: 12px; 
        padding: 5px 15px; display: flex; gap: 8px; 
        box-shadow: 0 0 20px rgba(255, 193, 7, 0.2); z-index: 10; align-items: center; 
    }
    .card { 
        width: 45px; height: 65px; 
        background: white; border-radius: 4px; position: relative; 
        color: black; font-family: 'Arial', sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }
    .tl { position: absolute; top: 1px; left: 3px; font-weight: bold; font-size: 14px; line-height: 1.1; }
    .cent { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 24px; }
    .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #212529; }

    /* КНОПКИ ДЕЙСТВИЙ (Плоские, современные) */
    div.stButton > button { 
        width: 100%; height: 50px !important; 
        font-size: 16px !important; font-weight: 600; 
        border-radius: 6px; border: none; text-transform: uppercase; 
        transition: all 0.2s;
    }
    /* Fold - Серый/Красный при наведении */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button { 
        background-color: #343a40 !important; color: #adb5bd !important; border: 1px solid #495057;
    }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover { 
        background-color: #dc3545 !important; color: white !important; border-color: #dc3545;
    }
    
    /* Raise - Зеленый */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button { 
        background-color: #28a745 !important; color: white !important; 
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover { 
        background-color: #218838 !important; 
    }

    /* МАТРИЦА СПРАВА */
    .range-grid { display: grid; grid-template-columns: repeat(13, 1fr); gap: 1px; margin-top: 0px; font-family: monospace; border: 1px solid #444; padding: 2px; background: #111; }
    .grid-cell { aspect-ratio: 1; display: flex; justify-content: center; align-items: center; font-size: 9px; color: #aaa; cursor: default; }
    .current-hand-highlight { border: 2px solid #ffc107 !important; z-index: 10; color: #fff !important; font-weight: bold; background-color: rgba(255, 193, 7, 0.2) !important; }
    
    /* СТАТИСТИКА СЛЕВА */
    .stats-box { background: #343a40; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 10px; }
    .stat-label { color: #adb5bd; font-size: 12px; text-transform: uppercase; }
    .stat-value { color: #fff; font-size: 20px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- ФАЙЛЫ ---
HISTORY_FILE = 'history_log.csv'
SRS_FILE = 'srs_data.json'
RANGES_FILE = 'ranges.json'
SETTINGS_FILE = 'user_settings.json'
ranks = 'AKQJT98765432'
all_hands = [r1+r2+s for r1 in ranks for r2 in ranks for s in ('s','o') if (r1<r2 and s=='s') or (r1>r2 and s=='o')] + [r+r for r in ranks]

# --- ФУНКЦИИ ---
@st.cache_data(ttl=0)
def load_ranges():
    try:
        with open(RANGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

ranges_db = load_ranges()

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
        if h in all_hands: hand_list.append(h)
        elif len(h) == 2:
            if h[0] == h[1]: hand_list.append(h)
            else: hand_list.extend([h+'s', h+'o'])
    return list(set(hand_list))

def get_chip_style(seat_index):
    # Адаптировано под овальный стол
    if seat_index == 0: return "bottom: 25%; left: 48%;"
    if seat_index == 1: return "bottom: 28%; left: 25%;"
    if seat_index == 2: return "top: 28%; left: 25%;"
    if seat_index == 3: return "top: 15%; left: 48%;"
    if seat_index == 4: return "top: 28%; right: 25%;"
    if seat_index == 5: return "bottom: 28%; right: 25%;"
    return ""

def render_range_matrix(range_str, target_hand=None):
    ranks_seq = "AKQJT98765432"
    html = '<div class="range-grid">'
    for r1 in ranks_seq:
        for r2 in ranks_seq:
            if ranks_seq.index(r1) == ranks_seq.index(r2): hand = r1 + r2
            elif ranks_seq.index(r1) < ranks_seq.index(r2): hand = r1 + r2 + 's'
            else: hand = r2 + r1 + 'o'
            
            w = get_weight(hand, range_str)
            css_class = "grid-cell"
            if target_hand and hand == target_hand: css_class += " current-hand-highlight"
            
            # Цвета FreeBetRange style
            if w > 0:
                # Градиент от прозрачного к зеленому/фиолетовому
                opacity = 0.4 + (0.6 * w)
                bg = f"rgba(102, 16, 242, {opacity})" if w < 1 else f"rgba(40, 167, 69, {opacity})" # Микс или Пьюр
                style = f"background: {bg}; color: #fff;"
            else:
                style = "background: #2c3034; color: #495057;"
            html += f'<div class="{css_class}" style="{style}">{hand}</div>'
    return html + '</div>'

# --- САЙДБАР (Настройки) ---
with st.sidebar:
    st.header("Settings")
    if not ranges_db: st.error("No ranges found."); st.stop()
    
    saved = load_user_settings()
    
    # 1. Source
    st.markdown("**1. Source**")
    all_src = list(ranges_db.keys())
    def_src = saved.get("sources", [all_src[0]])
    sel_src = []
    cols = st.columns(len(all_src))
    for i, s in enumerate(all_src):
        if cols[i].checkbox(s, value=(s in def_src)): sel_src.append(s)
    if not sel_src: st.warning("Pick source"); st.stop()

    # 2. Scenario
    st.markdown("**2. Scenario**")
    avail_sc = set()
    for s in sel_src: avail_sc.update(ranges_db[s].keys())
    sel_sc = []
    sc_cols = st.columns(min(3, len(avail_sc))) if avail_sc else []
    for i, sc in enumerate(list(avail_sc)):
        if sc_cols[i % 3].checkbox(sc, value=True): sel_sc.append(sc)
    if not sel_sc: st.warning("Pick scenario"); st.stop()

    # 3. Mode
    st.markdown("**3. Filter**")
    mode = st.radio("F", ["All", "Early", "Late", "Manual"], horizontal=True, label_visibility="collapsed")
    
    # Logic
    pool = []
    for src in sel_src:
        for sc in sel_sc:
            if sc in ranges_db[src]:
                for sp in ranges_db[src][sc]:
                    u = sp.upper()
                    m = False
                    if mode=="All": m=True
                    elif mode=="Early": m=any(x in u for x in ["EP","UTG","MP"])
                    elif mode=="Late": m=any(x in u for x in ["CO","BU","BTN","SB"])
                    if m or mode=="Manual": pool.append(f"{src}|{sc}|{sp}")
    
    if not pool: st.error("Empty pool"); st.stop()
    if mode=="Manual":
        sel_spot = st.selectbox("Spot", pool)
        pool = [sel_spot]
        
    save_user_settings({"sources": sel_src, "scenarios": sel_sc, "mode": mode})

# --- ГЛАВНЫЙ ЭКРАН (3 КОЛОНКИ) ---
# На десктопе 3 колонки, на мобильном сложатся
col_left, col_center, col_right = st.columns([1, 2, 1])

# --- STATE INIT ---
if 'hand' not in st.session_state: st.session_state.hand = None
if 'current_spot_key' not in st.session_state: st.session_state.current_spot_key = None
if 'suits' not in st.session_state: st.session_state.suits = None
if 'msg' not in st.session_state: st.session_state.msg = None
if 'srs_mode' not in st.session_state: st.session_state.srs_mode = False
if 'last_error' not in st.session_state: st.session_state.last_error = False

# --- HAND GENERATION ---
if st.session_state.hand is None:
    chosen = random.choice(pool)
    st.session_state.current_spot_key = chosen
    src, sc, sp = chosen.split('|')
    data = ranges_db[src][sc][sp]
    f_r = data.get("full", "") if isinstance(data, dict) else str(data)
    t_r = data.get("training", f_r) if isinstance(data, dict) else str(data)
    poss = parse_range_to_list(t_r)
    if not poss: poss = all_hands
    srs = load_srs_data()
    w = [srs.get(f"{src}_{sc}_{sp}_{h}".replace(" ","_"), 100) for h in poss]
    st.session_state.hand = random.choices(poss, weights=w, k=1)[0]
    ps = ['♠','♥','♦','♣']
    s1 = random.choice(ps)
    s2 = s1 if 's' in st.session_state.hand else random.choice([x for x in ps if x!=s1])
    st.session_state.suits = [s1, s2]
    st.session_state.srs_mode = False
    st.session_state.last_error = False

# --- ДАННЫЕ ТЕКУЩЕЙ РАЗДАЧИ ---
src, sc, sp = st.session_state.current_spot_key.split('|')
data = ranges_db[src][sc][sp]
full_r = data.get("full", "") if isinstance(data, dict) else str(data)
ans_w = get_weight(st.session_state.hand, full_r)

# --- ЛЕВАЯ КОЛОНКА (ИСТОРИЯ/СТАТЫ) ---
with col_left:
    st.markdown("### Session")
    df = load_history()
    
    # Статы за сегодня
    now = datetime.now()
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        df_today = df[df["Date"].dt.date == now.date()]
        total = len(df_today)
        correct = df_today["Result"].sum()
        acc = int(correct/total*100) if total > 0 else 0
        
        st.markdown(f"""
        <div class="stats-box">
            <div class="stat-label">Accuracy</div>
            <div class="stat-value" style="color: {'#28a745' if acc > 90 else '#ffc107'};">{acc}%</div>
            <div class="stat-label" style="margin-top:5px;">Hands: {total}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Последние ошибки
        errs = df_today[df_today["Result"]==0].sort_values("Date", ascending=False).head(5)
        if not errs.empty:
            st.markdown("**Recent Errors:**")
            for i, r in errs.iterrows():
                st.caption(f"{r['Hand']} in {r['Spot']}")

# --- ЦЕНТРАЛЬНАЯ КОЛОНКА (СТОЛ) ---
with col_center:
    st.markdown(f"<div style='text-align:center; color:#adb5bd; font-size:14px; margin-bottom: 5px;'>{src} > {sc} > <b>{sp}</b></div>", unsafe_allow_html=True)
    
    # HTML СТОЛА
    order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
    hero_idx = 0
    u = sp.upper()
    if any(p in u for p in ["EP", "UTG"]): hero_idx = 0
    elif "MP" in u: hero_idx = 1
    elif "CO" in u: hero_idx = 2
    elif any(p in u for p in ["BTN", "BU"]): hero_idx = 3
    elif "SB" in u: hero_idx = 4
    elif "BB" in u: hero_idx = 5
    
    rot = order[hero_idx:] + order[:hero_idx]
    h_val = st.session_state.hand
    s1, s2 = st.session_state.suits
    c1 = "suit-red" if s1 in '♥' else "suit-blue" if s1 in '♦' else "suit-black"
    c2 = "suit-red" if s2 in '♥' else "suit-blue" if s2 in '♦' else "suit-black"

    html = '<div class="game-area">' # Лого можно убрать для минимализма
    chips_html = ""

    for i in range(1, 6):
        pos = rot[i]
        std_i = order.index(pos)
        hero_i = order.index(rot[0])
        is_fold = std_i < hero_i
        if rot[0] == "SB" and pos == "BB": is_fold = False
        cls = "seat-folded" if is_fold else "seat-active"
        cards = '<div class="opp-cards"><div class="opp-c1"></div><div class="opp-c2"></div></div>' if not is_fold else ""
        html += f'<div class="seat pos-{i} {cls}">{cards}<span class="seat-label">{pos}</span></div>'
        sty = get_chip_style(i)
        if pos == "BTN": chips_html += f'<div class="dealer-button" style="{sty}">D</div>'
        elif pos == "SB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div></div>'
        elif pos == "BB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div><div class="poker-chip chip-stacked"></div></div>'

    hero = rot[0]
    sty = get_chip_style(0)
    if hero == "BTN": chips_html += f'<div class="dealer-button" style="{sty}">D</div>'
    elif hero == "SB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div></div>'
    elif hero == "BB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div><div class="poker-chip chip-stacked"></div></div>'

    html += f'<div class="hero-panel"><div style="display:flex;flex-direction:column;align-items:center;"><span style="color:#ffc107;font-weight:bold;font-size:12px;">HERO</span><span style="color:#adb5bd;font-size:10px;">{hero}</span></div><div class="card"><div class="tl {c1}">{h_val[0]}<br>{s1}</div><div class="cent {c1}">{s1}</div></div><div class="card"><div class="tl {c2}">{h_val[1]}<br>{s2}</div><div class="cent {c2}">{s2}</div></div></div>'
    html += chips_html + "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # КНОПКИ ДЕЙСТВИЙ (Горизонтальные)
    if not st.session_state.srs_mode:
        # Используем колонки 1:1
        b1, b2 = st.columns(2)
        with b1:
            if st.button("FOLD", use_container_width=True):
                corr = (ans_w == 0.0)
                st.session_state.last_error = not corr
                st.session_state.msg = "✅ Correct" if corr else f"❌ Error (Raise {int(ans_w*100)}%)"
                save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": f"{sp}", "Hand": h_val, "Result": 1 if corr else 0, "CorrectAction": "Fold" if ans_w==0 else "Raise"})
                st.session_state.srs_mode = True; st.rerun()
        with b2:
            if st.button("RAISE", use_container_width=True):
                corr = (ans_w > 0.0)
                st.session_state.last_error = not corr
                st.session_state.msg = f"✅ Correct" if corr else "❌ Error (Fold)"
                save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": f"{sp}", "Hand": h_val, "Result": 1 if corr else 0, "CorrectAction": "Raise" if ans_w>0 else "Fold"})
                st.session_state.srs_mode = True; st.rerun()
    else:
        # SRS Buttons
        st.info(st.session_state.msg)
        st.caption("How hard was it?")
        s1, s2, s3 = st.columns(3)
        key = f"{src}_{sc}_{sp}".replace(" ","_")
        if s1.button("HARD"): update_srs_smart(key, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
        if s2.button("NORMAL"): update_srs_smart(key, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
        if s3.button("EASY"): update_srs_smart(key, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()

# --- ПРАВАЯ КОЛОНКА (МАТРИЦА) ---
with col_right:
    # Показываем матрицу если была ошибка ИЛИ если пользователь сам открыл экспандер
    # Чтобы эмулировать FreeBetRange, можно показывать всегда, но подсвечивать текущую руку
    
    show_matrix = st.checkbox("Show Matrix", value=st.session_state.last_error)
    
    if show_matrix:
        st.markdown(f"**Range: {sp}**")
        st.markdown(render_range_matrix(full_r, target_hand=st.session_state.hand), unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align:center; color:#555; margin-top:100px;'>Matrix hidden<br><small>(Auto-shows on error)</small></div>", unsafe_allow_html=True)
