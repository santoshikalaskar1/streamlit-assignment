import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import pandas as pd
import pyarrow.parquet as pq
import seaborn as sns
import streamlit as st
import numpy as np

st.set_page_config(
    
    layout="wide"
)

header_style = '''
    <style>
        table th {
            background-color: #FFF933;
            font-size: 20px;
            font-family: "Courier New";
        }
        h1{
            color:Red;
            font-size:28px;
            text-align:center;
        }
        h2{
            color:#6B33FF;
            font-size:28px;
            text-align:center;
        }
        h4{
            color:#33ff33;
            font-size:18px;
            text-align:center;
        }

        div[data-testid="metric-container"] {
            background-color: rgba(28, 131, 225, 0.1);
            border: 1px solid rgba(28, 131, 225, 0.1);
            padding: 5% 5% 5% 10%;
            border-radius: 5px;
            color: rgb(30, 103, 119);
            font-size: 15px;
            overflow-wrap: break-word;
        }

        /* breakline for metric text  */
            div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
            overflow-wrap: break-word;
            white-space: break-spaces;
            color: blue;
            text-align:center;
        }

        .css-1xarl3l {
            font-size: 1.5rem;
            padding-bottom: 0.25rem;
            text-align:center;
        }
        
    </style>

'''
st.markdown(header_style, unsafe_allow_html=True)

st.title("Deep Dive")

data = pd.read_csv("Input_Sales_Data_v2.csv")

# Remove duplicate values in the 'Date' column
data = data[~data['Date'].duplicated()]
data["Date"] = pd.to_datetime(data["Date"]).dt.date
data["Year"] = pd.to_datetime(data["Date"]).dt.year

newdf = data.copy()

# Set up the layout using Streamlit columns
col1, col2, col3 = st.columns([1, 1, 1])

# Create select boxes for category, manufacturer, and brand in the second row
selected_category = col1.selectbox('Category', data['Category'].unique())
data = data[(data['Category'] == selected_category)]
selected_manufacturer = col2.selectbox('Manufacturer', data['Manufacturer'].unique())
data = data[(data['Manufacturer'] == selected_manufacturer)]
selected_brand = col3.selectbox('Brand', data['Brand'].unique())
data = data[(data['Brand'] == selected_brand)]

print(data.shape)
# Filter the DataFrame based on the selected values
filtered_df = newdf[(newdf['Category'] == selected_category) &
                 (newdf['Manufacturer'] == selected_manufacturer) &
                 (newdf['Brand'] == selected_brand)]

# Calculate YTD volume sales, YTD $ sales, YTD Market share, and #SKUs
ytd_volume_sales = filtered_df['Volume'].sum()
ytd_total_sales = filtered_df['Value'].sum()
ytd_market_share = ytd_volume_sales / ytd_total_sales
num_skus = filtered_df['SKU Name'].nunique()

# Display YTD statistics
col5, col6, col7, col8 = st.columns([1, 1, 1, 1])
col5.metric("YTD Volume Sales", f"{ytd_volume_sales:,}")
col6.metric("YTD $ Sales", f"$ {ytd_total_sales:,.2f}")
col7.metric("YTD Market Share", f"{ytd_market_share:.2%}")
col8.metric("# SKUs", num_skus)
st.write('---')

# Weekly Volume Sales and Value Sales Line Chart
filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce')
filtered_df.set_index('Date', inplace=True)
filtered_df = filtered_df.loc[:, ~filtered_df.columns.str.contains('^Unnamed')]

# Set up the layout for plots using Streamlit columns
col9, col10 = st.columns(2)
with col9:
    st.subheader('Weekly Volume Sales and Value Sales')
    weekly_sales = filtered_df.resample('W-Mon').sum()
    fig, ax1 = plt.subplots(figsize=(5, 5))

    sns.lineplot(data=weekly_sales, x=weekly_sales.index, y='Volume', color='blue', ax=ax1, label='Volume Sales')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Volume Sales')
    ax1.tick_params('y', colors='blue')
    ax1.legend(loc='upper right')
    
    ax2 = ax1.twinx()
    sns.lineplot(data=weekly_sales, x=weekly_sales.index, y='Value', color='green', ax=ax2, label='Value Sales')
    ax2.set_ylabel('Value Sales', color='green')
    ax2.tick_params('y', colors='green')

    plt.title('Weekly Volume Sales and Value Sales for Selected SKUs')
    fig.autofmt_xdate(rotation=45)
    st.pyplot(fig)

