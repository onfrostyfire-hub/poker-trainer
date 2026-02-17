import streamlit as st
import utils

def select_hierarchy_collapsible(ranges_db, suffix, emoji):
    """
    Рисует настройки выбора ренджа внутри Expander.
    Заголовок Expander меняется динамически в зависимости от выбора.
    """
    # 1. Пытаемся достать текущие значения из Session State, чтобы сформировать красивый заголовок
    # Ключи виджетов: src_A, sc_A, sp_A
    cur_src = st.session_state.get(f"src_{suffix}")
    cur_sc = st.session_state.get(f"sc_{suffix}")
    cur_sp = st.session_state.get(f"sp_{suffix}")

    # Формируем заголовок
    if cur_sp and cur_sc:
        # Если выбрано: "🅰️ Def vs 3bet: EP vs MP"
        # Сокращаем текст, чтобы влезало на мобилу
        short_sc = cur_sc.replace("Def vs 3bet", "Def 3B").replace("Open Raise", "OR")
        header_label = f"{emoji} {short_sc} ➝ {cur_sp}"
    else:
        header_label = f"{emoji} Select Range..."

    # 2. Рисуем Expander
    with st.expander(header_label, expanded=False):
        # Source
        src_options = list(ranges_db.keys())
        # Логика default index чтобы не сбрасывалось
        idx_src = 0
        if cur_src in src_options: idx_src = src_options.index(cur_src)
        
        src = st.selectbox(f"Source", src_options, key=f"src_{suffix}", index=idx_src)
        
        # Scenario
        sc_options = list(ranges_db[src].keys()) if src else []
        idx_sc = 0
        if cur_sc in sc_options: idx_sc = sc_options.index(cur_sc)
        
        sc = st.selectbox(f"Scenario", sc_options, key=f"sc_{suffix}", index=idx_sc)
        
        # Spot
        sp_options = []
        if src and sc:
            sp_options = list(ranges_db[src][sc].keys())
        idx_sp = 0
        if cur_sp in sp_options: idx_sp = sp_options.index(cur_sp)
            
        sp = st.selectbox(f"Spot", sp_options, key=f"sp_{suffix}", index=idx_sp)

    # 3. Возвращаем данные для отрисовки
    if src and sc and sp:
        return ranges_db[src][sc][sp]
    return None

def show():
    st.markdown("## 🔬 Range Lab")
    
    ranges_db = utils.load_ranges()
    if not ranges_db:
        st.error("No ranges found")
        return

    # CSS
    st.markdown("""
    <style>
        .block-container { padding-top: 3rem; }
        /* Убираем лишние отступы внутри экспандера */
        .streamlit-expanderContent { padding-top: 0px !important; }
        /* Стили для контейнера матрицы */
        .range-container {
            background: #222;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 15px;
        }
        .legend-text {
            font-size: 11px; color: #aaa; text-align: center; margin-top: 5px; font-family: monospace;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # --- RANGE A ---
    with col1:
        data_a = select_hierarchy_collapsible(ranges_db, "A", "🅰️")
        
        if data_a:
            st.markdown('<div class="range-container">', unsafe_allow_html=True)
            st.markdown(utils.render_range_matrix(data_a), unsafe_allow_html=True)
            
            # Легенда
            if "call" in data_a:
                st.markdown('<div class="legend-text">🟢Call 🔴4Bet</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="legend-text">🟢Open Raise</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👆 Pick Range A")

    # --- RANGE B ---
    with col2:
        data_b = select_hierarchy_collapsible(ranges_db, "B", "🅱️")
        
        if data_b:
            st.markdown('<div class="range-container">', unsafe_allow_html=True)
            st.markdown(utils.render_range_matrix(data_b), unsafe_allow_html=True)
            
            if "call" in data_b:
                st.markdown('<div class="legend-text">🟢Call 🔴4Bet</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="legend-text">🟢Open Raise</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👆 Pick Range B")
