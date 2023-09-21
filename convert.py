import csv
import json

def flatten_json(json_data, parent_key='', separator='_'):
    items = {}
    for key, value in json_data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        if isinstance(value, dict):
            items.update(flatten_json(value, new_key, separator=separator))
        else:
            items[new_key] = value
    return items

# Your JSON data
data = {

    "data": {
        "lectures": {
            "Math": 2,
            "English": 2,
            "Science": 2,
            "History": 2
        },
        "classrooms": {
            "Classroom 1": {
                "Math": 2,
                "English": 2,
                "Science": 2,
                "History": 2
            },
            "Classroom 2": {
                "Math": 2,
                "English": 2,
                "Science": 2,
                "History": 2
            }
        },
        "grades": {
            "A": {
                "Classroom 1": {
                    "Math": 2,
                    "English": 2,
                    "Science": 2,
                    "History": 2
                },
                "Classroom 2": {
                    "Math": 2,
                    "English": 2,
                    "Science": 2,
                    "History": 2
                }
            },
            "B": {
                "Classroom 1": {
                    "Math": 2,
                    "English": 2,
                    "Science": 2,
                    "History": 2
                },
                "Classroom 2": {
                    "Math": 2,
                    "English": 2,
                    "Science": 2,
                    "History": 2
                }
            }
        },
        "teachers": {
            "Smith": [100, ["Math", "History", "Science"], ["N", "Friday"]],
            "Johnson": [100, ["English"], ["Friday", "N"]],
            "Williams": [100, ["Science", "English"], ["N", "N"]]
        },
        "time_slots": ["8-9", "9-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17"],
        "days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    }
}



# Flatten the JSON data
flat_data = flatten_json(data['data'])

# Define the CSV file name
csv_file = 'data.csv'

# Write the flattened data to CSV
with open(csv_file, 'w', newline='') as csvfile:
    fieldnames = flat_data.keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow(flat_data)
