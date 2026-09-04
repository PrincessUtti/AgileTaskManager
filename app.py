##IMPORTS##
from asyncio import tasks

from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ENUM
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, time, date, timedelta
import json
import os


app = Flask(__name__)

# Set secret key (uses environment variable on Render, falls back to local string)
app.secret_key = os.getenv("SECRET_KEY", "my_secret_key")

# Set database URI (uses Render's DATABASE_URL, falls back to local Postgres)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:H0tGurl$ummer@localhost:5432/AgileTaskManager"
)

# Prevent database SSL disconnect crashes
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 280,
}

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

##APP SETUP##

##MODELS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    sprint_tokens_limit = db.Column(db.Integer, default=10)  # New column for token number
    token_duration = db.Column(db.Integer, default=10)  # New column for time per token - need to check if this converts to minutes or seconds

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    completion_level = db.Column(ENUM('Not Started', 'In Progress', 'Completed', 'Needs Further Work', name='completion_levels', create_type=True), nullable=True)
    set_priority = db.Column(ENUM('Low', 'Medium', 'High', name='priority_levels', create_type=True), nullable=False)
    
    #calendar fields
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    tokens = db.Column(db.Integer, nullable=True, default=1)  # Number of tokens for the task

    subtasks = db.relationship('Subtask', backref='task', cascade='all, delete-orphan', lazy=True)  # Relationship to Subtask

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

    tokens = db.Column(db.Integer, nullable=True, default=1)  # Number of tokens for the task

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
    if "user_id" not in session:
        return redirect("/login")  # Redirect to login if user is not logged in
    
    tasks = Task.query.filter(
        Task.user_id==session.get("user_id"),
        Task.completion_level != "Completed"
    ).all()  # Assuming you have a way to get the current logged-in user's ID
    return render_template("backlog.html", tasks=tasks)

@app.route("/nav")
def nav():
    return render_template("nav.html")

@app.route("/dragAndDrop", methods=["POST","GET"])
def dragTasks():
    if "user_id" not in session:
        return redirect("/login")  # Redirect to login if user is not logged in

    tasks = Task.query.filter_by(user_id=session.get("user_id")).all()  # Assuming you have a way to get the current logged-in user's ID

    '''scheduledTokens = sum(
            (t.tokens if getattr(t, "tokens", None) else 1)
            for t in tasks
            if t.start_time and t.due_date
        )'''
    
    today=date.today()
    monday = today - timedelta(days=today.weekday())
    
    scheduledTokens = 0
    for t in tasks:
        if t.subtasks:
            for sub in t.subtasks:
                if sub.start_time and sub.due_date and 0 <= ( sub.due_date - monday).days <7:
                    scheduledTokens += (sub.tokens if sub.tokens else 1)
        else:
            if t.start_time and t.due_date and 0 <= ( t.due_date - monday).days <7 :
                scheduledTokens += (t.tokens if t.tokens else 1)




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

    return render_template("dragAndDrop.html", tasks=tasks, timeslots=timeslots, days=days, scheduledTokens=scheduledTokens)

##Defining Functions##

@app.route("/update_task_time/<task_id>", methods=['POST'])
def update_task_time(task_id):
    if "user_id" not in session:
        return redirect("/login")

    # Handle both subtask string IDs and regular task IDs
    task_id_str = str(task_id)

    if task_id_str.startswith("sub-"):
        sub_id = int(task_id_str.replace("sub-", ""))
        item = Subtask.query.filter_by(id=sub_id, user_id=session["user_id"]).first_or_404()
    else:
        # Fallback check for subtask vs main task by integer ID
        item = Subtask.query.filter_by(id=int(task_id_str), user_id=session["user_id"]).first()
        if not item:
            item = Task.query.filter_by(id=int(task_id_str), user_id=session["user_id"]).first_or_404()

    start_time_str = request.form.get("start_time")
    due_date_str = request.form.get("due_date")

    if start_time_str:
        start_dt = datetime.strptime(start_time_str, "%H:%M")
        item.start_time = start_dt.time()

        item_tokens = int(item.tokens) if item.tokens else 1
        duration_per_token = int(session.get("token_duration", 10))
        total_minutes = item_tokens * duration_per_token

        end_dt = start_dt + timedelta(minutes=total_minutes)
        item.end_time = end_dt.time()
    else:
        item.start_time = None
        item.end_time = None

    if due_date_str:
        item.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    elif not start_time_str:
        item.due_date = None

    db.session.commit()
    return {
        "status": "success",
        "start_time": item.start_time.strftime("%H:%M") if item.start_time else None,
        "end_time": item.end_time.strftime("%H:%M") if item.end_time else None,
        "due_date": item.due_date.strftime("%Y-%m-%d") if item.due_date else None,
        "tokens": item.tokens if item.tokens else 1,
        "token_duration": session.get("token_duration", 10)

    }

