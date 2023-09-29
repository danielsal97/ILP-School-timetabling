
from flask import Flask, render_template, request, redirect, url_for
import json
import matplotlib.pyplot as plt
import numpy as np
from pulp import *
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
teacher_schedules = {}
schedules_by_day = {}
schedules = {}
days = []
unsatisfied_constraints = []
teacher_conflicts = {}
jsonFileResults = {}
def is_feasible(data, grades, teachers, time_slots, days):
    # Perform preliminary checks for feasibility

    # Check if there are enough classrooms and time slots to accommodate all lectures
    total_lectures = sum(len(lectures) for grade in grades for classroom, lectures in grades[grade].items())
    total_available_slots = len(time_slots) * len(days) * sum(len(grades[grade]) for grade in grades)
    
    if total_lectures > total_available_slots:
        return False, "Not enough slots and classrooms for all lectures."

    # Check for grade-specific constraints
    # for grade in grades:
    #     for classroom in grades[grade]:
    #         for lecture in grades[grade][classroom]:
                # Perform checks and add constraints for each lecture within a specific classroom and grade
                # For example, you can check if there are enough classrooms for each lecture

                # Example check:
                # classroom_capacity = data['classroom_capacity'].get(classroom, 0)
                # if classroom_capacity < some_threshold:
                #     return False, f"Not enough capacity in {classroom} for {lecture}."

    # Check if any teacher is assigned to invalid lectures
    for teacher, teacher_data in teachers.items():
        for lecture in teacher_data[1]:
            lecture_found = False
            for grade in grades:
                for classroom in grades[grade]:
                    if lecture in grades[grade][classroom]:
                        lecture_found = True
                        break
                if lecture_found:
                    break
            if not lecture_found:
                return False, f"Teacher {teacher} is not qualified for lecture {lecture}."

    # Check if the maximum workload of each teacher can be satisfied
    for teacher, teacher_data in teachers.items():
        max_workload = teacher_data[0]
        total_assigned_lectures = sum(len(lectures) for grade in grades for classroom, lectures in grades[grade].items() if lecture in teacher_data[1])
        if total_assigned_lectures > max_workload:
            return False, f"Teacher {teacher} has a maximum workload of {max_workload} but is assigned {total_assigned_lectures} lectures."

    # Check for any other specific constraints as needed

    return True, "Preliminary checks passed. The problem appears feasible."



def optimize_with_pulp(data, grades, teachers, time_slots, days):
     # Define the problem
    prob = LpProblem("School_Scheduling", LpMaximize)

    # Define the decision variables
    x = LpVariable.dicts("x", [(i, j, k,d, c, km) for i in teachers for km in grades for c in grades[km] for j in grades[km][c] for k in time_slots for d in days ],
                        cat='Binary')
    g = LpVariable.dicts("g", [(k, d) for k in range(len(time_slots) - 1) for d in days], cat='Binary')

    # Define the objective function
    prob += lpSum(x) + lpSum(g)



    # Add constraints
        # Add constraints

    for km in grades:
        for c in grades[km]:
            for j, amount in grades[km][c].items():
                #each lecture will be taught amount times
                prob += lpSum(x[i, j, k, d, c, km] for i in teachers for k in time_slots for d in days) == amount 
            
            for d in days:
                # Constraint: The totx al number of lectures in each classroom on each day must not exceed the
                prob += lpSum(x[i, j, k, d, c , km] for i in teachers for j in grades[km][c].keys() for k in time_slots) <= 4
                for k in time_slots:
                    # Constraint: Each lecture in each classroom on each day must be assigned up to one teacher
                    prob += lpSum(x[i, j, k, d, c, km] for i in teachers for j in grades[km][c].keys()) <= 1
                for k in range(len(time_slots)-1):
                        prob += lpSum(x[i, j, time_slots[k], d, c, km] for i in teachers for j in grades[km][c].keys()) - lpSum(
                            x[i, j, time_slots[k + 1], d, c, km] for i in teachers for j in grades[km][c].keys()) >=  -1+ g[k, d]
                            # print(amount)

    for i in teachers:
        # Constraint: The total number of lectures assigned to each teacher must not exceed their maximum workload
        prob += lpSum(x[i, j, k, d, c, km] for k in time_slots for d in days for km in grades for c in grades[km]  for j in grades[km][c].keys()) <= teachers[i][0]

        # for d in days:
        #     for k in time_slots:
        #         # Constraint: Each teacher can only be assigned to at most one lecture in each time slot
        #         prob += lpSum(x[i, j, k, d, c, km ] for km in grades for c in grades[km] for j in grades[km][c]) == 1

        if teachers[i][2] != 'N':
            for d in days:
                if d in teachers[i][2]:
                    # Constraint: If a teacher has a day off, they cannot be assigned to any lecture on that day
                    for k in time_slots:
                        prob += lpSum(x[i, j, k, d, c, km ] for km in grades for c in grades[km] for j in grades[km][c] ) == 0

    # prob.solve(GLPK_CMD(msg=0))
            # Check the status
