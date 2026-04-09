import os
import json
import sqlite3
import base64
import io
import csv
import pickle
from datetime import datetime, date, timedelta
from functools import wraps
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_file, make_response
)
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')   # ✅ ye hi rehna chahiye
    conn.row_factory = sqlite3.Row
    return conn
    
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from flask import render_template, request, send_file
import sqlite3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import os
import pandas as pd
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
import os
from datetime import datetime
import sqlite3
activity_log = []


app = Flask(__name__)

import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

app.secret_key = os.environ.get('SESSION_SECRET', 'attendance-secret')

DATABASE = 'database.db'
UPLOAD_FOLDER = 'static/images/students'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from functools import wraps
from flask import session, redirect, url_for

def log_activity(name, roll, student_class, action, status):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    now = datetime.now()

    cur.execute("""
        INSERT INTO activity_logs 
        (name, roll_number, class, action, status, time, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        roll,
        student_class,
        action,
        status,
        now.strftime("%H:%M:%S"),
        now.strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()



def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated
@app.route("/student/<int:student_id>/pdf")
def download_student_pdf(student_id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE id=?", (student_id,))
    student = cur.fetchone()

    conn.close()

    if not student:
        return "Student not found"

    filename = f"student_{student['roll_number']}.pdf"
    filepath = f"temp_{filename}"

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Student Profile", styles['Title']))
    elements.append(Spacer(1,20))

    data = [
        ["Name", student["name"]],
        ["Roll Number", student["roll_number"]],
        ["Class", student["class"]],
        ["Email", student["email"] or "-"],
        ["Parent Name", student["parent_name"] or "-"],
        ["Parent Phone", student["parent_phone"] or "-"]
    ]

    table = Table(data, colWidths=[150,300])

    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey)
    ]))

    elements.append(table)
    elements.append(Spacer(1,20))

    if student["photo_path"] and os.path.exists(student["photo_path"]):

        elements.append(Paragraph("Student Photo", styles['Heading2']))
        elements.append(Spacer(1,10))

        img = Image(student["photo_path"], width=150, height=150)
        elements.append(img)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    doc.build(elements)

    return send_file(filepath, as_attachment=True)


@app.route("/more")
def more():
    return render_template("more.html")


import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from flask import request, send_file

@app.route("/generate_report", methods=["POST"])
def generate_report():

    name = request.form.get("name")
    roll = request.form.get("roll")
    student_class = request.form.get("class")
    attendance = request.form.get("attendance")
    notes = request.form.get("notes")

    photo = request.files.get("student_photo")
    report_card = request.files.get("report_card")
    school_logo = request.files.get("school_logo")
    teacher_sign = request.files.get("teacher_sign")

    os.makedirs("static/report_cards", exist_ok=True)
    os.makedirs("static/reports", exist_ok=True)

    student_photo_path = None
    report_card_path = None
    logo_path = None
    sign_path = None

    if photo:
        student_photo_path = os.path.join("static/report_cards", photo.filename)
        photo.save(student_photo_path)

    if report_card:
        report_card_path = os.path.join("static/report_cards", report_card.filename)
        report_card.save(report_card_path)

    if school_logo:
        logo_path = os.path.join("static/report_cards", school_logo.filename)
        school_logo.save(logo_path)

    if teacher_sign:
        sign_path = os.path.join("static/report_cards", teacher_sign.filename)
        teacher_sign.save(sign_path)

    pdf_name = request.form.get("pdf_name")
    pdf_path = f"static/reports/{pdf_name}.pdf"

    styles = getSampleStyleSheet()
    story = []

    # SCHOOL HEADER
    if logo_path:
        story.append(Image(logo_path, width=80, height=80))

    story.append(Paragraph("<b>ABC SCHOOL</b>", styles['Title']))
    story.append(Paragraph("Student Academic Report", styles['Heading2']))
    story.append(Spacer(1,20))

    # STUDENT PROFILE
    profile_data = [
        ["Name", name],
        ["Roll Number", roll],
        ["Class", student_class],
        ["Attendance", attendance]
    ]

    table = Table(profile_data, colWidths=[150,250])
    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.grey),
        ('BACKGROUND',(0,0),(0,-1),colors.lightgrey)
    ]))

    story.append(table)
    story.append(Spacer(1,20))

    # STUDENT PHOTO
    if student_photo_path:
        story.append(Paragraph("<b>Student Photo</b>", styles['Heading3']))
        story.append(Image(student_photo_path, width=120, height=120))
        story.append(Spacer(1,20))

    # SUBJECT MARKS TABLE (MANUAL INPUT FROM FORM)
    subjects = request.form.getlist("subject[]")
    marks = request.form.getlist("marks[]")

    marks_data = [["Subject","Marks"]]

    for s,m in zip(subjects,marks):
        if s and m:
            marks_data.append([s,m])

    marks_table = Table(marks_data, colWidths=[200,200])
    marks_table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),colors.lightblue)
    ]))

    story.append(Paragraph("<b>Subject Marks</b>", styles['Heading3']))
    story.append(marks_table)
    story.append(Spacer(1,20))

    # ATTENDANCE CHART (simple visual bar)
    story.append(Paragraph("<b>Attendance Overview</b>", styles['Heading3']))
    story.append(Paragraph(f"Total Attendance: {attendance}", styles['Normal']))
    story.append(Spacer(1,20))

    # REPORT CARD IMAGE
    if report_card_path:
        story.append(Paragraph("<b>Report Card</b>", styles['Heading3']))
        story.append(Image(report_card_path, width=350, height=200))
        story.append(Spacer(1,20))

    # TEACHER REMARKS
    story.append(Paragraph("<b>Teacher Remarks</b>", styles['Heading3']))
    story.append(Paragraph(notes, styles['Normal']))
    story.append(Spacer(1,30))

    # SIGNATURE SECTION
    if sign_path:
        story.append(Image(sign_path, width=120, height=60))

    story.append(Paragraph("Teacher Signature", styles['Normal']))

    pdf = SimpleDocTemplate(pdf_path)
    pdf.build(story)

    return send_file(pdf_path, as_attachment=True)


@app.route("/delete_student/<int:student_id>", methods=["POST"])
@admin_required
def delete_student(student_id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    if not student:
        flash("Student not found!", "danger")
        return redirect(url_for("students"))

    conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    flash(f"Student '{student['name']}' deleted successfully!", "success")
    return redirect(url_for("students"))

    
@app.route("/api/activity-log")
def api_activity_log():
    return jsonify(activity_log)
# -------------------------------------------------
# DATABASE
# -------------------------------------------------

def get_db():
    # Added timeout to avoid "database is locked"
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_number TEXT UNIQUE NOT NULL,
                class TEXT NOT NULL,
                parent_name TEXT,
                parent_phone TEXT,
                email TEXT,
                photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                date TEXT,
                time TEXT,
                status TEXT,
                method TEXT
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                username TEXT UNIQUE,
                password TEXT,
                subject TEXT,
                class_assigned TEXT
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')

        c.execute("INSERT OR IGNORE INTO admins VALUES (1,'admin','admin123')")


# -------------------------------------------------
# AUTH
# -------------------------------------------------

@app.route("/check_roll")
def check_roll():

    roll=request.args.get("roll")

    conn=sqlite3.connect("database.db")
    cur=conn.cursor()

    cur.execute("SELECT id FROM students WHERE roll_number=?", (roll,))
    student=cur.fetchone()

    conn.close()

    return jsonify({"exists": student is not None})

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def teacher_or_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") not in ["admin", "teacher"]:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# -------------------------------------------------
# ROUTES
# -------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        with get_db() as conn:

            if role == "admin":
                user = conn.execute(
                    "SELECT * FROM admins WHERE username=? AND password=?",
                    (username, password)
                ).fetchone()
            else:
                user = conn.execute(
                    "SELECT * FROM teachers WHERE username=? AND password=?",
                    (username, password)
                ).fetchone()

        if user:
            session["user_id"] = user["id"]
            session["role"] = role
            # Fix: store user name for Jinja template
            session["name"] = user.get("name") if role == "teacher" else username
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    today = date.today()
    today_str = today.isoformat()

    with get_db() as conn:

        # ================= BASIC STATS =================

        total_students = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        present = conn.execute(
            "SELECT COUNT(*) FROM attendance WHERE date=? AND status='Present'",
            (today_str,)
        ).fetchone()[0]

        absent = conn.execute(
            "SELECT COUNT(*) FROM attendance WHERE date=? AND status='Absent'",
            (today_str,)
        ).fetchone()[0]

        # attendance percentage
        attendance_percentage = 0
        if total_students > 0:
            attendance_percentage = round((present / total_students) * 100)

        present_today = present
        absent_today = absent


        # ================= LOW ATTENDANCE =================

        students = conn.execute(
            "SELECT id,name,roll_number,class FROM students"
        ).fetchall()

        low_attendance = []

        for s in students:

            total = conn.execute(
                "SELECT COUNT(*) FROM attendance WHERE student_id=?",
                (s["id"],)
            ).fetchone()[0]

            present_count = conn.execute(
                "SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Present'",
                (s["id"],)
            ).fetchone()[0]

            if total > 0:
                pct = round((present_count / total) * 100)

                if pct < 75:
                    low_attendance.append({
                        "student": s,
                        "percentage": pct
                    })


        # ================= TOP ATTENDANCE =================

        top_students = []

        for s in students:

            total = conn.execute(
                "SELECT COUNT(*) FROM attendance WHERE student_id=?",
                (s["id"],)
            ).fetchone()[0]

            present_count = conn.execute(
                "SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Present'",
                (s["id"],)
            ).fetchone()[0]

            if total > 0:
                pct = round((present_count / total) * 100)

                top_students.append({
                    "name": s["name"],
                    "percentage": pct
                })

        top_students = sorted(top_students, key=lambda x: x["percentage"], reverse=True)[:5]


        # ================= FREQUENT ABSENTEES =================

        frequent_absentees = []

        for s in students:

            absent_days = conn.execute(
                "SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Absent'",
                (s["id"],)
            ).fetchone()[0]

            if absent_days >= 5:
                frequent_absentees.append({
                    "name": s["name"],
                    "absent_days": absent_days
                })


        # ================= RECENT STUDENTS =================

        recent_students = conn.execute(
            "SELECT name,class FROM students ORDER BY id DESC LIMIT 5"
        ).fetchall()


        # ================= BIRTHDAYS =================
        # (only if dob column exists)

        birthdays = []
        try:
            birthdays = conn.execute(
                """
                SELECT name,class 
                FROM students 
                WHERE strftime('%m-%d', dob)=?
                """,
                (today.strftime("%m-%d"),)
            ).fetchall()
        except:
            birthdays = []


    # ================= MONTHLY CHART =================

    monthly = [
        {"month": "Jan", "present": 20, "total": 25},
        {"month": "Feb", "present": 18, "total": 24},
        {"month": "Mar", "present": 22, "total": 26}
    ]


    # ================= RENDER =================

    return render_template(
        "dashboard.html",

        total_students=total_students,

        present=present,
        absent=absent,

        present_today=present_today,
        absent_today=absent_today,
        attendance_percentage=attendance_percentage,

        low_attendance=low_attendance,
        top_students=top_students,
        frequent_absentees=frequent_absentees,
        recent_students=recent_students,
        birthdays=birthdays,

        monthly=monthly
    )

@app.route("/bulk-attendance", methods=["POST"])
@teacher_or_admin
def bulk_attendance():

    data = request.json
    records = data.get("records", [])

    today = date.today().isoformat()
    now = datetime.now().strftime("%H:%M:%S")

    conn = get_db()

    for r in records:
        conn.execute(
            "INSERT INTO attendance (student_id,date,time,status,method) VALUES (?,?,?,?,?)",
            (r["student_id"], today, now, r["status"], "Manual")
        )

    conn.commit()

    return jsonify({"success": True})
@app.route("/face-recognition-attendance", methods=["POST"])
@teacher_or_admin
def face_recognition_attendance():
    data = request.json
    image = data.get("image")

    # yaha future me face recognition logic ayega

    return jsonify({
        "success": True,
        "matched": []
    })

def log_activity(name, roll, student_class, action, status="INFO"):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO activity_logs (name, roll_number, class, action, status, time)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        roll,
        student_class,
        action,
        status,
        datetime.now().strftime("%H:%M:%S")
    ))

    conn.commit()
    conn.close()
# -------------------------------------------------
# STUDENTS
# -------------------------------------------------

@app.route("/students")
@login_required
def students():

    q = request.args.get("q", "")
    selected_class = request.args.get("class", "")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if q:
        query += " AND (name LIKE ? OR roll_number LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])

    if selected_class:
        query += " AND class=?"
        params.append(selected_class)

    students = cur.execute(query, params).fetchall()

    students_list = []

    for s in students:

        student = dict(s)

        # total attendance days
        total = cur.execute(
            "SELECT COUNT(*) FROM attendance WHERE student_id=?",
            (s["id"],)
        ).fetchone()[0]

        # present days
        present = cur.execute(
            "SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Present'",
            (s["id"],)
        ).fetchone()[0]

        if total > 0:
            pct = round((present / total) * 100)
        else:
            pct = 0

        student["attendance_pct"] = pct

        # ✅ LOW ATTENDANCE LOG (SAFE CHECK)
        if pct < 75:
            # check if already logged today
            today = date.today().isoformat()

            existing = cur.execute("""
                SELECT * FROM activity_logs 
                WHERE roll_number=? AND action=? AND date=?
            """, (s["roll_number"], "Low Attendance", today)).fetchone()

            if not existing:
                log_activity(
                    s["name"],
                    s["roll_number"],
                    s["class"],
                    "Low Attendance",
                    "Warning"
                )

        students_list.append(student)

    classes = cur.execute("SELECT DISTINCT class FROM students").fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students_list,
        q=q,
        classes=classes,
        selected_class=selected_class
    )

@app.route('/register_student', methods=['GET', 'POST'])
@admin_required
def register_student():

    if request.method == 'POST':

        name = request.form['name']
        roll_number = request.form['roll_number']
        class_name = request.form['class']
        email = request.form.get('email')
        parent_name = request.form.get('parent_name')
        parent_phone = request.form.get('parent_phone')
        photo_data = request.form.get('photo_data')

        photo_path = None

        # SAVE PHOTO FROM BASE64
        if photo_data:

            # remove base64 header
            header, encoded = photo_data.split(",", 1)
            image_data = base64.b64decode(encoded)

            filename = f"{roll_number}.png"
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            with open(filepath, "wb") as f:
                f.write(image_data)

            photo_path = f"images/students/{filename}"

        conn = get_db()
        cursor = conn.cursor()

        # Duplicate check
        cursor.execute(
            "SELECT * FROM students WHERE roll_number=?",
            (roll_number,)
        )

        if cursor.fetchone():
            flash("Error: Roll number already exists!", "danger")
            return redirect(url_for('register_student'))

        cursor.execute("""
            INSERT INTO students
            (name, roll_number, class, email, parent_name, parent_phone, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, roll_number, class_name, email, parent_name, parent_phone, photo_path))

        conn.commit()

        # ✅ 👇 YAHI ADD KIYA HAI (IMPORTANT)
        log_activity(name, roll_number, class_name, "Student Registered", "Success")

        flash("Student registered successfully!", "success")
        return redirect(url_for('students'))

    return render_template('register_student.html')

