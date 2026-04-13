from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



# Helper Functions ------------------------------------------------------------------

def get_current_time():
    full_date = datetime.now()
    current_time = (full_date.hour * 60) + full_date.minute
    return current_time


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
    

    def sort_schedule(self):

        def ordering(time):
            return time[1][0]
          
        self.schedule_list = sorted(self.schedule_list, key=ordering)


    def add_busy_time_slot(self, start, end):

        if start < end:
        
            self.schedule_list.append(["BUSY", [start, end]])

        schedule.sort_schedule(self)
        

    def return_schedule(self):
        return self.schedule_list


    def system_add_task(self, task_id, designated_time):

        task_start_time = designated_time
        with app.app_context():
            duration = Task.query.get(task_id).duration
        task_end_time = task_start_time + duration

        self.schedule_list.append([task_id, [task_start_time, task_end_time]])

        schedule.sort_schedule(self)


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
    

    def get_free_time_slots(self):

        free_time = [] # free time is a 2D list, where each element is [free_time_start, free_time_end]
        
        if len(self.schedule_list) == 0:
        
            # If there are no blocks in the schedule, the free time spans the entirety of the day
            free_time.append([0, 1439])
            
            
        if len(self.schedule_list) > 0:
        
            # Append the free time block between the beginning of the day and the beginning of the first task		
            
            if self.schedule_list[0][1][0] != 0: # this checks that the start time is not the same as the end time
            
                free_time.append([0, self.schedule_list[0][1][0]])
        
        
            if len(self.schedule_list) > 1:
            
                i = 0
                
                while i <= len(self.schedule_list)-2:
                
                    # Append a free time block to the list, that contains the start and end of each gap between blocks in the schedule.
                    
                    if self.schedule_list[i][1][1] != self.schedule_list[i+1][1][0]:
                    
                        free_time.append([self.schedule_list[i][1][1], self.schedule_list[i+1][1][0]])
                    
                    i = i + 1
                    
            # Append the free time block between the end of the last task and the end of the day
            
            if self.schedule_list[-1][1][1] != 1439:
            
                free_time.append([self.schedule_list[-1][1][1], 1439])
            
        return free_time


    def return_future_tasks(self):

        current_time = get_current_time()
        
        future_tasks = []
        
        for task in self.schedule_list:

            if task[0] != "BUSY":
            
                if task[1][0] >= current_time:
                
                    future_tasks.append(task[0])
                        
        return future_tasks

    
    def automatic_scheduler(self, tasks_to_be_rescheduled):

        schedule.remove_selected_tasks(self, tasks_to_be_rescheduled)
        
        rescheduling = tasks_to_be_rescheduled
        
        current_time = get_current_time()

        future_tasks = schedule.return_future_tasks(self)

        for task_id in future_tasks:
            rescheduling.append(task_id)
        
        
        for task_id in rescheduling:
        
            list_of_free_times = schedule.get_free_time_slots(self)
            
            scheduled = False
            
            for i in range(0, len(list_of_free_times)):
            
                if scheduled == False:

                    with app.app_context():
                        task_duration = Task.query.get(int(task_id)).duration
                    
                    free_time_start = list_of_free_times[i][0]
                    free_time_end = list_of_free_times[i][1]
                    
                    free_time_width = free_time_end  - free_time_start
                
                    if task_duration <= free_time_width:
                    
                        schedule.system_add_task(self, task_id, free_time_start)
                        scheduled = True
                        
            schedule.sort_schedule(self)



Schedule = schedule()

Schedule.system_add_task(2, 500)
print("Schedule List: ", Schedule.return_schedule())

Schedule.system_add_task(1, 1000)
print("Schedule List: ", Schedule.return_schedule())

Schedule.system_add_task(3, 804)
print("Schedule List: ", Schedule.return_schedule())

Schedule.add_busy_time_slot(600, 700)
print("Schedule List: ", Schedule.return_schedule())

Schedule.add_busy_time_slot(200, 250)
print("Schedule List: ", Schedule.return_schedule())


tasks_to_be_rescheduled = [3, 1]

Schedule.automatic_scheduler(tasks_to_be_rescheduled)

print(Schedule.return_schedule())






# print(Schedule.return_future_tasks())

#print("Free Time Slots: ", Schedule.get_free_time_slots())


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
    app.run(debug=True, port=5001)