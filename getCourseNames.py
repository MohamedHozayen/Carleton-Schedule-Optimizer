import requests
import json

courses = []
url = 'http://at.eng.carleton.ca/engsched/scheduler.php?scope=all&term=201630'
allCourses = requests.get(url).json()

#gets the course Numbers of a given course Name
def getCourseNumber(courseName):
    return requests.get(url+'&dept='+courseName).json()

for course in allCourses:
    for number in getCourseNumber(course):
        courses.append(course+" "+number)

with open('scheduler/static/courseNames.json', 'w') as fp:
    json.dump(courses, fp)
