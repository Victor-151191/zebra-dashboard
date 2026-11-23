import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

DB_PATH = "Inventario de impresora zebra.db"

MESES_ES = {
    "01": "ENERO", "02": "FEBRERO", "03": "MARZO", "04": "ABRIL",
    "05": "MAYO", "06": "JUNIO", "07": "JULIO", "08": "AGOSTO",
    "09": "SEPTIEMBRE", "10": "OCTUBRE", "11": "NOVIEMBRE", "12": "DICIEMBRE",
}


def get_printer_by_serial(serial_input: str) -> list:
    termino = serial_input.strip().upper()
    if not termino:
        return []

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT ID, "Serial Number", "Host Name", "Fecha Mtto"
            FROM inventario_zebra
            WHERE UPPER(TRIM("Serial Number")) = ?
               OR UPPER(TRIM("Serial Number")) LIKE ?
            ORDER BY ID ASC
            ''',
            (termino, f"%{termino}"),
        )
        return cursor.fetchall()


def update_maintenance_date(serial: str, new_date: str) -> None:
    partes = new_date.strip().split("-")
    if len(partes) != 3:
        return

    anio, mes, dia = partes
    mes_nombre = MESES_ES.get(mes, mes)
    fecha_formateada = f"{dia}/{mes_nombre}/{anio}"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE inventario_zebra SET "Fecha Mtto" = ? WHERE TRIM("Serial Number") = ?',
            (fecha_formateada, serial.strip()),
        )
        conn.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    mensaje = None

    if request.method == "POST":
        serial = (request.form.get("serial") or "").strip()
        new_date = (request.form.get("new_date") or "").strip()

        if serial and new_date:
            update_maintenance_date(serial, new_date)
            mensaje = f"Fecha de mantenimiento actualizada para {serial}."

        results = get_printer_by_serial(serial)

    return render_template("index.html", results=results, mensaje=mensaje)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)