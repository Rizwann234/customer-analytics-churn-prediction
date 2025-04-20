import plotly.express as px
import plotly.graph_objects as go
from utils import *
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Create streamlit app
def main():
    
    # Wide layout
    st.set_page_config(layout="wide")

    # Database connection
    db_file = 'database/telco_churn_data.db'  # Replace with your database file path
    conn = create_connection(db_file)
    if conn is None:
        st.error("Error! Cannot create the database connection.")
        return
    st.success("Database connection established successfully.")
    st.markdown("### Customer Segmentation Analysis")
    
    # Show key metrics including total customers, churn rate, and average monthly charges
    query = """
        SELECT 
            COUNT(*) as Total_Customers,
            AVG(MonthlyCharges) as Avg_Monthly_Charges,
            AVG(tenure) as Avg_Tenure,
            ROUND(AVG(CASE WHEN Churn = '1' THEN 100.0 ELSE 0 END), 2) as Churn_Rate
        FROM cluster_analysis
    """
    metrics = load_data_from_db(conn, query)
    
    if metrics is None:
        st.error("Error loading data from database.")
        return  
    
    # Row A with styled metrics
    a1, a2, a3, a4 = st.columns(4)
    
    # Custom CSS for metric boxes
    metric_style = """
    <div style="
        padding: 20px;
        border-radius: 10px;
        background-color: #1f1f1f;
        border: 2px solid #1f77b4;
        text-align: center;
        margin: 5px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    ">
        <h3 style="color: #1f77b4; margin-bottom: 10px;">{label}</h3>
        <p style="font-size: 24px; font-weight: bold; color: #ffffff; margin: 0;">{value}</p>
    </div>
    """
    
    # Display metrics with custom styling
    a1.markdown(metric_style.format(
        label="Total Customers",
        value=f"{metrics['Total_Customers'][0]:,}"
    ), unsafe_allow_html=True)

    a2.markdown(metric_style.format(
        label="Churn Rate",
        value=f"{metrics['Churn_Rate'][0]:.2f}%"
    ), unsafe_allow_html=True)
    
    a3.markdown(metric_style.format(
        label="Average Monthly Charges",
        value=f"${metrics['Avg_Monthly_Charges'][0]:.2f}"
    ), unsafe_allow_html=True)
    
    a4.markdown(metric_style.format(
        label="Average Tenure (months)",
        value=f"{metrics['Avg_Tenure'][0]:.2f}"
    ), unsafe_allow_html=True)
    

    # Load data from database for customer segmentation analysis  
    query = "SELECT tenure,TotalCharges, MonthlyCharges,Cluster,Churn FROM cluster_analysis"  
    data = load_data_from_db(conn, query)
    if data is None:
        st.error("Error loading data from database.")
        return
    
    # Plot scatter plot with full width
    scatter_fig1 = plot_scatter(data, x_col='tenure', y_col='MonthlyCharges', hue_col='Cluster')
    scatter_fig1.update_layout(height=600)
    scatter_fig1.update_xaxes(title_text='Tenure (Months)')
    scatter_fig1.update_yaxes(title_text='Monthly Charges ($)')

    # Calculate churn rates by cluster
    churn_rates = data.groupby(['Cluster', 'Churn']).size().unstack()
    churn_rates_pct = churn_rates.div(churn_rates.sum(axis=1), axis=0) * 100

    # Plot donut charts with full width
    donut_fig = plot_churn_rates_by_cluster(churn_rates_pct)
    donut_fig.update_layout(height=600)

    # RowB Display plots side by side with full width
    b1, b2 = st.columns(2)
    with b1:
        b1.plotly_chart(scatter_fig1, use_container_width=True)
    with b2:
        b2.plotly_chart(donut_fig, use_container_width=True)



if __name__ == "__main__":
    main()
# Run the application
# streamlit run main.py
# Note: To run the application, use the command:
# streamlit run main.py
# Ensure you have the required libraries installed:
# pip install streamlit pandas plotly scikit-learn sqlalchemy
# sqlite3
# Make sure to replace the database file path and SQL queries as per your database structure.
# Ensure the SQLite database file is present in the specified path. 
