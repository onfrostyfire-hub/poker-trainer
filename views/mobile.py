import streamlit as st
import random
from datetime import datetime
import utils

def show():
    st.markdown("""
    <style>
        /* ОТСТУПЫ СВЕРХУ (ЧТОБЫ НЕ ЛЕЗЛО ПОД ЧЕЛКУ) */
        .block-container { 
            padding-top: 3.5rem !important; 
            padding-bottom: 2rem !important; 
            padding-left: 0.5rem !important; 
            padding-right: 0.5rem !important; 
        }
        
        /* СТОЛ */
        .mobile-game-area { 
            position: relative; width: 100%; height: 280px; margin: 0 auto 10px auto; 
            background: radial-gradient(ellipse at center, #1b5e20 0%, #0a2e0b 100%); 
            border: 8px solid #3e2723; border-radius: 140px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.8);
        }
        
        /* ИНФО */
        .mob-info { position: absolute; top: 25%; left: 50%; transform: translateX(-50%); text-align: center; width: 100%; z-index: 2; }
        .mob-info-src { font-size: 10px; color: #888; text-transform: uppercase; }
        .mob-info-spot { font-size: 24px; font-weight: 900; color: rgba(255,255,255,0.15); }

        /* МЕСТА (ОППОНЕНТЫ) */
        .seat { position: absolute; width: 45px; height: 45px; background: #222; border: 1px solid #444; border-radius: 6px; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 5; }
        .seat-label { font-size: 9px; color: #fff; margin-top: 2px; font-weight: bold; }
        .seat-folded { opacity: 0.4; }
        .seat-active { border-color: #ffc107; }
        
        .opp-cards-mob { position: absolute; top: -8px; width: 20px; height: 28px; background: #fff; border-radius: 2px; background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); z-index: 4; }
        
        /* ФИШКИ */
        .dealer-mob { position: absolute; width: 16px; height: 16px; background: #ffc107; border-radius: 50%; color: #000; font-weight: bold; font-size: 9px; display: flex; justify-content: center; align-items: center; z-index: 6; }
        .chip-mob { width: 14px; height: 14px; background: #111; border: 2px dashed #d32f2f; border-radius: 50%; }
        
        /* КООРДИНАТЫ (ПОД МАЛЕНЬКИЙ СТОЛ) */
        .m-pos-1 { bottom: 18%; left: 6%; } .m-pos-2 { top: 18%; left: 6%; } .m-pos-3 { top: -15px; left: 50%; transform: translateX(-50%); } .m-pos-4 { top: 18%; right: 6%; } .m-pos-5 { bottom: 18%; right: 6%; }

        /* HERO CARD */
        .hero-mob { position: absolute; bottom: -25px; left: 50%; transform: translateX(-50%); display: flex; gap: 4px; z-index: 10; background: #222; padding: 4px 8px; border-radius: 8px; border: 1px solid #ffc107; }
        .card-mob { width: 45px; height: 65px; background: white; border-radius: 4px; position: relative; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }
        .tl-mob { position: absolute; top: 1px; left: 3px; font-weight: bold; font-size: 16px; line-height: 1; }
        .c-mob { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 26px; }
        .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #111; }

        /* === КНОПКИ ДЕЙСТВИЙ (FORCE ROW) === */
        [data-testid="stHorizontalBlock"] { flex-direction: row !important; flex-wrap: nowrap !important; gap: 10px !important; }
        [data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; min-width: 50% !important; }
        
        .stButton > button { width: 100%; height: 75px !important; font-size: 20px !important; font-weight: 800; border-radius: 12px; border: none; text-transform: uppercase; margin-top: 5px; }
        
        div[data-testid="column"]:nth-of-type(1) div.stButton > button { background: #c62828 !important; color: white !important; box-shadow: 0 4px 0 #8e0000; }
        div[data-testid="column"]:nth-of-type(2) div.stButton > button { background: #2e7d32 !important; color: white !important; box-shadow: 0 4px 0 #1b5e20; }
        
        /* МАТРИЦА */
        .range-grid { display: grid; grid-template-columns: repeat(13, 1fr); gap: 1px; font-family: monospace; border: 1px solid #444; padding: 1px; background: #111; margin-top: 10px; }
        .grid-cell { aspect-ratio: 1; display: flex; justify-content: center; align-items: center; font-size: 7px; color: #aaa; cursor: default; }
        .current-hand-highlight { border: 2px solid #ffc107 !important; z-index: 10; color: #fff !important; font-weight: bold; background-color: rgba(255, 193, 7, 0.2) !important; }
    </style>
    """, unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: st.error("No ranges"); return

    # SETTINGS EXPANDER
    with st.expander("⚙️ Setup", expanded=False):
        saved = utils.load_user_settings()
        all_src = list(ranges_db.keys())
        def_src = saved.get("sources", [all_src[0]])
        sel_src = st.multiselect("Source", all_src, default=[s for s in def_src if s in all_src])
        
        avail_sc = set()
        for s in sel_src: avail_sc.update(ranges_db[s].keys())
        sel_sc = st.multiselect("Scenario", list(avail_sc), default=list(avail_sc)[:1])
        
        mode = st.selectbox("Positions", ["All", "Early", "Late", "Manual"])
        
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
            sel_manual = st.selectbox("Spot", pool)
            pool = [sel_manual]
            
        if st.button("Apply"):
            utils.save_user_settings({"sources": sel_src, "scenarios": sel_sc, "mode": mode})
            st.rerun()

    if 'hand' not in st.session_state: st.session_state.hand = None
    if 'suits' not in st.session_state: st.session_state.suits = None
    if 'msg' not in st.session_state: st.session_state.msg = None
    if 'srs_mode' not in st.session_state: st.session_state.srs_mode = False
    if 'last_error' not in st.session_state: st.session_state.last_error = False
    
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
        st.session_state.last_error = False

    src, sc, sp = st.session_state.current_spot_key.split('|')
    data = ranges_db[src][sc][sp]
    full_r = data.get("full", "") if isinstance(data, dict) else str(data)
    ans_w = utils.get_weight(st.session_state.hand, full_r)
    h_val = st.session_state.hand
    s1, s2 = st.session_state.suits
    c1 = "suit-red" if s1 in '♥' else "suit-blue" if s1 in '♦' else "suit-black"
    c2 = "suit-red" if s2 in '♥' else "suit-blue" if s2 in '♦' else "suit-black"

    # --- ГЕНЕРАЦИЯ СТОЛА И ОППОНЕНТОВ ---
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
    
    # Сгенерировать HTML для мест оппонентов
    opp_html = ""
    for i in range(1, 6):
        pos = rot[i]
        std_i = order.index(pos)
        hero_i = order.index(rot[0])
        is_fold = std_i < hero_i
        if rot[0] == "SB" and pos == "BB": is_fold = False
        
        cls = "seat-folded" if is_fold else "seat-active"
        cards = '<div class="opp-cards-mob"></div>' if not is_fold else ""
        
        # Фишки
        chips = ""
        # Координаты для фишек (упрощенно)
        if pos == "BTN": chips = '<div class="dealer-mob" style="top:-10px; right:-10px;">D</div>'
        
        opp_html += f'<div class="seat m-pos-{i} {cls}">{cards}{chips}<span class="seat-label">{pos}</span></div>'

    html = f"""
    <div class="mobile-game-area">
        <div class="mob-info">
            <div class="mob-info-src">{src}</div>
            <div class="mob-info-spot">{sp}</div>
        </div>
        {opp_html}
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

    # --- КНОПКИ ---
    if not st.session_state.srs_mode:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("FOLD"):
                corr = (ans_w == 0.0)
                st.session_state.last_error = not corr
                st.session_state.msg = "✅ Correct" if corr else f"❌ Err (R {int(ans_w*100)}%)"
                hf = f"{h_val[0]}{s1}{h_val[1]}{s2}"
                utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": hf, "Result": 1 if corr else 0, "CorrectAction": "Fold" if ans_w==0 else "Raise"})
                st.session_state.srs_mode = True; st.rerun()
        with c2:
            if st.button("RAISE"):
                corr = (ans_w > 0.0)
                st.session_state.last_error = not corr
                st.session_state.msg = f"✅ Correct" if corr else "❌ Err (Fold)"
                hf = f"{h_val[0]}{s1}{h_val[1]}{s2}"
                utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": hf, "Result": 1 if corr else 0, "CorrectAction": "Raise" if ans_w>0 else "Fold"})
                st.session_state.srs_mode = True; st.rerun()
    else:
        st.info(st.session_state.msg)
        
        # Если ошибка - показать матрицу
        if st.session_state.last_error:
            with st.expander("Show Range", expanded=True):
                st.markdown(utils.render_range_matrix(full_r, target_hand=st.session_state.hand), unsafe_allow_html=True)
        
        s1, s2, s3 = st.columns(3)
        k = f"{src}_{sc}_{sp}".replace(" ","_")
        st.markdown("""<style>div[data-testid="column"] div.stButton > button { height: 60px !important; background: #444 !important; font-size: 14px !important; box-shadow: none !important; }</style>""", unsafe_allow_html=True)
        
        if s1.button("HARD"): utils.update_srs_smart(k, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
        if s2.button("NORMAL"): utils.update_srs_smart(k, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
        if s3.button("EASY"): utils.update_srs_smart(k, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()
