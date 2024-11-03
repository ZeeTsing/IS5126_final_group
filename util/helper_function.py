import pandas as pd
import numpy as np
import pickle
import streamlit as st
import matplotlib.pyplot as plt

CATEGORICAL_COLS = ['merchant','category','gender','city','state', 'job']
NUMERIC_COLS = ['amt','age','distance_km']
MODELPATH = "util/model.pkl"

def haversine(lat1, lon1, lat2, lon2):
    # Radius of Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    # Distance in kilometers
    distance = R * c
    return distance

def pre_process(df , cate_cols = CATEGORICAL_COLS, numeric_cols = NUMERIC_COLS):
    """function to preprocess the dataframe of input
    input shape must be the same as the original data"""
    df['trans_datetime'] = pd.to_datetime(df.trans_date_trans_time)
    df['age'] = ((df.trans_datetime - pd.to_datetime(df.dob)).dt.days/365).round()
    df['distance_km'] = df.apply(lambda row: haversine(row['lat'],row['long'],row['merch_lat'],row['merch_long']),axis=1)

    file = open("util/dict_all.obj",'rb')
    dict_all_loaded = pickle.load(file)
    file.close()

    for col in cate_cols:
        df.replace(dict_all_loaded[col], inplace=True)

    return pd.DataFrame(df[cate_cols + numeric_cols]) , df.is_fraud

def prediction_model(modelpath=MODELPATH):
    with open(modelpath, 'rb') as f:
        model = pickle.load(f)

    return model


def calculate_fraud_rate(data, group_by_column):
    return data.groupby(group_by_column).apply(lambda x: (x['is_fraud'].sum() / len(x)) * 100)

def display_dataframe(title, data):
    st.write(title)
    st.dataframe(data)


def plot_bar_chart(data, title, xlabel, ylabel, reference_line=None, rotation=45, color="skyblue"):
    fig, ax = plt.subplots(figsize=(8, 6))
    data.plot(kind='bar', ax=ax, color=color, alpha=0.7)
    if reference_line:
        ax.axhline(y=reference_line, color='red', linestyle='--', label=f'Reference Line: {reference_line:.2f}%')
        ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    plt.xticks(rotation=rotation, fontsize=8)
    st.pyplot(fig, use_container_width=True)



@st.cache_data
def load_data():
    """Load and cache the machine learning model.
    hard coded path to read file in data folder"""
    return pd.read_csv("./util/data/credit_card_transactions.csv.bz2",compression='bz2')
    