# Pie Chart - Percentage of Value Sales of Top 10 SKUs within the Brand
with col10:
    st.subheader('Percentage of Value Sales of Top 10 SKUs within the Brand')
    top_10_sku_sales = filtered_df.groupby('SKU Name')['Value'].sum().nlargest(10)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(top_10_sku_sales, labels=top_10_sku_sales.index, autopct='%1.1f%%')
    plt.title('Percentage of Value Sales of Top 10 SKUs within the Brand')
    plt.xticks(rotation=45)
    st.pyplot(fig)

col11, col12 = st.columns(2)
with col11:
    st.subheader('Trend Line - Price and Volume Sales')
    fig, ax1 = plt.subplots(figsize=(6, 5))
    sns.lineplot(data=filtered_df, x=filtered_df.index, y='Price', color='blue', ax=ax1, label='Price')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.tick_params('y', colors='blue')

    ax2 = ax1.twinx()
    sns.lineplot(data=filtered_df, x=filtered_df.index, y='Volume', color='red', ax=ax2, label='Volume Sales')
    ax2.set_ylabel('Volume Sales', color='red')
    ax2.tick_params('y', colors='red')

    plt.title('Trend Line - Price and Volume Sales')
    fig.autofmt_xdate(rotation=45)
    st.pyplot(fig)

# Trend Line - Price and Value Sales
with col12:
    st.subheader('Trend Line - Price and Value Sales')
    fig, ax1 = plt.subplots(figsize=(6, 5))
    sns.lineplot(data=filtered_df, x=filtered_df.index, y='Price', color='blue', ax=ax1, label='Price')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Price')
    ax1.tick_params('y', colors='blue')

    ax2 = ax1.twinx()
    sns.lineplot(data=filtered_df, x=filtered_df.index, y='Value', color='red', ax=ax2, label='Value Sales')
    ax2.set_ylabel('Value Sales', color='red')
    ax2.tick_params('y', colors='red')

    plt.title('Trend Line - Price and Value Sales')
    fig.autofmt_xdate(rotation=45)
    st.pyplot(fig)


st.markdown("<h1 style='text-align: center;'>SKU Multi Select</h1>", unsafe_allow_html=True)

# Multiselect SKU Block
selected_skus = st.multiselect('Select SKUs', filtered_df['SKU Name'].unique())

# Filter the DataFrame based on selected SKUs
filtered_skus_df = filtered_df[filtered_df['SKU Name'].isin(selected_skus)]

# Calculate average $ value sales per month for selected SKUs
filtered_skus_df = filtered_skus_df[['Volume', 'Value', 'Price', 'Year']]
average_value_sales_per_month = filtered_skus_df.resample('M').mean()['Value']

# Set up the layout for the line chart and bar chart using Streamlit columns
col13, col14 = st.columns(2)

# Line chart - Weekly Volume Sales and Value Sales for Selected SKUs
with col13:
    st.subheader('Weekly Volume Sales and Value Sales for Selected SKUs')
    weekly_sales = filtered_skus_df.resample('W-Mon').sum()
    fig, ax1 = plt.subplots(figsize=(6, 5))

    sns.lineplot(data=weekly_sales, x=weekly_sales.index, y='Volume', color='blue', ax=ax1, label='Volume Sales')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Volume Sales')
    ax1.tick_params('y', colors='blue')
    ax1.legend(loc='upper right')

    ax2 = ax1.twinx()
    sns.lineplot(data=weekly_sales, x=weekly_sales.index, y='Value', color='red', ax=ax2, label='Value Sales')
    ax2.set_ylabel('Value Sales', color='red')
    ax2.tick_params('y', colors='red')


    plt.title('Weekly Volume Sales and Value Sales for Selected SKUs')
    fig.autofmt_xdate(rotation=45)
    st.pyplot(fig)


# Bar chart - Average $ Value Sales per Month for Selected SKUs
with col14:
    st.subheader('Average $ Value Sales per Month for Selected SKUs')
    fig, ax = plt.subplots(figsize=(6, 5))
    average_value_sales_per_month = filtered_skus_df.resample('M').mean()['Value']
    month_labels = average_value_sales_per_month.index.strftime('%b %Y')
    ax.bar(range(len(average_value_sales_per_month)), average_value_sales_per_month, color='green')
    ax.set_xlabel('Month')
    ax.set_ylabel('Average $ Value Sales')
    ax.set_xticks(range(len(average_value_sales_per_month)))
    ax.set_xticklabels(month_labels, rotation=45)
    plt.title('Average $ Value Sales per Month for Selected SKUs')
    fig.autofmt_xdate(rotation=45)
    st.pyplot(fig)
