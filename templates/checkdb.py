import os
import time
import psycopg2

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve PostgreSQL connection details from environment variables
db_host = os.environ.get('POSTGRES_HOST')
db_name = os.environ.get('POSTGRES_NAME')
db_port = os.environ.get('POSTGRES_PORT')
db_user = os.environ.get('POSTGRES_USERNAME')
db_password = os.environ.get('POSTGRES_PASSWORD')
wait_time = 15
# Create PostgreSQL connection string
conn_string = f"host='{db_host}' port='{db_port}' dbname='postgres' user='{db_user}' password='{db_password}'"

# Connect to PostgreSQL server
while True:
    try:
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        print("Connected to PostgreSQL server.")
        break
    except psycopg2.OperationalError:
        print(f"Could not connect to PostgreSQL server. Retrying in {wait_time} seconds...")
        time.sleep(wait_time)

# Check if database exists
while True:
    try:
        if conn is None:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        result = cursor.fetchone()
        if result:
            print(f"Database '{db_name}' exists.")
            break
        else:
            print(f"Database '{db_name}' does not exist. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    except psycopg2.OperationalError:
        conn = None
        print(f"Could not connect to PostgreSQL server. Retrying in {wait_time} seconds...")
        time.sleep(wait_time)

# Close database connection
cursor.close()
conn.close()
