from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Class Daily Check in Database Design ------------------------------------------------------------

class Mood(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer)  # 0 = Monday
    mood_value = db.Column(db.Integer)
    date = db.Column(db.Date)  # to prevent duplicates per day

    def __init__(self, u_day_of_week, u_mood_value, u_date):
        self.day_of_week = u_day_of_week
        self.mood_value = u_mood_value
        self.date = u_date


# Class Task Database Design ----------------------------------------------------------------------

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
        current_time = get_current_time()
        values = find_start_of_day(current_time, self.schedule_list)
        start_of_day = values[0]
        first_task_index = values[1]
        
        if len(self.schedule_list)-first_task_index == 0:
        
            # If there are no blocks in the schedule, the free time spans the entirety of the day
            if start_of_day != 1439:
                free_time.append([start_of_day, 1439])
            
            
        if len(self.schedule_list)-first_task_index > 0:
        
            # Append the free time block between the beginning of the day and the beginning of the first task		
            
            if self.schedule_list[first_task_index][1][0] != start_of_day: # this checks that the start time is not the same as the end time
            
                free_time.append([start_of_day, self.schedule_list[first_task_index][1][0]])
        
        
            if len(self.schedule_list)-first_task_index > 1:
            
                i = first_task_index
                
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
            
                if task[1][1] > current_time:
                
                    future_tasks.append(task[0])
                        
        return future_tasks

    
    def automatic_scheduler(self, tasks_to_be_rescheduled):

        current_time = get_current_time()
        
        future_tasks = schedule.return_future_tasks(self)

        rescheduling = list(set(tasks_to_be_rescheduled + future_tasks))

        schedule.remove_selected_tasks(self, rescheduling)
        print("This is the new schedule:")

        print(self.schedule_list)

        print("This is what we're rescheduling")

        print(rescheduling)
        
        
        for task_id in rescheduling:
        
            list_of_free_times = schedule.get_free_time_slots(self)

            print(f"List of free times: {list_of_free_times}")
            
            scheduled = False
            
            for i in range(0, len(list_of_free_times)):
            
                if scheduled is False:

                    with app.app_context():
                        task_duration = Task.query.get(int(task_id)).duration
                    
                    free_time_start = list_of_free_times[i][0]
                    free_time_end = list_of_free_times[i][1]
                    
                    free_time_width = free_time_end  - free_time_start
                
                    if task_duration <= free_time_width:
                    
                        schedule.system_add_task(self, task_id, free_time_start)
                        scheduled = True
                        print(f"{task_id} has been scheduled")

            if scheduled is False:
                print(f"Task ID: {task_id} could not be scheduled.")            
            schedule.sort_schedule(self)
            print(self.schedule_list)



Schedule = schedule()

Schedule.add_busy_time_slot(0, 465)

Schedule.add_busy_time_slot(525, 655)

Schedule.add_busy_time_slot(675, 775)

Schedule.add_busy_time_slot(845, 960)

Schedule.add_busy_time_slot(1025, 1200)

Schedule.add_busy_time_slot(1350, 1439)

print("Schedule List: ", Schedule.return_schedule())


"""tasks_to_be_rescheduled = [3, 1]

Schedule.automatic_scheduler(tasks_to_be_rescheduled)

print(Schedule.return_schedule())"""

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



# Helper Functions ------------------------------------------------------------------

def get_current_time():
    full_date = datetime.now()
    current_time = (full_date.hour * 60) + full_date.minute
    return current_time


