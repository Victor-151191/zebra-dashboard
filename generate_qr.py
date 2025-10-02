import sqlite3, qrcode, os
from PIL import Image, ImageDraw, ImageFont

# Configuración
db_path = "Inventario de impresora zebra.db"
output_folder = "qr_codes"
base_url = "https://victor-151191.github.io/zebra-dashboard/"
font_path = "arial.ttf"  # Asegúrate de tener esta fuente o usa una del sistema

os.makedirs(output_folder, exist_ok=True)

# Conexión a la base
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT ID, "Serial Number" FROM inventario_zebra ORDER BY ID ASC')
rows = cursor.fetchall()
conn.close()

for row in rows:
    id, serial = row
    if not serial or str(serial).strip().upper() == "NULL":
        print("Serial vacío, QR no generado:", row)
        continue

    serial = str(serial).strip()
    id = str(id).strip()
    url = f"{base_url}{serial}.html"

    # Generar QR
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_img = qr_img.resize((300, 300))

    # Crear imagen base
    img = Image.new("RGB", (300, 360), "white")
    img.paste(qr_img, (0, 30))  # Deja espacio arriba para el ID

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_path, 16)
    except:
        font = ImageFont.load_default()

    # Esquina superior derecha: ID
    draw.text((10, 5), f"ID: {id}", font=font, fill="black")

    # Centrado debajo del QR: Serial
    serial_text = f"Serial: {serial}"
    bbox = draw.textbbox((0, 0), serial_text, font=font)
    text_width = bbox[2] - bbox[0]
    x_center = (300 - text_width) // 2
    draw.text((x_center, 340), serial_text, font=font, fill="black")


    # Guardar imagen
    filename = f"{id}_{serial}.png"
    img.save(os.path.join(output_folder, filename))

    print(f"QR generado para ID {id} / Serial {serial} → {url}")