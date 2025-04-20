import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import gaussian_kde
import streamlit.components.v1 as components
import sqlalchemy
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_connection(db_file: str) -> sqlite3.Connection:
    """Create a database connection to the SQLite database.
    
    Args:
        db_file (str): Path to the SQLite database file
    
    Returns:
        sqlite3.Connection: Database connection object if successful, None otherwise
    
    Raises:
        sqlite3.Error: If connection cannot be established
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def load_data_from_db(conn: sqlite3.Connection, query: str) -> pd.DataFrame:
    """Load data from the SQLite database using the provided query.
    
    Args:
        conn (sqlite3.Connection): SQLite database connection object
        query (str): SQL query to execute
    
    Returns:
        pd.DataFrame: DataFrame containing query results if successful, None otherwise
    
    Raises:
        sqlite3.Error: If there is an error executing the SQL query
    """
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        print(e)
    return None


def plot_scatter(data: pd.DataFrame, x_col: str, y_col: str, hue_col: str) -> go.Figure:
    """Create an interactive scatter plot using Plotly Express.
    
    Args:
        data (pd.DataFrame): The input DataFrame containing the data to plot
        x_col (str): Name of the column to plot on x-axis
        y_col (str): Name of the column to plot on y-axis 
        hue_col (str): Name of the column to use for color-coding points
    
    Returns:
        go.Figure: A Plotly scatter plot figure object
    """
    fig = px.scatter(
        data, 
        title=" ",
        x=x_col, 
        y=y_col,
        color=hue_col,
        color_discrete_sequence=px.colors.qualitative.Set1,
        template='plotly_white'
    )
    
    fig.update_layout(
        title_x=0.5,
        legend_title_text='Customer Segment',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )
    return fig

def plot_churn_rates_by_cluster(churn_rate: pd.DataFrame) -> go.Figure:
    """Create interactive donut charts using Plotly subplots with enhanced styling.
    
    Args:
        churn_rate (pd.DataFrame): DataFrame containing churn rates by cluster
    
    Returns:
        go.Figure: Plotly figure containing donut charts for each cluster
    """
    clusters = churn_rate.index.unique()
    n_clusters = len(clusters)
    
    # Create a 2x2 grid for donut charts 
    fig = make_subplots(
        rows=2, 
        cols=2,
        specs=[[{'type': 'domain'}, {'type': 'domain'}],
               [{'type': 'domain'}, {'type': 'domain'}]]
    )
    
    x_positions = [0.2, 0.8, 0.2, 0.8]  # X positions for cluster names
    y_positions = [0.9, 0.9, 0.1, 0.1]  # Y positions for cluster names

    # Professional color palette
    colors = ['#1f77b4', '#d62728']  # Blue and Red
    
    for i, cluster in enumerate(clusters):
        row = (i // 2) + 1
        col = (i % 2) + 1
        
        fig.add_trace(
            go.Pie(
                labels=['No', 'Yes'],  # Churn labels
                values=churn_rate.loc[cluster],
                name=f"Cluster {cluster}",
                hole=0.6,
                sort=False,
                marker=dict(colors=colors),
                textinfo='percent',
                insidetextorientation='radial',
                textfont=dict(size=12)
            ),
            row=row,
            col=col
        )
        
        # Place the cluster name at the top right of the donut chart
        fig.add_annotation(
            x=x_positions[i],
            y=y_positions[i],
            text=f"<b>{cluster}</b>",
            showarrow=False,
            font=dict(size=14, color='white', family='Arial'),
            align="center",
            bgcolor="rgba(0,0,0,0.5)"  # Optional: Add a background color for better readability
        )
    
    fig.update_layout(
        title_text=" ",
        title_x=0.5,
        showlegend=True,
        legend_title_text='Churn',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.05,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=100, b=80, l=50, r=50),
        plot_bgcolor='rgba(0,0,0,0)'  # Set plot background to transparent
    )
    return fig


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
