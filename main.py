
from flask import Flask, render_template, request, redirect
from app import * 
import json


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'



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
                grades_data = data["data"]["grades"]
                classrooms_data = data["data"]["classroom"]
                teachers_data = data["data"]["teachers"]
                time_slots = data["data"]["time_slots"]
                days = data["data"]["days"]
                subjects_data = data["data"]["subjects"]
                print(grades_data)
                


            
            # Perform optimization using PuLP
            check = check_data(classrooms_data, grades_data, teachers_data, time_slots, days,subjects_data)
            if check[0] == False:
                print(check[1])
                exit(0)
            else:
                print("data is valid")

            
            results = optimize_with_pulp(classrooms_data, grades_data, teachers_data, time_slots, days,subjects_data)

            # Render the home page with results
            return render_template('teacher.html', teacher_schedules=teacher_schedules)
        except json.JSONDecodeError as e:
            return f"Error decoding JSON: {e}"
        except Exception as e:
            return f"An error occurred: {e}"

    return 'Invalid file format. Please upload a JSON file.', 400
    


@app.route('/day')
def render_day_page():
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