@app.route("/student/<int:student_id>")
@admin_required
def student_profile(student_id):

    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (student_id,)
    ).fetchone()

    if not student:
        flash("Student not found", "danger")
        return redirect(url_for("students"))

    # attendance stats
    total_days = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE student_id=?",
        (student_id,)
    ).fetchone()[0]

    present_days = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Present'",
        (student_id,)
    ).fetchone()[0]

    absent_days = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Absent'",
        (student_id,)
    ).fetchone()[0]

    late_days = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE student_id=? AND status='Late'",
        (student_id,)
    ).fetchone()[0]

    # attendance percentage
    if total_days > 0:
        attendance_pct = round((present_days / total_days) * 100)
    else:
        attendance_pct = 0

    # recent logs
    logs = conn.execute(
        """
        SELECT date,time,status,method
        FROM attendance
        WHERE student_id=?
        ORDER BY date DESC,time DESC
        LIMIT 10
        """,
        (student_id,)
    ).fetchall()

    # monthly summary
    monthly_raw = conn.execute(
        """
        SELECT substr(date,1,7) as month,
        SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) as present,
        COUNT(*) as total
        FROM attendance
        WHERE student_id=?
        GROUP BY month
        ORDER BY month
        """,
        (student_id,)
    ).fetchall()

    monthly = []
    for m in monthly_raw:
        monthly.append({
            "month": m["month"],
            "present": m["present"],
            "total": m["total"]
        })

    return render_template(
        "student_profile.html",
        student=student,
        total_days=total_days,
        present_days=present_days,
        absent_days=absent_days,
        late_days=late_days,
        attendance_pct=attendance_pct,
        logs=logs,
        monthly=monthly
    )

