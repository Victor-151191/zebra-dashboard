import sqlite3, os

db_path = r'C:\Program Files\DB Browser for SQLite\Inventario de impresora jabil.db'
output_folder = "docs"  # GitHub Pages sirve desde esta carpeta por defecto
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
    <meta charset="UTF-8">
    <title>Ficha Técnica - {serial}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="card">
        <h2>Ficha Técnica Zebra</h2>
        <table>
            {rows}
        </table>
    </div>
</body>
</html>
"""

for row in rows:
    data = dict(zip(columns, row))
    serial = data.get("Serial Number")

    if serial is None or str(serial).strip().upper() == "NULL":
        print("⏭️ Fila ignorada por serial vacío:", data)
        continue  # Salta esta fila

    html_rows = "\n".join([f"<tr><td class='label'>{k}</td><td>{v}</td></tr>" for k, v in data.items()])
    html = template.format(serial=serial, rows=html_rows)
    with open(os.path.join(output_folder, f"{serial}.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Ficha generada: {serial}.html")
    html_rows = "\n".join([f"<tr><td class='label'>{k}</td><td>{v}</td></tr>" for k, v in data.items()])
    html = template.format(serial=serial, rows=html_rows)
    with open(os.path.join(output_folder, f"{serial}.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Ficha generada: {serial}.html")