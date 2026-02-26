"""
Aplicación principal de Terramar.

Este módulo contiene todas las rutas de la plataforma:
- Inicio
- Login
- Catálogo
- Compras
- Ventas
- Stock
- Dashboard

Conectado a Supabase mediante database.py
"""

# ==========================
# IMPORTS (SIEMPRE ARRIBA)
# ==========================

import os
from datetime import date

from flask import Flask, render_template, request, session, redirect
from werkzeug.utils import secure_filename

from database import get_connection


# ==========================
# CONFIGURACIÓN APP
# ==========================

app = Flask(__name__)

# Clave para manejar sesiones de usuario
app.secret_key = "clave_super_segura"


# ==========================
# RUTA INICIO
# ==========================

@app.route("/")
def inicio():
    """
    Muestra la página principal (carátula).

    Esta es la primera pantalla que ve el usuario.
    Permite:
    - Entrar como cliente
    - Iniciar sesión como administradora
    """
    return render_template("index.html")


# ==========================
# LOGIN ADMIN
# ==========================

@app.route("/login", methods=["POST"])
def login():
    """
    Valida credenciales de administradora.

    Si son correctas:
        crea sesión como admin
        redirige a dashboard

    Si son incorrectas:
        regresa a inicio
    """

    usuario = request.form["usuario"]
    password = request.form["password"]

    if usuario == "admin" and password == "1234":

        session["rol"] = "admin"

        return redirect("/dashboard")

    return redirect("/")


# ==========================
# LOGIN CLIENTE
# ==========================

@app.route("/cliente")
def cliente():
    """
    Permite acceso al catálogo como cliente.

    No requiere contraseña.
    Solo permite ver productos.
    """

    session["rol"] = "cliente"

    return redirect("/catalogo")


# ==========================
# CATÁLOGO PRODUCTOS
# ==========================

@app.route("/catalogo", methods=["GET", "POST"])
def catalogo():
    """
    Muestra todos los productos.

    Si es admin:
        permite agregar productos

    Si es cliente:
        solo permite ver productos
    """

    conn = get_connection()
    cursor = conn.cursor()

    # Agregar producto
    if request.method == "POST":

        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = request.form["precio"]

        imagen = request.files.get("imagen")

        nombre_imagen = None

        if imagen and imagen.filename != "":

            nombre_imagen = secure_filename(imagen.filename)

            ruta = os.path.join(
                "static/uploads",
                nombre_imagen
            )

            imagen.save(ruta)

        cursor.execute(
            """
            INSERT INTO productos
            (nombre, descripcion, precio, imagen)
            VALUES (%s,%s,%s,%s)
            """,
            (nombre, descripcion, precio, nombre_imagen)
        )

        conn.commit()

    # Obtener productos
    cursor.execute(
        "SELECT * FROM productos ORDER BY id DESC"
    )

    productos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "catalogo.html",
        productos=productos
    )


# ==========================
# COMPRAS
# ==========================

@app.route("/compras", methods=["GET", "POST"])
def compras():
    """
    Permite registrar compras empresariales.

    Guarda:
    - costo empresarial
    - precio público
    - piezas
    """

    conn = get_connection()
    cursor = conn.cursor()

    hoy = date.today()

    if request.method == "POST":

        cursor.execute(
            """
            INSERT INTO compras
            (nombre, descripcion,
            costo_empresarial,
            precio_publico,
            piezas,
            fecha)

            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (
                request.form["nombre"],
                request.form["descripcion"],
                request.form["costo_empresarial"],
                request.form["precio_publico"],
                request.form["piezas"],
                hoy
            )
        )

        conn.commit()

    cursor.execute(
        "SELECT * FROM compras ORDER BY id DESC"
    )

    lista_compras = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "compras.html",
        compras=lista_compras
    )


# ==========================
# VENTAS
# ==========================

@app.route("/ventas", methods=["GET", "POST"])
def ventas():
    """
    Permite registrar ventas.

    Calcula automáticamente la utilidad.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM productos")

    productos = cursor.fetchall()

    if request.method == "POST":

        producto_id = request.form["producto_id"]

        cursor.execute(
            "SELECT * FROM productos WHERE id=%s",
            (producto_id,)
        )

        producto = cursor.fetchone()

        utilidad = (
            float(request.form["precio_venta"])
            - float(producto["precio"])
        ) * int(request.form["piezas"])

        cursor.execute(
            """
            INSERT INTO ventas
            (
                producto_id,
                nombre,
                descripcion,
                precio_compra,
                precio_venta,
                utilidad,
                piezas,
                fecha,
                comentarios
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                producto_id,
                producto["nombre"],
                producto["descripcion"],
                producto["precio"],
                request.form["precio_venta"],
                utilidad,
                request.form["piezas"],
                date.today(),
                request.form["comentarios"]
            )
        )

        conn.commit()

    cursor.execute(
        "SELECT * FROM ventas ORDER BY id DESC"
    )

    lista_ventas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "ventas.html",
        productos=productos,
        ventas=lista_ventas
    )


# ==========================
# STOCK
# ==========================

@app.route("/stock")
def stock():
    """
    Calcula el stock actual.

    Stock = compras - ventas
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            c.nombre,
            SUM(c.piezas) as comprado,
            COALESCE(SUM(v.piezas),0) as vendido,
            SUM(c.piezas) - COALESCE(SUM(v.piezas),0) as stock
        FROM compras c
        LEFT JOIN ventas v
            ON c.nombre = v.nombre
        GROUP BY c.nombre
        """
    )

    productos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "stock.html",
        productos=productos
    )


# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():
    """
    Muestra métricas principales:

    - Total ventas
    - Total utilidad
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            SUM(precio_venta*piezas) as ventas,
            SUM(utilidad) as utilidad
        FROM ventas
        """
    )

    kpi = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        kpi=kpi
    )


# ==========================
# NECESARIO PARA VERCEL
# ==========================
