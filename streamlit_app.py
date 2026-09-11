# Import convention
import streamlit as st
import pandas as pd     # Used to work with tabular data
import numpy as np      # Helps generate random numbers
import plotly.express as px  # For interactive charts

# Create sample data — just faking some numbers to simulate a small product dataset
np.random.seed(42)  # Setting a seed so results are consistent every time you run
sample_data = {
    'Product': ['Product A', 'Product B', 'Product C', 'Product D'],
    'Sales': np.random.randint(100, 500, size=4),   # Random sales numbers
    'Profit': np.random.randint(20, 100, size=4)    # Random profit numbers
}
df = pd.DataFrame(sample_data)  # Convert the data into a DataFrame for easy handling

# Sidebar filters — this shows up in the sidebar for user interaction
st.sidebar.header('Filter Options')  # Sidebar title
selected_product = st.sidebar.selectbox('Select Product', df['Product'])  # Dropdown to choose a product

# Filter the data based on the user's selection
filtered_df = df[df['Product'] == selected_product]  # Show only the row that matches the selected product

# Main app content starts here
st.title('Simple Product Dashboard')  # Big title for the dashboard

# Display key numbers using metrics — side-by-side using columns
col1, col2 = st.columns(2)  # Create two columns for layout
with col1:
    st.metric('Sales', f"${filtered_df['Sales'].values[0]:,}")  # Show sales in a pretty format
with col2:
    st.metric('Profit', f"${filtered_df['Profit'].values[0]:,}")  # Show profit similarly

# Add a bar chart comparing all products — gives full context beyond the filter
st.subheader('Sales and Profit Comparison')  # Subheading for the chart
bar_chart = px.bar(df, x='Product', y=['Sales', 'Profit'], barmode='group')  # Grouped bar chart
st.plotly_chart(bar_chart)  # Render the chart in the app