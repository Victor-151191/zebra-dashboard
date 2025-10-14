import sqlite3, os
from dotenv import load_dotenv

# 🔐 Configuración
load_dotenv(override=True)
PROTECCION = os.getenv("PROTECCION_FICHA", "ON")
DB_PATH = "Inventario de impresora zebra.db"
TABLE_NAME = "inventario_zebra"
BASE_URL = "https://Victor-151191.github.io/zebra-dashboard/docs/"
ZPL_FILE = "etiquetas_qr_compactas.zpl"

# 📦 Conexión a la base
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(f'SELECT ID, "Serial Number" FROM {TABLE_NAME} ORDER BY ID ASC')
rows = cursor.fetchall()
conn.close()

# 🧾 Generar etiquetas ZPL
with open(ZPL_FILE, "w", encoding="utf-8") as f:
    for row in rows:
        id, serial = row
        if not serial or str(serial).strip().upper() == "NULL":
            continue

        serial = str(serial).strip().replace(" ", "_").replace("/", "-")
        url = f"{BASE_URL}{serial}.html"
        estado = "Protegida" if PROTECCION == "ON" else "Libre"

        etiqueta = f"""
^XA
^LL177
^PW300
^FO220,10^A0N,20,20^FDID: {id}^FS
^FO90,30^BQN,2,4
^FDLA,{url}^FS
^FO10,130^A0N,20,20^FDSerial: {serial}^FS
^FO10,155^A0N,18,18^FDEstado: {estado}^FS
^XZ
"""
        f.write(etiqueta)

print(f"✅ Archivo ZPL generado para etiquetas de 1.181 x 0.591 in: {ZPL_FILE}")