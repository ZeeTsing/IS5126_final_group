import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.figure_factory as ff
from datetime import datetime
from util.helper_function import load_data, calculate_fraud_rate, display_dataframe, plot_bar_chart

# 加载数据
data = load_data()

# 计算整体欺诈率
total_fraud_rate = (data['is_fraud'].sum() / len(data)) * 100

# 左右布局
st.title("Statistical Analysis")
st.header("Fraud Rate by Amount & Category")
colA_1,colA_2=st.columns([1,2])
fig1, ax1 = plt.subplots(figsize=(3, 6))
ax1.scatter(data['is_fraud'], data['amt'], alpha=0.5)
ax1.set_ylabel("Transaction Amount (amt)")
ax1.set_xlabel("Is Fraud (0 = No, 1 = Yes)")
ax1.set_title("Fraud Distribution by Amount")
ax1.set_yscale('log')
#ax1.set_yticks(np.arange(0, data['amt'].max() + 1500, 1500))
ax1.set_xticks([0,1])
plt.xticks(rotation=45, fontsize=8)
with colA_1:
    st.pyplot(fig1, use_container_width=True)

category_fraud_rate = calculate_fraud_rate(data, 'category').sort_values(ascending=False)
with colA_2:
    plot_bar_chart(category_fraud_rate, "Fraud Rate by Category", "Category", "Fraud Rate (%)",
                reference_line=total_fraud_rate)
'---'

# Merchant Fraud Analysis
st.header("Fraud Rate by Merchant")
colB_1,colB_2=st.columns(2)
merchant_fraud_rate = calculate_fraud_rate(data, 'merchant').sort_values(ascending=False)
mean_merchant_fraud_rate = merchant_fraud_rate.mean()
std_merchant_fraud_rate = merchant_fraud_rate.std()
merchant_threshold = mean_merchant_fraud_rate + 3 * std_merchant_fraud_rate

# 绘制 merchant 的欺诈率图表
with colB_1:
    plot_bar_chart(merchant_fraud_rate, "Fraud Rate by Merchant Overview", "Merchant", "Fraud Rate (%)",
                reference_line=total_fraud_rate)

# 筛选高风险商户
high_risk_merchants = merchant_fraud_rate[merchant_fraud_rate > merchant_threshold].index
high_risk_transactions = data[data['merchant'].isin(high_risk_merchants)]
summary_table = high_risk_transactions.groupby('merchant').agg(
    Total_Amount=('amt', 'sum'),
    Fraud_Amount=('amt', lambda x: x[high_risk_transactions['is_fraud'] == 1].sum()),
    Total_Transactions=('amt', 'count'),
    Fraud_Transactions=('is_fraud', 'sum')
).reset_index()
summary_table['Fraud Rate (%)'] = (summary_table['Fraud_Transactions'] / summary_table['Total_Transactions']) * 100
with colB_2:
    plot_bar_chart(summary_table.set_index('merchant')['Fraud Rate (%)'], "Fraud Rate by High-Risk Merchants", "Merchant",
                "Fraud Rate (%)", reference_line=merchant_threshold)
display_dataframe("Detailed Transactions for High-Risk Merchants", summary_table)
'---'

# Last Name Fraud Analysis
st.header("Fraud Rate by Name & Gender")
colC_1,colC_2=st.columns(2)
last_fraud_rate = calculate_fraud_rate(data, 'last')
last_threshold = last_fraud_rate.mean() + 3 * last_fraud_rate.std()
high_risk_last_names = last_fraud_rate[last_fraud_rate > last_threshold].index
high_risk_last_transactions = data[data['last'].isin(high_risk_last_names)]
last_summary_table = high_risk_last_transactions.groupby(['last', 'first', 'cc_num']).agg(
    Total_Amount=('amt', 'sum'),
    Fraud_Amount=('amt', lambda x: x[high_risk_last_transactions['is_fraud'] == 1].sum()),
    Total_Transactions=('amt', 'count'),
    Fraud_Transactions=('is_fraud', 'sum')
).reset_index()
last_summary_table['Fraud Rate (%)'] = (last_summary_table['Fraud_Transactions'] / last_summary_table[
    'Total_Transactions']) * 100
with colC_1:
    plot_bar_chart(last_summary_table.set_index('last')['Fraud Rate (%)'], "Fraud Rate by High-Risk Last Names",
                "Last Name", "Fraud Rate (%)", reference_line=last_threshold)
display_dataframe("Detailed Transactions for High-Risk Last Names", last_summary_table)

# Gender Fraud Analysis
gender_fraud_rate = calculate_fraud_rate(data, 'gender')
with colC_2:
    plot_bar_chart(gender_fraud_rate, "Fraud Rate by Gender", "Gender", "Fraud Rate (%)")
