import streamlit as st
import time
from util.helper_function import load_data


st.set_page_config(
    page_title="Group 7 Final Project",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.header("Data-Driven Fraud Detection in Credit Card Payments")
st.write("\n\n\n\n")

with st.spinner('Loading dataset, please wait...'):
    data = load_data()
    st.info('Dataset loaded!')
st.image("meme.png",  use_column_width=False)