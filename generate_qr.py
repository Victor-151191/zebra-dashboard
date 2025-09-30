import sqlite3, qrcode, os

db_path = "Inventario de impresora zebra.db"
output_folder = "qr_codes"
os.makedirs(output_folder, exist_ok=True)

base_url = "https://victor-151191.github.io/zebra-dashboard/"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT "Serial Number" FROM inventario_zebra')
rows = cursor.fetchall()
conn.close()

for row in rows:
    serial = row[0]
    if not serial or str(serial).strip().upper() == "NULL":
        print("⏭️ Serial vacío, QR no generado:", row)
        continue

    url = f"{base_url}/{serial}.html"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="darkblue", back_color="white")
    img.save(os.path.join(output_folder, f"{serial}.png"))
    print(f"✅ QR generado para {serial} → {url}")