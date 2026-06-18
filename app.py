from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM equipment")
    equipment = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', equipment=equipment)

@app.route('/add_equipment', methods=['GET', 'POST'])
def add_equipment():
    if request.method == 'POST':
        name = request.form['equipment_name']
        serial = request.form['serial_number']
        dept = request.form['department']
        purchase = request.form['purchase_date']
        status = request.form['status']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO equipment (equipment_name, serial_number, department, purchase_date, status) VALUES (%s, %s, %s, %s, %s)",
            (name, serial, dept, purchase, status)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_equipment.html')

@app.route('/equipment/<int:id>')
def equipment_detail(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM equipment WHERE equipment_id=%s", (id,))
    equipment = cursor.fetchone()

    cursor.execute("SELECT * FROM maintenance_log WHERE equipment_id=%s", (id,))
    logs = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('equipment_detail.html', equipment=equipment, logs=logs)

@app.route('/add_log/<int:id>', methods=['GET', 'POST'])
def add_log(id):
    if request.method == 'POST':
        date = request.form['maintenance_date']
        tech = request.form['technician_name']
        issue = request.form['issue_reported']
        resolution = request.form['resolution_notes']
        next_due = request.form['next_due_date']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO maintenance_log (equipment_id, maintenance_date, technician_name, issue_reported, resolution_notes, next_due_date) VALUES (%s, %s, %s, %s, %s, %s)",
            (id, date, tech, issue, resolution, next_due)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('equipment_detail', id=id))
    return render_template('add_log.html', equipment_id=id)

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM equipment")
    total = cursor.fetchone()['total']

    cursor.execute("SELECT status, COUNT(*) AS count FROM equipment GROUP BY status")
    status_counts = cursor.fetchall()

    cursor.execute("SELECT * FROM equipment e JOIN maintenance_log m ON e.equipment_id=m.equipment_id WHERE m.next_due_date < CURDATE()")
    overdue = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('dashboard.html', total=total, status_counts=status_counts, overdue=overdue)

if __name__ == '__main__':
    app.run(debug=True)
