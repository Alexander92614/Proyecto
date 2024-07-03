from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        database='tienda',
        password=''
    )

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/compras")
def obtener_compras():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        consulta_compras = """
        SELECT c.nombre AS cliente_nombre, c.apellido AS cliente_apellido,
               p.nombre_producto, comp.fecha_compra, comp.cantidad, comp.total
        FROM compras comp
        JOIN clientes c ON comp.id_cliente = c.id_cliente
        JOIN productos p ON comp.id_producto = p.id_producto
        """
        cursor.execute(consulta_compras)
        compras = cursor.fetchall()

        consulta_clientes = "SELECT id_cliente, nombre, apellido FROM clientes"
        cursor.execute(consulta_clientes)
        clientes = cursor.fetchall()

        consulta_productos = "SELECT id_producto, nombre_producto, precio, stock FROM productos"
        cursor.execute(consulta_productos)
        productos = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('tablas.html', compras=compras, clientes=clientes, productos=productos)
    except mysql.connector.Error as e:
        return f"Error al conectar a MySQL: {e}"

@app.route("/factura", methods=['GET', 'POST'])
def factura():
    if request.method == 'POST':
        if 'eliminar' in request.form:
            return eliminar_factura(request.form['factura_id'])
        else:
            return registrar_factura(request.form)
    else:
        return mostrar_facturas()

def eliminar_factura(factura_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id_cliente, id_producto, cantidad FROM compras WHERE id_compra = %s", (factura_id,))
        factura = cursor.fetchone()
        if not factura:
            return f"No se encontró la factura con ID {factura_id}"

        id_cliente, id_producto, cantidad = factura

        cursor.execute("DELETE FROM compras WHERE id_compra = %s", (factura_id,))
        cursor.execute("UPDATE productos SET stock = stock + %s WHERE id_producto = %s", (cantidad, id_producto))
        cursor.execute("SELECT COUNT(*) FROM compras WHERE id_cliente = %s", (id_cliente,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('factura'))
    except mysql.connector.Error as e:
        return f"Error al conectar a MySQL: {e}"

def registrar_factura(form_data):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cliente_nombre, cliente_apellido, email, telefono, direccion = (
            form_data['cliente_nombre'], form_data['cliente_apellido'],
            form_data['email'], form_data['telefono'], form_data['direccion']
        )
        id_producto = int(form_data['nombre_producto'])
        fecha_compra, cantidad = (
            form_data['fecha_compra'], int(form_data['cantidad'])
        )

        cursor.execute("SELECT id_cliente FROM clientes WHERE email = %s", (email,))
        cliente = cursor.fetchone()
        if cliente:
            id_cliente = cliente[0]
        else:
            cursor.execute("""
                INSERT INTO clientes (nombre, apellido, email, telefono, direccion)
                VALUES (%s, %s, %s, %s, %s)
            """, (cliente_nombre, cliente_apellido, email, telefono, direccion))
            id_cliente = cursor.lastrowid

        cursor.execute("SELECT stock, precio FROM productos WHERE id_producto = %s", (id_producto,))
        producto = cursor.fetchone()
        if not producto:
            return f"No se encontró el producto con ID {id_producto}"

        stock, precio = producto
        if stock < cantidad:
            return f"Stock insuficiente para el producto con ID {id_producto}"

        total = precio * cantidad

        cursor.execute("""
            INSERT INTO compras (id_cliente, id_producto, fecha_compra, cantidad, total)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_cliente, id_producto, fecha_compra, cantidad, total))
        cursor.execute("UPDATE productos SET stock = stock - %s WHERE id_producto = %s", (cantidad, id_producto))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('factura'))
    except mysql.connector.Error as e:
        return f"Error al conectar a MySQL: {e}"

def mostrar_facturas():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        consulta_facturas = """
        SELECT comp.id_compra, c.nombre AS cliente_nombre, c.apellido AS cliente_apellido,
               c.email, c.telefono, c.direccion, p.nombre_producto, comp.fecha_compra, comp.cantidad, comp.total
        FROM compras comp
        JOIN clientes c ON comp.id_cliente = c.id_cliente
        JOIN productos p ON comp.id_producto = p.id_producto
        """
        cursor.execute(consulta_facturas)
        facturas = cursor.fetchall()

        consulta_productos = "SELECT id_producto, nombre_producto, precio, stock FROM productos"
        cursor.execute(consulta_productos)
        productos = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('factura.html', facturas=facturas, productos=productos)
    except mysql.connector.Error as e:
        return f"Error al conectar a MySQL: {e}"

@app.route("/productos", methods=['GET', 'POST'])
def gestionar_productos():
    if request.method == 'POST':
        return agregar_producto(request.form)
    else:
        return mostrar_productos()

def agregar_producto(form_data):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        nombre_producto, descripcion, precio, stock = (
            form_data['nombre_producto'], form_data['descripcion'],
            float(form_data['precio']), int(form_data['stock'])
        )

        cursor.execute("""
            INSERT INTO productos (nombre_producto, descripcion, precio, stock)
            VALUES (%s, %s, %s, %s)
        """, (nombre_producto, descripcion, precio, stock))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('gestionar_productos'))
    except mysql.connector.Error as e:
        return f"Error al conectar a MySQL: {e}"

def mostrar_productos():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        consulta_productos = "SELECT id_producto, nombre_producto, descripcion, precio, stock FROM productos"
        cursor.execute(consulta_productos)
        productos = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('productos.html', productos=productos)
    except mysql.connector.Error as e:
        return f"Error al conectar a MySQL: {e}"

@app.route("/productos/editar/<int:id>", methods=['GET', 'POST'])
def editar_producto(id):
    if request.method == 'POST':
        return actualizar_producto(id, request.form)
    else:
        return mostrar_formulario_editar(id)

def mostrar_formulario_editar(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id_producto, nombre_producto, descripcion, precio, stock FROM productos WHERE id_producto = %s", (id,))
        producto = cursor.fetchone()

        cursor.close()
        connection.close()

        if producto:
            return render_template('editar_producto.html', producto=producto)
        else:
            return f"No se encontró el producto con ID {id}"
    except mysql.connector.Error as e:
        return f"Error al conectar a MySQL: {e}"

def actualizar_producto(id, form_data):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        nombre_producto, descripcion, precio, stock = (
            form_data['nombre_producto'], form_data['descripcion'],
            float(form_data['precio']), int(form_data['stock'])
        )

        cursor.execute("""
            UPDATE productos
            SET nombre_producto = %s, descripcion = %s, precio = %s, stock = %s
            WHERE id_producto = %s
        """, (nombre_producto, descripcion, precio, stock, id))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('gestionar_productos'))
    except mysql.connector.Error as e:
        return f"Error al conectar a MySQL: {e}"

@app.route("/productos/eliminar/<int:id>", methods=['POST'])
def eliminar_producto(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Verificar si el producto está asociado con alguna compra
        cursor.execute("SELECT COUNT(*) FROM compras WHERE id_producto = %s", (id,))
        if cursor.fetchone()[0] > 0:
            return f"No se puede eliminar el producto con ID {id} porque está asociado a una o más compras."

        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id,))

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('gestionar_productos'))
    except mysql.connector.Error as e:
        return f"Error al conectar a MySQL: {e}"

if __name__ == "__main__":
    app.run(debug=True)
