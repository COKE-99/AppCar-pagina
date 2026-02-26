"""
Conexión a Supabase PostgreSQL
"""

import os
import psycopg2
import psycopg2.extras


def get_connection():
    """
    Crea conexión a la base de datos Supabase
    usando variables de entorno de Vercel
    """

    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        dbname=os.environ.get("DB_NAME"),
        port=5432,
        cursor_factory=psycopg2.extras.RealDictCursor
    )
