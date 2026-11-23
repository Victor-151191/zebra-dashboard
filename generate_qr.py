import os
import sqlite3
import sys
import cv2
import qrcode
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Cargar configuración desde archivo .env
load_dotenv(override=True)
PROTECCION = os.getenv("PROTECCION_FICHA", "ON").strip().upper()

# Rutas y parámetros base
DB_PATH = "Inventario de impresora zebra.db"
OUTPUT_FOLDER = "qr_codes"
DOCS_FOLDER = "docs"
BASE_URL = "https://victor-151191.github.io/zebra-dashboard/docs/"
FONT_PATH = "arial.ttf"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

try:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT ID, "Serial Number", "Host Name" '
            'FROM inventario_zebra ORDER BY ID ASC'
        )
        rows = cursor.fetchall()
except Exception as e:
    print(f"Error al conectar con la base: {e}")
    sys.exit(1)

print(f"Total de filas leídas: {len(rows)}")

try:
    font_host = ImageFont.truetype(FONT_PATH, 30)
    font_id = ImageFont.truetype(FONT_PATH, 30)
    font_serial = ImageFont.truetype(FONT_PATH, 30)
except Exception:
    font_host = font_id = font_serial = ImageFont.load_default()

lector_qr = cv2.QRCodeDetector()
total_qr = 0

for row in rows:
    id_eq, serial, host_name = row
    print(f"\nProcesando fila -> ID: {id_eq}, Serial: {serial}, Host: {host_name}")

    if not serial or str(serial).strip().upper() == "NULL":
        print("Serial vacío o inválido, QR no generado.")
        continue
    if not host_name or str(host_name).strip().upper() == "NULL":
        print("Host Name vacío o inválido, QR no generado.")
        continue

    serial_norm = str(serial).strip().replace(" ", "_").replace("/", "-")
    host_norm = str(host_name).strip()

    index_0 = host_norm.find("0")
    parte_variable = host_norm[index_0 + 1:] if index_0 != -1 else host_norm
    texto_host = f"Host: {parte_variable}"

    url = f"{BASE_URL}{serial_norm}.html"
    estado = "Protegida" if PROTECCION == "ON" else "Libre"

    ficha_path = os.path.join(DOCS_FOLDER, f"{serial_norm}.html")
    if not os.path.exists(ficha_path):
        print(f"Ficha no encontrada: {ficha_path}")
        continue

    filename = f"{parte_variable}_{serial_norm}_{estado}.png"
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    if os.path.exists(filepath):
        print(f"QR ya existe, se sobrescribe: {filename}")

    try:
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_img = qr_img.resize((150, 150))

        img = Image.new("RGB", (300, 230), "white")
        img.paste(qr_img, (75, 40))

        draw = ImageDraw.Draw(img)

        # Host arriba a la izquierda
        draw.text((10, 5), texto_host, font=font_host, fill="black")

        # ID arriba a la derecha
        texto_id = f"ID: {id_eq}"
        ancho_id = draw.textlength(texto_id, font=font_id)
        draw.text((300 - ancho_id - 10, 5), texto_id, font=font_id, fill="black")

        # Serial centrado abajo
        serial_text = f"Serial: {serial_norm}"
        serial_width = draw.textlength(serial_text, font=font_serial)
        draw.text(((300 - serial_width) // 2, 195), serial_text, font=font_serial, fill="black")

        img.save(filepath)
        print(f"QR generado y guardado: {filename}")
        total_qr += 1

        img_cv = cv2.imread(filepath)
        if img_cv is not None:
            texto_qr, _, _ = lector_qr.detectAndDecode(img_cv)
            if texto_qr:
                print(f"Contenido real del QR: {texto_qr}")
            else:
                print("Advertencia: no se pudo verificar el contenido del QR generado.")

    except Exception as e:
        print(f"Error al generar QR para ID {id_eq}: {e}")

if total_qr == 0:
    print("\nNo se generó ningún código QR nuevo. Verifica los datos en la base o las fichas en /docs.")
else:
    print(f"\nTotal de códigos QR generados: {total_qr}")
    print(f"Carpeta de salida: {OUTPUT_FOLDER}")