import streamlit as st
import utils

def render_selector(ranges_db, suffix, emoji):
    """
    Рисует шторку (Expander) для выбора ренджа.
    """
    # Формируем ключ для уникальности
    k_src = f"src_{suffix}"
    k_sc = f"sc_{suffix}"
    k_sp = f"sp_{suffix}"

    # Получаем текущие значения (чтобы написать их в заголовке шторки)
    curr_src = st.session_state.get(k_src)
    curr_sc = st.session_state.get(k_sc)
    curr_sp = st.session_state.get(k_sp)

    # Заголовок шторки
    if curr_sp and curr_sc:
        # Сокращаем длинные названия для мобилы
        short = curr_sc.replace("Def vs 3bet", "Def3B").replace("Open Raise", "OR")
        label = f"{emoji} {short} ➝ {curr_sp}"
    else:
        label = f"{emoji} Выбрать рендж..."

    # Рисуем шторку
    with st.expander(label, expanded=False):
        # 1. Source
        opts_src = list(ranges_db.keys())
        # Индекс по умолчанию (защита от сброса)
        idx_src = 0
        if curr_src in opts_src: idx_src = opts_src.index(curr_src)
        src = st.selectbox("Source", opts_src, key=k_src, index=idx_src)

        # 2. Scenario
        opts_sc = list(ranges_db[src].keys()) if src else []
        idx_sc = 0
        if curr_sc in opts_sc: idx_sc = opts_sc.index(curr_sc)
        sc = st.selectbox("Scenario", opts_sc, key=k_sc, index=idx_sc)

        # 3. Spot
        opts_sp = []
        if src and sc: opts_sp = list(ranges_db[src][sc].keys())
        idx_sp = 0
        if curr_sp in opts_sp: idx_sp = opts_sp.index(curr_sp)
        sp = st.selectbox("Spot", opts_sp, key=k_sp, index=idx_sp)

    # Возвращаем данные ренджа
    if src and sc and sp:
        return ranges_db[src][sc][sp]
    return None

def show():
    # --- CSS: УБИРАЕМ ОТСТУПЫ И ПОЛОСЫ ---
    st.markdown("""
        <style>
            /* Убираем гигантский отступ сверху */
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 2rem !important;
            }
            /* Скрываем стандартный хедер Streamlit (полосу меню), если она мешает */
            header {visibility: hidden;}
            
            /* Компактный контейнер для матрицы */
            .range-box {
                margin-top: 5px;
                margin-bottom: 20px;
                padding: 0px;
            }
            /* Текст легенды */
            .legend {
                font-family: monospace;
                font-size: 10px;
                color: #888;
                text-align: center;
                margin-top: 2px;
            }
            /* Уменьшаем отступы внутри экспандера */
            .streamlit-expanderContent {
                padding-top: 0rem !important;
                padding-bottom: 1rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### 🔬 Range Lab v2.0")

    ranges_db = utils.load_ranges()
    if not ranges_db:
        st.error("No ranges found")
        return

    # ДВЕ КОЛОНКИ
    col1, col2 = st.columns(2)

    # --- ЛЕВАЯ КОЛОНКА (A) ---
    with col1:
        data_a = render_selector(ranges_db, "A", "🅰️")
        if data_a:
            st.markdown('<div class="range-box">', unsafe_allow_html=True)
            st.markdown(utils.render_range_matrix(data_a), unsafe_allow_html=True)
            if "call" in data_a: st.markdown('<div class="legend">🟢Call 🔴4Bet</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="legend">🟢Open Raise</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # --- ПРАВАЯ КОЛОНКА (B) ---
    with col2:
        data_b = render_selector(ranges_db, "B", "🅱️")
        if data_b:
            st.markdown('<div class="range-box">', unsafe_allow_html=True)
            st.markdown(utils.render_range_matrix(data_b), unsafe_allow_html=True)
            if "call" in data_b: st.markdown('<div class="legend">🟢Call 🔴4Bet</div>', unsafe_allow_html=True)
            else: st.markdown('<div class="legend">🟢Open Raise</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