def convert_time(integer_time):

	hours = str((integer_time) // 60) # integer divides to find the number of hours
	minutes = str((integer_time) % 60) # finds the remainder after this division
	
	if len(hours) < 2: # checking if the hours length is too short
	
		hours = "0" + hours # performing concatenation to make the hours 2 digits, if not originally
		
	if len(minutes) < 2: # does the same for the minutes
	
		minutes = "0" + minutes
	
	converted_time = hours + ":" + minutes
			
	return converted_time


def find_start_of_day(current_time, times):
  
  counter = 0 # this will be the index of the task slot that the current time will be compared to
  found = False
  
  while found is False:
    if counter < len(times): # this condition ensures that an object not found error does not occur
      if current_time >= times[counter][1][0]: # if the current time is after the start time of the currently investigated task
        counter += 1
      else:
        found = True
    else:
      found = True
  
  counter -= 1 # goes back to the previous task slot once the comparisons fail
  
  if counter == -1: # if the current time is before the beginning of the first task
    start_of_day = current_time
  
  elif current_time <= times[counter][1][1]: # if the current time is before the end of the investigated task
    start_of_day = times[counter][1][1] # then the start of the day should be set to the end of the task
  
  else: # if the current time is after the end of the last task
    start_of_day = current_time # then the start of the day is the current time

  return [start_of_day, counter+1]


def get_mean_mood():

    with app.app_context():
        moods = Mood.query.order_by(Mood.date.desc()).limit(7).all()
        # gets a list of the 7 most recent mood entries

    for mood in moods:
        print("Mood: ", mood.mood_value)

    total = 0

    if len(moods) < 7: # if there are less than 7 entries

        placeholders = 7 - len(moods)
        # find the number of extra 5's to add to the total

        for i in range(0, placeholders):
            total = total + 5
            # adds a 5 for every mood entry missing of the 7 required

    for mood in moods:
        total = total + mood.mood_value
        # adds the mood value for every entry

    mean = total / 7

    return mean

print("Mean mood: ", get_mean_mood())


def ensure_check_in():
    today = datetime.now().date()
    existing = Mood.query.filter_by(date=today).first()
    if not existing: # if there is no mood entry for today
        print("FORCED")
        return redirect(url_for("check_in")) # go to the check in page


def calculate_shifting_factor(mood_today):

    mean_mood = get_mean_mood()

    difference = mood_today - mean_mood
        
    if difference >= 4: 
        
        shifting_factor = 2
            
    elif difference < 4 and difference >= 0:
        
        shifting_factor = 0.25*difference + 1
            
    elif difference < 0 and difference > -4:

        difference = -1 * difference

        shifting_factor = -1 *(0.25*difference + 1)
            
    elif difference <= -4:
        
        shifting_factor = -2
            
    return shifting_factor


# print("Shifting factor:", calculate_shifting_factor(5.714285714285714))


def calculate_difficulty_precedence_value(task_id, mood_today):

    shifting_factor = calculate_shifting_factor(mood_today)

    with app.app_context():
        difficulty = Task.query.get(task_id).difficulty

    difficulty_precedence = difficulty * shifting_factor

    return difficulty_precedence

# print(calculate_difficulty_precedence_value(7, 1))


def calculate_priority_precedence_value(task_id):
    with app.app_context():
        priority_precedence = Task.query.get(task_id).priority
    return priority_precedence

print(calculate_priority_precedence_value(7))


# Routes ----------------------------------------------------------------------------


@app.route("/")
def home():
    ensure_check_in()
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    ensure_check_in()
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
        Schedule.automatic_scheduler([new_task.id])

    print(Schedule.return_schedule())

    return redirect("/")


@app.route("/schedule_view")
def schedule_view():
    ensure_check_in()
    schedule_list = Schedule.return_schedule()

    def format_schedule(schedule_list):

        schedule_to_display = []

        for block in schedule_list:

            start_string = convert_time(block[1][0]) # converts the start minutes into time format
            end_string = convert_time(block[1][1]) # converts the end minutes into time format

            if block[0] == "BUSY":
                schedule_to_display.append(["BUSY", [start_string, end_string]])

            else:
                task_id = block[0]
                task = Task.query.get(task_id)
                schedule_to_display.append([task.name, [start_string, end_string], task_id])

        return schedule_to_display

    return render_template("schedule_view.html", schedule_list=format_schedule(schedule_list))


@app.route("/reschedule", methods=["POST"])
def reschedule():
    ensure_check_in()
    selected_ids = request.form.getlist("selected_tasks")

    print(selected_ids)

    selected_ids = [int(i) for i in selected_ids] # converts each string id into an integer in the list

    print(selected_ids)

    new_schedule = Schedule.automatic_scheduler(selected_ids)

    return redirect("/schedule_view")


@app.route("/check_in", methods=["GET", "POST"])
# GET is for rendering the HTML file and POST is for retrieving the information from the form
def check_in():

    today = datetime.now().date() # retrieves today's date
    day_of_week = datetime.now().weekday()  # returns an integer from 0–6

    if request.method == "POST": # if the form has been submitted
        mood_value = int(request.form["mood"])

        # Check if the form has already been submitted today
        existing = Mood.query.filter_by(date=today).first()

        if existing: # if the form has already been submitted
            existing.mood_value = mood_value
            # overwriting the old mood value with the new one
        else: # if the user has not checked in yet for today
            # the mood and its information is logged in the database
            new_mood = Mood(
                day_of_week=day_of_week,
                mood_value=mood_value,
                date=today
            )
            db.session.add(new_mood)

        db.session.commit() # updates the database

        return redirect("/") # goes back to the main menu of the list of tasks

    return render_template("check_in.html")

# --------------------------------------------------------


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)