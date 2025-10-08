# 🧱 1. Importaciones y configuración inicial
# ------------------------------------------
from flask import Flask, render_template, request, redirect
import sqlite3
import os
from dotenv import load_dotenv  # Carga variables desde .env

load_dotenv()

app = Flask(__name__)

# Ruta del archivo de base de datos (desde .env o valor por defecto)
DB_PATH = os.getenv("DB_PATH", "Inventario de impresora zebra.db")

# 🏠 2. Ruta principal '/' – Mostrar inventario
# --------------------------------------------
@app.route('/')
def index():
    # Conexión a la base de datos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Consulta todos los registros ordenados por ID
    cursor.execute('SELECT * FROM inventario_zebra ORDER BY ID ASC')
    rows = cursor.fetchall()
    conn.close()

    # Renderiza la plantilla con los datos
    return render_template('index.html', rows=rows)

# ➕ 3. Ruta '/add' – Agregar nueva impresora
# ------------------------------------------
@app.route('/add', methods=['POST'])
def add():
    try:
        # Captura los campos enviados desde el formulario HTML
        serial = request.form['Serial Number']
        modelo = request.form['Part Number']
        ubicacion = request.form['Location']
        fecha = request.form['Fecha Mtto']

        # Inserta el nuevo registro en la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO inventario_zebra ("Serial Number", "Part Number", "Location", "Fecha Mtto") VALUES (?, ?, ?, ?)',
                    (serial, modelo, ubicacion, fecha))
        conn.commit()
        conn.close()

        # Redirige al inicio después de guardar
        return redirect('/')
    except Exception as e:
        return f"Error: {e}", 400  # Muestra el error si algo falla

# 🔄 4. Ruta '/update' – Modificar fecha de mantenimiento
# -------------------------------------------------------
@app.route('/update', methods=['POST'])
def update():
    try:
        # Captura el ID y la nueva fecha desde el formulario
        id = request.form['id']
        fecha = request.form['fecha']

        # Ejecuta el UPDATE en la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE inventario_zebra SET "Fecha Mtto" = ? WHERE ID = ?', (fecha, id))
        conn.commit()
        conn.close()

        # Redirige al inicio después de actualizar
        return redirect('/')
    except Exception as e:
        return f"<h2>Error al actualizar: {e}</h2>", 400

# 🔐 5. Ruta '/ficha' – Acceso a la ficha electrónica
# ---------------------------------------------------
# 🔓 Ruta '/ficha' – Acceso libre a la ficha electrónica
#@app.route('/ficha')
#def ficha():
    #return redirect('/docs/inventario_exportado.html')
@app.route('/ficha', methods=['GET', 'POST'])
def ficha():
    load_dotenv(override=True)  # Recarga el estado actualizado

    #Si se envió el formulario con contraseña
    if request.method == 'POST':
        if request.form['password'] == os.getenv("QR_PASSWORD", "Zebra2025"):
            return redirect('/docs/inventario_exportado.html')
        else:
            return "<h3>Contraseña incorrecta</h3>"

    # Muestra el formulario de acceso
    return '''
        <h2>🔐 Acceso protegido</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña">
            <button type="submit">Ingresar</button>
        </form>
    '''

# 🚀 6. Lanzamiento del servidor
# ------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)