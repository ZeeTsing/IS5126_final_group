import streamlit as st

# Set up the Streamlit app
st.title("Fraud batch Prediction")
st.write("Upload transaction records: ")

uploaded_file = st.file_uploader(
    "Choose a CSV file", accept_multiple_files=False
)

bytes_data = uploaded_file.read()
st.write("filename:", uploaded_file.name)
st.write(bytes_data)
