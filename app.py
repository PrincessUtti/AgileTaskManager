##IMPORTS##
from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, time, date, timedelta
import json

##APP SETUP##
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:H0tGurl$ummer@localhost:5432/AgileTaskManager"
app.secret_key = "my_secret_key"  # Replace with a secure secret key

##DB SETUP##
db = SQLAlchemy(app)

##MODELS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    tokenNumber = db.Column(db.Integer, default=10)  # New column for token number
    timePerToken = db.Column(db.Integer, default=10)  # New column for time per token - need to check if this converts to minutes or seconds

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    ##completed = db.Column(db.Boolean, default=False)
    completion_level = db.Column(ENUM('Not Started', 'In Progress', 'Completed', 'Needs Further Work', name='completion_levels', create_type=True), nullable=True)
    ##priority = db.Column(db.String(20), nullable=True)
    set_priority = db.Column(ENUM('Low', 'Medium', 'High', name='priority_levels', create_type=True), nullable=False)
    
    #calendar fields
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    completion_level = db.Column(ENUM('Not Started', 'In Progress', 'Completed', 'Needs Further Work', name='subtask_completion_levels', create_type=True), nullable=True)
    set_priority = db.Column(ENUM('Low', 'Medium', 'High', name='subtask_priority_levels', create_type=True), nullable=False)

    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    duration= db.Column(db.Integer, nullable=True)  # Duration in minutes
    duration_seconds = db.Column(db.Integer, nullable=True)  # Duration in seconds

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)  # Foreign key to Task

##ROUTES##

##Render Pages##
@app.route("/") #used to decorate home page
def index():
    return render_template("index.html")

@app.route("/index")
def index_page():
    return render_template("index.html")

@app.route("/signup", methods=["GET"]) #used to decorate signup page
def signup_page():
    return render_template("signup.html")

@app.route("/login", methods=["GET"]) #login page
def login_page():
    return render_template("login.html")
    
@app.route("/calendar") #calendar page
def calendar_page():
    return render_template("calendar.html")

@app.route("/calendartasks") #calendar page
def calendartasks_page():
    return render_template("calendartasks.html")

@app.route("/backlog") #backlog page
def backlog_page():
    return render_template("backlog.html")

@app.route("/nav")
def nav():
    return render_template("nav.html")

@app.route("/dragAndDrop", methods=["POST","GET"])
def dragTasks():
    if "user_id" not in session:
        return "Not logged in", 401
        #return redirect("/login")  # Redirect to login if user is not logged in

    tasks = Task.query.filter_by(user_id=session.get("user_id")).all()  # Assuming you have a way to get the current logged-in user's ID

    today=date.today()
    monday = today - timedelta(days=today.weekday())

    days = []
    for i in range(7):
        day = monday + timedelta(days=i)
        days.append({
            "display": day.strftime("%A %d %B"),
            "date": day.strftime("%Y-%m-%d"),
            "day_name": day.strftime("%A")
        })

    timeslots = []

    currentTime = datetime.combine(date.today(), time(8, 0))  # Start at 8:00 AM
    endTime = datetime.combine(date.today(), time(20, 0))  # End at 8:00 PM 

    while currentTime <= endTime:
        timeslots.append(currentTime.strftime("%H:%M"))
        currentTime += timedelta(minutes=30)  # Increment by 30 minutes

    '''
    current_time = datetime.strptime("08:00", "%H:%M")
    end_time = datetime.strptime("20:00", "%H:%M")
'''

    ##days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    return render_template("dragAndDrop.html", tasks=tasks, timeslots=timeslots, days=days)


@app.route("/update_task_time/<int:task_id>", methods=['POST'])
def update_task_time(task_id):
    if "user_id" not in session:
        return redirect("/login")

    task = Task.query.filter_by(id=task_id, user_id=session["user_id"]).first_or_404()

    start_time_str = request.form.get("start_time")
    end_time_str = request.form.get("end_time")
    due_date_str = request.form.get("due_date")

    if start_time_str:
        task.start_time = datetime.strptime(start_time_str, "%H:%M").time()
    if end_time_str:
        task.end_time = datetime.strptime(end_time_str, "%H:%M").time()
    if due_date_str:
        task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()


    db.session.commit()
    return{"status": "success",
           "start_time": task.start_time.strftime("%H:%M") if task.start_time else None,
           "end_time": task.end_time.strftime("%H:%M") if task.end_time else None,
           "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else None
           }
    ##return redirect('/dragAndDrop')##


##Defining Functions##

@app.route("/signup", methods=["POST"]) #used to decorate signup page
def signup():
    username = request.form["username"]
    password = request.form["password"]

    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return "User created"

@app.route("/login", methods=["POST"]) #login page
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first() #[LOOK INTO]

    if user and user.check_password(password):
        session["user_id"] = user.id
        return "Logged in"
    else:
        return "Invalid credentials"

@app.route("/loginCheck") #logout page
def loginCheck():
    if "user_id" in session:
        return "User is logged in"
    else:
        return "User is not logged in"

@app.route("/logout", methods=["POST", "GET"]) #logout page
def logout():
    session.clear()
    return redirect("/login")
    #session.pop("user_id", None)
    #return "Logged out"

@app.route("/tasks")
def tasks():
    if "user_id" not in session:
        return "Not logged in", 401
        #return redirect("/login")  # Redirect to login if user is not logged in

    tasks = Task.query.filter_by(user_id=session.get("user_id")).all()  # Assuming you have a way to get the current logged-in user's ID
    return render_template("tasks.html", tasks=tasks)

@app.route("/add_task", methods=["POST"]) #add task page
def add_task():
    name=request.form["task_name"]
    description=request.form["task_description"]
    due_date=datetime.strptime(request.form["task_due_date"], "%Y-%m-%d").date() if request.form.get("task_due_date") else None
    start_time=datetime.strptime(request.form["task_time"], "%H:%M").time() if request.form.get("task_time") else None
    #time=request.form["task_time"]
    status=request.form["task_status"]
    priority=request.form["task_priority"]
    user_id=session.get("user_id")  # Assuming you have a way to get the current logged-in user's ID

    new_task = Task(title=name, description=description, due_date=due_date, start_time=start_time, completion_level=status, set_priority=priority, user_id=user_id)

    print(request.form)  # Debugging line to print the form data

    db.session.add(new_task)
    db.session.commit()

    return "Task added"

@app.route("/tasks_by_date")
def tasks_by_date():
    user_id = session.get("user_id")
    if "user_id" not in session:
        return "Not logged in", 401
    
    calendar_date = request.args.get("date")
    tasks = Task.query.filter_by(user_id=user_id, due_date=calendar_date).all()

    return {
        "tasks": [
            {"id": task.id,
            "title": task.title, 
             "description": task.description
             }
            for task in tasks
        ]
    }

@app.route("/update_task/<int:task_id>", methods=['POST'])
def update_task(task_id):
    if "user_id" not in session:
        return redirect("/login")

    task = Task.query.filter_by(id=task_id, user_id=session["user_id"]).first_or_404()

    field_map = {
        "title": "title",
        "description": "description",
        "due_date": "due_date",
        "time": "time",
        "completion_level": "completion_level",
        "set_priority": "set_priority"
    }

    for form_field, model_field in field_map.items():
        value = request.form.get(form_field)

        # Skip blank fields → leave unchanged
        if value in (None, "", " "):
            continue

        setattr(task, model_field, value)

    db.session.commit()
    return redirect('/tasks')

#makes sure all new tables are created in the database before the app runs
with app.app_context():
    db.create_all()

app.run(host="0.0.0.0", port=80)
