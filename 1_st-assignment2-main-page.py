
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from PIL import Image


st.set_page_config(
    page_title= "Multipage App",
    page_icon="🖐",
    layout="wide"
)
st.title("Main Page")

st.sidebar.success("select a page above.")

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
        
    </style>

'''
st.markdown(header_style, unsafe_allow_html=True)

data = pd.read_csv("Input_Sales_Data_v2.csv")
data["Date"] = pd.to_datetime(data["Date"]).dt.date

def create_slider_and_dropdown(data):

    st.markdown("""
    ## Sample Sales Data
    #### Shown are the sample sales data having **Date,Manufacturer,Category,Brand,SKU Name,Volume,Value and Price**
    """)
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]

    # print (data.Date.min())
    # print (data.Date.max())

    format = 'MMM DD, YYYY'  

    start_date = data.Date.min()  
    end_date = data.Date.max()
    max_days = end_date-start_date

    col1, col2 = st.columns(2)

    selected_date = col1.slider('Select Date Range', min_value=start_date, value=end_date ,max_value=end_date, format=format)

    calegory_list = data["Category"].unique()

    category_value = col2.selectbox(
        'Select the Category',
        calegory_list)

    st.table(pd.DataFrame([[start_date, selected_date, end_date, category_value]],
                    columns=['start',
                            'selected',
                            'end',
                            'Selected_category'],
                    index=['date']))

    st.write("---")
    return start_date, selected_date, category_value

def filter_df(start_date, selected_date, category_value):
    st.write("#### Total **Volume sales** and **Value sales** at the Manufacturer Level")

    # Filter the dataframe based on the selected date range
    filtered_df = data[(data['Date'] >= start_date) & (data['Date'] <= selected_date) & (data['Category'] == category_value)]

    # Display the total volume and value sales at the manufacturer level
    manufacturer_sales = filtered_df.groupby('Manufacturer')[['Volume', 'Value']].sum().sort_values(by='Value', ascending=False)
    
    st.dataframe(manufacturer_sales, width=800)
    st.markdown("---")
    return manufacturer_sales, filtered_df

def plot_line_chart(filtered_df):
    # Get the top 5 manufacturers for the selected period
    top_manufacturers = filtered_df.groupby('Manufacturer')['Value'].sum().nlargest(5).index.tolist()

    # Group the data by manufacturer and date to calculate the total sales over time
    manufacturer_sales = filtered_df.groupby(['Manufacturer', 'Date'], as_index=False)['Value'].sum()

    # filter out top manufactor data by date wise
    new_manufacturer = manufacturer_sales["Manufacturer"].isin(top_manufacturers)
    new_manufacturer_df = manufacturer_sales[new_manufacturer].sort_values(by='Date')

    for manufacturer in top_manufacturers:
        new_manufacturer_df_plot = new_manufacturer_df[new_manufacturer_df['Manufacturer'] == manufacturer]
        # Plot the filtered data
        plt.plot(new_manufacturer_df_plot['Date'], new_manufacturer_df_plot['Value'], label=manufacturer)

    plt.xlabel('Date')
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.xticks(rotation=45)
    plt.ylabel('Value Sales')
    plt.title('Top 5 Manufacturers Sales Trends')
    # Move the legend outside the plot
    plt.legend(bbox_to_anchor=(0.05, 1), loc='upper left')
    
    # Display the plot
    st.write("#### Line chart Showing the trends for top 5 manufacturers")
    st.pyplot(plt, use_container_width=True)
    st.markdown("---")

    # sort df in ascending order
    new_manufacturer_sort_df = new_manufacturer_df.sort_values(by=['Value'], ascending=False)

    # Calculating Market_share Percentage
    new_manufacturer_sort_df['Market_share'] = (new_manufacturer_sort_df['Value'] / 
                    new_manufacturer_sort_df['Value'].sum())
    
    # Colour code the % column in descending order
    column_formatter = { 
        'Market_share' : '{:.2%}', 
        'Value': '$ {0:,.0f}'
         }
    
    colormap = sns.light_palette('green', as_cmap=True)
    new_manufacturer_sort_df = new_manufacturer_sort_df.style\
        .background_gradient(axis=0, subset='Market_share', cmap=colormap)\
        .bar(color='lightgreen', subset='Value', align='zero')\
        .format( column_formatter)
    
    st.write("#### Dataframe of Line chart Showing the trends for top 5 manufacturers based on Value Sales")
    st.dataframe(new_manufacturer_sort_df, width=800)
    return True

start_date, selected_date, category_value = create_slider_and_dropdown(data)

manufacturer_sales, filtered_df = filter_df(start_date, selected_date, category_value)

dane = plot_line_chart(filtered_df)

# print(manufacturer_sales.head())

