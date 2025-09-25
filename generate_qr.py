import sqlite3
import qrcode
import os

# Ruta a la base de datos
db_path = r'C:\Program Files\DB Browser for SQLite\Inventario de impresora jabil.db'

# Carpeta donde guardar los QR
output_folder = "qr_codes"
os.makedirs(output_folder, exist_ok=True)

# Tu URL base de GitHub Pages (ajusta con tu usuario y repo)
base_url = "https://tuusuario.github.io/zebra-dashboard"

# Conexión a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT "Serial Number" FROM inventario_zebra')
rows = cursor.fetchall()
conn.close()

# Generar QR solo para seriales válidos
for row in rows:
    serial = row[0]

    if serial is None or str(serial).strip().upper() == "NULL":
        print("⏭️ Serial vacío, QR no generado:", row)
        continue

    url = f"{base_url}/{serial}.html"
    qr = qrcode.make(url)
    qr_path = os.path.join(output_folder, f"{serial}.png")
    qr.save(qr_path)
    print(f"✅ QR generado para {serial} → {url}")

