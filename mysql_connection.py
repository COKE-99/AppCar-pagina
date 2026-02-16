"""Module for testing MySQL connection functionality."""
import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="Marcos1234",
    database="database")

print("Conector funcionando 🎉")
