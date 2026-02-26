"""
Módulo de gestión de conexiones a base de datos.

Proporciona funciones para conectar y consultar la base de datos de la aplicación.
"""
import os
from datetime import date

from flask import Flask, render_template, request
from flask import session, redirect, url_for

from werkzeug.utils import secure_filename
from database import get_connection


app = Flask(__name__)


# 🔹 Ruta principal
@app.route("/")
def inicio():
    """Renderiza la página de inicio."""
    return render_template("index.html")



app.secret_key = "clave_super_segura"

@app.route("/login", methods=["POST"])
def login():
    """Gestion de ususarios"""
    usuario = request.form["usuario"]
    password = request.form["password"]

    if usuario == "admin" and password == "1234":
        session["rol"] = "admin"
        return redirect(url_for("dashboard"))

    return redirect(url_for("index.html"))

@app.route("/cliente")
def cliente():
    """Usuario como cliente"""
    session["rol"] = "cliente"
    return redirect(url_for("catalogo"))


# 🔹 Ruta catálogo
@app.route("/catalogo", methods=["GET", "POST"])
def catalogo():
    """Gestiona el catálogo de productos, permitiendo listar y agregar nuevos productos."""
    conn = get_connection()
    cursor = cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = request.form["precio"]

        imagen = request.files["imagen"]

        nombre_imagen = None

        if imagen and imagen.filename != "":
            nombre_imagen = secure_filename(imagen.filename)
            ruta = os.path.join("static/uploads", nombre_imagen)
            imagen.save(ruta)

        cursor.execute(
            "INSERT INTO productos (nombre, descripcion, precio, imagen) VALUES (%s,%s,%s,%s)",
            (nombre, descripcion, precio, nombre_imagen)
        )
        conn.commit()

    cursor.execute("SELECT id, nombre, descripcion, precio, imagen FROM productos")
    productos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("catalogo.html", productos=productos)

# Ruta ventas
@app.route("/ventas", methods=["GET", "POST"])
def ventas():
    """jbksdbbvkbdbfkjbkudbkbcdjbuvbdfbkdjfbuibdvfd."""
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener productos
    cursor.execute("SELECT id, nombre, descripcion, precio FROM productos")
    productos_catalogo = cursor.fetchall()

    if request.method == "POST":
        producto_id = int(request.form["producto_id"])
        precio_venta = float(request.form["precio_venta"])
        comentarios = request.form.get("comentarios", "")
        piezas = int(request.form.get("piezas", 1))

        # Obtener producto
        cursor.execute(
            "SELECT nombre, descripcion, precio FROM productos WHERE id=%s",
            (producto_id,)
        )
        producto = cursor.fetchone()

        if producto:
            nombre = producto["nombre"]
            descripcion = producto["descripcion"]
            precio_compra = float(producto["precio"])

            # ✔ Cálculo correcto
            utilidad = (precio_venta - precio_compra) * piezas
            fecha = date.today()

            cursor.execute("""
                INSERT INTO ventas 
                (producto_id, nombre, descripcion, precio_compra, 
                 precio_venta, utilidad, fecha, comentarios, piezas)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                producto_id,
                nombre,
                descripcion,
                precio_compra,
                precio_venta,
                utilidad,
                fecha,
                comentarios,
                piezas
            ))

            conn.commit()

    # Obtener ventas
    cursor.execute("""
        SELECT id, nombre, piezas, precio_compra, 
               precio_venta, utilidad, fecha, comentarios
        FROM ventas
        ORDER BY id DESC
    """)
    ventas_list = cursor.fetchall()

    # Totales
    cursor.execute("""
        SELECT 
            COALESCE(SUM(precio_venta * piezas), 0) as total_v, 
            COALESCE(SUM(utilidad), 0) as total_u 
        FROM ventas
    """)
    totales = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "ventas.html",
        productos=productos_catalogo,
        ventas=ventas_list,
        total_ventas=totales["total_v"],
        total_utilidad=totales["total_u"]
    )

@app.route("/compras", methods=["GET", "POST"])
def compras():
    """
    Gestiona las compras de productos, permitiendo registrar nuevas compras y listar las existentes.
    """
    conn = get_connection()
    cursor = conn.cursor()

    hoy = date.today()

    # Obtener productos del catálogo
    cursor.execute("SELECT id, nombre, descripcion, precio FROM productos")
    productos_catalogo = cursor.fetchall()

    if request.method == "POST":

        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        costo_empresarial = request.form["costo_empresarial"]
        precio_publico = request.form["precio_publico"]
        piezas = int(request.form["piezas"])

        cursor.execute("""
            INSERT INTO compras
            (nombre, descripcion, costo_empresarial, precio_publico, fecha, piezas)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (nombre, descripcion, costo_empresarial, precio_publico, hoy, piezas))

        conn.commit()

    cursor.execute("SELECT * FROM compras ORDER BY id DESC")
    compras_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "compras.html",
        compras=compras_list,
        productos_catalogo=productos_catalogo,
        hoy=hoy
    )

