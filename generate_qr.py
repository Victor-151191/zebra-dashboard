import sqlite3
import qrcode
import os

# Ruta a la base de datos
db_path = r'C:\Program Files\DB Browser for SQLite\Inventario de impresora jabil.db'

# Carpeta donde guardar los QR
output_folder = "qr_codes"
os.makedirs(output_folder, exist_ok=True)

# Tu URL base de GitHub Pages (ajusta con tu usuario y repo)
base_url = "https://victor-151191.github.io/zebra-dashboard/"

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
        print("Serial vacío, QR no generado:", row)
        continue

    url = f"{base_url}/{serial}.html"

    # Personalización del color del QR
    qr = qrcode.QRCode(
        version=1,
        box_size=20,
        border=6
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Cambia el color aquí 
    img = qr.make_image(fill_color="purple", back_color="white")

    qr_path = os.path.join(output_folder, f"{serial}.png")
    img.save(qr_path)

    print(f"QR generado para {serial} → {url}")