# Crea página HTML para cada impresora Zebra
import sqlite3, os, sys, shutil
from datetime import datetime
from dotenv import load_dotenv

# Configuración de rutas y nombres
DB_PATH = "Inventario de impresora zebra.db"
TABLE_NAME = "inventario_zebra"
OUTPUT_FOLDER = "docs"
LOG_FILE = "log.txt"

# Función para registrar mensajes en log.txt y mostrar en consola
def log(mensaje):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    mensaje_final = f"[{fecha}] {mensaje}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(mensaje_final + "\n")
    print(mensaje_final)

# Verifica que la base y la tabla existan
def validar_base():
    if not os.path.exists(DB_PATH):
        log(f"Base de datos no encontrada: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [t[0] for t in cursor.fetchall()]
    conn.close()

    if TABLE_NAME not in tablas:
        log(f"Tabla '{TABLE_NAME}' no encontrada en la base.")
        sys.exit(1)

# Genera fichas HTML para cada registro con serial válido
def generar_fichas_html():
    load_dotenv(override=True)  # Recarga .env en tiempo real
    PASSWORD = os.getenv("QR_PASSWORD", "QR_PASSWORD")
    PROTECCION = os.getenv("PROTECCION_FICHA", "ON")

    # Limpia carpeta de fichas anteriores
    for archivo in os.listdir(OUTPUT_FOLDER):
        ruta = os.path.join(OUTPUT_FOLDER, archivo)
    if archivo.endswith(".html"):
        os.remove(ruta)

    log("Conectando a la base de datos...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    log(f"Registros encontrados: {len(rows)}")

    # Bloque de protección con contraseña
    password_block = f'''<script>
window.addEventListener("DOMContentLoaded", function() {{
const clave = prompt("Ingrese la contraseña para acceder a esta ficha:");
if (!clave || clave.trim() !== "{PASSWORD}") {{
    document.body.innerHTML = `
    <div style="text-align:center; font-family:sans-serif; margin-top:100px;">
        <img src="qualtec.ico" width="80" />
        <h2 style="color:#B22222;">Acceso denegado</h2>
        <p style="font-size:20px; color:black; margin-top:40px;">Esta ficha técnica está protegida. Verifique la contraseña o contacte a soporte IT.</p>
        <button onclick="location.reload()" style="margin-top:20px; padding:10px 20px;">Reintentar</button>
        <p style="font-size:12px; color:gray; margin-top:40px;">Sistema desarrollado por Víctor Manuel Salinas González</p>
    </div>
    `;
}}
}});
</script>'''

    # Plantilla HTML base con banner dinámico
    template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.2, maximum-scale=1.5, user-scalable=no">
    <title>Ficha Técnica - {serial}</title>
    <link rel="stylesheet" href="style.css">
    <link rel="icon" href="qualtec.ico" type="image/x-icon">
</head>
<body>
    <div style="position:fixed; top:10px; right:10px; 
                background:#eee; padding:5px 10px; 
                border-radius:5px; font-weight:bold;">
        {banner}
    </div>

    <div class="ficha">
        <h2>Ficha Técnica Zebra</h2>
        <table>
            {rows}
        </table>
        <p class="actualizado">Última actualización: {fecha}</p>
    </div>

    <footer class="footer">
        <p>© 2025 · Ficha técnica desarrollada por Víctor Manuel Salinas González · 
        <!-- Número de teléfono clickeable -->
<a href="tel:8118211034">Llámanos al 81 18 21 1034</a>
    </footer>
</body>
</html>
"""

    total = 0
    for row in rows:
        data = dict(zip(columns, row))
        serial = data.get("Serial Number")

        if not serial or str(serial).strip().upper() == "NULL":
            log(f"Fila ignorada por serial vacío: {data}")
            continue

        html_rows = "\n".join([f"<tr><td class='label'>{k}</td><td>{v}</td></tr>" for k, v in data.items()])
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
        banner = "Protegida" if PROTECCION == "ON" else "Libre"

        # Genera HTML con o sin protección según .env
        if PROTECCION == "ON":
            html = password_block + template.format(serial=serial, rows=html_rows, fecha=fecha_actual, banner=banner)
        else:
            html = template.format(serial=serial, rows=html_rows, fecha=fecha_actual, banner=banner)

        with open(os.path.join(OUTPUT_FOLDER, f"{serial}.html"), "w", encoding="utf-8") as f:
            f.write(html)

        log(f"Ficha generada: {serial}.html ({banner})")
        total += 1

    log(f"Total de fichas generadas: {total}")

# Punto de entrada
if __name__ == "__main__":
    validar_base()
    generar_fichas_html()