import subprocess
from datetime import datetime

# 🛠️ Ejecutar script que genera fichas HTML
subprocess.run(["python", "export_html.py"], check=True)

# 🛠️ Ejecutar script que genera códigos QR
subprocess.run(["python", "generate_qr.py"], check=True)

# 🔍 Verificar si hay cambios
result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)

if result.stdout.strip():
    # 🚀 Subir cambios a GitHub
    subprocess.run(["git", "add", "."], cwd=".")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    mensaje = f"🔄 Actualización automática ({fecha})"
    subprocess.run(["git", "commit", "-m", mensaje], cwd=".")
    subprocess.run(["git", "push"], cwd=".")
    print("✅ Cambios publicados en GitHub Pages.")
else:
    print("⚠️ No hay cambios nuevos para subir.")