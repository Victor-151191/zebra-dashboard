import subprocess, os, sqlite3
from datetime import datetime
import sys

print("Python ejecutándose desde:", sys.executable)

# Función de limpieza robusta (Conecta a la DB y compara IDs y Seriales)
def limpiar_archivos_basura(output_folder, docs_folder):
    print("\n--- Iniciando limpieza de archivos huérfanos ---")
    db_path = "Inventario de impresora zebra.db"
    
    try:
        # 1. Nos conectamos a la base de datos directamente desde aquí
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT ID, "Serial Number" FROM inventario_zebra')
        filas = cursor.fetchall()
        
        # 2. Creamos una lista "permitida" con TODOS los IDs y Seriales
        permitidos = set()
        for f in filas:
            permitidos.add(str(f[0])) # Guardamos el ID
            if f[1]: # Si tiene serial, también lo guardamos normalizado
                permitidos.add(str(f[1]).strip().replace(" ", "_").replace("/", "-"))
        conn.close()

        # 3. Limpiar la carpeta de QR
        if os.path.exists(output_folder):
            for archivo in os.listdir(output_folder):
                # FILTRO DE SEGURIDAD: Ignorar todo lo que no sea una imagen .png
                if not archivo.lower().endswith('.png'): continue
                
                # Si el archivo NO contiene ningún ID o Serial válido, lo borramos
                if not any(p in archivo for p in permitidos if p):
                    os.remove(os.path.join(output_folder, archivo))
                    print(f"QR eliminado (ya no existe en DB): {archivo}")

        # 4. Limpiar la carpeta de DOCS (Fichas HTML)
        if os.path.exists(docs_folder):
            for archivo in os.listdir(docs_folder):
                # FILTRO DE SEGURIDAD: Ignorar carpetas, CSS, JPGs... solo leer .html
                if not archivo.lower().endswith('.html'): continue
                if archivo == "index.html": continue
                
                nombre_sin_ext = archivo.replace(".html", "")
                
                # Aquí verificamos exactitud
                if nombre_sin_ext not in permitidos:
                    os.remove(os.path.join(docs_folder, archivo))
                    print(f"Ficha eliminada (ya no existe en DB): {archivo}")

    except Exception as e:
        print(f"Error durante la limpieza: {e}")

# Ejecuta un script Python y muestra su salida en tiempo real
def ejecutar(script):
    print(f"\n Ejecutando {script}...")
    try:
        subprocess.run(["python", script], check=True)
    except subprocess.CalledProcessError:
        print(f"El script {script} terminó con errores.\n")

# Muestra un resumen final en consola
def resumen_final():
    print("\n Resumen de ejecución:")
    print("Fichas HTML y Códigos QR generados correctamente")
    print("Limpieza de archivos huérfanos completada")
    print("Verifica tus archivos en /docs y /qr_codes")

# Publica los cambios en GitHub si hay archivos modificados
def publicar_git():
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)

    if result.stdout.strip():
        repo_path = os.path.abspath(os.path.dirname(__file__))
        subprocess.run(["git", "add", "."], cwd=repo_path)

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        mensaje = f"Actualización automática y limpieza ({fecha})"

        subprocess.run(["git", "commit", "-m", mensaje], cwd=repo_path)
        subprocess.run(["git", "push"], cwd=repo_path)

        print("Cambios publicados en GitHub Pages.")
    else:
        print("No hay cambios nuevos para subir.")

# Punto de entrada principal
if __name__ == "__main__":
    try:
        ejecutar("export_html.py")       # 1. Genera fichas HTML
        ejecutar("generate_qr.py")       # 2. Genera códigos QR
        
        # Mandar a llamar a la función de limpieza
        limpiar_archivos_basura("qr_codes", "docs") 
        
        resumen_final()                  # 4. Muestra resumen
        publicar_git()                   # 5. Sube cambios a GitHub
    except Exception as e:
        print(f"Falló el proceso general: {e}")