@app.route("/signup", methods=["POST"]) #used to decorate signup page
def signup():
    username = request.form["username"]
    password = request.form["password"]

    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return redirect("login")

@app.route("/login", methods=["POST"]) #login page
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first() #[LOOK INTO]

    if user and user.check_password(password):
        session["user_id"] = user.id
        session["token_limit"] = user.sprint_tokens_limit  # Store the token limit in the session
        session["token_duration"] = user.token_duration  # Store the token duration in the session
        return redirect ("/backlog")
    else:
        return "Invalid credentials"

@app.route("/loginCheck") #logout page
def loginCheck():
    if "user_id" in session:
        return "User is logged in"
    else:
        return "User not logged in"

@app.route("/logout", methods=["POST", "GET"]) #logout page
def logout():
    session.clear()
    return redirect("/login")

@app.route("/tasks")
def tasks():
    if "user_id" not in session:
        return redirect("/login")  # Redirect to login if user is not logged in

    tasks = Task.query.filter_by(user_id=session.get("user_id")).all()  # Assuming you have a way to get the current logged-in user's ID
    return render_template("tasks.html", tasks=tasks)

@app.route("/add_task", methods=["POST"]) #add task page
def add_task():
    if "user_id" not in session:
        return redirect("/login")  # Redirect to login if user is not logged in

    name=request.form["task_name"]
    description=request.form["task_description"]
    due_date=datetime.strptime(request.form["task_due_date"], "%Y-%m-%d").date() if request.form.get("task_due_date") else None
    start_time=datetime.strptime(request.form["task_time"], "%H:%M").time() if request.form.get("task_time") else None
    status=request.form["task_status"]
    priority=request.form["task_priority"]

    user_id=session.get("user_id")  # Assuming you have a way to get the current logged-in user's ID

    tokens = int(request.form.get("task_tokens", 1) or 1)  # Get the task tokens from the form, default to 1 if not provided

    new_task = Task(title=name, description=description, due_date=due_date, start_time=start_time, completion_level=status, set_priority=priority, user_id=user_id, tokens=tokens)

    db.session.add(new_task)
    db.session.flush()  # Flush to get the new_task.id before committing
    print(request.form)  # Debugging line to print the form data

    subtask_titles = request.form.getlist("subtask_title[]")
    #subtask_descriptions = request.form.getlist("subtask_description[]")   
    subtask_tokens_list = request.form.getlist("subtask_tokens[]")  # Get the list of tokens for each subtask

    sub_tokens = [
        int(token) for sub_title, token in zip(subtask_titles, subtask_tokens_list) 
        if sub_title.strip() and token#.strip()
    ]

    if sub_tokens:
        tokens = sum(sub_tokens)
    else:
        tokens = int(request.form.get("task_tokens", 1) or 1)  # Get the task tokens from the form, default to 1 if not provided

    for sub_title, sub_token in zip(subtask_titles, sub_tokens):
        if sub_title.strip():  # Only add subtasks with non-empty titles
            new_subtask = Subtask(title=sub_title.strip(), task_id=new_task.id, user_id=user_id, set_priority=priority, completion_level=status, tokens=int(sub_token) if sub_token else 1)  # Default to 1 if no token is provided
            db.session.add(new_subtask)

    db.session.commit()

    return redirect("/backlog")

@app.route("/tasks_by_date")
def tasks_by_date():
    user_id = session.get("user_id")
    if "user_id" not in session:
        return redirect("/login")  # Redirect to login if user is not logged in
    
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
    return redirect('/backlog')

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    if request.method == "POST":
        new_token_limit = request.form.get("token_limit")
        new_token_duration = request.form.get("token_duration")

        if new_token_limit:
            user.sprint_tokens_limit = int(new_token_limit)
            session["token_limit"] = int(new_token_limit)  # Update session value

        if new_token_duration:
            user.token_duration = int(new_token_duration)
            session["token_duration"] = int(new_token_duration)  # Update session value

            db.session.commit()
            return redirect("/settings")

    return render_template("settings.html", user=user)




#makes sure all new tables are created in the database before the app runs
with app.app_context():
    db.create_all()

app.run(host="0.0.0.0", port=80)
