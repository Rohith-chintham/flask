from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)

# MySQL DB connection (change as needed)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask:12345678@localhost/students'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    attendance_records = db.relationship('Attendance', backref='student', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(10), nullable=False)  # "Present" or "Absent"

# Routes
@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        new_student = Student(name=name, age=int(age))
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    students = Student.query.all()
    today = date.today()

    if request.method == 'POST':
        for student in students:
            status = 'Present' if request.form.get(str(student.id)) == 'on' else 'Absent'
            record = Attendance(student_id=student.id, date=today, status=status)
            db.session.add(record)
        db.session.commit()
        return redirect(url_for('attendance_records'))

    return render_template('attendance.html', students=students, date=today)

@app.route('/attendance/records')
def attendance_records():
    records = db.session.query(Attendance, Student).join(Student).order_by(Attendance.date.desc()).all()
    return render_template('attendance_records.html', records=records)

# Run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
