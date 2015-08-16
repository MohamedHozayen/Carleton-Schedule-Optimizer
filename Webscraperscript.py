import sys
import requests
from bs4 import BeautifulSoup
		
def getWebsiteData(term, subject, coursecode):
	url = 'https://central.carleton.ca/prod/bwckschd.p_get_crse_unsec'
	params = 'term_in='+term+'&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj='+subject+'&sel_crse='+coursecode+'&sel_title=&sel_schd=%25&sel_from_cred=&sel_to_cred=&sel_levl=%25&sel_instr=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a'
	r = requests.post(url, data=params)
	soup = BeautifulSoup(r.text, "html.parser", from_encoding='utf8')
	return soup

def getCourseData(data):
	# These strings are replaced when found in the professor list
	r1 = '(<abbr title="Primary">P</abbr>)</td>'
	r2 = '<abbr title="To Be Announced">'
	r3 = '</abbr></td>'
	
	# Here we make a list containing all the sections and all their details
	lis = []
	for child in data.children:
		for item in child:
			if item != '\n':
				lis.append(item)
	
	# For ELEC 2501, 11 is the type of class, 28 the time, 29 the day, 30 the location, and 33 the prof
	result = []
	courseSections = []
	courseCRNs = []
	typeOfClass = []
	timeOfClass = []
	dayOfClass = []
	locationOfClass = []
	profOfClass = []
	
	# When the flag is true, we are grabbing the section title. When the flag is false, we are grabbing the section details
	sectionflag = True
	firstSectionGrab = True
	
	for child in lis:
		child = str(child)
		sectionflag = not sectionflag
		
		# Here we make a list of all the course sections
		if sectionflag:
			crnAndSection = child[114:].strip('</a></th>').partition(' - ')[2]
			crn = crnAndSection.partition(' - ')[0]
			sectionLetter = crnAndSection.partition(' - ')[2].partition(' - ')[2]
			courseSections.append(sectionLetter)
			courseCRNs.append(crn)
			
			# On the first pass we grab the course title
			if firstSectionGrab:
				result.append(child[114:].strip('</a></th>').partition(' - ')[0])
				firstSectionGrab = not firstSectionGrab
		
		# Here we make lists of the details for the course sections
		else:	
			j = 1
			typeIncrement = 0
			for thing in child.splitlines():
				if j == 11 :
					typeOfClass.append(thing.replace('Schedule Type','').replace('Campus','').replace('Main','Lecture'))
					# Here we check if we are dealing with a lecture or not (shown as 'Main')
					if 'Main' in thing:
						typeIncrement = 2
					else:
						typeIncrement = 0
				# The increment depends on the type of section we are looking at and is determined earlier
				if j == (28 + typeIncrement):
					timeOfClass.append(thing[22:].strip('</td>').replace('am','').replace('pm','').replace(' ',''))
				if j == (29 + typeIncrement):
					dayOfClass.append(thing[22:].strip('</td>'))
				if j == (30 + typeIncrement):
					locationOfClass.append(thing[22:].strip('</td>'))
				if j == (33 + typeIncrement):
					profOfClass.append(thing[22:].replace(r1,'').replace(r2,'').replace(r3,'').replace('   ',' ').replace('  ',' '))
				j += 1	
	
	# The zeroth element in the result list is the course title, followed by the sections [1], the CRNs [2], section type [3], time [4], day [5], location [6], and professor [7]
	result.append(courseSections)
	result.append(courseCRNs)
	result.append(typeOfClass)
	result.append(timeOfClass)
	result.append(dayOfClass)
	result.append(locationOfClass)
	result.append(profOfClass)
	return result

def getSemesterData(term, subject, coursecode):
	semesterData = []
	
	# We add each course's data to the semester data
	for i in range(1, len(subject)+1):
		soup = getWebsiteData(term, subject[str(i)], coursecode[str(i)])
		tag = soup.body.contents[5].contents[13]
		semesterData.append(getCourseData(tag))
		
	return semesterData
	
def outputAllSectionData(semesterData):
	# We open an output text file
	text_file = open("Output.txt", "w")

	for course in semesterData:
		text_file.write('********************************************\n')
		text_file.write((course[0])+'\n\n')
		
		# This loop prints every section
		for i in range(0, len(course[1])):
			text_file.write('Section: '+(course[1][i])+'\n')
			text_file.write('CRN: '+(course[2][i])+'\n')
			text_file.write('Type: '+(course[3][i])+'\n')
			text_file.write('Time: '+(course[4][i])+'\n')
			text_file.write('Days: '+(course[5][i])+'\n')
			text_file.write('Location: '+(course[6][i])+'\n')
			text_file.write('Professor: '+(course[7][i])+'\n\n')
			
	text_file.close()

term = '201530'
subject = {'1': 'SYSC', '2': 'SYSC', '3': 'MATH', '4': 'ELEC', '5': 'CCDP', }
coursecode = {'1': '2004', '2': '2001', '3': '2004', '4': '2501', '5': '2100', }

semesterData = getSemesterData(term, subject, coursecode)
outputAllSectionData(semesterData)