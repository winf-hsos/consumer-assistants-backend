import mysql.connector
from mysql.connector import Error
from mysql.connector.conversion import MySQLConverter
from lib.config import configure
import datetime
from icecream import ic
import sys
# Replace with your MySQL server details
host = configure('connections.products_db.host')
database = configure('connections.products_db.database')
user = configure('connections.products_db.user')
password = configure('connections.products_db.password')

db_connection = None


def execute_select_query(query):
    try:
        # Connect to the database
    
        connection = connect()

        # Execute the query
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            for key, value in row.items():
                if isinstance(value, datetime.datetime):  # Check if value is a datetime object
                    row[key] = value.isoformat()  # Convert to ISO format string

        cursor.close()
        return rows


    except Error as e:
        print(f"Error executing query: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def connect():
    try:
        # Establish a connection to the database
        global db_connection

        if db_connection is not None and db_connection.is_connected():
            return db_connection

        db_connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )

        if db_connection.is_connected():
            print('Successfully connected to the database')

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")

    return db_connection

