import os
import sqlite3
import subprocess
import sys
from datetime import datetime

print("Python ejecutándose desde:", sys.executable)

DB_PATH = "Inventario de impresora zebra.db"


def limpiar_archivos_basura(output_folder: str, docs_folder: str) -> None:
    print("\n--- Iniciando limpieza de archivos huérfanos ---")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT "Serial Number" FROM inventario_zebra')
            filas = cursor.fetchall()

        seriales_activos = {
            str(f[0]).strip().replace(" ", "_").replace("/", "-")
            for f in filas
            if f[0] and str(f[0]).strip().upper() != "NULL"
        }

        # Limpiar carpeta de QR
        if os.path.exists(output_folder):
            for archivo in os.listdir(output_folder):
                if not archivo.lower().endswith(".png"):
                    continue

                es_valido = any(serial in archivo for serial in seriales_activos)
                if not es_valido:
                    os.remove(os.path.join(output_folder, archivo))
                    print(f"QR eliminado (Serial ya no existe en DB): {archivo}")

        # Limpiar carpeta de DOCS (Fichas HTML)
        if os.path.exists(docs_folder):
            for archivo in os.listdir(docs_folder):
                if not archivo.lower().endswith(".html") or archivo == "index.html":
                    continue

                nombre_sin_ext = os.path.splitext(archivo)[0]
                if nombre_sin_ext not in seriales_activos:
                    os.remove(os.path.join(docs_folder, archivo))
                    print(f"Ficha eliminada (Serial ya no existe en DB): {archivo}")

    except Exception as e:
        print(f"Error durante la limpieza: {e}")


def ejecutar(script: str) -> bool:
    print(f"\nEjecutando {script}...")
    try:
        subprocess.run([sys.executable, script], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"El script {script} terminó con errores.\n")
        return False


def resumen_final() -> None:
    print("\nResumen de ejecución:")
    print("- Fichas HTML y Códigos QR generados correctamente")
    print("- Limpieza de archivos huérfanos completada")
    print("- Verifica tus archivos en /docs y /qr_codes")


def publicar_git() -> None:
    repo_path = os.path.abspath(os.path.dirname(__file__))
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )

    if result.stdout.strip():
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        mensaje = f"Actualización automática y limpieza ({fecha})"
        subprocess.run(["git", "commit", "-m", mensaje], cwd=repo_path, check=True)
        subprocess.run(["git", "push"], cwd=repo_path, check=True)
        print("Cambios publicados en GitHub Pages.")
    else:
        print("No hay cambios nuevos para subir.")


if __name__ == "__main__":
    try:
        ok_html = ejecutar("export_html.py")
        ok_qr = ejecutar("generate_qr.py")

        if ok_html and ok_qr:
            limpiar_archivos_basura("qr_codes", "docs")
            resumen_final()
            publicar_git()
        else:
            print("Se canceló la publicación en GitHub debido a errores en la generación.")
    except Exception as e:
        print(f"Falló el proceso general: {e}")