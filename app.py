from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Class Task Design and Database ----------------------------------------------------------------------

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

# Class Schedule Design -------------------------------------

class schedule():
	
    def __init__(self):
        self.schedule_list = []
    

    def add_busy_time_slot(self, start, end):

        def sort_by_start_time(busy_times):
        
            def ordering(time):
                return time[1][0]
          
            sorted_schedule = sorted(busy_times, key=ordering)
        
            return(sorted_schedule)
        
        if start < end:
        
            self.schedule_list.append(["BUSY", [start, end]])
        
        self.schedule_list = sort_by_start_time(self.schedule_list)


    def return_schedule(self):
        return self.schedule_list


    def system_add_task(self, task_id, designated_time):

	    task_start_time = designated_time
	    duration = Task.query.get(task_id).duration
	    task_end_time = task_start_time + duration
	
	    self.schedule_list.append([task_id, [task_start_time, task_end_time]])


    def remove_selected_tasks(self, list_of_tasks_to_remove):

        for i in range(0, len(list_of_tasks_to_remove)):
        
            task_to_remove = list_of_tasks_to_remove[i]
            
            removed = False
            block = 0
        
            while removed is False and block < len(self.schedule_list):
        
                if self.schedule_list[block][0] == task_to_remove:
            
                    self.schedule_list.pop(block)
                    removed = True
                    
                block = block + 1
                
            if removed is False:
                print("The system could not find the task to be deleted.")


    def remove_all_tasks(self):

        returned_tasks = []
        block = len(self.schedule_list) - 1
        
        while block >= 0:
        
            if self.schedule_list[block][0] != "BUSY":
            
                returned_tasks.append(self.schedule_list[block][0])
                self.schedule_list.pop(block)
                    
            block = block - 1

        returned_tasks = returned_tasks[::-1]
        return returned_tasks

Schedule = schedule()
print(Schedule.return_schedule())


"""with app.app_context():
    Schedule.system_add_task(1, 400)""" # this is system_add_task()

"""@app.route("/remove")
def remove():
    with app.app_context():
        Schedule.remove_selected_tasks([1, 3])
        print(Schedule.return_schedule())
    return redirect("/schedule_view")"""

"""@app.route("/remove_all")
def remove_all():
    with app.app_context():
        print("Before:", Schedule.return_schedule())
        tasks = Schedule.remove_all_tasks()
        print("After:", Schedule.return_schedule())
        print(tasks)
    return redirect("/schedule_view")"""



# Routes ----------------------------------------------------------------------------


@app.route("/")
def home():
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    name = request.form["name"]
    duration = int(request.form["duration"])
    deadline = int(request.form["deadline"])
    priority = int(request.form["priority"])
    difficulty = int(request.form["difficulty"])

    new_task = Task(name, duration, deadline, priority, difficulty)

    db.session.add(new_task)
    db.session.commit()

    # THIS IS WHERE A NEW TASK GETS AUTOMATICALLY SCHEDULED IN!
    with app.app_context():
        Schedule.system_add_task(new_task.id, 100)

    print(Schedule.return_schedule())

    return redirect("/")


@app.route("/schedule_view")
def schedule_view():
    schedule_list = Schedule.return_schedule()

    def format_schedule(schedule_list):

        schedule_to_display = []

        for block in schedule_list:

            if block[0] == "BUSY":
                schedule_to_display.append(["BUSY", block[1]])

            else:
                task_id = block[0]
                task = Task.query.get(task_id)
                schedule_to_display.append([task.name, block[1]])

        return schedule_to_display

    schedule_list = format_schedule(schedule_list)

    return render_template("schedule_view.html", schedule_list=schedule_list)

# --------------------------------------------------------


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)