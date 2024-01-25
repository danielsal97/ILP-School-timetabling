from pulp import *
def teacher_subject_assignment(teachers, subjects, days):

    # Initialize the problem
    assignment_problem = LpProblem("Teacher_Subject_Assignment", LpMaximize)

    # Decision variables: 1 if a teacher is assigned to a subject, else 0
    assign = LpVariable.dicts("assign", [(t, s) for t in teachers for s in subjects], cat='Binary')
    dayFree = LpVariable.dicts("dayFree", [(t, d) for t in teachers for d in days], cat='Binary')
    group = LpVariable.dicts("group", [(t, sub) for t in teachers for s in subjects for sub in subjects[s]], cat='Binary')
    # Objective: Maximize the coverage of subjects by qualified teachers
    assignment_problem += lpSum(assign[t, s] for t in teachers for s in subjects)
    assignment_problem += lpSum(dayFree[t, d] for t in teachers for d in days)
    assignment_problem += lpSum(group[t, sub] for t in teachers for s in subjects for sub in subjects[s])

    # Constraints
    for t in teachers:
        print(f"Schedule for Teacher {t}:")
        for d in days:
            if value(dayFree[t, d]) == 1:
                assigned_subjects = [s for s in subjects if value(assign[t, s]) == 1]
                print(f"  Day {d}: {', '.join(assigned_subjects) if assigned_subjects else 'No classes'}")
        print("\n")

        # Workload constraint
        assignment_problem += lpSum(assign[t, s] for s in subjects) <= teachers[t][0]

        # Day availability constraint
        for d in days:
            if d  in teachers[t][2]:
                assignment_problem += dayFree[t, d] == 1
    for s in subjects:
        if len(subjects[s]) > 1:
                for sub in subjects[s]:
                    assignment_problem += lpSum(group[t, sub]             for t in teachers) <= 1
    # Solve the problem
    assignment_problem.solve()
    print(assignment_problem.toDict)

        # Assuming the problem is already solved
    for t in teachers:
        print(f"\nSchedule for Teacher {t}:")

        # Subjects assigned to the teacher
        assigned_subjects = [s for s in subjects if value(assign[t, s]) == 1]
        if assigned_subjects:
            print(f"  Assigned Subjects: {', '.join(assigned_subjects)}")
        else:
            print("  No Assigned Subjects")

        # Groups within subjects
        for s in assigned_subjects:
            assigned_groups = [sub for sub in subjects[s] if value(group[t, sub]) == 1]
            print(f"    - Subject {s}: {'Groups ' + ', '.join(assigned_groups) if assigned_groups else 'No specific group'}")

        # Day availability
        available_days = [d for d in days if value(dayFree[t, d]) == 1]
        print(f"  Available Days: {', '.join(available_days) if available_days else 'No available days'}")


        # Initialize an empty dictionary to store the results
    teacher_schedule = {}

    # Assuming the problem is already solved
    for t in teachers:
        teacher_data = {
            "assigned_subjects": [],
            "groups": {},
            "available_days": []
        }

        # Subjects assigned to the teacher
        for s in subjects:
            if value(assign[t, s]) :
                teacher_data["assigned_subjects"].append(s)

                # Groups within the subject
                assigned_groups = [sub for sub in subjects[s]  ]
                teacher_data["groups"] = assigned_groups

        # Day availability
        teacher_data["available_days"] = [d for d in days if value(dayFree[t, d]) ]

        # Store the teacher's data in the dictionary
        teacher_schedule[t] += teacher_data

    # Now you can use the teacher_schedule dictionary for other purposes
    print(teacher_schedule)
