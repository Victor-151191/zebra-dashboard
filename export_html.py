# export_html.py

print("Ejecutando export_html.py")

import sqlite3, os
from datetime import datetime
import shutil
shutil.copy("C:\\qr_dashboard\\docs\\qualtec.ico", "docs/favicon.ico")
import shutil, os

favicon_origen = r"C:\qr_dashboard\docs\qualtec.ico"
favicon_destino = "docs/favicon.ico"

if os.path.exists(favicon_origen):
    shutil.copy(favicon_origen, favicon_destino)
    print("✅ Favicon copiado correctamente")
else:
    print(f"⚠️ El archivo favicon no fue encontrado: {favicon_origen}")

def generar_fichas_html():
    db_path = r'C:\Program Files\DB Browser for SQLite\Inventario de impresora jabil.db'
    output_folder = "docs"
    os.makedirs(output_folder, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inventario_zebra')
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

    for row in rows:
        data = dict(zip(columns, row))
        serial = data.get("Serial Number")

        if serial is None or str(serial).strip().upper() == "NULL":
            print("Fila ignorada por serial vacío:", data)
            continue

        html_rows = "\n".join([f"<tr><td class='label'>{k}</td><td>{v}</td></tr>" for k, v in data.items()])
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
        html = template.format(serial=serial, rows=html_rows, fecha=fecha_actual)

        with open(os.path.join(output_folder, f"{serial}.html"), "w", encoding="utf-8") as f:
            f.write(html)

if __name__ == "__main__":
    generar_fichas_html()
    print("Fichas HTML generadas")

