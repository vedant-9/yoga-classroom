from flask import Flask,render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

port = 8080

app.config['SECRET_KEY'] = 'abcd1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    batch = db.Column(db.String(80), nullable=False)
    joining_date = db.Column(db.String(80), nullable=False, default=datetime.utcnow().date)

    def __repr__(self):
        # by id
        return '<Student %r>' % self.id

    def __init__(self, name, age, batch):
        self.name = name
        self.age = age
        self.batch = batch


db.init_app(app)
with app.app_context():
    # db.drop_all()
    db.create_all()

# get all yoga students
@app.route('/', methods=['GET'])
@app.route('/users', methods=['GET'])
def index():
    data = Student.query.all()
    return render_template('index.html', data=data)

# register a new yoga student
@app.route('/users/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        batch = request.form['batch']

        # age check if age >= 18 and <=65
        if(int(age) < 18 or int(age) > 65):
            flash("Age should be between 18 and 65", "warning")
            return redirect(url_for('index'))

        student = Student(name=name, age=age, batch=batch)

        # payment check if checkbox is checked
        def completePayment(student):
            return request.form.get('payment') != None

        if(completePayment(student) == False):
            flash("Please complete payment", "warning")
            return redirect(url_for('index'))

        db.session.add(student)
        db.session.commit()
        flash("Student registered successfully", "success")
        return redirect(url_for('index'))
    return render_template('register.html')

# update a yoga student
@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    student = Student.query.get(id)
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        batch = request.form['batch']

        # batch check it can change only on 1st of every month
        if(student.batch != batch):
            if(datetime.utcnow().date().day == 1):
                flash("Batch changed successfully", "success")
                student.batch = batch
            else:
                flash("You can change batch only on 1st of every month", "warning")
                return redirect(url_for('index'))

        student.name = name
        student.age = age
        student.batch = batch
        db.session.commit()
        flash("Student updated successfully", "success")
        return redirect('/users')
    return render_template('edit.html', data=student)

# delete a yoga student
@app.route('/users/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    student = Student.query.get(id)
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully", "success")
    return redirect('/users') 

if __name__ == '__main__':
    app.run(debug=True, port=port)