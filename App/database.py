
"""Module for managing MySQL database connections."""
import mysql.connector

DB_NAME = "database"

def get_connection():
    """Creates and returns a MySQL database connection."""
    return mysql.connector.connect(
        host="localhost",
        user="appuser",
        password="1234",
        database= "appcar"
    )
