import subprocess, os, sqlite3
from datetime import datetime
import sys

print("Python ejecutándose desde:", sys.executable)

# Función de limpieza basada ÚNICAMENTE en el Número de Serie
def limpiar_archivos_basura(output_folder, docs_folder):
    print("\n--- Iniciando limpieza de archivos huérfanos ---")
    db_path = "Inventario de impresora zebra.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Obtenemos SOLO los Números de Serie que existen actualmente en la base de datos
        cursor.execute('SELECT "Serial Number" FROM inventario_zebra')
        filas = cursor.fetchall()
        
        # 2. Creamos nuestra lista de "Seriales Activos"
        seriales_activos = set()
        for f in filas:
            if f[0]: # Si la celda del serial no está vacía
                seriales_activos.add(str(f[0]).strip().replace(" ", "_").replace("/", "-"))
        conn.close()

        # 3. Limpiar la carpeta de QR
        if os.path.exists(output_folder):
            for archivo in os.listdir(output_folder):
                # Filtro: Solo tocar los archivos .png
                if not archivo.lower().endswith('.png'): continue
                
                # Buscamos si ALGÚN serial activo está escrito dentro del nombre de este archivo
                es_valido = False
                for serial in seriales_activos:
                    if serial in archivo:
                        es_valido = True
                        break
                
                # Si el archivo tiene un serial que YA NO EXISTE en la base de datos, se borra
                if not es_valido:
                    os.remove(os.path.join(output_folder, archivo))
                    print(f"QR eliminado (Su ID/Serial ya no existe en DB): {archivo}")

        # 4. Limpiar la carpeta de DOCS (Fichas HTML)
        if os.path.exists(docs_folder):
            for archivo in os.listdir(docs_folder):
                # Filtro: Solo tocar los archivos .html (Respeta imágenes y CSS)
                if not archivo.lower().endswith('.html'): continue
                if archivo == "index.html": continue
                
                # Le quitamos el .html para comparar puramente el número de serie
                nombre_sin_ext = archivo.replace(".html", "")
                
                # Si este serial YA NO EXISTE en la base de datos, a la basura
                if nombre_sin_ext not in seriales_activos:
                    os.remove(os.path.join(docs_folder, archivo))
                    print(f"Ficha eliminada (Su ID/Serial ya no existe en DB): {archivo}")

    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")

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
        
        limpiar_archivos_basura("qr_codes", "docs") 
        
        resumen_final()                  # 4. Muestra resumen
        publicar_git()                   # 5. Sube cambios a GitHub
    except Exception as e:
        print(f"Falló el proceso general: {e}")