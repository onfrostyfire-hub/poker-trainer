import streamlit as st
import utils

def select_hierarchy(ranges_db, key_suffix, default_src=None):
    """Помощник для выбора ренджа (Source -> Scenario -> Spot)"""
    
    # 1. Source
    src_options = list(ranges_db.keys())
    src = st.selectbox(f"Source {key_suffix}", src_options, key=f"src_{key_suffix}")
    
    # 2. Scenario
    sc_options = list(ranges_db[src].keys()) if src else []
    sc = st.selectbox(f"Scenario {key_suffix}", sc_options, key=f"sc_{key_suffix}")
    
    # 3. Spot
    sp_options = []
    if src and sc:
        sp_options = list(ranges_db[src][sc].keys())
    sp = st.selectbox(f"Spot {key_suffix}", sp_options, key=f"sp_{key_suffix}")
    
    # Return data
    if src and sc and sp:
        return ranges_db[src][sc][sp], f"{src} > {sc} > {sp}"
    return None, None

def show():
    st.markdown("## 🔬 Range Lab")
    
    # Загружаем базу
    ranges_db = utils.load_ranges()
    if not ranges_db:
        st.error("No ranges found in ranges.json")
        return

    # CSS для компактности
    st.markdown("""
    <style>
        .block-container { padding-top: 3rem; }
        /* Убираем лишние отступы у заголовков селектов */
        .stSelectbox label { font-size: 12px; font-weight: bold; color: #ffc107; }
        /* Рамка вокруг вьюверов */
        .range-box { border: 1px solid #444; padding: 10px; border-radius: 8px; background: #222; margin-bottom: 20px; }
        .range-title { text-align: center; font-weight: bold; margin-bottom: 10px; color: #fff; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

    # ДВЕ КОЛОНКИ
    col1, col2 = st.columns(2)

    # --- ЛЕВЫЙ РЕНДЖ (Range A) ---
    with col1:
        st.markdown('<div class="range-box">', unsafe_allow_html=True)
        st.markdown('<div class="range-title">🅰️ RANGE A</div>', unsafe_allow_html=True)
        
        data_a, name_a = select_hierarchy(ranges_db, "A")
        
        if data_a:
            # Рисуем матрицу
            st.markdown(utils.render_range_matrix(data_a), unsafe_allow_html=True)
            
            # Показываем легенду (какие веса есть)
            if "call" in data_a:
                st.caption(f"🟢 Call / 🔴 4Bet (Defense)")
            elif "full" in data_a:
                st.caption(f"🟢 Open Raise")
        else:
            st.info("Select Spot A")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ПРАВЫЙ РЕНДЖ (Range B) ---
    with col2:
        st.markdown('<div class="range-box">', unsafe_allow_html=True)
        st.markdown('<div class="range-title">🅱️ RANGE B</div>', unsafe_allow_html=True)
        
        data_b, name_b = select_hierarchy(ranges_db, "B")
        
        if data_b:
            st.markdown(utils.render_range_matrix(data_b), unsafe_allow_html=True)
            
            if "call" in data_b:
                st.caption(f"🟢 Call / 🔴 4Bet (Defense)")
            elif "full" in data_b:
                st.caption(f"🟢 Open Raise")
        else:
            st.info("Select Spot B")
        st.markdown('</div>', unsafe_allow_html=True)
