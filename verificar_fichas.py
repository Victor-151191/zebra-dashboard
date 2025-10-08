import os
import requests

# 🌐 Configuración base
docs_folder = "docs"
base_url = "https://victor-151191.github.io/zebra-dashboard/docs/"

# 📦 Verificación por archivo
print("\n🔍 Verificando fichas publicadas en GitHub Pages...\n")
for filename in os.listdir(docs_folder):
    if filename.endswith(".html"):
        url = base_url + filename
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {filename} → Publicada")
            else:
                print(f"❌ {filename} → No encontrada (Código {response.status_code})")
        except Exception as e:
            print(f"⚠️ {filename} → Error de conexión: {e}")

print("\n📊 Verificación completa.")