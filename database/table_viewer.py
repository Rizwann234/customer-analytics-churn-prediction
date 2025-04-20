# File to check tables in the SQLite database
import sqlite3
import pandas as pd
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy import inspect

# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory
parent_directory = os.path.dirname(current_directory)
# Add the parent directory to the system path
sys.path.append(parent_directory)
# Define the function to check the tables   
def check_tables():
    try:
        # Create a connection to the SQLite database
        conn = sqlite3.connect('telco_churn_data.db')
        cursor = conn.cursor()

        # Get the list of tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Print the list of tables
        print("Tables in the database:")
        for table in tables:
            print(table[0])

        # Close the connection
        conn.close()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

check_tables()