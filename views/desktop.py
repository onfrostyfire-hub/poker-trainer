import streamlit as st
import random
from datetime import datetime
import pandas as pd
import utils

def show():
    # --- CSS SPECIFIC FOR DESKTOP ---
    st.markdown("""
    <style>
        .stApp { background-color: #212529; color: #e9ecef; }
        .block-container { padding-top: 4rem; padding-bottom: 2rem; }

        /* СТОЛ */
        .game-area { 
            position: relative; width: 100%; max-width: 600px; height: 340px; 
            margin: 0 auto 20px auto; 
            background: radial-gradient(ellipse at center, #2e7d32 0%, #1b5e20 100%); 
            border: 15px solid #4a1c1c; border-radius: 170px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
        }
        
        .table-info { position: absolute; top: 18%; left: 50%; transform: translateX(-50%); text-align: center; pointer-events: none; z-index: 2; }
        .info-src { font-size: 10px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 1px; }
        .info-spot { font-size: 24px; font-weight: 800; color: rgba(255,255,255,0.15); margin-top: -5px; }

        /* МЕСТА */
        .seat { position: absolute; width: 60px; height: 60px; background: #343a40; border: 2px solid #495057; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 8px rgba(0,0,0,0.4); z-index: 5; }
        .seat-active { border-color: #ffc107; background: #343a40; }
        .seat-folded { opacity: 0.4; border-color: #212529; }
        .seat-label { color: #fff; font-weight: bold; font-size: 11px; margin-top: 15px; }
        
        /* ЭЛЕМЕНТЫ */
        .opp-cards { position: absolute; top: -10px; width: 30px; height: 42px; background: #fff; border-radius: 4px; border: 1px solid #ccc; background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); box-shadow: 1px 1px 3px rgba(0,0,0,0.5); z-index: 4; }
        .dealer-button { position: absolute; width: 20px; height: 20px; background: #ffc107; border: 1px solid #e0a800; border-radius: 50%; color: #000; font-weight: bold; font-size: 10px; display: flex; justify-content: center; align-items: center; box-shadow: 1px 1px 3px rgba(0,0,0,0.5); z-index: 15; }
        .poker-chip { width: 18px; height: 18px; background: #222; border: 3px dashed #d32f2f; border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.7); }
        .blind-stack { position: absolute; z-index: 15; display: flex; flex-direction: column; align-items: center; }
        .chip-stacked { margin-top: -14px; }

        /* КООРДИНАТЫ */
        .pos-1 { bottom: 20%; left: 8%; } .pos-2 { top: 20%; left: 8%; } .pos-3 { top: -25px; left: 50%; transform: translateX(-50%); } .pos-4 { top: 20%; right: 8%; } .pos-5 { bottom: 20%; right: 8%; }
        
        /* HERO */
        .hero-panel { position: absolute; bottom: -35px; left: 50%; transform: translateX(-50%); background: #212529; border: 2px solid #ffc107; border-radius: 12px; padding: 5px 15px; display: flex; gap: 8px; box-shadow: 0 0 20px rgba(255, 193, 7, 0.2); z-index: 10; align-items: center; }
        .card { width: 45px; height: 65px; background: white; border-radius: 4px; position: relative; color: black; font-family: 'Arial', sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .tl { position: absolute; top: 1px; left: 3px; font-weight: bold; font-size: 14px; line-height: 1.1; }
        .cent { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 24px; }
        .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #212529; }

        /* КНОПКИ */
        div.stButton > button { width: 100%; height: 50px !important; font-size: 16px !important; font-weight: 600; border-radius: 6px; border: none; text-transform: uppercase; transition: all 0.2s; }
        div[data-testid="column"]:nth-of-type(1) div.stButton > button { background-color: #343a40 !important; color: #adb5bd !important; border: 1px solid #495057; }
        div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover { background-color: #dc3545 !important; color: white !important; border-color: #dc3545; }
        div[data-testid="column"]:nth-of-type(2) div.stButton > button { background-color: #28a745 !important; color: white !important; }
        div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover { background-color: #218838 !important; }

        /* СТАТЫ */
        .stats-box { background: #343a40; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 20px; }
        .stat-val { color: #fff; font-size: 20px; font-weight: bold; }
        .h-s { color: #e0e0e0; } .h-h { color: #ff6b6b; } .h-d { color: #4dabf7; } .h-c { color: #69db7c; }
        .hist-row { font-family: monospace; font-size: 14px; margin-bottom: 4px; border-bottom: 1px solid #444; padding-bottom: 4px; }
        .hist-spot { color: #888; font-size: 11px; float: right; }

        /* МАТРИЦА */
        .range-grid { display: grid; grid-template-columns: repeat(13, 1fr); gap: 1px; font-family: monospace; border: 1px solid #444; padding: 2px; background: #111; }
        .grid-cell { aspect-ratio: 1; display: flex; justify-content: center; align-items: center; font-size: 9px; color: #aaa; cursor: default; }
        .current-hand-highlight { border: 2px solid #ffc107 !important; z-index: 10; color: #fff !important; font-weight: bold; background-color: rgba(255, 193, 7, 0.2) !important; }
    </style>
    """, unsafe_allow_html=True)

    # --- ЛОГИКА ---
    ranges_db = utils.load_ranges()
    
    # Сайдбар настроек
    with st.sidebar:
        st.header("Settings")
        saved = utils.load_user_settings()
        
        all_src = list(ranges_db.keys())
        def_src = saved.get("sources", [all_src[0]])
        sel_src = []
        cols = st.columns(len(all_src))
        for i, s in enumerate(all_src):
            if cols[i].checkbox(s, value=(s in def_src)): sel_src.append(s)
        
        avail_sc = set()
        for s in sel_src: avail_sc.update(ranges_db[s].keys())
        sel_sc = []
        sc_cols = st.columns(min(3, len(avail_sc))) if avail_sc else []
        for i, sc in enumerate(list(avail_sc)):
            if sc_cols[i % 3].checkbox(sc, value=True): sel_sc.append(sc)
            
        mode = st.radio("F", ["All", "Early", "Late", "Manual"], horizontal=True, label_visibility="collapsed")
        
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
        
        if mode=="Manual" and pool:
            sel_spot = st.selectbox("Spot", pool)
            pool = [sel_spot]
            
        utils.save_user_settings({"sources": sel_src, "scenarios": sel_sc, "mode": mode})

    # --- UI ---
    col_left, col_center, col_right = st.columns([1, 2, 1])

    if 'hand' not in st.session_state: st.session_state.hand = None
    if 'current_spot_key' not in st.session_state: st.session_state.current_spot_key = None
    if 'suits' not in st.session_state: st.session_state.suits = None
    if 'msg' not in st.session_state: st.session_state.msg = None
    if 'srs_mode' not in st.session_state: st.session_state.srs_mode = False
    if 'last_error' not in st.session_state: st.session_state.last_error = False

    # Генерация
    if st.session_state.hand is None:
        if not pool: st.error("No spots"); return
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

    # --- LEFT ---
    with col_left:
        st.markdown("### Session")
        df = utils.load_history()
        now = datetime.now()
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"])
            df_today = df[df["Date"].dt.date == now.date()]
            total = len(df_today)
            correct = df_today["Result"].sum()
            acc = int(correct/total*100) if total > 0 else 0
            st.markdown(f"<div class='stats-box'><div style='font-size:12px;color:#adb5bd;'>ACCURACY</div><div class='stat-val' style='color:{'#28a745' if acc>90 else '#ffc107'};'>{acc}%</div><div style='font-size:12px;color:#adb5bd;margin-top:5px;'>HANDS: {total}</div></div>", unsafe_allow_html=True)
            errs = df_today[df_today["Result"]==0].sort_values("Date", ascending=False).head(7)
            if not errs.empty:
                st.markdown("**Recent Errors:**")
                for i, r in errs.iterrows():
                    h_fmt = utils.format_hand_colored(r['Hand'])
                    st.markdown(f"<div class='hist-row'>{h_fmt} <span class='hist-spot'>{r['Spot']}</span></div>", unsafe_allow_html=True)

    # --- CENTER ---
    with col_center:
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
        html = f'<div class="game-area"><div class="table-info"><div class="info-src">{src} • {sc}</div><div class="info-spot">{sp}</div></div>'
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
            sty = utils.get_chip_style(i)
            if pos == "BTN": chips_html += f'<div class="dealer-button" style="{sty}">D</div>'
            elif pos == "SB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div></div>'
            elif pos == "BB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div><div class="poker-chip chip-stacked"></div></div>'
        
        sty = utils.get_chip_style(0)
        if rot[0] == "BTN": chips_html += f'<div class="dealer-button" style="{sty}">D</div>'
        elif rot[0] == "SB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div></div>'
        elif rot[0] == "BB": chips_html += f'<div class="blind-stack" style="{sty}"><div class="poker-chip"></div><div class="poker-chip chip-stacked"></div></div>'
        
        html += f'<div class="hero-panel"><div style="display:flex;flex-direction:column;align-items:center;"><span style="color:#ffc107;font-weight:bold;font-size:12px;">HERO</span><span style="color:#adb5bd;font-size:10px;">{rot[0]}</span></div><div class="card"><div class="tl {c1}">{h_val[0]}<br>{s1}</div><div class="cent {c1}">{s1}</div></div><div class="card"><div class="tl {c2}">{h_val[1]}<br>{s2}</div><div class="cent {c2}">{s2}</div></div></div>'
        html += chips_html + "</div>"
        st.markdown(html, unsafe_allow_html=True)

        if not st.session_state.srs_mode:
            b1, b2 = st.columns(2)
            with b1:
                if st.button("FOLD", use_container_width=True):
                    corr = (ans_w == 0.0)
                    st.session_state.last_error = not corr
                    st.session_state.msg = "✅ Correct" if corr else f"❌ Error (Raise {int(ans_w*100)}%)"
                    hf = f"{h_val[0]}{s1}{h_val[1]}{s2}"
                    utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": hf, "Result": 1 if corr else 0, "CorrectAction": "Fold" if ans_w==0 else "Raise"})
                    st.session_state.srs_mode = True; st.rerun()
            with b2:
                if st.button("RAISE", use_container_width=True):
                    corr = (ans_w > 0.0)
                    st.session_state.last_error = not corr
                    st.session_state.msg = f"✅ Correct" if corr else "❌ Error (Fold)"
                    hf = f"{h_val[0]}{s1}{h_val[1]}{s2}"
                    utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": hf, "Result": 1 if corr else 0, "CorrectAction": "Raise" if ans_w>0 else "Fold"})
                    st.session_state.srs_mode = True; st.rerun()
        else:
            st.info(st.session_state.msg)
            s1, s2, s3 = st.columns(3)
            k = f"{src}_{sc}_{sp}".replace(" ","_")
            if s1.button("HARD"): utils.update_srs_smart(k, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
            if s2.button("NORMAL"): utils.update_srs_smart(k, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
            if s3.button("EASY"): utils.update_srs_smart(k, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()

    # --- RIGHT ---
    with col_right:
        show_matrix = st.checkbox("Show Matrix", value=st.session_state.last_error)
        if show_matrix:
            st.markdown(f"**{sp} Range**")
            st.markdown(utils.render_range_matrix(full_r, target_hand=st.session_state.hand), unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; color:#555; margin-top:100px;'>Matrix hidden</div>", unsafe_allow_html=True)
