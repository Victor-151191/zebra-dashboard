from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

DB_PATH = "Inventario de impresora zebra.db"

def get_printer_by_serial(serial_input):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ID, "Serial Number", "Host Name", "Fecha Mtto"
        FROM inventario_zebra
        WHERE "Serial Number" = ?
        OR "Serial Number" LIKE ?
    ''', (serial_input, f'%{serial_input}'))
    results = cursor.fetchall()
    conn.close()
    return results

def update_maintenance_date(serial, new_date):
    # new_date = "2025-11-10"
    partes = new_date.split("-")  # ['2025', '11', '10']
    dia = partes[2]
    mes = partes[1]
    año = partes[0]

    meses_es = {
        "01": "ENERO", "02": "FEBRERO", "03": "MARZO", "04": "ABRIL",
        "05": "MAYO", "06": "JUNIO", "07": "JULIO", "08": "AGOSTO",
        "09": "SEPTIEMBRE", "10": "OCTUBRE", "11": "NOVIEMBRE", "12": "DICIEMBRE"
    }

    mes_nombre = meses_es.get(mes, mes)
    fecha_formateada = f"{dia}/{mes_nombre}/{año}"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE inventario_zebra SET "Fecha Mtto" = ? WHERE "Serial Number" = ?', (fecha_formateada, serial))
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    if request.method == "POST":
        serial = request.form.get("serial").strip()
        new_date = request.form.get("new_date")
        if new_date:
            update_maintenance_date(serial, new_date)
        results = get_printer_by_serial(serial)
    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)