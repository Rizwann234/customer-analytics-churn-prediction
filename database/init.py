import pandas as pd
from sqlalchemy import create_engine
import sqlite3

# Create a SQLite database
engine = create_engine('sqlite:///telco_churn_data.db')

# Read in data from .csv and write it to the database
try:
    eda_table = pd.read_csv('data/eda_data.csv')
    clustered_table = pd.read_csv('data/clustered.csv')

except FileNotFoundError:
    print("File not found. Please check the file path.")
    exit()

eda_table.to_sql('eda', con=engine, if_exists='replace', index=False)
clustered_table.to_sql('cluster_analysis', con=engine, if_exists='replace', index=False)