@app.route("/api/news")
def news():
    import requests
    url = "https://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey=YOUR_KEY"
    data = requests.get(url).json()
    return jsonify(data["articles"][:5])

# ---------------------------------------------------------


# import face_recognition
# import numpy as np
# import json
# from flask import request

# @app.route('/register_face/<int:student_id>', methods=['POST'])
# def register_face(student_id):
#     file = request.files['photo']
#     image = face_recognition.load_image_file(file)
#     encodings = face_recognition.face_encodings(image)

#     if len(encodings) == 0:
#         return {"status":"error","message":"No face detected!"}, 400

#     # Save encoding as JSON string in DB
#     face_encoding = json.dumps(encodings[0].tolist())
#     conn = get_db_connection()
#     conn.execute("UPDATE students SET face_encoding=? WHERE id=?", (face_encoding, student_id))
#     conn.commit()
#     conn.close()

#     return {"status":"success","message":"Face registered successfully!"}


# import cv2
# import face_recognition
# from datetime import date

# @app.route('/scan_attendance', methods=['GET'])
# def scan_attendance():
#     conn = get_db_connection()
#     students = conn.execute("SELECT id, name, face_encoding FROM students").fetchall()

#     known_encodings = []
#     student_ids = []

#     for s in students:
#         if s['face_encoding']:
#             known_encodings.append(np.array(json.loads(s['face_encoding'])))
#             student_ids.append(s['id'])

