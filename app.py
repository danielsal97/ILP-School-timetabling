
from flask import Flask, render_template, request, redirect, url_for
from pulp import *


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
teacher_schedules = {}
schedules_by_day = {}
schedules = {}
days = []
unsatisfied_constraints = []
teacher_conflicts = {}
jsonFileResults = {}
def check_data(classrooms, grades, teachers, time_slots, days,subject):
    max_workload = {}
    # # Perform preliminary checks for feasibility
    for teacher, teacher_data in teachers.items():
        max_workload.update({teacher: teacher_data[0]})
        
  
    for teacher in max_workload:
        for grade in grades:
            sum=0
            for classroom in grades[grade]:
                for subject in grades[grade][classroom]:
                    for amount in grades[grade][classroom][subject]:
                        if isinstance(amount, int):
                            sum+=amount
                            if grades[grade][classroom][subject][1] == teacher:
                               max_workload[teacher] -= grades[grade][classroom][subject][0]


        if max_workload[teacher] < 0:
            return False, f"Teacher {teacher} has got more lesson from his maximum workload."
        print(teacher, max_workload[teacher])


    return True, "Preliminary checks passed. data is ok ."



def optimize_with_pulp(classrooms, grades, teachers, time_slots, days,subjects):
     # Define the problem
    prob = LpProblem("School_Timetabling", LpMaximize)
   
    # Define the decision variables
    x = LpVariable.dicts("x", [(teacher, subject, time_slot,day, classroom, grade) for teacher  in teachers \
                               for grade in grades for classroom in classrooms for subject in subjects \
                                for time_slot in time_slots for day in days], cat='Binary')
    # Define the objective function here
    prob += lpSum(x)
    #constraints
    for day in days:
        for time  in time_slots:
            for teacher in teachers:
                # teacher can teach only one subject at a time
                prob += lpSum(x[(teacher, subject, time, day, classroom, grade)] \
                              for grade in grades for classroom in classrooms\
                                  for subject in subjects) <= 1

        for teacher in teachers:
            if day in teachers[teacher][2]:
                for time in time_slots:
                    # teacher has days off 
                    prob += lpSum(x[(teacher, subject, time, day, classroom, grade)]\
                                   for grade in grades for classroom in classrooms \
                                    for subject in subjects) == 0
    
        for grade in grades:
            for classroom in classrooms:
                if classroom in grades[grade]:

                    for teacher in teachers:
                        for subject in subjects:
                            if subject in grades[grade][classroom]:
                                #each can be taught once a day
                                prob += lpSum(x[(teacher, subject, time, day, classroom, grade)] for time in time_slots) <= 1



    for grade in grades:
        for classroom in classrooms:
            if classroom not in grades[grade]:
                prob += lpSum(x[(teacher, subject, time, day, classroom, grade)] for teacher in teachers for time in time_slots for day in days for subject in subjects) == 0

            else:
                for day in days:
                    #each day has at least 2 lessons
                    prob+= lpSum(x[(teacher, subject, time, day, classroom, grade)] for teacher in teachers for time in time_slots for subject in subjects) >=2
                    
                    for time in range(len(time_slots)-1):
                        #minimize the number of breaks between lessons
                        prob += lpSum(x[(teacher, subject, time_slots[time], day, classroom, grade)] for teacher in teachers for subject in subjects) - lpSum(x[(teacher, subject, time_slots[time+1], day, classroom, grade)] for teacher in teachers for subject in subjects) >= 0
                    for time in time_slots:
                        #at every time slot there is only one subject taught by one teacher
                        prob += lpSum(x[(teacher, subject, time, day, classroom, grade)] for teacher in teachers for subject in subjects) <= 1
                for subject in subjects:
                    if subject not in grades[grade][classroom]:
                        prob += lpSum(x[(teacher, subject, time, day, classroom, grade)] for teacher in teachers for time in time_slots for day in days) == 0 
                    else:
                        #number of subjects in a classroom is as demanded by the school
                        prob += lpSum(x[(teacher, subject, time, day, classroom, grade)] for teacher in teachers for time in time_slots for day in days) == grades[grade][classroom][subject][0]
                        for teacher in teachers:
                            if teacher != grades[grade][classroom][subject][1]:
                                prob += lpSum(x[(teacher, subject, time, day, classroom, grade)] for time in time_slots for day in days) == 0

                                
    # Solve the optimization problem with the default solver 
    prob.solve()
    # Check if the problem status is optimal
    if LpStatus[prob.status] != "Optimal":
        print("The problem is not solved optimally.")
        print("GLPk simplex is running...")
        prob.solve(GLPK_CMD("/opt/homebrew/bin/glpsol"))
        if LpStatus[prob.status] != "Optimal":
            print("The problem is not solved optimally. ")
        else:
            print("The problem is solved optimally.")       


# sorder result and pass it to schedule view 
    for grade in grades:
        schedules[grade] = {}  # Use a dictionary to store schedules for each grade
        for classroom in classrooms:
            if classroom in grades[grade]:
                schedules[grade][classroom] = []  # Use a list to store schedules for each classroom
                for time_slot in time_slots:
                    entry = {'time_slot': time_slot, 'schedule': {day: '' for day in days}}
                    for day in days:
                        for teacher in teachers:
                            for subject in subjects:
                                if x[(teacher, subject, time_slot, day, classroom, grade)].varValue == True:
                                    entry['schedule'][day] = f"{teacher}/{subject}"
                    schedules[grade][classroom].append(entry)
         


    # sorder result and pass it to teachers view 
    for teacher in teachers:
        teacher_schedules[teacher] = []  # Use a list to store schedules for each teacher
        for time_slot in time_slots:
            entry = {'time_slot': time_slot, 'schedule': {day: '' for day in days}}
            for day in days:
                for grade in grades:
                    for classroom in classrooms:
                        if classroom in grades[grade]:
                            for subject in subjects:
                                if subject in grades[grade][classroom]:
                                    if x[(teacher, subject, time_slot, day, classroom, grade )].varValue == 1:
                                        entry['schedule'][day] = f"{subject}/{classroom}/{grade}"
            teacher_schedules[teacher].append(entry)

    
    
    # sorder result and pass it to days view 
    for day in days:
        schedules_by_day[day] = []  # Use a list to store schedules for each day
        for time_slot in time_slots:
            entry = {'time_slot': time_slot, 'schedule': {}}
            for teacher in teachers:
                for grade in grades:
                    for classroom in classrooms:
                        if classroom in grades[grade]:
                            for subject in subjects:
                                if x[(teacher, subject, time_slot, day, classroom, grade)].varValue == 1:
                                    entry['schedule'][f"{teacher}/{subject}/{classroom}/{grade}"] = subject
            schedules_by_day[day].append(entry)




