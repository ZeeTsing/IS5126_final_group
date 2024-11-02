import streamlit as st
import pandas as pd
from util.helper_function import pre_process, prediction_model

# Set up the Streamlit app
st.title("Fraud batch Prediction")
st.write("Upload transaction records: ")

uploaded_file = st.file_uploader(
    "Choose a CSV file", accept_multiple_files=False
)

target_dict = {0:"Not Fraud",1:"Fraud"}

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("file uploaded successfully:", uploaded_file.name)
    st.write(df)
    X_pred, truth = pre_process(df)

    model = prediction_model()

    y_pred = model.predict(X_pred)
    st.write("Here is our prediction: ",[target_dict[y] for y in y_pred], "Here is the truth: ", [target_dict[y] for y in truth.values])
