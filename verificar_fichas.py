import os
import sys
import requests

DOCS_FOLDER = "docs"
BASE_URL = "https://victor-151191.github.io/zebra-dashboard/docs/"

if not os.path.exists(DOCS_FOLDER):
    print(f"❌ No existe la carpeta '{DOCS_FOLDER}'.")
    sys.exit(1)

print("\n🔍 Verificando fichas publicadas en GitHub Pages...\n")

publicadas = 0
errores = 0

for filename in sorted(os.listdir(DOCS_FOLDER)):
    if filename.endswith(".html"):
        url = BASE_URL + filename
        try:
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                print(f"✅ {filename} → Publicada")
                publicadas += 1
            else:
                print(f"❌ {filename} → No encontrada (Código {response.status_code})")
                errores += 1
        except Exception as e:
            print(f"⚠️ {filename} → Error de conexión: {e}")
            errores += 1

print(f"\n📊 Verificación completa: {publicadas} publicadas, {errores} con error.")