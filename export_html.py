# Crea página HTML para cada impresora Zebra y un Dashboard principal
import sqlite3, os, sys, shutil
from datetime import datetime
from dotenv import load_dotenv

# Configuración de rutas y nombres
DB_PATH = "Inventario de impresora zebra.db"
TABLE_NAME = "inventario_zebra"
OUTPUT_FOLDER = "docs"
LOG_FILE = "log.txt"

def log(mensaje):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    mensaje_final = f"[{fecha}] {mensaje}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(mensaje_final + "\n")
    print(mensaje_final)

def validar_base():
    if not os.path.exists(DB_PATH):
        log(f"Base de datos no encontrada: {DB_PATH}")
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [t[0] for t in cursor.fetchall()]
    conn.close()
    if TABLE_NAME not in tablas:
        log(f"Tabla '{TABLE_NAME}' no encontrada en la base.")
        sys.exit(1)

# --- ESTA FUNCIÓN DEBE ESTAR AFUERA, AL MISMO NIVEL QUE LAS DEMÁS ---
def generar_dashboard_index(filas, columnas):
    log("Generando Dashboard Protegido (Fichas Libres)...")
    
    load_dotenv(override=True)
    # Contraseña exclusiva para el Dashboard
    DASH_PASS = os.getenv("DASHBOARD_PASSWORD", "admin123") 

    # Contadores para el encabezado
    total = len(filas)
    idx_status = columnas.index("Status") if "Status" in columnas else -1
    activas = sum(1 for f in filas if str(f[idx_status]).upper() == "ACTIVA") if idx_status != -1 else total

    # Bloque de seguridad EXCLUSIVO para el Dashboard
    password_script = f'''
    <script>
    (function() {{
        const clave = prompt("🛡️ ACCESO RESTRINGIDO\\nIngrese clave de Administrador para ver el inventario global:");
        if (!clave || clave.trim() !== "{DASH_PASS}") {{
            document.documentElement.innerHTML = `
            <body style="background:#121212; color:white; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; font-family:sans-serif; text-align:center;">
                <div style="background:#1e1e26; padding:40px; border-radius:15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                    <h1 style="color:#ff4b2b; font-size:40px;">⚠️</h1>
                    <h2 style="color:white;">Dashboard Bloqueado</h2>
                    <p style="color:#888;">Se requiere nivel de Administrador para ver esta sección.</p>
                    <button onclick="location.href='javascript:history.back()'" style="padding:10px 20px; background:#444; color:white; border:none; border-radius:5px; cursor:pointer; margin-right:10px;">Volver</button>
                    <button onclick="location.reload()" style="padding:10px 20px; background:#00d4ff; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">Reintentar</button>
                </div>
            </body>`;
        }}
    }})();
    </script>'''

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Zebra Fleet Manager</title>
    {password_script}
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="dashboard-container">
        <header class="dashboard-header">
            <div class="brand">Zebra Fleet Manager</div>
            <div class="stats">
                <div class="stat-item"><span>TOTAL IMPRESORAS</span><br><strong>{total}</strong></div>
                <div class="stat-item"><span>ACTIVAS</span><br><strong>{activas}</strong></div>
                <div class="stat-item"><span>RESULTADOS</span><br><strong>{total}</strong></div>
            </div>
        </header>
        <div class="table-container">
            <table class="zebra-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Modelo</th>
                        <th>Serial</th>
                        <th>Ubicación</th>
                        <th>Conexión</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>"""

    idx_id = columnas.index("ID")
    idx_mod = columnas.index("Modelo")
    idx_ser = columnas.index("Serial Number")
    idx_ubi = columnas.index("Ubicación")
    idx_con = columnas.index("Conección")

    for f in filas:
        serial_raw = str(f[idx_ser]).strip()
        serial_url = serial_raw.replace(" ", "_").replace("/", "-")
        conexion = str(f[idx_con]).upper()
        estado = str(f[idx_status]).upper() if idx_status != -1 else "N/A"

        icon_conn = '<i class="fas fa-network-wired"></i> RED'
        if "WIFI" in conexion: icon_conn = '<i class="fas fa-wifi"></i> WIFI'
        elif "USB" in conexion: icon_conn = '<i class="fas fa-microchip"></i> USB'

        status_class = "status-activa"
        if "REPARACION" in estado: status_class = "status-reparacion"
        elif "INACTIVA" in estado: status_class = "status-inactiva"

        html_content += f"""
                    <tr onclick="window.location='{serial_url}.html';" style="cursor:pointer;">
                        <td class="text-muted">#{f[idx_id]}</td>
                        <td><strong>{f[idx_mod]}</strong></td>
                        <td class="serial-text">{serial_raw}</td>
                        <td>{f[idx_ubi]}</td>
                        <td>{icon_conn}</td>
                        <td><span class="status-badge {status_class}">{estado}</span></td>
                    </tr>"""
     #Boton de descarga               
    html_content += """
        <div class="actions-bar" style="margin-bottom: 20px; text-align: right;">
            <button onclick="descargarCSV()" class="btn-download">
                <i class="fas fa-file-csv"></i> Descargar Inventario (Excel)
            </button>
        </div>
    """

    html_content += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""

    with open(os.path.join(OUTPUT_FOLDER, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

def generar_fichas_html():
    load_dotenv(override=True)
    PASSWORD = os.getenv("QR_PASSWORD", "QR_PASSWORD")
    PROTECCION = os.getenv("PROTECCION_FICHA", "ON")

    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    for archivo in os.listdir(OUTPUT_FOLDER):
        if archivo.endswith(".html") and archivo != "index.html":
            os.remove(os.path.join(OUTPUT_FOLDER, archivo))

    log("Conectando a la base de datos...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    
    log(f"Registros encontrados: {len(rows)}")

    # Bloque de protección para FICHAS (solo si PROTECCION == "ON")
    password_block = f'''<script>
window.addEventListener("DOMContentLoaded", function() {{
const clave = prompt("Ingrese la contraseña para acceder a esta ficha:");
if (!clave || clave.trim() !== "{PASSWORD}") {{
    document.body.innerHTML = `<div style="text-align:center; font-family:sans-serif; margin-top:100px;">
        <h2 style="color:#B22222;">Acceso denegado</h2>
        <button onclick="location.reload()">Reintentar</button>
    </div>`;
}}
}});
</script>'''

    template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.2">
    <title>Ficha - {serial}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div style="position:fixed; top:10px; right:10px; background:#eee; padding:5px 10px; border-radius:5px;">{banner}</div>
    <div class="ficha">
        <h2>Ficha Técnica Zebra</h2>
        <table>{rows}</table>
        <p class="actualizado">Actualizado: {fecha}</p>
        <button onclick="window.location='index.html'" style="margin-top:20px;">Volver al Dashboard</button>
    </div>
</body>
</html>"""

    total_fichas = 0
    for row in rows:
        data = dict(zip(columns, row))
        serial = data.get("Serial Number")
        if not serial or str(serial).strip().upper() == "NULL": continue

        html_rows = "\n".join([f"<tr><td class='label'>{k}</td><td>{v}</td></tr>" for k, v in data.items()])
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
        banner = "Protegida" if PROTECCION == "ON" else "Libre"
        
        cuerpo = (password_block if PROTECCION == "ON" else "") + template.format(serial=serial, rows=html_rows, fecha=fecha_actual, banner=banner)

        nombre_archivo = str(serial).strip().replace(" ", "_").replace("/", "-")
        with open(os.path.join(OUTPUT_FOLDER, f"{nombre_archivo}.html"), "w", encoding="utf-8") as f:
            f.write(cuerpo)
        total_fichas += 1

    generar_dashboard_index(rows, columns)
    log(f"Proceso terminado. Fichas: {total_fichas} + Dashboard generado.")

if __name__ == "__main__":
    validar_base()
    generar_fichas_html()