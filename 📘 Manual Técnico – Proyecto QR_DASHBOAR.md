📘 Manual Técnico – Proyecto QR_DASHBOARD
# 📘 Manual Técnico del Proyecto QR_DASHBOARD

---

## 🧾 Portada

**Proyecto:** QR_DASHBOARD  
**Autor:** Víctor Manuel Salinas González  
**Colaborador técnico:** Hyunkeel  
**Fecha:** Octubre 2025  
**Versión:** 1.0  
**Descripción:** Sistema automatizado para generar fichas técnicas y etiquetas QR para impresoras Zebra, con trazabilidad, protección y publicación web.

---

## 📚 Tabla de Contenido

1. [Propósito General](#propósito-general)  
2. [Estructura del Proyecto](#estructura-del-proyecto)  
3. [Archivo `.env`](#archivo-env)  
4. [Base de Datos](#base-de-datos)  
5. [Script `generate_qr.py`](#script-generate_qrpy)  
6. [Script `export_html.py`](#script-export_htmlpy)  
7. [Script `actualizar.py`](#script-actualizarpy)  
8. [Carpeta `docs/`](#carpeta-docs)  
9. [Carpeta `qr_codes/`](#carpeta-qr_codes)  
10. [Archivo `log.txt`](#archivo-logtxt)  
11. [Recomendaciones para Escalar](#recomendaciones-para-escalar)

---

## 🎯 Propósito General

Este sistema automatiza la generación de fichas técnicas y etiquetas QR para impresoras Zebra registradas en una base de datos SQLite. Produce:

- Fichas HTML individuales con los datos del activo
- Imágenes QR listas para impresión en etiquetas de 1.181 x 0.591 pulgadas
- Control de estado (“Protegida” o “Libre”) configurable desde `.env`
- Publicación automática en GitHub Pages

---

## 📁 Estructura del Proyecto

QR_DASHBOARD/ 
├── .env 
├── actualizar.py 
├── export_html.py 
├── generate_qr.py 
├── Inventario de impresora zebra.db 
├── log.txt 
├── docs/ 
└── qr_codes/

---

## ⚙️ Archivo `.env`

```env
PROTECCION_FICHA=ON
QR_PASSWORD=QR_PASSWORD


- PROTECCION_FICHA: controla si las fichas HTML están protegidas por contraseña.
- QR_PASSWORD: contraseña solicitada al abrir fichas protegidas.

🗃️ Base de Datos
- Archivo: Inventario de impresora zebra.db
- Tabla esperada: inventario_zebra
- Campos clave: ID, "Serial Number" (más otros que se mostrarán en la ficha)

🧠 Script generate_qr.py
Función principal
Genera imágenes QR por cada activo con serial válido, incluyendo ID, estado y serial en el diseño.
Flujo detallado
- Carga configuración desde .env
- Conecta a la base y extrae registros
- Verifica existencia de ficha HTML
- Genera QR con qrcode
- Crea imagen base de 300x177 px
- Dibuja ID, Estado y Serial con fuentes pequeñas
- Guarda imagen en qr_codes/
- Verifica contenido del QR con pyzbar
Fragmento clave
qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
qr_img = qr_img.resize((130, 130))  # QR cuadrado
img = Image.new("RGB", (300, 177), "white")
img.paste(qr_img, (85, 25))         # Centrado

🖥️ Script export_html.py
Función principal
Genera fichas HTML por cada activo con serial válido, usando una plantilla visual y protección opcional.
Flujo detallado
- Verifica existencia de base y tabla
- Limpia fichas anteriores en docs/
- Carga configuración desde .env
- Recorre cada registro
- Construye tabla HTML con los datos
- Inserta banner de estado (“Protegida” o “Libre”)
- Si está protegido, agrega script de contraseña
- Guarda archivo en docs/{serial}.html
- Registra eventos en log.txt
Fragmento clave
html_rows = "\n".join([f"<tr><td class='label'>{k}</td><td>{v}</td></tr>" for k, v in data.items()])
banner = "Protegida" if PROTECCION == "ON" else "Libre"

🔄 Script actualizar.py
Función principal
Ejecuta los dos scripts anteriores y publica los cambios en GitHub si hay archivos modificados.
Flujo detallado
- Ejecuta export_html.py
- Ejecuta generate_qr.py
- Muestra resumen en consola
- Verifica cambios con git status
- Si hay cambios:
- git add .
- git commit -m "Actualización automática (fecha)"
- git push

📂 Carpeta docs/
- Contiene fichas HTML por activo
- Nombre: {serial}.html
- Protegidas si PROTECCION_FICHA=ON
- Publicables en GitHub Pages

🖼️ Carpeta qr_codes/
- Contiene imágenes QR por activo
- Nombre: {id}_{serial}.png
- Tamaño: 300x177 px
- Listas para impresión directa

📋 Archivo log.txt
- Registra eventos del script export_html.py
- Incluye fecha, tipo de evento y detalles
- Útil para auditoría y depuración

🚀 Recomendaciones para Escalar
- Exportar etiquetas QR a PDF por lote
- Agregar logo en la imagen QR
- Incluir campos como ubicación, responsable, fecha de mantenimiento
- Crear dashboard web para registrar activos
- Integrar con Google Sheets o Forms
- Generar fichas visuales con glassmorphism y branding


Este archivo puedes guardarlo como `manual_qr_dashboard.md`. Para convertirlo a Word o PDF:

- Abre en Typora → `Archivo > Exportar > Word (.docx)` o `PDF`
- O usa [Pandoc](https://pandoc.org/) con este comando:
  ```bash
  pandoc manual_qr_dashboard.md -o manual_qr_dashboard.docx



