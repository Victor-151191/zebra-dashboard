import sqlite3, qrcode, os
from PIL import Image, ImageDraw, ImageFont
from pyzbar.pyzbar import decode
from dotenv import load_dotenv

# 🔐 Cargar configuración desde .env
load_dotenv(override=True)
PROTECCION = os.getenv("PROTECCION_FICHA", "ON")

# 📁 Configuración
db_path = "Inventario de impresora zebra.db"
output_folder = "qr_codes"
docs_folder = "docs"
base_url = "https://Victor-151191.github.io/zebra-dashboard/docs/"
font_path = "arial.ttf"

# 📁 Crear carpeta si no existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 🔗 Conexión a la base
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT ID, "Serial Number" FROM inventario_zebra ORDER BY ID ASC')
    rows = cursor.fetchall()
    conn.close()
except Exception as e:
    print(f"💥 Error al conectar con la base: {e}")
    exit()

print(f"📦 Total de filas leídas: {len(rows)}")

# 🔄 Generación de QR por registro
total_qr = 0
for row in rows:
    id, serial = row
    print(f"\n🔍 Procesando fila → ID: {id}, Serial: {serial}")

    if not serial or str(serial).strip().upper() == "NULL":
        print("⚠️ Serial vacío o inválido, QR no generado.")
        continue

    serial = str(serial).strip().replace(" ", "_").replace("/", "-")
    id = str(id).strip()
    url = f"{base_url}{serial}.html"
    estado = "🔒 Protegida" if PROTECCION == "ON" else "🔓 Libre"

    # 📁 Verifica que el archivo HTML exista en /docs
    ficha_path = os.path.join(docs_folder, f"{serial}.html")
    if not os.path.exists(ficha_path):
        print(f"❌ Ficha no encontrada: {ficha_path}")
        continue

    # 📦 Verifica si el QR ya existe
    filename = f"{id}_{serial}_{estado.replace(' ', '_')}.png"
    filepath = os.path.join(output_folder, filename)
    if os.path.exists(filepath):
        print(f"📌 QR ya existe, no se regenera: {filename}")
        continue

    # 🎯 Generar QR
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_img = qr_img.resize((300, 300))

        # 🖼️ Crear imagen base
        img = Image.new("RGB", (300, 380), "white")
        img.paste(qr_img, (0, 30))

        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype(font_path, 16)
        except:
            font = ImageFont.load_default()

        draw.text((10, 5), f"ID: {id}", font=font, fill="black")
        draw.text((180, 5), estado, font=font, fill="black")

        serial_text = f"Serial: {serial}"
        bbox = draw.textbbox((0, 0), serial_text, font=font)
        text_width = bbox[2] - bbox[0]
        x_center = (300 - text_width) // 2
        draw.text((x_center, 350), serial_text, font=font, fill="black")

        img.save(filepath)
        print(f"✅ QR generado y guardado: {filename}")
        total_qr += 1

        # 🔍 Verificar contenido del QR generado
        decoded = decode(Image.open(filepath))
        if decoded:
            contenido_qr = decoded[0].data.decode("utf-8")
            print(f"📥 Contenido real del QR: {contenido_qr}")
        else:
            print("⚠️ No se pudo leer el contenido del QR generado.")

    except Exception as e:
        print(f"💥 Error al generar QR para ID {id}: {e}")

# 📊 Resumen final
if total_qr == 0:
    print("\n⚠️ No se generó ningún código QR nuevo. Verifica los datos en la base o las fichas en /docs.")
else:
    print(f"\n✅ Total de códigos QR generados: {total_qr}")
    print(f"📁 Carpeta de salida: {output_folder}")