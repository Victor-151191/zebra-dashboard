import subprocess, os
from datetime import datetime



def ejecutar(script):
    print(f"🚀 Ejecutando {script}...")
    result = subprocess.run(["python", script], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"❌ Error en {script}:\n{result.stderr}")
    result.check_returncode()

try:
    ejecutar("export_html.py")
    ejecutar("generate_qr.py")

    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if result.stdout.strip():
        repo_path = os.path.abspath(os.path.dirname(__file__))
        subprocess.run(["git", "add", "."], cwd=repo_path)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        mensaje = f"🕓 Actualización automática ({fecha})"
        subprocess.run(["git", "commit", "-m", mensaje], cwd=repo_path)
        subprocess.run(["git", "push"], cwd=repo_path)
        print("✅ Cambios publicados en GitHub Pages.")
    else:
        print("🟡 No hay cambios nuevos para subir.")

except subprocess.CalledProcessError as e:
    print(f"💥 Falló el script: {e}")