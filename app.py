import streamlit as st
import views.mobile
import views.desktop

st.set_page_config(page_title="GTO Pro", page_icon="♠️", layout="wide", initial_sidebar_state="collapsed")

# Простой переключатель для теста (потом сделаем авто-детект)
# На телефоне сайдбар скрыт, так что это не помешает.
# Но мы можем добавить query param ?view=mobile

query_params = st.query_params
view_mode = query_params.get("view", "mobile") # По дефолту Mobile для тебя сейчас

if view_mode == "mobile":
    views.mobile.show()
elif view_mode == "desktop":
    views.desktop.show()
else:
    views.mobile.show()

# Внизу страницы добавим ссылку для переключения (для дебага)
st.markdown("---")
if view_mode == "mobile":
    if st.button("Switch to Desktop View"):
        st.query_params["view"] = "desktop"
        st.rerun()
else:
    if st.button("Switch to Mobile View"):
        st.query_params["view"] = "mobile"
        st.rerun()
