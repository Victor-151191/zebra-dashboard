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

def generar_dashboard_index(filas, columnas):
    log("Generando Dashboard Protegido (index.html)...")
    
    load_dotenv(override=True)
    DASH_PASS = os.getenv("DASHBOARD_PASSWORD", "admin123") 

    total = len(filas)
    idx_status = columnas.index("Status") if "Status" in columnas else -1
    activas = sum(1 for f in filas if str(f[idx_status]).upper() == "ACTIVA") if idx_status != -1 else total

    password_script = f'''
    <script>
    (function() {{
        const clave = prompt("🛡️ ACCESO RESTRINGIDO\\nIngrese clave de Administrador:");
        if (!clave || clave.trim() !== "{DASH_PASS}") {{
            document.documentElement.innerHTML = `
            <body style="background:#121212; color:white; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; font-family:sans-serif; text-align:center;">
                <div style="background:#1e1e26; padding:40px; border-radius:15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                    <h1 style="color:#ff4b2b; font-size:40px;">⚠️</h1>
                    <h2>Dashboard Bloqueado</h2>
                    <button onclick="location.reload()" style="padding:10px 20px; background:#00d4ff; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">Reintentar</button>
                </div>
            </body>`;
        }}
    }})();
    </script>'''

    # INICIO DEL HTML
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
                <div class="stat-item"><span>TOTAL</span><br><strong>{total}</strong></div>
                <div class="stat-item"><span>ACTIVAS</span><br><strong>{activas}</strong></div>
            </div>
        </header>

        <div class="actions-bar" style="margin-bottom: 20px; text-align: right;">
            <button onclick="descargarCSV()" class="btn-download" style="background:#2ecc71; color:black; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold; border:none;">
                <i class="fas fa-file-csv"></i> Descargar Excel
            </button>
        </div>

        <div class="table-container">
            <table class="zebra-table">
                <thead>
                    <tr>
                        <th>ID</th><th>Modelo</th><th>Serial</th><th>Ubicación</th><th>Conexión</th><th>Estado</th>
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

    # CIERRE DE TABLA Y SCRIPT DE DESCARGA (Todo en el Dashboard)
    html_content += """
                </tbody>
            </table>
        </div>
    </div>

   <script>
    function descargarCSV() {
        try {
            const tabla = document.querySelector(".zebra-table");
            let csv = [];
            const filas = tabla.querySelectorAll("tr");
            
            filas.forEach(fila => {
                const celdas = fila.querySelectorAll("th, td");
                const datosFila = Array.from(celdas).map(celda => {
                    // Limpiamos espacios y comillas
                    let texto = celda.innerText.replace(/"/g, '""').trim();
                    return `"${texto}"`;
                });
                // USAMOS PUNTO Y COMA (;) para que Excel en español lo separe bien
                csv.push(datosFila.join(";")); 
            });
            
            const contenidoCSV = csv.join("\\n");
            
            // EL TRUCO: \ufeff es el "BOM" para que Excel vea bien los acentos
            const blob = new Blob(["\\ufeff" + contenidoCSV], { type: 'text/csv;charset=utf-8;' });
            
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "Inventario_Zebra_Jabil.csv";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (err) {
            alert("Error al generar el archivo");
        }
    }
    </script>
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

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    password_block = f'''<script>
    window.addEventListener("DOMContentLoaded", function() {{
        const clave = prompt("Contraseña de Ficha:");
        if (!clave || clave.trim() !== "{PASSWORD}") {{
            document.body.innerHTML = "<h2>Acceso denegado</h2>";
        }}
    }});
    </script>'''

    template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Ficha - {serial}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="ficha">
        <h2>Ficha Técnica Zebra</h2>
        <table>{rows}</table>
        <p>Actualizado: {fecha}</p>
        <button onclick="window.location='index.html'">Volver al Dashboard</button>
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
        
        cuerpo = (password_block if PROTECCION == "ON" else "") + template.format(serial=serial, rows=html_rows, fecha=fecha_actual)

        nombre_archivo = str(serial).strip().replace(" ", "_").replace("/", "-")
        with open(os.path.join(OUTPUT_FOLDER, f"{nombre_archivo}.html"), "w", encoding="utf-8") as f:
            f.write(cuerpo)
        total_fichas += 1

    generar_dashboard_index(rows, columns)
    log(f"Fichas: {total_fichas} + Dashboard OK.")

if __name__ == "__main__":
    validar_base()
    generar_fichas_html()