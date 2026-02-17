import streamlit as st
import random
from datetime import datetime
import utils

def show():
    # --- CSS ---
    st.markdown("""
    <style>
        .block-container { padding-top: 3.5rem !important; padding-bottom: 2rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
        
        /* КНОПКИ В РЯД */
        div[data-testid="stHorizontalBlock"] { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; align-items: center !important; justify-content: center !important; gap: 10px !important; }
        div[data-testid="column"] { flex: 1 1 0% !important; min-width: 0 !important; }
        .action-btn button { height: 75px !important; font-size: 22px !important; font-weight: 900 !important; border-radius: 12px !important; text-transform: uppercase !important; }
        .fold-btn button { background: #c62828 !important; color: white !important; box-shadow: 0 5px 0 #8e0000 !important; }
        .raise-btn button { background: #2e7d32 !important; color: white !important; box-shadow: 0 5px 0 #1b5e20 !important; }
        .srs-btn button { height: 50px !important; font-size: 14px !important; background: #343a40 !important; color: #adb5bd !important; border: 1px solid #495057 !important; }

        /* СТОЛ */
        .mobile-game-area { position: relative; width: 100%; height: 260px; margin: 0 auto 10px auto; background: radial-gradient(ellipse at center, #1b5e20 0%, #0a2e0b 100%); border: 6px solid #3e2723; border-radius: 130px; box-shadow: 0 4px 10px rgba(0,0,0,0.8); }
        .mob-info { position: absolute; top: 22%; left: 50%; transform: translateX(-50%); text-align: center; width: 100%; z-index: 2; }
        .mob-info-src { font-size: 9px; color: #888; text-transform: uppercase; }
        .mob-info-spot { font-size: 20px; font-weight: 900; color: rgba(255,255,255,0.15); margin-top: -3px; }
        .mob-mode-tag { font-size: 10px; font-weight: bold; color: #ffc107; opacity: 0.6; }

        .seat { position: absolute; width: 42px; height: 42px; background: #222; border: 1px solid #444; border-radius: 6px; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 5; }
        .seat-label { font-size: 8px; color: #fff; font-weight: bold; }
        .seat-folded { opacity: 0.3; }
        .dealer-mob { position: absolute; width: 14px; height: 14px; background: #ffc107; border-radius: 50%; color: #000; font-weight: bold; font-size: 8px; display: flex; justify-content: center; align-items: center; z-index: 10; }
        .poker-chip-mob { width: 12px; height: 12px; background: #111; border: 2px dashed #d32f2f; border-radius: 50%; }
        .m-pos-1 { bottom: 18%; left: 4%; } .m-pos-2 { top: 18%; left: 4%; } .m-pos-3 { top: -15px; left: 50%; transform: translateX(-50%); } .m-pos-4 { top: 18%; right: 4%; } .m-pos-5 { bottom: 18%; right: 4%; }

        .hero-mob { position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%); display: flex; gap: 4px; z-index: 10; background: #212529; padding: 4px 10px; border-radius: 10px; border: 1px solid #ffc107; }
        .card-mob { width: 42px; height: 60px; background: white; border-radius: 4px; position: relative; color: black; box-shadow: 0 2px 5px rgba(0,0,0,0.5); }
        .tl-mob { position: absolute; top: 1px; left: 3px; font-weight: bold; font-size: 14px; line-height: 1; }
        .c-mob { position: absolute; top: 55%; left: 50%; transform: translate(-50%,-50%); font-size: 24px; }
        .suit-red { color: #d32f2f; } .suit-blue { color: #0056b3; } .suit-black { color: #111; }

        /* RNG BADGE */
        .rng-badge {
            position: absolute;
            bottom: 45px; /* Чуть выше карт */
            right: -15px;
            width: 30px; height: 30px;
            background: #6f42c1; /* Фиолетовый как в GTO Wizard */
            border: 2px solid #fff;
            border-radius: 50%;
            color: white;
            font-weight: bold;
            font-size: 12px;
            display: flex; justify-content: center; align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.5);
            z-index: 20;
        }
    </style>
    """, unsafe_allow_html=True)

    ranges_db = utils.load_ranges()
    if not ranges_db: return

    with st.expander("⚙️ Setup Training", expanded=False):
        saved = utils.load_user_settings()
        sel_src = st.multiselect("Source", list(ranges_db.keys()), default=saved.get("sources", [list(ranges_db.keys())[0]]))
        avail_sc = set()
        for s in sel_src: avail_sc.update(ranges_db[s].keys())
        sel_sc = st.multiselect("Scenario", list(avail_sc), default=saved.get("scenarios", [list(avail_sc)[0]] if avail_sc else []))
        mode = st.selectbox("Positions", ["All", "Early", "Late", "Manual"], index=["All", "Early", "Late", "Manual"].index(saved.get("mode", "All")))
        
        if st.button("🚀 Apply & Start"):
            utils.save_user_settings({"sources": sel_src, "scenarios": sel_sc, "mode": mode})
            st.session_state.hand = None
            st.rerun()

    # Сборка пула
    pool = []
    for src in sel_src:
        for sc in sel_sc:
            if sc in ranges_db[src]:
                for sp in ranges_db[src][sc]:
                    u = sp.upper()
                    if mode=="All" or (mode=="Early" and any(x in u for x in ["EP","UTG","MP"])) or (mode=="Late" and any(x in u for x in ["CO","BU","BTN","SB"])) or mode=="Manual":
                        pool.append(f"{src}|{sc}|{sp}")
    
    if not pool: st.warning("Check filters"); return
    if mode == "Manual":
        sp_man = st.selectbox("Spot", pool)
        pool = [sp_man]

    # --- Генерация руки и RNG ---
    if 'hand' not in st.session_state or st.session_state.hand is None:
        chosen = random.choice(pool)
        st.session_state.current_spot_key = chosen
        src, sc, sp = chosen.split('|')
        data = ranges_db[src][sc][sp]
        st.session_state.is_training_mode = "training" in data
        t_range = data.get("training", data.get("full", ""))
        poss = utils.parse_range_to_list(t_range)
        srs = utils.load_srs_data()
        w = [srs.get(f"{src}_{sc}_{sp}_{h}".replace(" ","_"), 100) for h in poss]
        
        # Сдаем карты
        st.session_state.hand = random.choices(poss, weights=w, k=1)[0]
        
        # Генерируем RNG (0-99)
        st.session_state.rng = random.randint(0, 99)
        
        ps = ['♠','♥','♦','♣']; s1 = random.choice(ps)
        st.session_state.suits = [s1, s1 if 's' in st.session_state.hand else random.choice([x for x in ps if x!=s1])]
        st.session_state.srs_mode = False; st.session_state.last_error = False

    # Получаем данные
    src, sc, sp = st.session_state.current_spot_key.split('|')
    full_r = ranges_db[src][sc][sp].get("full", "")
    
    # Вес руки (Частота Raise)
    hand_weight = utils.get_weight(st.session_state.hand, full_r)
    
    # RNG Logic
    rng_val = st.session_state.rng
    # Если RNG < Частоты, то мы ДОЛЖНЫ рейзить. Иначе Фолдить (или Коллить)
    should_raise = rng_val < hand_weight
    
    h_val = st.session_state.hand; s1, s2 = st.session_state.suits
    c1 = "suit-red" if s1 in '♥' else "suit-blue" if s1 in '♦' else "suit-black"
    c2 = "suit-red" if s2 in '♥' else "suit-blue" if s2 in '♦' else "suit-black"

    # TABLE RENDER
    mode_tag = "TRAINING MODE" if st.session_state.is_training_mode else "FULL RANGE"
    opp_html = ""
    order = ["EP", "MP", "CO", "BTN", "SB", "BB"]; hero_idx = 0; u = sp.upper()
    if any(p in u for p in ["EP", "UTG"]): hero_idx = 0
    elif "MP" in u: hero_idx = 1
    elif "CO" in u: hero_idx = 2
    elif any(p in u for p in ["BTN", "BU"]): hero_idx = 3
    elif "SB" in u: hero_idx = 4
    elif "BB" in u: hero_idx = 5
    rot = order[hero_idx:] + order[:hero_idx]

    for i in range(1, 6):
        pos = rot[i]
        is_f = order.index(pos) < order.index(rot[0]) and not (rot[0] == "SB" and pos == "BB")
        chips = f'<div class="dealer-mob" style="{utils.get_chip_style(i)}">D</div>' if pos=="BTN" else ""
        opp_html += f'<div class="seat m-pos-{i} {"seat-folded" if is_f else ""}"><span class="seat-label">{pos}</span></div>{chips}'

    # Вставляем RNG badge рядом с картами
    hero_html = f"""
    <div class="hero-mob">
        <div class="card-mob"><div class="tl-mob {c1}">{h_val[0]}<br>{s1}</div><div class="c-mob {c1}">{s1}</div></div>
        <div class="card-mob"><div class="tl-mob {c2}">{h_val[1]}<br>{s2}</div><div class="c-mob {c2}">{s2}</div></div>
        <div class="rng-badge">{rng_val}</div>
    </div>
    """

    st.markdown(f'<div class="mobile-game-area"><div class="mob-info"><div class="mob-info-src">{src}</div><div class="mob-info-spot">{sp}</div><div class="mob-mode-tag">{mode_tag}</div></div>{opp_html}{hero_html}</div>', unsafe_allow_html=True)

    # BUTTONS
    if not st.session_state.srs_mode:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("FOLD", key="f", help="fold-btn", use_container_width=True):
                # Ошибка если надо было рейзить
                st.session_state.last_error = should_raise
                st.session_state.msg = f"✅ Correct (Freq {int(hand_weight)}% > RNG {rng_val})" if not st.session_state.last_error else f"❌ Error! Freq {int(hand_weight)}% > RNG {rng_val} -> RAISE"
                utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val[0]}{s1}{h_val[1]}{s2}", "Result": 0 if st.session_state.last_error else 1, "CorrectAction": "Fold"})
                st.session_state.srs_mode = True; st.rerun()
        with c2:
            if st.button("RAISE", key="r", help="raise-btn", use_container_width=True):
                # Ошибка если НЕ надо было рейзить
                st.session_state.last_error = not should_raise
                st.session_state.msg = f"✅ Correct (Freq {int(hand_weight)}% > RNG {rng_val})" if not st.session_state.last_error else f"❌ Error! Freq {int(hand_weight)}% <= RNG {rng_val} -> FOLD"
                utils.save_to_history({"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Spot": sp, "Hand": f"{h_val[0]}{s1}{h_val[1]}{s2}", "Result": 0 if st.session_state.last_error else 1, "CorrectAction": "Raise"})
                st.session_state.srs_mode = True; st.rerun()
        st.markdown('<script>document.querySelectorAll("button[aria-help=\'fold-btn\']").forEach(b => b.parentElement.classList.add("action-btn", "fold-btn")); document.querySelectorAll("button[aria-help=\'raise-btn\']").forEach(b => b.parentElement.classList.add("action-btn", "raise-btn"));</script>', unsafe_allow_html=True)
    else:
        # Show result
        if st.session_state.last_error:
            st.error(st.session_state.msg)
            with st.expander("Show Range", expanded=True): st.markdown(utils.render_range_matrix(full_r, st.session_state.hand), unsafe_allow_html=True)
        else:
            st.success(st.session_state.msg)

        s1, s2, s3 = st.columns(3)
        k = f"{src}_{sc}_{sp}".replace(" ","_")
        if s1.button("HARD", key="h", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'hard'); st.session_state.hand = None; st.rerun()
        if s2.button("NORM", key="n", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'normal'); st.session_state.hand = None; st.rerun()
        if s3.button("EASY", key="e", use_container_width=True): utils.update_srs_smart(k, st.session_state.hand, 'easy'); st.session_state.hand = None; st.rerun()
        st.markdown('<script>document.querySelectorAll(".stButton").forEach(b => b.classList.add("srs-btn"));</script>', unsafe_allow_html=True)
