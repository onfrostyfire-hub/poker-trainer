import streamlit as st
import utils

def select_hierarchy_collapsible(ranges_db, suffix, emoji):
    """
    Рисует настройки выбора ренджа внутри Expander.
    Заголовок Expander меняется динамически в зависимости от выбора.
    """
    # Достаем текущие значения из стейта
    cur_src = st.session_state.get(f"src_{suffix}")
    cur_sc = st.session_state.get(f"sc_{suffix}")
    cur_sp = st.session_state.get(f"sp_{suffix}")

    # Формируем умный заголовок
    if cur_sp and cur_sc:
        # Сокращаем названия для мобилы
        short_sc = cur_sc.replace("Def vs 3bet", "Def 3B").replace("Open Raise", "OR")
        header_label = f"{emoji} {short_sc} ➝ {cur_sp}"
    else:
        header_label = f"{emoji} Выбрать рендж..."

    # Рисуем Шторку
    with st.expander(header_label, expanded=False):
        # 1. Source
        src_options = list(ranges_db.keys())
        idx_src = src_options.index(cur_src) if cur_src in src_options else 0
        src = st.selectbox(f"Source", src_options, key=f"src_{suffix}", index=idx_src)
        
        # 2. Scenario
        sc_options = list(ranges_db[src].keys()) if src else []
        idx_sc = sc_options.index(cur_sc) if cur_sc in sc_options else 0
        sc = st.selectbox(f"Scenario", sc_options, key=f"sc_{suffix}", index=idx_sc)
        
        # 3. Spot
        sp_options = []
        if src and sc:
            sp_options = list(ranges_db[src][sc].keys())
        idx_sp = sp_options.index(cur_sp) if cur_sp in sp_options else 0
        sp = st.selectbox(f"Spot", sp_options, key=f"sp_{suffix}", index=idx_sp)

    # Возвращаем данные
    if src and sc and sp:
        return ranges_db[src][sc][sp]
    return None

def show():
    # --- CSS: Убираем полосы и отступы ---
    st.markdown("""
    <style>
        /* Подтягиваем контент наверх */
        .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
        
        /* Стили для контейнера матрицы (без лишних рамок) */
        .range-container {
            margin-bottom: 15px;
        }
        
        /* Легенда под матрицей */
        .legend-text {
            font-size: 10px; color: #888; text-align: center; margin-top: 2px; font-family: monospace;
        }
        
        /* Убираем отступы внутри шторки */
        .streamlit-expanderContent { padding-bottom: 10px !important; }
    </style>
    """, unsafe_allow_html=True)
    
    ranges_db = utils.load_ranges()
    if not ranges_db:
        st.error("No ranges found")
        return

    # Две колонки (на мобиле встанут одна под другой)
    col1, col2 = st.columns(2)

    # --- RANGE A ---
    with col1:
        data_a = select_hierarchy_collapsible(ranges_db, "A", "🅰️")
        
        if data_a:
            st.markdown('<div class="range-container">', unsafe_allow_html=True)
            # Рисуем матрицу (используем универсальный рендер из utils)
            st.markdown(utils.render_range_matrix(data_a), unsafe_allow_html=True)
            
            # Легенда
            if "call" in data_a:
                st.markdown('<div class="legend-text">🟢Call 🔴4Bet</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="legend-text">🟢Open Raise</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("👆 Выбери Range A")

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
            st.info("👆 Выбери Range B")