@app.route("/stock")
def stock():
    """
    Calcula y muestra el stock actual usando JOIN.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
    c.nombre,
    COALESCE(SUM(c.piezas), 0) as total_comprado,
    COALESCE(SUM(v.piezas), 0) as total_vendido,
    COALESCE(SUM(c.piezas), 0) - COALESCE(SUM(v.piezas), 0) as stock
    FROM compras c
    LEFT JOIN ventas v ON c.nombre = v.nombre
    GROUP BY c.nombre
    HAVING stock > 0

            """)
    productos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("stock.html", productos=productos)


@app.route("/dashboard")
def dashboard():
    """
    Muestra el dashboard empresarial con KPIs, ventas por día, top productos vendidos y rentables.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ==============================
    # KPIs GENERALES
    # ==============================

    cursor.execute("""
        SELECT 
            COALESCE(SUM(precio_venta * piezas), 0) as total_ventas,
            COALESCE(SUM(utilidad), 0) as total_utilidad,
            COALESCE(AVG(precio_venta * piezas), 0) as ticket_promedio
        FROM ventas
    """)
    kpis = cursor.fetchone()

    # ==============================
    # VENTAS POR DÍA
    # ==============================

    cursor.execute("""
        SELECT fecha, 
               SUM(precio_venta * piezas) as total_dia
        FROM ventas
        GROUP BY fecha
        ORDER BY fecha
    """)
    ventas_por_dia = cursor.fetchall()

    # ==============================
    # TOP PRODUCTOS MÁS VENDIDOS
    # ==============================

    cursor.execute("""
        SELECT nombre,
               SUM(piezas) as total_vendido
        FROM ventas
        GROUP BY nombre
        ORDER BY total_vendido DESC
        LIMIT 5
    """)
    top_vendidos = cursor.fetchall()

    # ==============================
    # TOP PRODUCTOS MÁS RENTABLES
    # ==============================

    cursor.execute("""
        SELECT nombre,
               SUM(utilidad) as utilidad_total
        FROM ventas
        GROUP BY nombre
        ORDER BY utilidad_total DESC
        LIMIT 5
    """)
    top_rentables = cursor.fetchall()

    # ==============================
    # VALOR INVENTARIO
    # ==============================

    cursor.execute("""
        SELECT 
            COALESCE(SUM(c.costo_empresarial * c.piezas),0) -
            COALESCE(SUM(v.precio_compra),0) as valor_inventario
        FROM compras c
        LEFT JOIN ventas v ON c.nombre = v.nombre
    """)
    inventario = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        kpis=kpis,
        ventas_por_dia=ventas_por_dia,
        top_vendidos=top_vendidos,
        top_rentables=top_rentables,
        valor_inventario=inventario["valor_inventario"]
    )

# NECESARIO PARA VERCEL
application = app

if __name__ == "__main__":
    app.run(debug=True)
