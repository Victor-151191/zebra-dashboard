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
#base_url = "https://victor151191.pythonanywhere.com/docs/"
base_url = "https://Victor-151191.github.io/zebra-dashboard/docs/"
font_path = "arial.ttf"  # Fuente para los textos en la imagen

# 📂 Crear carpeta de salida si no existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 🗃️ Leer datos desde la base
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT ID, "Serial Number", "Host Name" FROM inventario_zebra ORDER BY ID ASC')
    rows = cursor.fetchall()
    conn.close()
except Exception as e:
    print(f"Error al conectar con la base: {e}")
    exit()

print(f"Total de filas leídas: {len(rows)}")

# 🔄 Generar QR por cada registro
total_qr = 0
for row in rows:
    id, serial, host_name = row
    print(f"\n Procesando fila → ID: {id}, Serial: {serial}, Host: {host_name}")

    # Validar serial y host
    if not serial or str(serial).strip().upper() == "NULL":
        print("Serial vacío o inválido, QR no generado.")
        continue
    if not host_name or str(host_name).strip().upper() == "NULL":
        print("Host Name vacío o inválido, QR no generado.")
        continue

    # Normalizar datos
    serial = str(serial).strip().replace(" ", "_").replace("/", "-")
    host_name = str(host_name).strip()

    # Extraer parte después del primer "0"
    index_0 = host_name.find("0")
    parte_variable = host_name[index_0 + 1:] if index_0 != -1 else host_name
    texto_host = f"Host: {parte_variable}"

    url = f"{base_url}{serial}.html"
    estado = "Protegida" if PROTECCION == "ON" else "Libre"

    # Verificar que la ficha HTML exista
    ficha_path = os.path.join(docs_folder, f"{serial}.html")
    if not os.path.exists(ficha_path):
        print(f"Ficha no encontrada: {ficha_path}")
        continue

    # Evitar duplicados
    filename = f"{parte_variable}_{serial}_{estado.replace(' ', '_')}.png"
    filepath = os.path.join(output_folder, filename)
    if os.path.exists(filepath):
        print(f"QR ya existe, se sobrescribe: {filename}")
    #if os.path.exists(filepath):
        #print(f"QR ya existe, no se regenera: {filename}")
        #continue

    try:
        # 🧠 Generar código QR compacto
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        qr_img = qr_img.resize((150, 150))  # Tamaño reducido para etiquetas pequeñas

        # 🖼️ Crear imagen base del tamaño físico de la etiqueta
        img = Image.new("RGB", (300, 230), "white")
        img.paste(qr_img, (70, 40))  # Centrado horizontal

        draw = ImageDraw.Draw(img)

        # 🖋️ Cargar fuentes con tamaños optimizados
        try:
            font_host = ImageFont.truetype(font_path, 30)       # Host Name
            font_ID = ImageFont.truetype(font_path, 30)     # Estado
            font_serial = ImageFont.truetype(font_path, 30)     # Serial
        except:
            font_host = font_ID = font_serial = ImageFont.load_default()

        # 🏷️ Host en esquina superior izquierda
        draw.text((10, 5), texto_host, font=font_host, fill="black")

        # 🏷️ ID en esquina superior Derecha
        draw.text((5, 10), texto_ID, font=font_ID, fill="black")

        # 🔢 Serial centrado debajo del QR
        serial_text = f"Serial: {serial}"
        serial_width = draw.textlength(serial_text, font=font_serial)
        draw.text(((300 - serial_width) // 2, 200), serial_text, font=font_serial, fill="black")

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