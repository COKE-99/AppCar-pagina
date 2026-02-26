"""
Módulo de conexión a la base de datos Supabase (PostgreSQL).

Este módulo proporciona una función para obtener una conexión
a la base de datos utilizando variables de entorno configuradas
en el sistema o en Vercel.
"""

import os
import psycopg2
import psycopg2.extras


def get_connection():
    """
    Crea y retorna una conexión a la base de datos PostgreSQL (Supabase).

    La conexión usa las variables de entorno:

    DB_HOST: host de la base de datos
    DB_USER: usuario
    DB_PASSWORD: contraseña
    DB_NAME: nombre de la base de datos

    Returns:
        connection: objeto de conexión psycopg2
    """
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        dbname=os.environ.get("DB_NAME"),
        port=5432,
        cursor_factory=psycopg2.extras.RealDictCursor
)
