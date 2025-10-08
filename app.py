# 🧱 1. Importaciones y configuración inicial
# ------------------------------------------
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from datetime import datetime

load_dotenv()
app = Flask(__name__)

# Ruta del archivo de base de datos
DB_PATH = os.getenv("DB_PATH", "Inventario de impresora zebra.db")

# Carpeta donde se guardarán las imágenes
UPLOAD_FOLDER = 'static/defectos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 🏠 2. Ruta principal '/' – Mostrar inventario
# --------------------------------------------
@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inventario_zebra ORDER BY ID ASC')
    rows = cursor.fetchall()
    conn.close()
    return render_template('index.html', rows=rows)

# ➕ 3. Ruta '/add' – Agregar nueva impresora
# ------------------------------------------
@app.route('/add', methods=['POST'])
def add():
    try:
        serial = request.form['Serial Number']
        modelo = request.form['Part Number']
        ubicacion = request.form['Location']
        fecha = request.form['Fecha Mtto']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventario_zebra ("Serial Number", "Part Number", "Location", "Fecha Mtto")
            VALUES (?, ?, ?, ?)
        ''', (serial, modelo, ubicacion, fecha))
        conn.commit()
        conn.close()
        return redirect('/')
    except Exception as e:
        return f"Error: {e}", 400

# 🔄 4. Ruta '/update' – Modificar fecha de mantenimiento
# -------------------------------------------------------
@app.route('/update', methods=['POST'])
def update():
    try:
        id = request.form['id']
        fecha = request.form['fecha']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE inventario_zebra SET "Fecha Mtto" = ? WHERE ID = ?', (fecha, id))
        conn.commit()
        conn.close()
        return redirect('/')
    except Exception as e:
        return f"<h2>Error al actualizar: {e}</h2>", 400

# 🖼️ 5. Ruta '/defecto/<id>' – Registrar imagen de defecto
# ---------------------------------------------------------
@app.route('/defecto/<int:id>', methods=['GET', 'POST'])
def registrar_defecto(id):
    if request.method == 'POST':
        try:
            fecha = request.form['fecha']
            descripcion = request.form['descripcion']
            imagen = request.files['imagen']

            fecha_formato = datetime.strptime(fecha, '%Y-%m-%d').strftime('%Y-%m-%d')
            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], str(id), fecha_formato)
            os.makedirs(folder_path, exist_ok=True)

            filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(folder_path, filename)
            imagen.save(imagen_path)

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO defectos (zebra_id, fecha_mtto, descripcion, imagen_path)
                VALUES (?, ?, ?, ?)
            ''', (id, fecha, descripcion, imagen_path))
            conn.commit()
            conn.close()

            return redirect('/')
        except Exception as e:
            return f"<h3>Error al registrar defecto: {e}</h3>", 400

    return render_template('registrar_defecto.html', id=id)

# 📋 6. Ruta '/ver_defectos/<id>' – Ver imágenes por impresora
# ------------------------------------------------------------
@app.route('/ver_defectos/<int:id>')
def ver_defectos(id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT fecha_mtto, descripcion, imagen_path FROM defectos WHERE zebra_id = ?', (id,))
    defectos = cursor.fetchall()
    conn.close()

    html = f"<h2>🧾 Defectos registrados para impresora ID {id}</h2>"
    for fecha, descripcion, path in defectos:
        rel_path = path.replace('static/', '')
        html += f'''
            <div>
                <p><strong>{fecha}</strong>: {descripcion}</p>
                <img src="/static/{rel_path}" width="300"><br><br>
            </div>
        '''
    return html

# 🔐 7. Ruta '/ficha' – Acceso protegido
# --------------------------------------
@app.route('/ficha', methods=['GET', 'POST'])
def ficha():
    load_dotenv(override=True)
    if request.method == 'POST':
        if request.form['password'] == os.getenv("QR_PASSWORD", "Zebra2025"):
            return redirect('/docs/inventario_exportado.html')
        else:
            return "<h3>Contraseña incorrecta</h3>"
    return '''
        <h2>🔐 Acceso protegido</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña">
            <button type="submit">Ingresar</button>
        </form>
    '''

# 🚀 8. Lanzamiento del servidor
# ------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)