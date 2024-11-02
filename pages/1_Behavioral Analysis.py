import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from scipy import stats
from util.helper_function import load_data

st.set_page_config(
    page_title="Behavioral Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


data = load_data()
# transform the date column to weekday
data["day_of_week"] = pd.to_datetime(data['trans_date_trans_time']).dt.day_name()
data["age"] = 2024 - data["dob"].apply(lambda x: int(x.split("-")[0]))
data["date"] = pd.to_datetime(data["trans_date_trans_time"]).dt.date
data["trans_hour"] = pd.to_datetime(data["trans_date_trans_time"]).dt.hour
data["timeperiod"] = data["trans_hour"].apply(
    lambda x: "morning" if 6 <= x < 12 else
              "noon" if 12 <= x < 14 else
              "afternoon" if 14 <= x < 18 else
              "evening" if 18 <= x < 22 else
              "midnight"
)

st.write("# Behavioral Analysis")
st.write("\n\n\n\n")
st.header("Conclusion")

st.write("1. Fraudulent transactions are more likely to occur consecutively.")
st.write("2. Fraudulent transactions are slightly more likely to occur on weekends.")
st.write("3. Fraudulent transactions are more likely to occur in the midnight.")
st.write("4. Fraudulent transactions are more likely to occur in online activities.")
st.write("\n\n\n")
#########1. Consecutive Transactions#########

cc_cards = data.groupby("cc_num")["is_fraud"].sum().sort_values(ascending=False).reset_index()
cc_cards.columns = ["card_number","fraud_count"]


def plot_transcation_of_card(cc_num):
    a = data[data["cc_num"] == cc_num].reset_index()
    a.sort_values("trans_date_trans_time")
    fig = go.Figure()
    
    # 添加折线图
    fig.add_trace(go.Scatter(
        x=a['trans_date_trans_time'],
        y=a['amt'],
        mode='lines',
        name='Amount'
    ))
    
    # 添加欺诈交易的红色点
    fraud_transactions = a[a['is_fraud'] == True]
    fig.add_trace(go.Scatter(
        x=fraud_transactions['trans_date_trans_time'],
        y=fraud_transactions['amt'],
        mode='markers',
        marker=dict(color='red'),
        name='Fraud'
    ))
    
    # 添加标题和标签
    fig.update_layout(
        title='Transaction Amount Over Time',
        xaxis_title='Time',
        yaxis_title='Amount',
        legend_title='Legend'
    )
    
    return fig


col1, col2 = st.columns([1,2])
with col1:
    st.dataframe(cc_cards)
with col2:
    cc_num = st.selectbox("Select a credit card number", cc_cards["card_number"])
    st.plotly_chart(plot_transcation_of_card(cc_num))
st.write("\n\n\n\n")


st.dataframe(data[data["cc_num"] == cc_num])

#########2. Day of Week#########
days_distribution = data.groupby("day_of_week")["is_fraud"].sum().reset_index()
days_distri_bar = go.Figure()
colors = ['rgb(55, 83, 109)' if day not in ['Saturday', 'Sunday'] else 'red' for day in days_distribution["day_of_week"]]

days_distri_bar.add_trace(go.Bar(
    x=days_distribution["day_of_week"],
    y=days_distribution["is_fraud"],
    marker_color=colors
))
days_distri_bar.update_layout(
    title_text="Fraudulent Transactions by Day of Week",
    xaxis_title="Day of Week",
    yaxis_title="Number of Fraudulent Transactions",
    yaxis=dict(range=[0, 2000])
)
st.plotly_chart(days_distri_bar, use_container_width=True)



# 获取欺诈交易的类别数据并计数
fraud_data = data[data["is_fraud"] == 1]
cat_data = fraud_data.groupby("category")["amt"].agg(total_amount="sum", average_amount="mean",count="size").reset_index()
cat_data = cat_data.sort_values(by="total_amount", ascending=False)

#######3. Time Period#########

time_period = data.groupby("timeperiod")["is_fraud"].sum().reset_index()
time_period_bar = go.Figure()
time_period_bar.add_trace(go.Bar(
    x=time_period["timeperiod"],
    y=time_period["is_fraud"],
    marker_color=['rgb(55, 83, 109)' if day not in ["midnight"] else 'red' for day in time_period["timeperiod"]]
))
time_period_bar.update_layout(
    title_text="Fraudulent Transactions by Time Period",
    xaxis_title="Time Period",
    yaxis_title="Number of Fraudulent Transactions",
    yaxis=dict(range=[0, 2000]),
    xaxis=dict(categoryorder='array', categoryarray=["morning", "noon", "afternoon", "evening", "midnight"])

)
st.plotly_chart(time_period_bar, use_container_width=True)

#########4. Category#########

col4_1,col4_2 = st.columns([1,2])
cat_pie = go.Figure()   
cat_pie.add_trace(go.Pie(
    labels=cat_data["category"],
    values=cat_data["count"],
    hole=0.3
))
cat_pie.update_layout(
    title_text="Fraudulent Transactions by Category"
)
cat_pie.update_layout(
    width=800,
    height=600
)



cat_bar = go.Figure()
# 添加总金额的条形图
cat_bar.add_trace(go.Bar(
    x=cat_data["category"],
    y=cat_data["total_amount"],
    name='Total Amount',
    yaxis='y1'
))
# 添加平均金额的折线图
cat_bar.add_trace(go.Scatter(
    x=cat_data["category"],
    y=cat_data["average_amount"],
    name='Average Amount',
    yaxis='y2',
    mode='lines+markers',
    line=dict(color='orange')
))

# 更新布局
cat_bar.update_layout(
    title_text="Fraudulent Transactions by Category",
    xaxis_title="Category",
    yaxis=dict(
        title="Total Amount",
        titlefont=dict(color="#1f77b4"),
        tickfont=dict(color="#1f77b4"),
        side="left"
    ),
    yaxis2=dict(
        title="Average Amount",
        titlefont=dict(color="orange"),
        tickfont=dict(color="orange"),
        overlaying="y",
        side="right"
    ),
    legend=dict(
        x=0.8,
        y=0.95,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    )
)
cat_bar.update_layout(
    width=800,
    height=600
)

with col4_1:
    st.plotly_chart(cat_pie, use_container_width=True)

with col4_2:
    st.plotly_chart(cat_bar, use_container_width=True)
