from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Class Task Design and Database

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False) 
    deadline = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.Integer, nullable=False)                   
    difficulty = db.Column(db.Integer, nullable=False)                

    def __init__(self, u_name, u_duration, u_deadline, u_priority, u_difficulty):
        self.name = u_name
        self.duration = (u_duration * 1.2) // 1
        self.deadline = u_deadline
        self.priority = u_priority
        self.difficulty = u_difficulty


@app.route("/")
def home():
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)