#     cap = cv2.VideoCapture(0)

#     while True:
#         ret, frame = cap.read()
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for face_encoding in face_encodings:
#             matches = face_recognition.compare_faces(known_encodings, face_encoding)
#             face_distances = face_recognition.face_distance(known_encodings, face_encoding)

#             best_match_index = np.argmin(face_distances)

#             if matches[best_match_index]:
#                 student_id = student_ids[best_match_index]

#                 # Mark attendance if not already marked today
#                 today = date.today().isoformat()
#                 exists = conn.execute("SELECT * FROM attendance WHERE student_id=? AND date=?", (student_id, today)).fetchone()
#                 if not exists:
#                     conn.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (student_id, today, "present"))
#                     conn.commit()
#                     print(f"✅ Attendance marked for {student_id}")
#             else:
#                 print("⚠️ Unknown student detected!")
#         # Display video feed (optional)
#         cv2.imshow('Attendance Scanner', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     conn.close()
#     return "Attendance scan completed"

# -----------------------------------------------------------------------------------------------------

@app.route("/api/attendance-live")
def attendance_live():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT name, roll_number, class, status, time
        FROM activity_logs
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cur.fetchall()
    conn.close()

    return jsonify([dict(r) for r in rows])

@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
@admin_required
def edit_student(student_id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    if not student:
        flash("Student not found", "danger")
        return redirect(url_for("students"))

    if request.method == "POST":
        name = request.form['name']
        roll_number = request.form['roll_number']
        class_name = request.form['class']
        email = request.form.get('email')
        parent_name = request.form.get('parent_name')
        parent_phone = request.form.get('parent_phone')
        photo_data = request.form.get('photo_data')

        # Duplicate roll number check
        existing = conn.execute(
            "SELECT * FROM students WHERE roll_number=? AND id!=?",
            (roll_number, student_id)
        ).fetchone()
        if existing:
            flash("Error: Roll number already exists!", "danger")
            return redirect(url_for("edit_student", student_id=student_id))

        # Update student
        conn.execute("""
            UPDATE students
            SET name=?, roll_number=?, class=?, email=?, parent_name=?, parent_phone=?, photo_path=?
            WHERE id=?
        """, (name, roll_number, class_name, email, parent_name, parent_phone, photo_data, student_id))
        conn.commit()
        flash("Student updated successfully!", "success")
        return redirect(url_for("students"))

    return render_template("edit_student.html", student=student)
# -------------------------------------------------
# ATTENDANCE
# -------------------------------------------------
# -------------------------------------------------
# API STUDENT SEARCH
# -------------------------------------------------

@app.route("/api/student-search")
@teacher_or_admin
def student_search():

    q = request.args.get("q", "").strip()

    with get_db() as conn:

        students = conn.execute("""
            SELECT id,name,roll_number,class
            FROM students
            WHERE name LIKE ? OR roll_number LIKE ?
            ORDER BY name
            LIMIT 10
        """, (f"%{q}%", f"%{q}%")).fetchall()

    return jsonify([
        {
            "id": s["id"],
            "name": s["name"],
            "roll_number": s["roll_number"],
            "class": s["class"]
        }
        for s in students
    ])

@app.route("/teacher-dashboard")
@teacher_or_admin
def teacher_dashboard():

    today = date.today().isoformat()

    with get_db() as conn:

        students = conn.execute(
            "SELECT * FROM students ORDER BY name"
        ).fetchall()

        attendance = conn.execute(
            "SELECT student_id,status,method FROM attendance WHERE date=?",
            (today,)
        ).fetchall()

    attendance_map = {}

    for a in attendance:
        attendance_map[a["student_id"]] = {
            "status": a["status"],
            "method": a["method"]
        }

    return render_template(
        "teacher_dashboard.html",
        students=students,
        attendance_map=attendance_map
    )
@app.route("/mark-attendance", methods=["GET", "POST"])
@teacher_or_admin
def mark_attendance():

    if request.method == "POST":

        student_id = request.form.get("student_id")
        status = request.form.get("status")
        method = request.form.get("method", "Manual")

        # ✅ NEW: get selected date from frontend
        selected_date = request.form.get("date")

        # अगर date nahi aayi toh fallback today
        today = selected_date if selected_date else date.today().isoformat()

        now = datetime.now().strftime("%H:%M:%S")

        with get_db() as conn:

            # Insert attendance
            conn.execute(
                "INSERT INTO attendance (student_id,date,time,status,method) VALUES (?,?,?,?,?)",
                (student_id, today, now, status, method)
            )

            # Get student info
            student = conn.execute(
                "SELECT name, roll_number, class FROM students WHERE id=?",
                (student_id,)
            ).fetchone()

            conn.commit()

        # ✅ ALREADY CORRECT (NO CHANGE)
        if student:
            log_activity(
                student["name"],
                student["roll_number"],
                student["class"],
                "Attendance Marked",
                status
            )

        flash("Attendance saved!", "success")
        return redirect(url_for("teacher_dashboard"))

    return redirect(url_for("teacher_dashboard"))

# -------------------------------------------------
# EXPORT CSV
# -------------------------------------------------

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import io
from flask import make_response

@app.route("/export-pdf")
@admin_required
def export_pdf():

    from datetime import date
    today = date.today().isoformat()

    with get_db() as conn:

        # ✅ OLD DATA DELETE (same as your logic)
        conn.execute("DELETE FROM attendance WHERE date != ?", (today,))
        conn.execute("DELETE FROM activity_logs WHERE date != ?", (today,))

        records = conn.execute(
            '''
            SELECT s.name,s.roll_number,s.class,a.date,a.time,a.status
            FROM attendance a
            JOIN students s ON s.id=a.student_id
            WHERE a.date = ?
            ORDER BY s.roll_number ASC
            ''', (today,)
        ).fetchall()

    # 📄 Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(f"Attendance Report - {today}", styles['Title']))

    # Table Data
    data = [["Name", "Roll", "Class", "Date", "Time", "Status"]]

    for r in records:
        data.append([r["name"], r["roll_number"], r["class"], r["date"], r["time"], r["status"]])

    table = Table(data)

    # Style
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("GRID", (0, 0), (-1, -1), 1, colors.black),

        ("ALIGN", (0, 0), (-1, -1), "CENTER"),

        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=attendance_{today}.pdf"
    response.headers["Content-Type"] = "application/pdf"

    return response


from flask import Flask, render_template, request

from flask import Flask, render_template, request

@app.route('/parent', methods=['GET', 'POST'])
def parent_portal():
    student = None
    stats = None
    logs = None
    error = None

    if request.method == 'POST':
        roll_number = request.form['roll_number'].strip()
        parent_phone = request.form['parent_phone'].strip()

        conn = get_db_connection()

        student = conn.execute(
            "SELECT * FROM students WHERE roll_number=? AND parent_phone=?",
            (roll_number, parent_phone)
        ).fetchone()

        if not student:
            error = "Invalid Roll Number or Phone Number ❌"
        else:
            logs = conn.execute(
                "SELECT * FROM attendance WHERE student_id=? ORDER BY date DESC LIMIT 30",
                (student['id'],)
            ).fetchall()

            total = len(logs)
            present = sum(1 for l in logs if l['status'] == 'Present')
            absent = sum(1 for l in logs if l['status'] == 'Absent')
            late = sum(1 for l in logs if l['status'] == 'Late')

            pct = int((present / total) * 100) if total > 0 else 0

            stats = {
                'total': total,
                'present': present,
                'absent': absent,
                'late': late,
                'pct': pct
            }

    return render_template(
        'parent_portal.html',
        student=student,
        stats=stats,
        logs=logs,
        error=error
    )


# -------------------------------------------------
# MAIN
# -------------------------------------------------

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)