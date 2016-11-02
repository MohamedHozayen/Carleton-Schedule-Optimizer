import requests
import json

TERMS = ['201630','201710']

# Grabs all the course codes in a given term
def getCourseCodes(term):
    courseCodes = []
    weirdCourseCodes = []
    url = 'http://at.eng.carleton.ca/engsched/scheduler.php?scope=all&term='+term
    departments = requests.get(url).json()
    for department in departments:
        courseNumbers = requests.get(url+'&dept='+department).json()
        for number in courseNumbers:
            # Weird courses are those that have a number with less than 4 digits
            # This seems to apply only to MATH courses meant to substitute grade 12 courses
            if len(number) < 4:
                weirdCourseCodes.append(department+' '+number)
            else:
                courseCodes.append(department+' '+number)
    return courseCodes,weirdCourseCodes

courseCodes = []
weirdCourseCodes = []

for term in TERMS:
    result = getCourseCodes(term)
    courseCodes += result[0]
    weirdCourseCodes += result[1]

courseCodes = sorted(list(set(courseCodes)))
weirdCourseCodes = sorted(list(set(weirdCourseCodes)))

# Now we output the courseCodes to a file to be used for autocomplete in the form
with open('scheduler/static/courseNames.json', 'w') as fp:
    json.dump(courseCodes, fp)

# The weird course codes are used by the view to ensure they don't get filtered out
# for looking like invalid codes
with open('scheduler/static/weirdCourseCodes.py', 'w') as fp:
    print('WEIRD_COURSE_CODES = '+str(weirdCourseCodes), file=fp)
