import subprocess

# 🛠️ Ejecutar script que genera fichas HTML
subprocess.run(["python", "export_html.py"],check=True)

# 🛠️ Ejecutar script que genera códigos QR
subprocess.run(["python", "generate_qr.py"],check=True)

#verificar si hay cambios

result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
if result.stdout.strip():
    subprocess.run(["git", "add", "."], cwd=".")
    subprocess.run(["git", "commit", "-m", "🔄 Actualización automática de fichas y QR"], cwd=".")
    subprocess.run(["git", "push"], cwd=".")
    print("✅ Cambios publicados en GitHub Pages.")
else:
    print("⚠️ No hay cambios nuevos para subir.")

# 🚀 Subir cambios a GitHub
subprocess.run(["git", "add", "."], cwd=".")
subprocess.run(["git", "commit", "-m", "🔄 Actualización automática de fichas y QR"], cwd=".")
subprocess.run(["git", "push"], cwd=".")

#agregar fecha al commit

from datetime import datetime
fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
mensaje = f"🔄 Actualización automática ({fecha})"
subprocess.run(["git", "commit", "-m", mensaje], cwd=".")

print("✅ Todo actualizado y publicado en GitHub Pages.")

