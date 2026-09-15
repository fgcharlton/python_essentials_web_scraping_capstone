# Import convention
import streamlit as st
import sqlite3 
from datetime import datetime
from sqlalchemy import create_engine 
import pandas as pd     # Used to work with tabular data
import numpy as np      # Helps generate random numbers
import plotly.express as px  # For interactive charts

# Create sample data — just faking some numbers to simulate a small product dataset
engine = create_engine('sqlite:///weather_database.db')
sql = """
SELECT *
FROM (
    SELECT * FROM capital_cities
    UNION
    SELECT * FROM most_popular_cities 
    UNION
    SELECT * FROM popular_cities
    UNION
    SELECT * FROM somewhat_popular_cities
    );
"""
with engine.connect() as conn:
    df = pd.read_sql_query(sql, conn)

print(df.head())

# Sidebar filters — this shows up in the sidebar for user interaction
st.sidebar.header('Filter Options')  # Sidebar title
category = df['city_category'].drop_duplicates()
selected_category = st.sidebar.selectbox('Select City Category', category)  # Dropdown to choose a category

# Select cities
cities = df['Name'].loc[df["city_category"] == selected_category]
selected_city = st.sidebar.selectbox('Select City', cities)

# Filter the data based on the user's selection
filtered_category = df[df['city_category'] == selected_category].reset_index(drop=True)  # Show only the row that matches the selected category
filtered_city = df[df['Name'] == selected_city].reset_index(drop=True) # Show only the row that matches the select city

# Main app content starts here
st.title('Weather Dashboard 🌦️')  # Big title for the dashboard
st.caption('This dashboard displays key weather conditions from the capital cities as well as popular, somewhat popular, and the most popular cities.')

# Display metrics for selected city
st.header(f"Weather in {filtered_city['Name'].values[0]}")

# Display day and time
st.caption(f"It is {filtered_city['Day'].values[0]} in {filtered_city['Name'].values[0]}.")

col1, col2, col3 = st.columns([24, 8, 12])  # Create three columns for layout
with col1:
    st.metric('Weather Conditions', f"{filtered_city['Weather Conditions'].values[0]}")  # Show weather conditions in a pretty format
with col2:
    st.metric('Temperature', f"{filtered_city['Temperature'].values[0]}°F") # Show temperature of selected city
with col3:
    st.metric('Rain Category', f"{filtered_city['Rain'].values[0]}")  # Show rain categories similarly

# Display metrics for other cities in the selected category
st.header(f"Weather in Other {filtered_category['city_category'].values[0]}")

# Histogram of temperatures
st.subheader(f"Temperatures in Other {filtered_category['city_category'].values[0]}")  # Subheading for the histogram
histogram = px.histogram(filtered_category, x='Temperature', text_auto = True)  # Histogram
histogram.update_yaxes(title_text='Count of Cities')
st.plotly_chart(histogram)  # Render the chart in the app

# Bar chart of Weather conditions
# Create aggregate count prior to making chart
weather_count = filtered_category["Weather Conditions"].value_counts()

bar_chart_df = pd.DataFrame({
    "Weather Category": [str(i) for i in weather_count.index],
    "Weather Count": weather_count.values,
})

# Create bar chart 
st.subheader(f"Weather Conditions in Other {filtered_category['city_category'].values[0]}")  # Subheading for the chart
bar_chart = px.bar(bar_chart_df, x='Weather Category', y="Weather Count", labels = {'Weather Category': 'Weather Conditions', 'Weather Count': 'Count of Cities'}, text_auto = True)
st.plotly_chart(bar_chart)  # Render the chart in the app

# Pie chart of rain
# Create aggregate count prior to making chart
rain_count = filtered_category["Rain"].value_counts()

pie_chart_df = pd.DataFrame({
    "Rain Category": [str(i) for i in rain_count.index],
    "Rain Count": rain_count.values,
})

# Create pie chart
st.subheader(f"Rain in Other {filtered_category['city_category'].values[0]}")  # Subheading for the pie chart
piechart = px.pie(pie_chart_df, values='Rain Count', names='Rain Category')
st.plotly_chart(piechart)  # Render the chart in the app

# Give credit to where data is pulled.
st.caption('Data from the [Weather Around The World](https://www.timeanddate.com/weather/) website.')

# Put data time stamp
st.caption("Data pulled on 9/15/2026.")
