import streamlit as st
import numpy as np
import pandas as pd
from util.helper_function import load_data

st.set_page_config(
    page_title="Behavioral Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

data = load_data()

'### Preview Dataset'
st.write(data.head(3))
f"Rows, Columns: {data.shape}"
st.write(data.is_fraud.value_counts())
'---'
'### Map Dtypes'
st.write(pd.DataFrame(data.dtypes).transpose())
'Convert CC number as string, Transaction datetime as datetime:'
data['cc_num']=data['cc_num'].astype(str)
data['trans_date_trans_time']=pd.to_datetime(data['trans_date_trans_time'])
st.write(pd.DataFrame(data.dtypes).transpose())
'---'
'### Merge Columns'
'New columns:'
'- "name" = "first" + "last"'
'- "lat_long" = "lat" , "long"'
data['name']=data['first']+' '+data['last']
data['lat_long']=list(zip(data.lat,data.long))
data['merch_lat_long']=list(zip(data.merch_lat,data.merch_long))
st.write(data.head(3))
'---'
col1,col2,col3,col4=st.columns(4)
with col1:
    '### Name vs CC Number'
    f"Unique Names: {data.name.nunique()}"
    f"Unique CC Numbers: {data.cc_num.nunique()}"
    df_name_cc=data[['name','cc_num']].drop_duplicates()
    st.warning('Some names have 2 CC numbers!')
    st.write(df_name_cc.name.value_counts())
with col2:
    '### Name vs Address (Street)'
    f"Unique Names: {data.name.nunique()}"
    f"Unique Address(Street): {data.street.nunique()}"
    df_name_street=data[['name','street']].drop_duplicates()
    st.warning('Some names have 2 addresses!')
    st.write(df_name_street.name.value_counts())
with col3:
    '### CC Number vs Address (Street)'
    f"Unique CC Numbers: {data.cc_num.nunique()}"
    f"Unique Address(Street): {data.street.nunique()}"
    df_cc_street=data[['cc_num','street']].drop_duplicates()
    st.success('Each CC Num has unique address.')
    st.write(df_cc_street.cc_num.value_counts())
with col4:
    '### Address (Street) vs Latitude & Longitude'
    f"Unique Address(Street): {data.street.nunique()}"
    f"Unique Latitude&Longitude: {data.lat_long.nunique()}"
    df_street_latlong=data[['street','lat_long']].drop_duplicates()
    st.info('Some streets has common latitude & longitude.')
    st.write(df_street_latlong.lat_long.value_counts())
'---'
data['color']=data['is_fraud'].map(lambda x:(x,1.0-x,0.0))
with st.spinner('Loading map visualisation, please wait..'):
    st.map(data,latitude='lat',longitude='long',color='color')