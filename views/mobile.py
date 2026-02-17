import streamlit as st
import random
from datetime import datetime
import utils

def show():
    # --- МОБИЛЬНЫЙ CSS ---
    st.markdown("""
    <style>
        .block-container { padding-top: 3rem !important; padding-bottom: 5rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }

        /* КНОПКИ */
        .mobile-controls { display: flex; flex-direction: row; width: 100%; gap: 10px; margin-top: 10px; }
        .mobile-controls div[data-testid="column"] { width: 50% !important; flex: 1 1 50% !important; min-width: 0 !important; }
        .mobile-controls button { width: 100% !important; height: 70px !important; font-size: 20px !important; font-weight: 900 !important; border-radius: 12px !important; border: none !important; text-transform: uppercase !important; margin: 0px !important; }
        .fold-btn button { background: #c62828 !important; color: white !important; box-shadow: 0 4px 0 #8e0000 !important; }
        .raise-btn button { background: #2e7d32 !important; color: white !important; box-shadow: 0 4px 0 #1b5e20 !important; }
        .srs-container button { height: 55px !important; font-size: 14px !important; background: #343a40 !important; color: #adb5bd !important; border: 1px solid #495057 !important; box-shadow: none !important; }

        /* СТОЛ */
        .mobile-game-area { position: relative; width: 100%; height: 260px; margin: 0 auto 10px auto; background: radial-gradient(ellipse at center, #1b5e20 0%, #0a2e0b 100%); border: 6px solid #3e2723; border-radius: 130px; box-shadow: 0 4px 10px rgba(0,0,0,0.8); }
        .mob-info { position: absolute; top: 22%; left: 50%; transform: translateX(-50%); text-align: center; width: 100%; z-index: 2; pointer-events: none; }
        .mob-info-src { font-size: 9px; color: #888; text-transform: uppercase; }
        .mob-info-spot { font-size: 20px; font-weight: 900; color: rgba(255,255,255,0.15); }
        .mob-mode-tag { font-size: 10px; font-weight: bold; color: #ffc107; opacity: 0.6; }

        .seat { position: absolute; width: 42px; height: 42px; background: #222; border: 1px solid #444; border-radius: 6px; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 5; }
        .seat-label { font-size: 8px; color: #fff; font-weight: bold; margin-top: auto; margin-bottom: 2px; }
        .seat-active { border-color: #ffc107; background: #2a2a2a; }
        .seat-folded { opacity: 0.4; border-color: #333; }
        .opp-cards-mob { position: absolute; top: -10px; width: 22px; height: 30px; background: #fff; border-radius: 3px; border: 1px solid #ccc; background-image: repeating-linear-gradient(45deg, #b71c1c 0, #b71c1c 2px, #fff 2px, #fff 4px); z-index: 20; box-shadow: 1px 1px 3px rgba(0,0,0,0.8); }

        /* ФИШКИ */
        .dealer-mob { position: absolute; width: 14px; height: 14px; background: #ffc107; border-radius: 50%; color: #000; font-weight: bold; font-size: 8px; display: flex; justify-content: center; align-items: center; z-index: 10; border: 1px solid #bfa006; }
        .blind-mob { position: absolute; z-index: 9; display: flex; flex-direction: column; align-items: center; }
        .chip-mob { width: 12px; height: 12px; background: #111; border: 2px dashed #d32f2f; border-radius: 50%; box-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
        /* 3-BET STACK */
        .chip-3bet { width: 14px; height: 14px; background: #d32f2f; border: 2px solid #fff; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.6); }
        
        .m-pos-1 { bottom: 18%; left: 4%; } .m-pos-2 { top: 18%; left: 4%; } .m-pos-3 { top: -15px; left: 50%; transform: translateX(-50%); } .m-pos-4 { top: 18%; right: 4%; } .m-pos-5 { bottom: 18%; right: 4%; }

        .hero-mob { position: absolute; bottom: -25px; left: 50%; transform: translateX(-50%); display: flex; gap: 4px; z-index: 30; background: #212529; padding: 4px 10px; border-radius: 10px; border: 1px solid #ffc107; }
        .card-mob { width: 42px; height: 60px; background: white; border-radius: 4px; position: relative; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }
        .tl-mob { position: absolute; top: 1px; left: 3px; font-weight: bold; font-size: 14px; line-height: 1; }
        .c-mob { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 24px; }
        .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #111; }
        .rng-badge { position: absolute; bottom: 50px; right: -15px; width: 28px; height: 28px; background: #6f42c1; border: 2px solid #fff; border-radius: 50%; color: white; font-weight: bold; font-size: 11px; display: flex; justify-content: center; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.5); z-index: 40; }
    </style>
    """, unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: st.error("No ranges"); return

    # --- SETTINGS ---
    with st.expander("⚙️ Settings", expanded=False):
        saved = utils.load_user_settings()
        sel_src = st.multiselect("Source", list(ranges_db.keys()), default=saved.get("sources", [list(ranges_db.keys())[0]]))
        avail_sc = set()
        for s in sel_src: avail_sc.update(ranges_db[s].keys())
        sel_sc = st.multiselect("Scenario", list(avail_sc), default=saved.get("scenarios", [list(avail_sc)[0]] if avail_sc else []))
        mode = st.selectbox("Positions", ["All", "Early", "Late", "Manual"], index=["All", "Early", "Late", "Manual"].index(saved.get("mode", "All")))
        
        if st.button("🚀 Apply & Reset"):
            utils.save_user_settings({"sources": sel_src, "scenarios": sel_sc, "mode": mode})
            st.session_state.hand = None; st.rerun()

    pool = []
    for src in sel_src:
        for sc in sel_sc:
            if sc in ranges_db[src]:
                for sp in ranges_db[src][sc]:
                    u = sp.upper()
                    m = (mode=="All" or (mode=="Early" and any(x in u for x in ["EP","UTG","MP"])) or (mode=="Late" and any(x in u for x in ["CO","BU","BTN","SB"])) or mode=="Manual")
                    if m: pool.append(f"{src}|{sc}|{sp}")
    if not pool: st.error("No spots"); return
    if mode == "Manual": sp_man = st.selectbox("Spot", pool); pool = [sp_man]

    # --- STATE INIT ---
    if 'hand' not in st.session_state: st.session_state.hand = None
    if 'rng' not in st.session_state: st.session_state.rng = 0
    if 'suits' not in st.session_state: st.session_state.suits = None
    if 'msg' not in st.session_state: st.session_state.msg = None
    if 'srs_mode' not in st.session_state: st.session_state.srs_mode = False
    if 'last_error' not in st.session_state: st.session_state.last_error = False

    # --- GENERATION ---
    if st.session_state.hand is None:
        chosen = random.choice(pool)
        st.session_state.current_spot_key = chosen
        src, sc, sp = chosen.split('|')
        data = ranges_db[src][sc][sp]
        st.session_state.is_training_mode = "training" in data
        t_range = data.get("training", data.get("full", ""))
        poss = utils.parse_range_to_list(t_range)
        srs = utils.load_srs_data()
        w = [srs.get(f"{src}_{sc}_{sp}_{h}".replace(" ","_"), 100) for h in poss]
        st.session_state.hand = random.choices(poss, weights=w, k=1)[0]
        st.session_state.rng = random.randint(0, 99)
        ps = ['♠','♥','♦','♣']; s1 = random.choice(ps)
        st.session_state.suits = [s1, s1 if 's' in st.session_state.hand else random.choice([x for x in ps if x!=s1])]
        st.session_state.srs_mode = False; st.session_state.last_error = False

    # DATA PREP
    src, sc, sp = st.session_state.current_spot_key.split('|')
    full_r = ranges_db[src][sc][sp].get("full", "")
    hand_weight = utils.get_weight(st.session_state.hand, full_r)
    rng_val = st.session_state.rng
    should_raise = rng_val < hand_weight
    h_val = st.session_state.hand; s1, s2 = st.session_state.suits
    c1 = "suit-red" if s1 in '♥' else "suit-blue" if s1 in '♦' else "suit-black"
    c2 = "suit-red" if s2 in '♥' else "suit-blue" if s2 in '♦' else "suit-black"

    # --- TABLE LOGIC (SMART VISUALS) ---
    order = ["EP", "MP", "CO", "BTN", "SB", "BB"]
    hero_idx = 0; u = sp.upper()
    if any(p in u for p in ["EP", "UTG"]): hero_idx = 0
    elif "MP" in u: hero_idx = 1
    elif "CO" in u: hero_idx = 2
    elif any(p in u for p in ["BTN", "BU"]): hero_idx = 3
    elif "SB" in u: hero_idx = 4
    elif "BB" in u: hero_idx = 5
    rot = order[hero_idx:] + order[:hero_idx]

    # Определяем тип спота
    is_3bet_pot = "3bet" in sc or "Def" in sc
    villain_pos = None
    
    if is_3bet_pot:
        # Парсим злодея из названия спота
        if "vs MP" in sp: villain_pos = "MP"
        elif "vs CO" in sp: villain_pos = "CO"
        elif "vs BU" in sp or "vs BTN" in sp: villain_pos = "BTN"
        elif "vs SB" in sp: villain_pos = "SB"
        elif "vs BB" in sp: villain_pos = "BB"
        elif "vs Blinds" in sp: villain_pos = random.choice(["SB", "BB"]) # Рандом если против блайндов

    opp_html = ""
    chips_html = ""
    def get_pos_style(idx):
        return {0: "bottom:25%;left:47%;", 1: "bottom:25%;left:22%;", 2: "top:25%;left:22%;", 
                3: "top:10%;left:47%;", 4: "top:25%;right:22%;", 5: "bottom:25%;right:22%;"}.get(idx, "")

    for i in range(1, 6):
        pos_name = rot[i]
        
        # ЛОГИКА АКТИВНОСТИ ИГРОКОВ
        is_active = False
        chips_type = "none" # none, blind, 3bet
        
        if is_3bet_pot:
            # В 3-бет поте активен только Злодей (ну и Хиро)
            if pos_name == villain_pos:
                is_active = True
                chips_type = "3bet"
            else:
                is_active = False # Все остальные фолд
        else:
            # В Опен-Рейзе: активны те, кто ПОСЛЕ хиро (ждут хода)
            # Индексы в порядке игры: EP=0 ... BB=5
            idx_current = order.index(pos_name)
            idx_hero = order.index(rot[0])
            # Если Хиро EP(0), то MP(1)...BB(5) активны (ждут).
            # Если Хиро SB(4), то EP...BTN сфолдили (индекс меньше), BB активен.
            if idx_current > idx_hero or (rot[0] == "SB" and pos_name == "BB"):
                is_active = True
                if pos_name in ["SB", "BB"]: chips_type = "blind"
            else:
                is_active = False

        cls = "seat-active" if is_active else "seat-folded"
        cards = '<div class="opp-cards-mob"></div>' if is_active else ""
        opp_html += f'<div class="seat m-pos-{i} {cls}">{cards}<span class="seat-label">{pos_name}</span></div>'
        
        # Рисуем фишки оппонентов
        s = get_pos_style(i)
        if chips_type == "blind":
            chips_html += f'<div class="blind-mob" style="{s}"><div class="chip-mob"></div></div>'
        elif chips_type == "3bet":
            chips_html += f'<div class="blind-mob" style="{s}"><div class="chip-3bet"></div><div class="chip-3bet" style="margin-top:-10px"></div><div class="chip-3bet" style="margin-top:-10px"></div></div>'
        
        # Кнопка дилера
        if pos_name == "BTN": chips_html += f'<div class="dealer-mob" style="{s}">D</div>'

    # ФИШКИ ХИРО
    hs = get_pos_style(0)
    if is_3bet_pot:
        # Хиро всегда ставит опен-рейз в 3бет поте
        chips_html += f'<div class="blind-mob" style="{hs}"><div class="chip-mob"></div><div class="chip-mob" style="margin-top:-5px"></div></div>'
    elif rot[0] in ["SB", "BB"]:
        # Хиро ставит блайнд в RFI
        chips_html += f'<div class="blind-mob" style="{hs}"><div class="chip-mob"></div></div>'
    if rot[0] == "BTN": chips_html += f'<div class="dealer-mob" style="{hs}">D</div>'

    mode_tag = "TRAINING MODE" if st.session_state.is_training_mode else "FULL RANGE"
    
    html = f"""
    <div class="mobile-game-area">
        <div class="mob-info"><div class="mob-info-src">{src}</div><div class="mob-info-spot">{sp}</div><div class="mob-mode-tag">{mode_tag}</div></div>
        {opp_html} {chips_html}
        <div class="hero-mob">
            <div class="card-mob"><div class="tl-mob {c1}">{h_val[0]}<br>{s1}</div><div class="c-mob {c1}">{s1}</div></div>
            <div class="card-mob"><div class="tl-mob {c2}">{h_val[1]}<br>{s2}</div><div class="c-mob {c2}">{s2}</div></div>
            <div class="rng-badge">{rng_val}</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    # --- КНОПКИ ---
    st.markdown('<div class="mobile-controls">', unsafe_allow_html=True)
    if not st.session_state.srs_mode:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("FOLD", key="btn_fold", use_container_width=True):
                st.session_state.last_error = should_raise
                st.session_state.msg = f"✅ Correct (Freq {int(hand_weight)}% > RNG {rng_val})" if not st.session_state.last_error else f"❌ Error! Freq {int(hand_weight)}% > RNG {rng_val} -> RAISE"
                utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val[0]}{s1}{h_val[1]}{s2}", "Result": 0 if st.session_state.last_error else 1, "CorrectAction": "Fold"})
                st.session_state.srs_mode = True; st.rerun()
            st.markdown('<script>parent.document.querySelector("div[data-testid=\'column\']:nth-child(1) button").classList.add("fold-btn");</script>', unsafe_allow_html=True)
        with c2:
            if st.button("RAISE", key="btn_raise", use_container_width=True):
                st.session_state.last_error = not should_raise
                st.session_state.msg = f"✅ Correct (Freq {int(hand_weight)}% > RNG {rng_val})" if not st.session_state.last_error else f"❌ Error! Freq {int(hand_weight)}% <= RNG {rng_val} -> FOLD"
                utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val[0]}{s1}{h_val[1]}{s2}", "Result": 0 if st.session_state.last_error else 1, "CorrectAction": "Raise"})
                st.session_state.srs_mode = True; st.rerun()
            st.markdown('<script>parent.document.querySelector("div[data-testid=\'column\']:nth-child(2) button").classList.add("raise-btn");</script>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.srs_mode:
        if st.session_state.last_error:
            st.error(st.session_state.msg)
            with st.expander("Show Range", expanded=True): st.markdown(utils.render_range_matrix(full_r, st.session_state.hand), unsafe_allow_html=True)
        else:
            st.success(st.session_state.msg)
        
        st.markdown('<div class="mobile-controls srs-container">', unsafe_allow_html=True)
        s1, s2, s3 = st.columns(3)
        k = f"{src}_{sc}_{sp}".replace(" ","_")
        if s1.button("HARD", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
        if s2.button("NORM", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
        if s3.button("EASY", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
