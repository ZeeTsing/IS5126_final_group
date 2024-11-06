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

'### Identity and Geospatial Analysis'
data['name']=data['first']+' '+data['last']
data['cc_num']=data['cc_num'].astype(str)
data['trans_date_trans_time']=pd.to_datetime(data['trans_date_trans_time'])
data['lat_long']=list(zip(data.lat,data.long))
data['merch_lat_long']=list(zip(data.merch_lat,data.merch_long))

tab1,tab2,tab3,tab4=st.tabs(['Name vs CC','Name vs Address','CC vs Address/Geolocation','Geospatial Analysis'])
with tab1:
    '### Name vs CC Number'
    col1a,col1b=st.columns(2)
    with col1a:
        f"Unique Names: {data.name.nunique()}"
        f"Unique CC Numbers: {data.cc_num.nunique()}"
        df_name_cc=data[['name','cc_num']].drop_duplicates()
        df_name_cc2=df_name_cc.name.value_counts().reset_index().rename(columns={'index':'name','name':'cc_num'})
        st.warning('Some names have 2 CC numbers!')
        st.write(df_name_cc2)
    with col1b:
        name = st.selectbox("Select name to check CC:", df_name_cc2['name'],index=None)
        if name:
            st.write(df_name_cc[df_name_cc['name']==name])
with tab2:
    '### Name vs Address (Street)'
    col2a,col2b=st.columns(2)
    with col2a:
        f"Unique Names: {data.name.nunique()}"
        f"Unique Address(Street): {data.street.nunique()}"
        df_name_street=data[['name','street']].drop_duplicates()
        df_name_street2=df_name_street.name.value_counts().reset_index().rename(columns={'index':'name','name':'street'})
        st.warning('Some names have 2 addresses!')
        st.write(df_name_street2)
    with col2b:
        name = st.selectbox("Select name to check address:", df_name_street2['name'],index=None)
        if name:
            st.write(df_name_street[df_name_street['name']==name])
with tab3:
    col3a,col3b=st.columns(2)
    with col3a:
        '### CC Number vs Address (Street)'
        f"Unique CC Numbers: {data.cc_num.nunique()}"
        f"Unique Address(Street): {data.street.nunique()}"
        df_cc_street=data[['cc_num','street']].drop_duplicates()
        df_cc_street2=df_cc_street.cc_num.value_counts().reset_index().rename(columns={'index':'cc_num','cc_num':'street'})
        st.success('Each CC Num has unique address.')
        st.write(df_cc_street2)
    with col3b:
        '### Address (Street) vs Geolocation'
        f"Unique Address(Street): {data.street.nunique()}"
        f"Unique Latitude&Longitude: {data.lat_long.nunique()}"
        df_street_latlong=data[['street','lat_long']].drop_duplicates()
        df_street_latlong2=df_street_latlong.lat_long.value_counts().reset_index().rename(columns={'index':'geolocation','lat_long':'street'})
        st.info('Some streets has common latitude & longitude.')
        st.write(df_street_latlong2)
with tab4:
    '### Geospatial Analysis'
    cc = st.selectbox("Select CC:", df_name_cc['cc_num'].sort_values(),index=None)
    if cc:
        col4a,col4b=st.columns(2)
        with col4a:
            street=df_cc_street[df_cc_street['cc_num']==cc].iloc[0,1]
            f"**Name:** {df_name_cc[df_name_cc['cc_num']==cc].iloc[0,0]}"
            f"**Address (Street):** {street}"
            "*Map Legend: Blue = Address, Green = Merchant, Red = Fraud*"
            geo=df_street_latlong[df_street_latlong['street']==street].iloc[0,1]
            df_locs=data[data['cc_num']==cc][['merch_lat','merch_long','is_fraud']]
        with col4b:
            "**Transactions:**"
            trans_count=df_locs['is_fraud'].value_counts()
            trans_count.index=trans_count.index.map({0:'not fraud',1:'is fraud'})
            trans_count.rename('Count',inplace=True)
            st.write(trans_count)
        df_locs['color']=df_locs['is_fraud'].map(lambda x:(255*(x),255*(1-x),0))
        df_locs.loc[-1] = [geo[0], geo[1], 0, (0,0,255)]
        with st.spinner('Loading map visualisation, please wait..'):
            st.map(df_locs,latitude='merch_lat',longitude='merch_long',color='color')