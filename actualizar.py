import subprocess, os
from datetime import datetime

import sys
print("Python ejecutándose desde:", sys.executable)

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
if __name__ == "__main__":
    try:
        ejecutar("export_html.py")      # Genera fichas HTML
        ejecutar("generate_qr.py")      # Genera códigos QR
        resumen_final()                 # Muestra resumen
        publicar_git()                  # Sube cambios a GitHub
    except subprocess.CalledProcessError as e:
        print(f"Falló el script: {e}")