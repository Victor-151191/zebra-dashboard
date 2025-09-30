import subprocess, os
from datetime import datetime

# Función que ejecuta un script Python y muestra su salida
def ejecutar(script):
    print(f"\n🚀 Ejecutando {script}...")

    # Ejecuta el script y captura su salida estándar y errores
    result = subprocess.run(["python", script], capture_output=True, text=True)

    # Muestra la salida normal del script (print)
    if result.stdout:
        print(result.stdout)

    # Muestra errores si ocurrieron
    if result.stderr:
        print(f"❌ Error en {script}:\n{result.stderr}")

    # Lanza excepción si el script terminó con error (exit code ≠ 0)
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        print(f"⚠️ El script {script} terminó con errores.\n")

# Función que imprime un resumen final en consola
def resumen_final():
    print("\n📊 Resumen de ejecución:")
    print("✅ Fichas HTML generadas correctamente")
    print("✅ Códigos QR generados correctamente")
    print("📁 Revisa export_log.txt para detalles")
    print("🌐 Verifica tus archivos en /docs y /qr_codes")

# Función que publica los cambios en GitHub si hay archivos modificados
def publicar_git():
    # Verifica si hay cambios en el repositorio
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)

    if result.stdout.strip():
        # Obtiene la ruta del proyecto actual
        repo_path = os.path.abspath(os.path.dirname(__file__))

        # Agrega todos los archivos modificados al commit
        subprocess.run(["git", "add", "."], cwd=repo_path)

        # Genera un mensaje con la fecha actual
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        mensaje = f"Actualización automática ({fecha})"

        # Crea el commit y lo sube al repositorio remoto
        subprocess.run(["git", "commit", "-m", mensaje], cwd=repo_path)
        subprocess.run(["git", "push"], cwd=repo_path)

        print("🚀 Cambios publicados en GitHub Pages.")
    else:
        print("📦 No hay cambios nuevos para subir.")

# Punto de entrada principal del script
if __name__ == "__main__":
    try:
        # Ejecuta el script que genera las fichas HTML
        ejecutar("export_html.py")

        # Ejecuta el script que genera los códigos QR
        ejecutar("generate_qr.py")

        # Muestra resumen final en consola
        resumen_final()

        # Publica los cambios en GitHub si hay algo nuevo
        publicar_git()

    # Captura errores generales si algún script falla
    except subprocess.CalledProcessError as e:
        print(f"💥 Falló el script: {e}")