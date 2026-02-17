import streamlit as st
import random
from datetime import datetime
import pandas as pd
import utils

def show():
    # --- DESKTOP CSS ---
    st.markdown("""
    <style>
        .stApp { background-color: #212529; color: #e9ecef; }
        .block-container { padding-top: 4rem; padding-bottom: 2rem; }

        /* СТОЛ (RACETRACK) */
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
        .mode-tag { font-size: 11px; font-weight: bold; color: #ffc107; opacity: 0.7; margin-top: 2px; }

        /* МЕСТА */
        .seat { position: absolute; width: 60px; height: 60px; background: #343a40; border: 2px solid #495057; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 4px 8px rgba(0,0,0,0.4); z-index: 5; }
        .seat-active { border-color: #ffc107; background: #343a40; }
        .seat-folded { opacity: 0.4; border-color: #212529; }
        .seat-label { color: #fff; font-weight: bold; font-size: 11px; margin-top: 15px; }
        
        /* КАРТЫ ОППОНЕНТОВ */
        .opp-cards { position: absolute; top: -10px; width: 30px; height: 42px; background: #fff; border-radius: 4px; border: 1px solid #ccc; background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); box-shadow: 1px 1px 3px rgba(0,0,0,0.5); z-index: 4; }
        
        /* ФИШКИ */
        .dealer-button { position: absolute; width: 20px; height: 20px; background: #ffc107; border: 1px solid #e0a800; border-radius: 50%; color: #000; font-weight: bold; font-size: 10px; display: flex; justify-content: center; align-items: center; box-shadow: 1px 1px 3px rgba(0,0,0,0.5); z-index: 15; }
        .poker-chip { width: 18px; height: 18px; background: #222; border: 3px dashed #d32f2f; border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.7); }
        .chip-3bet-desk { width: 20px; height: 20px; background: #d32f2f; border: 2px solid #fff; border-radius: 50%; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }
        .blind-stack { position: absolute; z-index: 15; display: flex; flex-direction: column; align-items: center; }
        
        .pos-1 { bottom: 20%; left: 8%; } .pos-2 { top: 20%; left: 8%; } .pos-3 { top: -25px; left: 50%; transform: translateX(-50%); } .pos-4 { top: 20%; right: 8%; } .pos-5 { bottom: 20%; right: 8%; }
        
        /* HERO & RNG */
        .hero-panel { position: absolute; bottom: -35px; left: 50%; transform: translateX(-50%); background: #212529; border: 2px solid #ffc107; border-radius: 12px; padding: 5px 15px; display: flex; gap: 8px; box-shadow: 0 0 20px rgba(255, 193, 7, 0.2); z-index: 10; align-items: center; }
        .card { width: 45px; height: 65px; background: white; border-radius: 4px; position: relative; color: black; font-family: 'Arial', sans-serif; box-shadow: 0 2px 5px rgba(0,0,0,0.3); }
        .tl { position: absolute; top: 1px; left: 3px; font-weight: bold; font-size: 14px; line-height: 1.1; }
        .cent { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 24px; }
        .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #212529; }
        
        .rng-desktop {
            position: absolute; right: -40px; top: 10px;
            width: 35px; height: 35px; background: #6f42c1; border: 2px solid #fff; border-radius: 50%;
            color: white; font-weight: bold; font-size: 14px;
            display: flex; justify-content: center; align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.6);
        }

        /* КНОПКИ */
        div.stButton > button { width: 100%; height: 60px !important; font-size: 18px !important; font-weight: 700; border-radius: 8px; border: none; text-transform: uppercase; transition: all 0.2s; }
        
        .fold-btn button { background: #495057 !important; color: #adb5bd !important; border: 1px solid #6c757d !important; }
        .fold-btn button:hover { background: #343a40 !important; }
        
        .call-btn button { background: #28a745 !important; color: white !important; }
        .call-btn button:hover { background: #218838 !important; }
        
        .raise-btn button { background: #d63384 !important; color: white !important; } /* 4Bet */
        .raise-btn button:hover { background: #c2185b !important; }
        
        .open-raise-btn button { background: #2e7d32 !important; color: white !important; } /* OR */

        /* СТАТЫ */
        .stats-box { background: #343a40; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 20px; }
        .stat-val { color: #fff; font-size: 20px; font-weight: bold; }
        .hist-row { font-family: monospace; font-size: 14px; margin-bottom: 4px; border-bottom: 1px solid #444; padding-bottom: 4px; }
        .hist-spot { color: #888; font-size: 11px; float: right; }
    </style>
    """, unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: st.error("No ranges found"); return
    
    # --- SETTINGS SIDEBAR ---
    with st.sidebar:
        st.header("Settings")
        saved = utils.load_user_settings()
        
        sel_src = st.multiselect("Source", list(ranges_db.keys()), default=saved.get("sources", [list(ranges_db.keys())[0]]))
        avail_sc = set()
        for s in sel_src: avail_sc.update(ranges_db[s].keys())
        sel_sc = st.multiselect("Scenario", list(avail_sc), default=saved.get("scenarios", [list(avail_sc)[0]] if avail_sc else []))
        mode = st.selectbox("Positions", ["All", "Early", "Late", "Manual"], index=["All", "Early", "Late", "Manual"].index(saved.get("mode", "All")))
        
        # Pool
        pool = []
        for src in sel_src:
            for sc in sel_sc:
                if sc in ranges_db[src]:
                    for sp in ranges_db[src][sc]:
                        u = sp.upper()
                        if mode=="All" or (mode=="Early" and any(x in u for x in ["EP","UTG","MP"])) or (mode=="Late" and any(x in u for x in ["CO","BU","BTN","SB"])) or mode=="Manual":
                            pool.append(f"{src}|{sc}|{sp}")
        
        if mode == "Manual" and pool:
            sp_man = st.selectbox("Select Spot", pool)
            pool = [sp_man]
            
        if st.button("Apply & Reset", type="primary"):
            utils.save_user_settings({"sources": sel_src, "scenarios": sel_sc, "mode": mode})
            st.session_state.hand = None
            st.rerun()

    # --- STATE ---
    if 'hand' not in st.session_state: st.session_state.hand = None
    if 'rng' not in st.session_state: st.session_state.rng = 0
    if 'suits' not in st.session_state: st.session_state.suits = None
    if 'msg' not in st.session_state: st.session_state.msg = None
    if 'srs_mode' not in st.session_state: st.session_state.srs_mode = False
    if 'last_error' not in st.session_state: st.session_state.last_error = False

    if not pool: st.error("No spots available"); return

    # --- GENERATION ---
    if st.session_state.hand is None:
        chosen = random.choice(pool)
        st.session_state.current_spot_key = chosen
        src, sc, sp = chosen.split('|')
        data = ranges_db[src][sc][sp]
        t_range = data.get("source", data.get("training", data.get("full", "")))
        poss = utils.parse_range_to_list(t_range)
        srs = utils.load_srs_data()
        w = [srs.get(f"{src}_{sc}_{sp}_{h}".replace(" ","_"), 100) for h in poss]
        st.session_state.hand = random.choices(poss, weights=w, k=1)[0]
        st.session_state.rng = random.randint(0, 99)
        ps = ['♠','♥','♦','♣']; s1 = random.choice(ps)
        st.session_state.suits = [s1, s1 if 's' in st.session_state.hand else random.choice([x for x in ps if x!=s1])]
        st.session_state.srs_mode = False; st.session_state.last_error = False

    # --- LOGIC ---
    src, sc, sp = st.session_state.current_spot_key.split('|')
    data = ranges_db[src][sc][sp]
    is_defense_mode = "call" in data
    
    rng = st.session_state.rng
    correct_act = "FOLD"
    
    if is_defense_mode:
        w_call = utils.get_weight(st.session_state.hand, data.get("call", ""))
        w_4bet = utils.get_weight(st.session_state.hand, data.get("4bet", ""))
        if rng < w_4bet: correct_act = "4BET"
        elif rng < (w_4bet + w_call): correct_act = "CALL"
    else:
        full_r = data.get("full", "")
        w = utils.get_weight(st.session_state.hand, full_r)
        if w > 0: correct_act = "RAISE"

    h_val = st.session_state.hand; s1, s2 = st.session_state.suits
    c1 = "suit-red" if s1 in '♥' else "suit-blue" if s1 in '♦' else "suit-black"
    c2 = "suit-red" if s2 in '♥' else "suit-blue" if s2 in '♦' else "suit-black"

    # --- UI COLUMNS ---
    col_left, col_center, col_right = st.columns([1, 2, 1])

    # LEFT: Stats
    with col_left:
        st.markdown("### Session")
        df = utils.load_history()
        now = datetime.now()
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"])
            df_today = df[df["Date"].dt.date == now.date()]
            total = len(df_today)
            corr = df_today["Result"].sum()
            acc = int(corr/total*100) if total > 0 else 0
            st.markdown(f"<div class='stats-box'><div style='font-size:12px;color:#adb5bd;'>ACCURACY</div><div class='stat-val' style='color:{'#28a745' if acc>90 else '#ffc107'};'>{acc}%</div><div style='font-size:12px;color:#adb5bd;margin-top:5px;'>HANDS: {total}</div></div>", unsafe_allow_html=True)
            errs = df_today[df_today["Result"]==0].sort_values("Date", ascending=False).head(7)
            if not errs.empty:
                st.markdown("**Recent Errors:**")
                for i, r in errs.iterrows():
                    h_fmt = utils.format_hand_colored(r['Hand'])
                    st.markdown(f"<div class='hist-row'>{h_fmt} <span class='hist-spot'>{r['Spot']}</span></div>", unsafe_allow_html=True)

    # CENTER: Table & Actions
    with col_center:
        order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
        hero_idx = 0; u = sp.upper()
        if any(p in u for p in ["EP", "UTG"]): hero_idx = 0
        elif "MP" in u: hero_idx = 1
        elif "CO" in u: hero_idx = 2
        elif any(p in u for p in ["BTN", "BU"]): hero_idx = 3
        elif "SB" in u: hero_idx = 4
        elif "BB" in u: hero_idx = 5
        rot = order[hero_idx:] + order[:hero_idx]

        # Логика фишек (как на мобиле)
        is_3bet_pot = "3bet" in sc or "Def" in sc
        villain_pos = None
        if is_3bet_pot:
            if "vs MP" in sp: villain_pos = "MP"
            elif "vs CO" in sp: villain_pos = "CO"
            elif "vs BU" in sp or "vs BTN" in sp: villain_pos = "BTN"
            elif "vs SB" in sp: villain_pos = "SB"
            elif "vs BB" in sp: villain_pos = "BB"
            elif "vs Blinds" in sp: villain_pos = random.choice(["SB", "BB"])

        opp_html = ""; chips_html = ""
        def get_pos_style(idx):
            return {0: "bottom:25%;left:48%;", 1: "bottom:28%;left:25%;", 2: "top:28%;left:25%;", 
                    3: "top:15%;left:48%;", 4: "top:28%;right:25%;", 5: "bottom:28%;right:25%;"}.get(idx, "")

        for i in range(1, 6):
            p = rot[i]
            is_active = False; c_type = "none"
            if is_3bet_pot:
                if p == villain_pos: is_active=True; c_type="3bet"
            else:
                if order.index(p) > order.index(rot[0]) or (rot[0]=="SB" and p=="BB"): is_active=True; c_type="blind" if p in ["SB","BB"] else "none"
            
            cls = "seat-active" if is_active else "seat-folded"
            cards = '<div class="opp-cards"></div>' if is_active else ""
            opp_html += f'<div class="seat pos-{i} {cls}">{cards}<span class="seat-label">{p}</span></div>'
            
            s = get_pos_style(i)
            if c_type == "blind": chips_html += f'<div class="blind-stack" style="{s}"><div class="poker-chip"></div></div>'
            elif c_type == "3bet": chips_html += f'<div class="blind-stack" style="{s}"><div class="chip-3bet-desk"></div><div class="chip-3bet-desk" style="margin-top:-15px;"></div></div>'
            if p == "BTN": chips_html += f'<div class="dealer-button" style="{s}">D</div>'

        hs = get_pos_style(0)
        if is_3bet_pot: chips_html += f'<div class="blind-stack" style="{hs}"><div class="poker-chip"></div><div class="poker-chip" style="margin-top:-10px"></div></div>'
        elif rot[0] in ["SB", "BB"]: chips_html += f'<div class="blind-stack" style="{hs}"><div class="poker-chip"></div></div>'
        if rot[0] == "BTN": chips_html += f'<div class="dealer-button" style="{hs}">D</div>'

        mode_tag = "TRAINING MODE" if "training" in data or "source" in data else "FULL RANGE"
        html = f"""
        <div class="game-area">
            <div class="table-info"><div class="info-src">{src} • {sc}</div><div class="info-spot">{sp}</div><div class="mode-tag">{mode_tag}</div></div>
            {opp_html} {chips_html}
            <div class="hero-panel">
                <div style="display:flex;flex-direction:column;align-items:center;"><span style="color:#ffc107;font-weight:bold;font-size:12px;">HERO</span><span style="color:#adb5bd;font-size:10px;">{rot[0]}</span></div>
                <div class="card"><div class="tl {c1}">{h_val[0]}<br>{s1}</div><div class="cent {c1}">{s1}</div></div>
                <div class="card"><div class="tl {c2}">{h_val[1]}<br>{s2}</div><div class="cent {c2}">{s2}</div></div>
                <div class="rng-desktop">{rng}</div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

        if is_defense_mode:
            st.markdown('<div class="rng-hint" style="text-align:center;margin-bottom:10px;color:#888;">📉 0..Freq → Action | 📈 Freq..100 → Fold</div>', unsafe_allow_html=True)

        # ACTION BUTTONS
        if not st.session_state.srs_mode:
            if is_defense_mode:
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("FOLD", use_container_width=True):
                        is_c = (correct_act == "FOLD")
                        st.session_state.last_error = not is_c
                        st.session_state.msg = f"✅ Correct" if is_c else f"❌ Err! RNG {rng} -> {correct_act}"
                        utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val}", "Result": int(is_c), "CorrectAction": correct_act})
                        st.session_state.srs_mode = True; st.rerun()
                    st.markdown('<script>parent.document.querySelectorAll("div[data-testid=\'column\'] button")[0].parentElement.classList.add("fold-btn");</script>', unsafe_allow_html=True)
                with c2:
                    if st.button("CALL", use_container_width=True):
                        is_c = (correct_act == "CALL")
                        st.session_state.last_error = not is_c
                        st.session_state.msg = f"✅ Correct" if is_c else f"❌ Err! RNG {rng} -> {correct_act}"
                        utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val}", "Result": int(is_c), "CorrectAction": correct_act})
                        st.session_state.srs_mode = True; st.rerun()
                    st.markdown('<script>parent.document.querySelectorAll("div[data-testid=\'column\'] button")[1].parentElement.classList.add("call-btn");</script>', unsafe_allow_html=True)
                with c3:
                    if st.button("4BET", use_container_width=True):
                        is_c = (correct_act == "4BET")
                        st.session_state.last_error = not is_c
                        st.session_state.msg = f"✅ Correct" if is_c else f"❌ Err! RNG {rng} -> {correct_act}"
                        utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val}", "Result": int(is_c), "CorrectAction": correct_act})
                        st.session_state.srs_mode = True; st.rerun()
                    st.markdown('<script>parent.document.querySelectorAll("div[data-testid=\'column\'] button")[2].parentElement.classList.add("raise-btn");</script>', unsafe_allow_html=True)
            else:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("FOLD", use_container_width=True):
                        is_c = (correct_act == "FOLD")
                        st.session_state.last_error = not is_c
                        st.session_state.msg = "✅ Correct" if is_c else "❌ Should be RAISE"
                        utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val}", "Result": int(is_c), "CorrectAction": correct_act})
                        st.session_state.srs_mode = True; st.rerun()
                    st.markdown('<script>parent.document.querySelectorAll("div[data-testid=\'column\'] button")[0].parentElement.classList.add("fold-btn");</script>', unsafe_allow_html=True)
                with c2:
                    if st.button("RAISE", use_container_width=True):
                        is_c = (correct_act == "RAISE")
                        st.session_state.last_error = not is_c
                        st.session_state.msg = "✅ Correct" if is_c else "❌ Should be FOLD"
                        utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val}", "Result": int(is_c), "CorrectAction": correct_act})
                        st.session_state.srs_mode = True; st.rerun()
                    st.markdown('<script>parent.document.querySelectorAll("div[data-testid=\'column\'] button")[1].parentElement.classList.add("open-raise-btn");</script>', unsafe_allow_html=True)
        else:
            st.info(st.session_state.msg)
            s1, s2, s3 = st.columns(3)
            k = f"{src}_{sc}_{sp}".replace(" ","_")
            if s1.button("HARD", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
            if s2.button("NORM", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
            if s3.button("EASY", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()

    # --- RIGHT: MATRIX ---
    with col_right:
        # Авто-показ при ошибке ИЛИ кнопка при успехе
        if st.session_state.srs_mode:
            range_to_show = ""
            if is_defense_mode:
                if correct_act == "4BET": range_to_show = data.get("4bet", "")
                elif correct_act == "CALL": range_to_show = data.get("call", "")
                else: range_to_show = data.get("call", "")
            else:
                range_to_show = data.get("full", "")

            if st.session_state.last_error:
                st.write(f"**Correct: {correct_act}**")
                st.markdown(utils.render_range_matrix(range_to_show, st.session_state.hand), unsafe_allow_html=True)
            else:
                with st.expander(f"View Range ({correct_act})", expanded=False):
                    st.markdown(utils.render_range_matrix(range_to_show, st.session_state.hand), unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center;color:#555;margin-top:150px;'>Matrix hidden</div>", unsafe_allow_html=True)