# Solve the linear programming problem

    prob.solve()


    filename = "example_problem.json"
    prob.toJson(filename)
    # Check if the problem status is optimal
    if LpStatus[prob.status] != "Optimal":
        print("The problem is not solved optimally with CBC.")
        # prob.solve(GLPK_CMD())
        # if LpStatus[prob.status] != "Optimal":
        #     print("The problem is not solved optimally.")        
        # # Iterate through the constraints and check if each one is violated
        # for constraint_name, constraint_expr in prob.constraints.items():
        #     if constraint_expr.value() > 0:
        #         # Print the associated error message for the violated constraint
        #         if constraint_name in constraint_messages:
        #             print(constraint_messages[constraint_name])
        #         else:
        #             print(f"Constraint {constraint_name} is not satisfied (Value = {constraint_expr.value()})")
        for i in unsatisfied_constraints:
            print(i)
    else:
        # The problem is optimal, and the constraints are satisfied
        print("The problem is solved optimally, and the constraints are satisfied.")





    for grade in grades:
        schedules[grade] = {}  # Use a dictionary to store schedules for each grade

        for classroom in grades[grade]:
            schedules[grade][classroom] = []  # Use a list to store schedules for each classroom

            for time_slot in time_slots:
                entry = {'time_slot': time_slot, 'schedule': {day: '' for day in days}}

                for day in days:
                    for teacher in teachers:
                        for lecture in grades[grade][classroom]:
                            if x[(teacher, lecture, time_slot, day, classroom, grade)].varValue == True:
                                entry['schedule'][day] = f"{teacher}/{lecture}"

                schedules[grade][classroom].append(entry)
        print(schedules)



    # Iterate over teachers
    for teacher in teachers:
        teacher_schedules[teacher] = []  # Use a list to store schedules for each teacher

        for time_slot in time_slots:
            entry = {'time_slot': time_slot, 'schedule': {day: '' for day in days}}

            for day in days:
                for grade in grades:
                    for classroom in grades[grade]:
                        for lecture in grades[grade][classroom]:
                            if x[(teacher, lecture, time_slot, day, classroom, grade)].varValue == 1:
                                entry['schedule'][day] = f"{lecture}/{classroom}/{grade}"

            teacher_schedules[teacher].append(entry)

    
    
    # Iterate over days
    for day in days:
        schedules_by_day[day] = []  # Use a list to store schedules for each day

        for time_slot in time_slots:
            entry = {'time_slot': time_slot, 'schedule': {}}

            for teacher in teachers:
                for grade in grades:
                    for classroom in grades[grade]:
                        for lecture in grades[grade][classroom]:
                            if x[(teacher, lecture, time_slot, day, classroom, grade)].varValue == 1:
                                entry['schedule'][f"{teacher}/{lecture}/{classroom}/{grade}"] = lecture

            schedules_by_day[day].append(entry)
            
    
def find_teacher_conflicts(schedules_by_day):
    # Create a dictionary to store merged lectures
    teacher_conflicts = {}

#     for day, day_schedule in schedules_by_day.items():
#         for entry in day_schedule:
#             for schedule, lecture in entry['schedule'].items():
#                 if "/" in schedule:
#                     teacher, _, _, time_slot = schedule.split('/')
#                     # Create a unique key based on teacher, day, and time slot
#                     key = (teacher, day, entry['time_slot'])
#                     # Initialize the list if it doesn't exist in the dictionary
#                     if key not in teacher_conflicts:
#                         teacher_conflicts[key] = []
#                     # Append the lecture to the list
#                     teacher_conflicts[key].append(lecture)

#     # Remove entries where the number of lectures is 1 or less
#     teacher_conflicts = {key: lectures for key, lectures in teacher_conflicts.items() if len(lectures) > 1}

    print(teacher_conflicts)

    return teacher_conflicts


@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and file.filename.endswith('.json'):
        try:
            # Save the uploaded file with a unique name
            unique_filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(unique_filename)

            # Process the JSON file
            with open(unique_filename, 'r') as json_file:
                data = json.load(json_file)
                # lectures = data["data"]["lectures"]
                # classrooms = data["data"]["classrooms"]
                grades = data["data"]["grades"]
                teachers = data["data"]["teachers"]
                time_slots = data["data"]["time_slots"]
                days = data["data"]["days"]
            # Perform optimization using PuLP
            check = is_feasible(data, grades, teachers, time_slots, days)
            if check[0] == False:
                print(check[1])
                exit(0)
            else:
                print("feasible")
                print(check[1])

            results = optimize_with_pulp(data, grades, teachers, time_slots, days)

            # Render the home page with results
            return render_template('teacher.html', teacher_schedules=teacher_schedules)
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {e}"
        except Exception as e:
            return f"An error occurred: {e}"

    return 'Invalid file format. Please upload a JSON file.', 400


@app.route('/day')
def render_day_page():
    teacher_conflicts = find_teacher_conflicts(schedules_by_day)
    return render_template('day.html', schedules_by_day=schedules_by_day, days=days, teacher_conflicts=teacher_conflicts)

@app.route('/teacher')
def render_teacher_page():
    return render_template('teacher.html', teacher_schedules=teacher_schedules)

@app.route('/schedule')
def render_schedule_page():
    return render_template('schedule.html', schedules=schedules)

if __name__ == '__main__':
    app.run(debug=True)
            # Define a dictionary to store teacher schedules
