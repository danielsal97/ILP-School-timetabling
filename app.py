import os
from flask import Flask, render_template, request, redirect, url_for
import json
import matplotlib.pyplot as plt
import numpy as np
from pulp import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
teacher_schedules = {}
schedules_by_day = {}
schedules = {}
days = []

def optimize_with_pulp(data, lectures, classrooms, grades, teachers, time_slots, days):
     # Define the problem
    prob = LpProblem("School_Scheduling", LpMaximize)

    # Define the decision variables
    x = LpVariable.dicts("x", [(i, j, k,d, c, km) for i in teachers for j in lectures for k in time_slots for d in days for c in classrooms for km in grades],
                        cat='Binary')
    g = LpVariable.dicts("g", [(k, d) for k in range(len(time_slots) - 1) for d in days], cat='Binary')

    # Define the objective function
    prob += lpSum(x) + lpSum(g)



    # Add constraints
    for km in grades:
        for c in classrooms:
            for j in lectures:
                # Constraint: Each lecture in each classroom must be assigned to exactly the specified number of teachers
                prob += lpSum(x[i, j, k, d, c ,km] for i in teachers for k in time_slots for d in days) == lectures[j]
                print(lectures,j)

                for i in teachers:
                    if j in teachers[i][1]:
                        # Constraint: If a teacher is qualified for a lecture, they can be assigned to at most their maximum workload
                        prob += lpSum(x[i, j, k, d, c, km] for k in time_slots for d in days) <= min(lectures[j], teachers[i][0])
                    else:
                        # Constraint: If a teacher is not qualified for a lecture, they cannot be assigned to it
                        prob += lpSum(x[i, j, k, d, c, km] for k in time_slots for d in days) == 0

            for d in days:
                # Constraint: The totx al number of lectures in each classroom on each day must not exceed the
                prob += lpSum(x[i, j, k, d, c , km] for i in teachers for j in lectures for k in time_slots) <= 4
                for k in time_slots:
                    # Constraint: Each lecture in each classroom on each day must be assigned to at most one teacher
                    prob += lpSum(x[i, j, k, d, c, km] for i in teachers for j in lectures) <= 1
                for k in range(len(time_slots) - 1):
                    # Constraint: If a teacher is assigned to a lecture in consecutive time slots, the binary variable g should be 1
                    prob += lpSum(x[i, j, time_slots[k], d, c, km] for i in teachers for j in lectures) - lpSum(
                        x[i, j, time_slots[k + 1], d, c, km] for i in teachers for j in lectures) >= -1 + g[k, d]

    for i in teachers:
        # Constraint: The total number of lectures assigned to each teacher must not exceed their maximum workload
        prob += lpSum(x[i, j, k, d, c, km] for j in lectures for k in time_slots for d in days for c in classrooms for km in grades) <= teachers[i][0]

        for d in days:
            for k in time_slots:
                # Constraint: Each teacher can only be assigned to at most one lecture in each time slot
                prob += lpSum(x[i, j, k, d, c, km ] for j in lectures for c in classrooms for km in grades) <= 1

        if teachers[i][2] != 'N':
            for d in days:
                if d in teachers[i][2]:
                    # Constraint: If a teacher has a day off, they cannot be assigned to any lecture on that day
                    for k in time_slots:
                        prob += lpSum(x[i, j, k, d, c, km ] for j in lectures for c in classrooms for km in grades ) == 0
    


    prob.solve()
            # Check the status
    status = LpStatus[prob.status]

    # Check if a feasible solution exists
    if status == "Optimal":
        print("A feasible solution exists.")
    else:
        print("No feasible solution exists.")
        exit()


    # Check if the problem is infeasible
    if prob.status == LpStatusInfeasible:
        infeasible_constraints = [constraint for constraint in prob.constraints if prob.constraints[constraint].slack < 0]

        print("The problem is infeasible. The following constraint(s) cannot be satisfied:")
        for constraint in infeasible_constraints:
            print(constraint)
    else:
        print("The problem is feasible. All constraints can be satisfied.")


    for grade in grades:
        schedules[grade] = {}  # Use a dictionary to store schedules for each grade

        for classroom in classrooms:
            schedules[grade][classroom] = []  # Use a list to store schedules for each classroom

            for time_slot in time_slots:
                entry = {'time_slot': time_slot, 'schedule': {day: '' for day in days}}

                for day in days:
                    for teacher in teachers:
                        for lecture in lectures:
                            if x[(teacher, lecture, time_slot, day, classroom, grade)].varValue == 1:
                                print(teacher, lecture, time_slot, day, classroom, grade)
                                entry['schedule'][day] = f"{teacher}/{lecture}"

                schedules[grade][classroom].append(entry)
    


    # Iterate over teachers
    for teacher in teachers:
        teacher_schedules[teacher] = []  # Use a list to store schedules for each teacher

        for time_slot in time_slots:
            entry = {'time_slot': time_slot, 'schedule': {day: '' for day in days}}

            for day in days:
                for lecture in lectures:
                    for classroom in classrooms:
                        for grade in grades:
                            if x[(teacher, lecture, time_slot, day, classroom, grade)].varValue == 1:
                                entry['schedule'][day] = f"{lecture}/{classroom}/{grade}"

            teacher_schedules[teacher].append(entry)

    

    # Iterate over days
    for day in days:
        schedules_by_day[day] = []  # Use a list to store schedules for each day

        for time_slot in time_slots:
            entry = {'time_slot': time_slot, 'schedule': {}}

            for teacher in teachers:
                for lecture in lectures:
                    for classroom in classrooms:
                        for grade in grades:
                            if x[(teacher, lecture, time_slot, day, classroom, grade)].varValue == 1:
                                entry['schedule'][f"{teacher}/{lecture}/{classroom}/{grade}"] = lecture

            schedules_by_day[day].append(entry)

    

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
                lectures = data["data"]["lectures"]
                classrooms = data["data"]["classrooms"]
                grades = data["data"]["grades"]
                teachers = data["data"]["teachers"]
                time_slots = data["data"]["time_slots"]
                days = data["data"]["days"]

            # Perform optimization using PuLP
            results = optimize_with_pulp(data, lectures, classrooms, grades, teachers, time_slots, days)

            # Render the home page with results
            return render_template('teacher.html', teacher_schedules=teacher_schedules)
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {e}"
        except Exception as e:
            return f"An error occurred: {e}"

    return 'Invalid file format. Please upload a JSON file.', 400


@app.route('/day')
def render_day_page():
    return render_template('day.html', schedules_by_day=schedules_by_day, days=days)

@app.route('/teacher')
def render_teacher_page():
    return render_template('teacher.html', teacher_schedules=teacher_schedules)

@app.route('/schedule')
def render_schedule_page():
    return render_template('schedule.html', schedules=schedules)

if __name__ == '__main__':
    app.run(debug=True)
            # Define a dictionary to store teacher schedules
