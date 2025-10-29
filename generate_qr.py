import sqlite3, qrcode, os
from PIL import Image, ImageDraw, ImageFont
from pyzbar.pyzbar import decode
from dotenv import load_dotenv

# 🔧 Cargar configuración desde archivo .env
load_dotenv(override=True)
PROTECCION = os.getenv("PROTECCION_FICHA", "ON")

# 📁 Rutas y parámetros base
db_path = "Inventario de impresora zebra.db"
output_folder = "qr_codes"
docs_folder = "docs"
base_url = "https://Victor-151191.github.io/zebra-dashboard/docs/"
font_path = "arial.ttf"  # Fuente para los textos en la imagen

# 📂 Crear carpeta de salida si no existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 🗃️ Leer datos desde la base
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT ID, "Serial Number" FROM inventario_zebra ORDER BY ID ASC')
    rows = cursor.fetchall()
    conn.close()
except Exception as e:
    print(f"Error al conectar con la base: {e}")
    exit()

print(f"Total de filas leídas: {len(rows)}")

# 🔄 Generar QR por cada registro
total_qr = 0
for row in rows:
    id, serial = row
    print(f"\n Procesando fila → ID: {id}, Serial: {serial}")

    # Validar serial
    if not serial or str(serial).strip().upper() == "NULL":
        print("Serial vacío o inválido, QR no generado.")
        continue

    # Normalizar datos
    serial = str(serial).strip().replace(" ", "_").replace("/", "-")
    id = str(id).strip()
    url = f"{base_url}{serial}.html"
    estado = "Protegida" if PROTECCION == "ON" else "Libre"

    # Verificar que la ficha HTML exista
    ficha_path = os.path.join(docs_folder, f"{serial}.html")
    if not os.path.exists(ficha_path):
        print(f"Ficha no encontrada: {ficha_path}")
        continue

    # Evitar duplicados
    filename = f"{id}_{serial}_{estado.replace(' ', '_')}.png"
    filepath = os.path.join(output_folder, filename)
    if os.path.exists(filepath):
        print(f"QR ya existe, no se regenera: {filename}")
        continue

    try:
        # 🧠 Generar código QR compacto
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_img = qr_img.resize((150, 150))  # Tamaño reducido para etiquetas pequeñas

        # 🖼️ Crear imagen base del tamaño físico de la etiqueta (300x177 px ≈ 1.181 x 0.591 in a 300 dpi)
        img = Image.new("RGB", (300, 230), "white")#(A=400, es el ancho y B=155, es el largo)
        img.paste(qr_img, (70, 40))  # Centrado horizontal

        draw = ImageDraw.Draw(img)

        # 🖋️ Cargar fuentes con tamaños optimizados
        try:
            font_id = ImageFont.truetype(font_path, 30)       # ID
            font_estado = ImageFont.truetype(font_path, 30)    # Estado
            font_serial = ImageFont.truetype(font_path, 30)    # Serial
        except:
            font_id = font_estado = font_serial = ImageFont.load_default()

        # 🏷️ ID en esquina superior izquierda
        draw.text((10, 5), f"ID: {id}", font=font_id, fill="black")

        # 🔒 Estado en esquina superior derecha
        #estado_width = draw.textlength(estado, font=font_estado)
        #draw.text((300 - estado_width - 10, 5), estado, font=font_estado, fill="black")

        # 🔢 Serial centrado debajo del QR
        serial_text = f"Serial: {serial}"
        serial_width = draw.textlength(serial_text, font=font_serial)
        draw.text(((300 - serial_width) // 2, 200), serial_text, font=font_serial, fill="black")
                #(300)mover lados      (2)centrado(200)Arriba abajo
        # 💾 Guardar imagen final
        img.save(filepath)
        print(f"QR generado y guardado: {filename}")
        total_qr += 1

        # 🔍 Verificar contenido del QR
        decoded = decode(Image.open(filepath))
        if decoded:
            contenido_qr = decoded[0].data.decode("utf-8")
            print(f"Contenido real del QR: {contenido_qr}")
        else:
            print("No se pudo leer el contenido del QR generado.")

    except Exception as e:
        print(f"Error al generar QR para ID {id}: {e}")

# 📊 Resumen final
if total_qr == 0:
    print("\n No se generó ningún código QR nuevo. Verifica los datos en la base o las fichas en /docs.")
else:
    print(f"\n Total de códigos QR generados: {total_qr}")
    print(f" Carpeta de salida: {output_folder}")