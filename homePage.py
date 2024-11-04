import streamlit as st
from util.helper_function import load_data

st.set_page_config(
    page_title="Group 7 Final Project",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

"# Data-Driven Fraud Detection in Credit Card Payments"
"#### IS5126 Final Project - Group 7"
col1,col2=st.columns(2)
with col1:
    with st.expander("##### Group Members"):
        "Du Hong"
        "Long Ke"
        "Seah Zuo Sheng"
        "Zhao Xinyan"
        "Zheng Zhiqing"
"---"
with st.spinner('Loading dataset, please wait...'):
    data = load_data()
    st.info('##### Dataset loaded! *Select a page on the sidebar to continue.*')
st.image("meme.png",  use_column_width=False)