import streamlit as st
import random
from datetime import datetime
import utils # Подключаем наши мозги

def show():
    # --- CSS SPECIFIC FOR IPHONE ---
    st.markdown("""
    <style>
        /* Убираем лишние отступы для мобилы */
        .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
        
        /* СТОЛ (Компактный) */
        .mobile-game-area { 
            position: relative; width: 100%; height: 280px; margin: 0 auto 10px auto; 
            background: radial-gradient(ellipse at center, #1b5e20 0%, #0a2e0b 100%); 
            border: 8px solid #3e2723; border-radius: 140px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.8);
        }
        
        /* ИНФО В ЦЕНТРЕ СТОЛА */
        .mob-info { position: absolute; top: 25%; left: 50%; transform: translateX(-50%); text-align: center; width: 100%; }
        .mob-info-src { font-size: 10px; color: #888; text-transform: uppercase; }
        .mob-info-spot { font-size: 28px; font-weight: 900; color: rgba(255,255,255,0.1); }

        /* HERO CARD (КРУПНО) */
        .hero-mob { position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%); display: flex; gap: 4px; z-index: 10; }
        .card-mob { width: 55px; height: 80px; background: white; border-radius: 6px; position: relative; color: black; box-shadow: 0 2px 10px rgba(0,0,0,0.5); border: 2px solid #ffc107; }
        .tl-mob { position: absolute; top: 2px; left: 4px; font-weight: bold; font-size: 18px; line-height: 1; }
        .c-mob { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); font-size: 32px; }
        .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #111; }

        /* КНОПКИ ДЕЙСТВИЙ (ОГРОМНЫЕ И ВНИЗУ) */
        .stButton > button { width: 100%; height: 80px !important; font-size: 24px !important; font-weight: 900; border-radius: 16px; border: none; text-transform: uppercase; margin-top: 10px; }
        
        /* Фикс колонок на мобиле, чтобы кнопки были рядом */
        div[data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; min-width: 50% !important; }
        
        /* Цвета кнопок */
        div[data-testid="column"]:nth-of-type(1) div.stButton > button { background: #c62828 !important; color: white !important; box-shadow: 0 6px 0 #8e0000; }
        div[data-testid="column"]:nth-of-type(2) div.stButton > button { background: #2e7d32 !important; color: white !important; box-shadow: 0 6px 0 #1b5e20; }
        
        /* Нажатие */
        div.stButton > button:active { transform: translateY(4px); box-shadow: 0 2px 0 #000; }
    </style>
    """, unsafe_allow_html=True)

    # --- ЛОГИКА (Копия из desktop, но упрощенная) ---
    ranges_db = utils.load_ranges()
    if not ranges_db: st.error("Ranges not found"); return

    # НАСТРОЙКИ (В Expandere)
    with st.expander("⚙️ Setup Training", expanded=False):
        saved = utils.load_user_settings()
        
        # 1. Source
        all_src = list(ranges_db.keys())
        def_src = saved.get("sources", [all_src[0]])
        sel_src = st.multiselect("Source", all_src, default=[s for s in def_src if s in all_src])
        
        # 2. Scenario
        avail_sc = set()
        for s in sel_src: avail_sc.update(ranges_db[s].keys())
        sel_sc = st.multiselect("Scenario", list(avail_sc), default=list(avail_sc)[:1])
        
        # 3. Filter
        mode = st.selectbox("Positions", ["All", "Early", "Late", "Manual"])
        
        # Pool logic
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
        
        if not pool: st.error("No spots"); return
        
        if mode == "Manual":
            sel_manual = st.selectbox("Pick Spot", pool)
            pool = [sel_manual]
            
        if st.button("Save & Apply"):
            utils.save_user_settings({"sources": sel_src, "scenarios": sel_sc, "mode": mode})
            st.rerun()

    # --- STATE ---
    if 'hand' not in st.session_state: st.session_state.hand = None
    if 'suits' not in st.session_state: st.session_state.suits = None
    if 'msg' not in st.session_state: st.session_state.msg = None
    if 'srs_mode' not in st.session_state: st.session_state.srs_mode = False
    
    # --- GENERATION ---
    if st.session_state.hand is None:
        chosen = random.choice(pool)
        st.session_state.current_spot_key = chosen
        src, sc, sp = chosen.split('|')
        
        data = ranges_db[src][sc][sp]
        f_r = data.get("full", "") if isinstance(data, dict) else str(data)
        t_r = data.get("training", f_r) if isinstance(data, dict) else str(data)
        
        poss = utils.parse_range_to_list(t_r)
        if not poss: poss = utils.ALL_HANDS
        
        srs = utils.load_srs_data()
        w = [srs.get(f"{src}_{sc}_{sp}_{h}".replace(" ","_"), 100) for h in poss]
        st.session_state.hand = random.choices(poss, weights=w, k=1)[0]
        
        ps = ['♠','♥','♦','♣']
        s1 = random.choice(ps)
        s2 = s1 if 's' in st.session_state.hand else random.choice([x for x in ps if x!=s1])
        st.session_state.suits = [s1, s2]
        st.session_state.srs_mode = False

    # --- RENDER MOBILE TABLE ---
    src, sc, sp = st.session_state.current_spot_key.split('|')
    data = ranges_db[src][sc][sp]
    full_r = data.get("full", "") if isinstance(data, dict) else str(data)
    ans_w = utils.get_weight(st.session_state.hand, full_r)
    
    h_val = st.session_state.hand
    s1, s2 = st.session_state.suits
    c1 = "suit-red" if s1 in '♥' else "suit-blue" if s1 in '♦' else "suit-black"
    c2 = "suit-red" if s2 in '♥' else "suit-blue" if s2 in '♦' else "suit-black"

    html = f"""
    <div class="mobile-game-area">
        <div class="mob-info">
            <div class="mob-info-src">{src} • {sc}</div>
            <div class="mob-info-spot">{sp}</div>
        </div>
        <div class="hero-mob">
            <div class="card-mob">
                <div class="tl-mob {c1}">{h_val[0]}<br>{s1}</div>
                <div class="c-mob {c1}">{s1}</div>
            </div>
            <div class="card-mob">
                <div class="tl-mob {c2}">{h_val[1]}<br>{s2}</div>
                <div class="c-mob {c2}">{s2}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # --- BIG BUTTONS ---
    if not st.session_state.srs_mode:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("FOLD"):
                corr = (ans_w == 0.0)
                st.session_state.msg = "✅ Correct" if corr else f"❌ Err (R {int(ans_w*100)}%)"
                utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": h_val, "Result": 1 if corr else 0, "CorrectAction": "Fold" if ans_w==0 else "Raise"})
                st.session_state.srs_mode = True; st.rerun()
        with c2:
            if st.button("RAISE"):
                corr = (ans_w > 0.0)
                st.session_state.msg = f"✅ Correct" if corr else "❌ Err (Fold)"
                utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": h_val, "Result": 1 if corr else 0, "CorrectAction": "Raise" if ans_w>0 else "Fold"})
                st.session_state.srs_mode = True; st.rerun()
    else:
        # SRS Buttons (Smaller)
        st.info(st.session_state.msg)
        s1, s2, s3 = st.columns(3)
        k = f"{src}_{sc}_{sp}".replace(" ","_")
        
        # Override styles for SRS buttons to be smaller/different color
        st.markdown("""<style>div[data-testid="column"] div.stButton > button { height: 60px !important; background: #444 !important; font-size: 14px !important; box-shadow: none !important; }</style>""", unsafe_allow_html=True)
        
        if s1.button("HARD"): utils.update_srs_smart(k, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
        if s2.button("NORMAL"): utils.update_srs_smart(k, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
        if s3.button("EASY"): utils.update_srs_smart(k, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()
