import streamlit as st
import views.mobile
import views.desktop
import views.compare
import views.stats
import utils

# Настройка страницы
st.set_page_config(page_title="Poker Trainer", layout="wide", initial_sidebar_state="collapsed")

def main():
    # Я УБРАЛ СТРОКУ, КОТОРАЯ СКРЫВАЛА МЕНЮ
    
    with st.sidebar:
        st.title("Poker Trainer")
        
        # Главное меню
        app_mode = st.radio("Menu", ["🎮 Trainer", "🔬 Range Lab", "📊 Statistics"])
        
        st.markdown("---")
        
        # Выбор вида (только для режима Тренера)
        view_type = "Mobile"
        if app_mode == "🎮 Trainer":
            view_type = st.radio("View Mode", ["Mobile", "Desktop"], index=0)

    # Роутинг (переключение страниц)
    if app_mode == "🔬 Range Lab":
        views.compare.show()
        
    elif app_mode == "📊 Statistics":
        views.stats.show()
        
    else:
        # TRAINER MODE
        if view_type == "Mobile":
            views.mobile.show()
        else:
            views.desktop.show()

if __name__ == "__main__":
    main()
