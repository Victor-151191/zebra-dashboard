#crea pagina HTML
import sqlite3, os, sys
from datetime import datetime

DB_PATH = "Inventario de impresora zebra.db"
TABLE_NAME = "inventario_zebra"
OUTPUT_FOLDER = "docs"
LOG_FILE = "export_log.txt"

#def log(mensaje):
    #fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    #with open(LOG_FILE, "a", encoding="utf-8") as f:
        #f.write(f"[{fecha}] {mensaje}\n")
    #print(mensaje)

def log(mensaje):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    mensaje_final = f"[{fecha}] {mensaje}"
    with open("export_log.txt", "a", encoding="utf-8") as f:
        f.write(mensaje_final + "\n")
    print(log(f"📦 Total de fichas generadas: {total}"))  # ← Esto muestra en consola

def validar_base():
    if not os.path.exists(DB_PATH):
        log(f"❌ Base de datos no encontrada: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [t[0] for t in cursor.fetchall()]
    conn.close()

    if TABLE_NAME not in tablas:
        log(f"❌ Tabla '{TABLE_NAME}' no encontrada en la base.")
        sys.exit(1)

def generar_fichas_html():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    template = """<!DOCTYPE html>
    <html lang="es">
    <head>
    <link rel="icon" href="qualtec.ico" type="image/x-icon">
        <meta charset="UTF-8">
        <title>Ficha Técnica - {serial}</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
    <img src="jabil.png" alt="image/png">
<video autoplay muted loop id="video-fondo">
<source src="video.mp4" type="video/mp4">
</video>
        <div class="card">
            <h2>Ficha Técnica Zebra</h2>
            <table>
                {rows}
            </table>
            <p class="actualizado">Última actualización: {fecha}</p>
        </div>

<footer class="footer">
<p>
    © 2025 · Ficha técnica desarrollada por Víctor Manuel Salinas González · 
    <a href="https://qualtec.odoo.com/" target="_blank" style="color: #eee; text-decoration: underline;">
    Qualtec Monterrey
    </a>
</p>
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
        html = template.format(serial=serial, rows=html_rows, fecha=fecha_actual)

        with open(os.path.join(OUTPUT_FOLDER, f"{serial}.html"), "w", encoding="utf-8") as f:
            f.write(html)
        log(f"Ficha generada: {serial}.html")
        total += 1

    log(f" Total de fichas generadas: {total}")
    print(f" Total de fichas generadas: {total}")  # ← Esto sí se muestra en consola

