Conexion a base de datos tienda prendas de ropa

# Tienda ModaNova

Este proyecto es una aplicación web para la gestión de una tienda en línea llamada Tienda ModaNova. La aplicación permite registrar, gestionar y visualizar compras, clientes y productos utilizando Flask y MySQL.

## Contenido

- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Rutas de la Aplicación](#rutas-de-la-aplicación)
- [Contribución](#contribución)
- [Licencia](#licencia)

## Instalación

### Requisitos

- Python 3.x
- MySQL
- Flask
- Conector MySQL para Python (`mysql-connector-python`)
- Bootstrap (para el diseño de la interfaz de usuario)

### Pasos para la instalación

1. Clona el repositorio:

    ```sh
    git clone https://github.com/tuusuario/tu-repositorio.git
    cd tu-repositorio
    ```

2. Crea un entorno virtual y actívalo:

    ```sh
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instala las dependencias necesarias:

    ```sh
    pip install flask mysql-connector-python
    ```

4. Configura la base de datos MySQL:

    - Crea una base de datos llamada `tienda`.
    - Asegúrate de que la base de datos tiene las tablas necesarias (`clientes`, `productos`, `compras`).
    - Puedes usar un script SQL para crear las tablas (ejemplo):

    ```sql
    CREATE TABLE clientes (
        id_cliente INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100),
        apellido VARCHAR(100),
        email VARCHAR(100) UNIQUE,
        telefono VARCHAR(15),
        direccion VARCHAR(255)
    );

    CREATE TABLE productos (
        id_producto INT AUTO_INCREMENT PRIMARY KEY,
        nombre_producto VARCHAR(100),
        descripcion TEXT,
        precio DECIMAL(10, 2),
        stock INT
    );

    CREATE TABLE compras (
        id_compra INT AUTO_INCREMENT PRIMARY KEY,
        id_cliente INT,
        id_producto INT,
        fecha_compra DATE,
        cantidad INT,
        total DECIMAL(10, 2),
        FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
        FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
    );
    ```

5. Ejecuta la aplicación:

    ```sh
    flask run
    ```

## Uso

### Navegación en la aplicación

- **Inicio**: Muestra la página principal con un carrusel de productos.
- **Registrar Factura**: Permite registrar nuevas facturas.
- **Ver Tablas**: Muestra tablas de compras, clientes y productos.
- **Gestionar Productos**: Permite agregar, editar y eliminar productos.

## Estructura del Proyecto

