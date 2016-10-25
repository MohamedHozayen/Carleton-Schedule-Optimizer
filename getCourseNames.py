import requests
import json

courses = []
weirdCourses = []
url = 'http://at.eng.carleton.ca/engsched/scheduler.php?scope=all&term=201630'
allCourses = requests.get(url).json()

#gets the course Numbers of a given course Name
def getCourseNumber(courseName):
    return requests.get(url+'&dept='+courseName).json()

for course in allCourses:
    for number in getCourseNumber(course):
        if len(number) < 4:
            # Weird courses are those that have a number with less than 4 digits
            # This seems to apply only to MATH courses meant to substitute grade 12 courses
            weirdCourses.append(course+number)
        courses.append(course+" "+number)

with open('scheduler/static/courseNames.json', 'w') as fp:
    json.dump(courses, fp)

# The weird course codes are used by the view to ensure they don't get filtered out
# for looking like invalid codes
with open('scheduler/static/weirdCourseCodes.py', 'w') as fp:
    print('WEIRD_COURSE_CODES = '+str(weirdCourses), file=fp)
