from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:H0tGurl$ummer@localhost/AgileTaskManager

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_passowrd(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(Self, password):
        return check_password_hash(self.password_hash, password)

@app.route("/") #used to decorate home page

def index():
    return render_template("index.html")

@app.route("/signup", method=["POST"]) #used to decorate signup page

def signup():
    username = request.form["Username: "]
    password = request.form["Password: "]

    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return "User created"

@app.route("/login", method=["POST"]) #login page

def login():
    username = request.form["Username: "]
    password = request.form["Password: "]

    user = User.query.filter_by(username=username).first() #[LOOK INTO]

    if user and user.check_password(password):
        return "Logged in"
    else:
        return "Invalid credentials"

app.run(host="0.0.0.0", port=80)
