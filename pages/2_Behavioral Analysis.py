import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from scipy import stats
from util.helper_function import load_data
import plotly.express as px

st.set_page_config(
    page_title="Behavioral Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


## data processing
data = load_data()
data['cc_num']=data['cc_num'].astype(str)

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
is_fraud = data[data["is_fraud"]==1]
not_fraud = data[data["is_fraud"]==0]
# 计算男女的欺诈交易比例
fraud_counts = data[data["is_fraud"] == 1].groupby("gender").size()
total_counts = data.groupby("gender").size()
fraud_ratio = fraud_counts / total_counts
# 将数据转换为DataFrame以便于绘图
fraud_ratio_df = fraud_ratio.reset_index()
fraud_ratio_df.columns = ['gender', 'fraud_ratio']
tab1, tab2 = st.tabs(["Behavioral","Customer"])



with tab1:
    st.write("## Behavioral Analysis")
    st.write("\n\n\n\n")
    st.header("Conclusion")

    st.write("1. Fraudulent transactions are more likely to occur consecutively.\n2. Fraudulent transactions are slightly more likely to occur on weekends.\n3. Fraudulent transactions are more likely to occur in the midnight.\n4. Fraudulent transactions are more likely to occur in online activities.")

    st.write("\n\n\n")
    #########1. Consecutive Transactions#########
    st.write("### Consecutive Transactions")
    st.write("The table below displays the credit card numbers with the highest number of consecutive transactions. The line plot highlights the exact times when fraud occurs, marked with red dots. ")
    st.write("The chart highlights that fraudulent transactions often appear clustered within a short period This visual pattern is consistent with scenarios involving card theft or unauthorized use, where fraudsters rapidly perform a series of transactions to take advantage of the card before it is reported or blocked. The cluster of red markers indicates consecutive high-value transactions, suggesting that once a fraudster gains access, they act quickly to maximize their illicit use before detection systems or cardholder intervention halt further activity.")
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
        st.markdown("**Card Number and total fraud count**")
        st.dataframe(cc_cards)
    with col2:
        cc_num = st.selectbox("Select a credit card number", cc_cards["card_number"])
        st.plotly_chart(plot_transcation_of_card(cc_num))
    st.write("\n\n\n\n")

    st.write("The following table shows the detailed transactions of the selected credit card number.")
    fraud_data = data[(data["cc_num"] == cc_num) & (data["is_fraud"] == 1)]
    st.dataframe(fraud_data)



    #########2. Day of Week#########
    st.write("### Fraudulent Transactions by Day of Week")
    st.write("The bar chart below shows the number of fraudulent transactions that occur on each day of the week. The chart highlights that fraudulent transactions are more likely to occur on weekends, with Sunday having the highest number of fraudulent transactions. This pattern may be due to reduced monitoring or oversight on weekends, making it easier for fraudsters to exploit vulnerabilities in the system.")
    days_distribution = data.groupby("day_of_week")["is_fraud"].sum().reset_index()
    days_distri_bar = go.Figure()
    colors = ['rgb(55, 83, 109)' if day not in ['Saturday', 'Sunday'] else 'red' for day in days_distribution["day_of_week"]]

    days_distri_bar.add_trace(go.Bar(
        x=days_distribution["day_of_week"],
        y=days_distribution["is_fraud"],
        marker_color=colors
    ))
    days_distri_bar.add_hline(y=1216, line_dash="dot", line_color="blue", annotation_text="Sunday", annotation_position="bottom right")
    days_distri_bar.update_layout(
        title_text="Fraudulent Transactions by Day of Week",
        xaxis_title="Day of Week",
        yaxis_title="Number of Fraudulent Transactions",
        yaxis=dict(range=[0, 2000]),
        xaxis=dict(categoryorder='array', categoryarray=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

    )
    st.plotly_chart(days_distri_bar, use_container_width=True)



    # 获取欺诈交易的类别数据并计数
    fraud_data = data[data["is_fraud"] == 1]
    cat_data = fraud_data.groupby("category")["amt"].agg(total_amount="sum", average_amount="mean",count="size").reset_index()
    cat_data = cat_data.sort_values(by="total_amount", ascending=False)

    #######3. Time Period#########
    st.write("### Fraudulent Transactions by Time Period")
    st.write("The chart clearly illustrates that the highest number of fraudulent transactions occur during the midnight period, with a substantial spike compared to other time periods like morning, noon, afternoon, and evening. This pattern suggests that fraudsters prefer late-night hours for their activities, likely because it is a time when cardholders and financial institutions are less active. During these hours, individuals are often asleep, reducing the chance of immediate detection or transaction verification by cardholders.")
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
    st.write("### Fraudulent Transactions by Category")

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


    st.plotly_chart(cat_pie, use_container_width=True)
    st.plotly_chart(cat_bar, use_container_width=True)


    st.write("### Fraudulent Transactions by Amount")
    # 创建重叠的直方图
    amt_distribution = go.Figure()


    # 添加欺诈交易的直方图
    amt_distribution.add_trace(go.Histogram(
        x=is_fraud["amt"],
        histnorm='probability density',
        name='Fraud',
        marker_color='red',
        opacity=0.5
    ))

    # 添加非欺诈交易的直方图
    amt_distribution.add_trace(go.Histogram(
        x=not_fraud["amt"],
        histnorm='probability density',
        name='Non-Fraud',
        marker_color='green',
        opacity=0.5
    ))

    # 更新布局
    amt_distribution.update_layout(
        title_text='Amount Distribution',
        xaxis_title_text='Amount',
        yaxis_title_text='Density',
        barmode='overlay'
    )
    amt_distribution.update_xaxes(range=[0,1500])
    st.plotly_chart(amt_distribution)

with tab2:
    st.header("## Customer Segmentation")
    st.write("Our goal is to segment customers based on their spending behavior, age, trends, and geographic locations. This segmentation will enable customized marketing strategies and personalized offers to boost customer engagement. To achieve this, we will utilize a subset of data known as the 'df' dataset.")
    


    gender_pie = px.pie(fraud_ratio_df, names='gender', values='fraud_ratio', title='Fraud Transaction Ratio by Gender')
    st.plotly_chart(gender_pie)
    

    # 创建重叠的直方图
    age_distribution = go.Figure()

    # 添加欺诈交易的直方图
    age_distribution.add_trace(go.Histogram(
        x=is_fraud["age"],
        histnorm='probability density',
        name='Fraud',
        marker_color='red',
        opacity=0.5
    ))

    # 添加非欺诈交易的直方图
    age_distribution.add_trace(go.Histogram(
        x=not_fraud["age"],
        histnorm='probability density',
        name='Non-Fraud',
        marker_color='green',
        opacity=0.5
    ))

    # 更新布局
    age_distribution.update_layout(
        title_text='Age Distribution',
        xaxis_title_text='Age',
        yaxis_title_text='Density',
        barmode='overlay'
    )

    st.plotly_chart(age_distribution)

    