'---'

# City Fraud Analysis
st.header("Fraud Rate by City")
colD_1,colD_2=st.columns(2)
city_fraud_rate = calculate_fraud_rate(data, 'city')
city_threshold = city_fraud_rate.mean() + 3 * city_fraud_rate.std()
high_risk_cities = city_fraud_rate[city_fraud_rate > city_threshold].index
high_risk_city_transactions = data[data['city'].isin(high_risk_cities)]
city_summary_table = high_risk_city_transactions.groupby(['city', 'first', 'last']).agg(
    Total_Amount=('amt', 'sum'),
    Fraud_Amount=('amt', lambda x: x[high_risk_city_transactions['is_fraud'] == 1].sum()),
    Total_Transactions=('amt', 'count'),
    Fraud_Transactions=('is_fraud', 'sum')
).reset_index()
city_summary_table['Fraud Rate (%)'] = (city_summary_table['Fraud_Transactions'] / city_summary_table[
    'Total_Transactions']) * 100
with colD_1:
    plot_bar_chart(city_summary_table.set_index('city')['Fraud Rate (%)'], "Fraud Rate by High-Risk Cities", "City",
                "Fraud Rate (%)", reference_line=city_threshold)
with colD_2:
    display_dataframe("Detailed Transactions for High-Risk Cities", city_summary_table)
'---'

# Job Fraud Analysis
st.header("Fraud Rate by Job")
colE_1,colE_2=st.columns(2)
job_fraud_rate = calculate_fraud_rate(data, 'job')
job_threshold = job_fraud_rate.mean() + 3 * job_fraud_rate.std()
high_risk_jobs = job_fraud_rate[job_fraud_rate > job_threshold].index
high_risk_job_transactions = data[data['job'].isin(high_risk_jobs)]
job_summary_table = high_risk_job_transactions.groupby(['job', 'last', 'first']).agg(
    Total_Amount=('amt', 'sum'),
    Fraud_Amount=('amt', lambda x: x[high_risk_job_transactions['is_fraud'] == 1].sum()),
    Total_Transactions=('amt', 'count'),
    Fraud_Transactions=('is_fraud', 'sum')
).reset_index()
job_summary_table['Fraud Rate (%)'] = (job_summary_table['Fraud_Transactions'] / job_summary_table[
    'Total_Transactions']) * 100
colE_1,colE_2=st.columns(2)
with colE_1:
    plot_bar_chart(job_summary_table.set_index('job')['Fraud Rate (%)'], "Fraud Rate by High-Risk Jobs", "Job",
                "Fraud Rate (%)", reference_line=job_threshold)
with colE_2:
    display_dataframe("Detailed Transactions for High-Risk Jobs", job_summary_table)
'---'

# Age Group Fraud Analysis
st.header("Fraud Rate by Age")
colF_1,colF_2=st.columns(2)
data['dob'] = pd.to_datetime(data['dob'], errors='coerce')
data['age'] = datetime.now().year - data['dob'].dt.year
data['age_group'] = pd.cut(data['age'], bins=list(range(0, 101, 5)))

age_group_fraud_rate = calculate_fraud_rate(data, 'age_group')
with colF_1:
    plot_bar_chart(age_group_fraud_rate, "Fraud Rate by Age Group", "Age Group", "Fraud Rate (%)")
with colF_2:
    display_dataframe("Fraud Rate by Age Group", age_group_fraud_rate.reset_index().rename(columns={0: 'Fraud Rate (%)'}))
'---'

# Card BIN Fraud Analysis
st.header("Fraud Rate by CC Number Prefix (6 Digits)")
colG_1,colG_2,colG_3=st.columns([2,1,1])
data['card_bin'] = data['cc_num'].astype(str).str[:6]
card_bin_fraud_rate = calculate_fraud_rate(data, 'card_bin')
fraud_100_card_bins = card_bin_fraud_rate[card_bin_fraud_rate == 100]
with colG_2:
    display_dataframe("Card BINs with 100% Fraud Rate",
                    fraud_100_card_bins.reset_index().rename(columns={0: 'Fraud Rate (%)'}))
card_bin_fraud_rate_filtered = card_bin_fraud_rate[card_bin_fraud_rate < 100].sort_values(ascending=False)
with colG_3:
    display_dataframe("Card BINs with Fraud Rate < 100%",
                    card_bin_fraud_rate_filtered.reset_index().rename(columns={0: 'Fraud Rate (%)'}))
with colG_1:
    plot_bar_chart(card_bin_fraud_rate_filtered, "Fraud Rate by Card BIN (Less than 100%)", "Card BIN", "Fraud Rate (%)",
                color="lightcoral")
