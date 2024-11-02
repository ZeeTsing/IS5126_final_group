import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# 加载数据
data = pd.read_csv('credit_card_transactions.csv')


# 通用函数：计算欺诈率
def calculate_fraud_rate(data, group_by_column):
    return data.groupby(group_by_column).apply(lambda x: (x['is_fraud'].sum() / len(x)) * 100)


# 通用函数：显示数据表格
def display_dataframe(title, data):
    st.write(title)
    st.dataframe(data)


# 通用函数：绘制直方图
def plot_bar_chart(data, title, xlabel, ylabel, reference_line=None, rotation=45, color="skyblue"):
    fig, ax = plt.subplots(figsize=(10, 6))
    data.plot(kind='bar', ax=ax, color=color, alpha=0.7)
    if reference_line:
        ax.axhline(y=reference_line, color='red', linestyle='--', label=f'Reference Line: {reference_line:.2f}%')
        ax.legend()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    plt.xticks(rotation=rotation, fontsize=8)
    st.pyplot(fig, use_container_width=True)


# 计算整体欺诈率
total_fraud_rate = (data['is_fraud'].sum() / len(data)) * 100

# 左右布局
st.title("信用卡交易欺诈分析")
st.write("amt 和 is_fraud 散点图")
fig1, ax1 = plt.subplots()
ax1.scatter(data['amt'], data['is_fraud'], alpha=0.5)
ax1.set_xlabel("Transaction Amount (amt)")
ax1.set_ylabel("Is Fraud (0 = No, 1 = Yes)")
ax1.set_title("Transaction Amount vs Fraud Indicator")
ax1.set_xticks(np.arange(0, data['amt'].max() + 1500, 1500))
plt.xticks(rotation=45, fontsize=8)
st.pyplot(fig1, use_container_width=True)

category_fraud_rate = calculate_fraud_rate(data, 'category').sort_values(ascending=False)
plot_bar_chart(category_fraud_rate, "Fraud Rate by Category", "Category", "Fraud Rate (%)",
               reference_line=total_fraud_rate)

# Merchant Fraud Analysis
merchant_fraud_rate = calculate_fraud_rate(data, 'merchant').sort_values(ascending=False)
mean_merchant_fraud_rate = merchant_fraud_rate.mean()
std_merchant_fraud_rate = merchant_fraud_rate.std()
merchant_threshold = mean_merchant_fraud_rate + 3 * std_merchant_fraud_rate

# 绘制 merchant 的欺诈率图表
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
display_dataframe("Detailed Transactions for High-Risk Merchants", summary_table)
plot_bar_chart(summary_table.set_index('merchant')['Fraud Rate (%)'], "Fraud Rate by High-Risk Merchants", "Merchant",
               "Fraud Rate (%)", reference_line=merchant_threshold)

# Last Name Fraud Analysis
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
display_dataframe("Detailed Transactions for High-Risk Last Names", last_summary_table)
plot_bar_chart(last_summary_table.set_index('last')['Fraud Rate (%)'], "Fraud Rate by High-Risk Last Names",
               "Last Name", "Fraud Rate (%)", reference_line=last_threshold)

# Gender Fraud Analysis
gender_fraud_rate = calculate_fraud_rate(data, 'gender')
plot_bar_chart(gender_fraud_rate, "Fraud Rate by Gender", "Gender", "Fraud Rate (%)")

# City Fraud Analysis
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
display_dataframe("Detailed Transactions for High-Risk Cities", city_summary_table)
plot_bar_chart(city_summary_table.set_index('city')['Fraud Rate (%)'], "Fraud Rate by High-Risk Cities", "City",
               "Fraud Rate (%)", reference_line=city_threshold)

# Job Fraud Analysis
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
display_dataframe("Detailed Transactions for High-Risk Jobs", job_summary_table)
plot_bar_chart(job_summary_table.set_index('job')['Fraud Rate (%)'], "Fraud Rate by High-Risk Jobs", "Job",
               "Fraud Rate (%)", reference_line=job_threshold)

# Age Group Fraud Analysis
data['dob'] = pd.to_datetime(data['dob'], errors='coerce')
data['age'] = datetime.now().year - data['dob'].dt.year
data['age_group'] = pd.cut(data['age'], bins=list(range(0, 101, 5)))
age_group_fraud_rate = calculate_fraud_rate(data, 'age_group')
display_dataframe("Fraud Rate by Age Group", age_group_fraud_rate.reset_index().rename(columns={0: 'Fraud Rate (%)'}))
plot_bar_chart(age_group_fraud_rate, "Fraud Rate by Age Group", "Age Group", "Fraud Rate (%)")

# Card BIN Fraud Analysis
data['card_bin'] = data['cc_num'].astype(str).str[:6]
card_bin_fraud_rate = calculate_fraud_rate(data, 'card_bin')
fraud_100_card_bins = card_bin_fraud_rate[card_bin_fraud_rate == 100]
display_dataframe("Card BINs with 100% Fraud Rate",
                  fraud_100_card_bins.reset_index().rename(columns={0: 'Fraud Rate (%)'}))
card_bin_fraud_rate_filtered = card_bin_fraud_rate[card_bin_fraud_rate < 100].sort_values(ascending=False)
display_dataframe("Card BINs with Fraud Rate < 100%",
                  card_bin_fraud_rate_filtered.reset_index().rename(columns={0: 'Fraud Rate (%)'}))
plot_bar_chart(card_bin_fraud_rate_filtered, "Fraud Rate by Card BIN (Less than 100%)", "Card BIN", "Fraud Rate (%)",
               color="lightcoral")
