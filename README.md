# Introduction
Finding an optimal solution for creating a school timetable is a complex and challenging task. This process involves considering numerous constraints. Manual timetable creation often results in deficiencies, scheduling conflicts, and suboptimal resource utilization. As data scales up, both in terms of volume and constraints, the problem becomes even more daunting. Multiple variables must be adjusted to accommodate the needs of teachers, students, and classrooms.
In this project, an internet-based model using linear planning was developed to address various constraints and solve the following problem:
Assigning teachers and lectures according to requirements for multiple grades and classes, while considering various constraints and requirements, to create an efficient and balanced timetable that maximizes resource utilization and minimizes conflicts.


# Project Goals:
Automatic scheduling - The project aims to automate the process of creating school timetables, eliminating the need for manual scheduling efforts. This not only saves time but also reduces the risk of human error.
Optimization - Using mathematical optimization algorithms, the application aims to optimize resource utilization, such as classroom availability and teacher workload, by allocating resources in the most efficient manner possible.
Flexible customization - The application will adapt to different scheduling constraints and preferences, making it suitable for a wide range of educational institutions, from elementary schools to universities.
User-friendly interface - To make the scheduling process accessible to administrators and educators, the project provides an intuitive web interface where users can upload data and view timetables in a convenient and easy-to-understand format.


# Solving the Problem Using Linear Planning
A linear planning problem involves optimizing a linear function subject to linear constraints. In other words, given variables and a set of inequalities between a linear equation involving the variables and constants, the objective is to find the maximum or minimum value of the linear function subject to all the inequalities.
Integer Linear Programming (ILP) addresses a similar problem to linear planning, but with the additional constraint that variables must have integer values. While a regular linear planning problem can be solved by polynomial algorithms, ILP problems are NP-hard.
To solve the timetable system problem, several parameters need to be defined: decision variables, objective function, constraints, and the problem definition (i.e., whether to maximize or minimize it).
The problem entails solving the timetable system for a school, addressing constraints related to working hours, classes, teachers, grades, days, time slots, and subjects. In optimization terms, the objective is to maximize the number of teacher and subject assignments to classes and grades while prioritizing constraints.
Based on your parameters for ILP troubleshooting.
Based on the definition, we aim to maximize the results.
For each teacher (t), subject (s), day (d), hour (h), and class (g), x is defined as a binary variable, taking values of 0 or 1. It equals 1 if teacher t teaches subject s to class g on day d and at hour h, otherwise it equals 0.
Mathematically, given the sets of teachers (), subjects (), days (), time slots (), classes (), and grades ().
The decision variable is defined as follows:

Define x: a teacher teaching a subject at a specific day and time, belonging to a class.
x[teacher, subject, time_slot, day, class, grade] ∈ {0,1}
Based on defined constraints, it will be assigned 1 when meeting other conditions, otherwise 0.

Now, after defining the decision variables and the problem definition (maximization/minimization), we will construct our functions. That is, we want to maximize the possible assignments function and the constraints function, encompassing all decision variables:

∑_(t∈Teachers,s∈Subjects, ts∈Time_slots, d∈Days, c∈Classes, g∈Grades)▒〖x[t,s,ts,d,c,g]〗


Finally, we aim to define the constraints for selecting the optimal assignments.
Examples of some constraints include:
- A teacher cannot teach more than one class at the same time and on the same day.
- A teacher should not exceed the assigned number of hours.
- Days off can be defined for teachers when they do not teach.
- Teachers will only teach subjects within their field.
- The number of lessons for each subject in each class should meet the requirements.

Some constraints are easy to define mathematically (and simpler to program),
while others are more complex, such as prioritizing early hours to avoid gaps.

Practically, you can see an implementation in Python using the PuLP library.

The PuLP library is a Python library used for building and solving optimization problems. It aids in solving various mathematical and logical problems, including linear problems, integer variables, and more.

With PuLP, you can define variables, objectives (functions of interest), and linear and logical constraints. Once the problem is defined, there are a variety of optimization algorithms that can be used.


# Project structure:
This project is built from two parts backend and frontend, linked by flask.
Bottle is a library for web applications written in Python. It provides a simple and flexible tool for developing and building network applications, and it makes for efficient and simple endpoint representation and access.
The frontend - written in html css and js
On the user page, the user must upload a json file and he will receive 3 views of the time system. Display of teachers, classes/layers and days.
Shown can examine the various aspects.
An example of the file structure:
Grades - contains the requirements, which layers and classes exist in it, in addition which subjects are studied, how many time slots for each of them and who is the teacher who teaches them.
Teachers - an array containing the maximum number of weekly hours for a teacher, subjects he teaches, and days off he will not teach.
Lectures - an array of subjects
Classroom - an array of classrooms
Time_slots – an array of times
Days - an array of days

After uploading a file, you will receive the following views:

The backend is written in python
Its function is to read the data of the Json file and performs preliminary checks for the input in order to save running time, for example the number of study hours the lecturer received does not exceed the maximum registered to him.
Information and an error occurred will show an error message.
Otherwise, optimization will be performed by cbc or simplex , info and simplex will fail and try using cbc .
The system will organize the data and transfer it via flask to the appropriate html pages, where a translation will be made to the time and time system display.

# Technologies and tools:
Python 3 – the main programming language used by the project.
Flask – a python web framework used to create the backend of the application.
The pulp library - a library for linear programming that is used to write the constraints and solve them.
CBC solver - open source ILP solver, used by default in the pulp library
GLPK - an external solver used for optimization tasks, part of an open source library that provides for solving LP and ILP problems using simplex
Use of HTML, CSS, JAVASCRIPT languages



