import subprocess, os
from datetime import datetime
import os

import sys
print("Python ejecutándose desde:", sys.executable)

#Limpieza de archivos no encontrados en la BdD
def limpiar_archivos_basura(cursor, output_folder, docs_folder):
    print("\n--- Iniciando limpieza de archivos huérfanos ---")
    
    # 1. Obtenemos la lista real de lo que DEBERÍA existir (según la DB)
    cursor.execute('SELECT "Serial" FROM inventario_zebra')
    # Normalizamos los seriales igual que cuando creas los archivos
    Serial_validos = {str(row[0]).strip().replace(" ", "_").replace("/", "-") for row in cursor.fetchall()}

    # 2. Limpiar la carpeta de QR
    for archivo in os.listdir(output_folder):
        # Extraemos el serial del nombre del archivo (ajusta según tu formato de nombre)
        # Si tu formato es "Host_Serial_Estado.png", buscamos si el serial está contenido
        if any(s in archivo for s in Serial_validos):
            continue # El archivo es válido, no lo borres
        
        # Si llegamos aquí, el archivo no pertenece a nadie en la DB actual
        os.remove(os.path.join(output_folder, archivo))
        print(f"🗑️ QR eliminado (ya no existe en DB): {archivo}")

    # 3. Limpiar la carpeta de DOCS (Fichas HTML)
    for archivo in os.listdir(docs_folder):
        Serial_validos_archivo = archivo.replace(".html", "")
        if Serial_validos_archivo not in Serial_validos:
            # Ojo: asegúrate de no borrar el index.html si tienes uno
            if archivo == "index.html": continue 
            
            os.remove(os.path.join(docs_folder, archivo))
            print(f"🗑️ Ficha eliminada (ya no existe en DB): {archivo}")


# Ejecuta un script Python y muestra su salida en tiempo real
def ejecutar(script):
    print(f"\n Ejecutando {script}...")

    try:
        # Ejecuta el script sin capturar la salida, para que se imprima directamente
        subprocess.run(["python", script], check=True)
    except subprocess.CalledProcessError:
        print(f"El script {script} terminó con errores.\n")

# Muestra un resumen final en consola
def resumen_final():
    print("\n Resumen de ejecución:")
    print("Fichas HTML generadas correctamente")
    print("Códigos QR generados correctamente")
    print("Revisa export_log.txt para detalles")
    print("Verifica tus archivos en /docs y /qr_codes")

# Publica los cambios en GitHub si hay archivos modificados
def publicar_git():
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)

    if result.stdout.strip():
        repo_path = os.path.abspath(os.path.dirname(__file__))
        subprocess.run(["git", "add", "."], cwd=repo_path)

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        mensaje = f"Actualización automática ({fecha})"

        subprocess.run(["git", "commit", "-m", mensaje], cwd=repo_path)
        subprocess.run(["git", "push"], cwd=repo_path)

        print("Cambios publicados en GitHub Pages.")
    else:
        print("No hay cambios nuevos para subir.")

# Punto de entrada principal
#if __name__ == "__main__":
   # try:
        #ejecutar("export_html.py")      # Genera fichas HTML
        #ejecutar("generate_qr.py")      # Genera códigos QR
        #resumen_final()                 # Muestra resumen
        #publicar_git()                  # Sube cambios a GitHub
   # except subprocess.CalledProcessError as e:
        #print(f"Falló el script: {e}")

# Punto de entrada principal
if __name__ == "__main__":
    try:
        ejecutar("export_html.py")      # Genera fichas HTML
        ejecutar("generate_qr.py")      # Genera códigos QR
        
        # --- EL ARREGLO PARA QUE TU CÓDIGO FUNCIONE ---
        import sqlite3 # Importamos la librería de base de datos aquí
        
        # 1. Creamos la conexión y el cursor de verdad
        conexion = sqlite3.connect("Inventario de impresora zebra.db")
        mi_cursor_real = conexion.cursor()
        
        # 2. Le pasamos el cursor (sin comillas) y los nombres reales de las carpetas
        limpiar_archivos_basura(mi_cursor_real, "qr_codes", "docs")
        
        # 3. Cerramos la conexión para no dejarla abierta
        conexion.close()
        # -----------------------------------------------

        resumen_final()                 # Muestra resumen
        publicar_git()                  # Sube cambios a GitHub
    except Exception as e:
        print(f"Falló el script: {e}")