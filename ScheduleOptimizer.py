import sys
import requests
import os.path
import pickle
from bs4 import BeautifulSoup
	
class Course:
	# This class has attributes containing the course title and the sections for each of the lectures, labs, and tutorials
	def __init__(self, title, lectures, labs, tutorials):
		self.title = title
		self.lectures = lectures
		self.labs = labs
		self.tutorials = tutorials
		# If there are no tuttorials or labs, we append dummy sections to those lists
		if self.tutorials == []:
			self.tutorials.append(Section('Dummy Tutorial','','','','','','',''))
		if self.labs == []:
			self.labs.append(Section('Dummy Lab','','','','','','',''))
			
	def ChangeTutorials(self, newtutorials):
		self.tutorials = newtutorials

	def CombineTutorials(self):
		if self.tutorials[0].title == 'Dummy Tutorial': # We don't do anything if the course has no tutorials
			return
		sections = '' # This string will hold all the sections for a given lecture (A, B, etc.)
		firstletter = ''
		firsttime = ''
		newtutorials = []
		firstpass = True
		i = 0 # i counts each tutorial in the list of tutorials
		x = 0 # x keeps track of the index containing the first tutorial for a given section (A, B, etc.)
		for tutorial in self.tutorials:
			currentletter = tutorial.GetSection()[0]
			currenttime = tutorial.GetTime()
			# Here we are not at the first tutorial for a given lecture section, so we add the current section to the growing sections string
			if currentletter == firstletter and currenttime == firsttime:
				sections = sections + '/' + tutorial.GetSection()
				i = i + 1
			# Here we are at the first tutorial for a given lecture section, so we assign the first letter. If we are not on the first pass, then we have hit the end of a section's tutorials and must add the previous letter's combined tutorial to the newtutorial list 
			else:
				firstletter = currentletter
				firsttime = currenttime
				if firstpass == True:
					firstpass = False
				else:
					# Since we are not on the first pass, we must put the combined sections into the first tutorial of a given letter and then add it to the newtutorials list
					newtutorials.append(self.tutorials[x].ChangeSection(sections))
					x = i
					i = i + 1
				# Here the sections string restarts, beginning with the current tutorial's section
				sections = tutorial.GetSection()
		# This step is skipped if there are no tutorials
		if not self.tutorials == []:
			# Here we put the combined sections into the first tutorial of the last letter and add it to the newtutorials list. We then change the tutorials in the object to the new combined ones.
			newtutorials.append(self.tutorials[x].ChangeSection(sections))
			self.ChangeTutorials(newtutorials)
		
class Section:
	# This class has 4 instance variables containing info on the listings
	def __init__(self, title, courseCode, section, CRN, time, day, location, prof):
		self.title = title
		self.courseCode = courseCode
		self.section = section
		self.CRN = CRN
		self.time = time
		self.day = day
		self.location = location
		self.prof = prof
	
	def GetSection(self):
		return self.section

	def GetTime(self):
		return self.time
		
	def ChangeSection(self, newsection):
		self.section = newsection
		return self

class Schedule:
	# This class has an attribute for each day of the week
	def __init__(self):
		self.monday = Day()
		self.tuesday = Day()
		self.wednesday = Day()
		self.thursday = Day()
		self.friday = Day()
		self.breaks = 10000
		self.conflict = False

	# This method adds a section to the schedule. It checks which days to add the section to and then adds them using the addClass method. After adding, we check if the day has a conflict
	def addSection(self, newsection):
		if self.breaks == 10000: # The break time is reinitialized to 0 when we initially add a section
			self.breaks = 0
		for day in newsection.day: # section.day is a string storing the days the class is held
			if 'M' in day:
				self.breaks = self.breaks - self.monday.getBreaks()
				self.monday.addClass(newsection)
				self.breaks = self.breaks + self.monday.getBreaks()
				if self.monday.conflict == True:
					self.conflict = True
			elif 'T' in day:
				self.breaks = self.breaks - self.tuesday.getBreaks()
				self.tuesday.addClass(newsection)
				self.breaks = self.breaks + self.tuesday.getBreaks()
				if self.tuesday.conflict == True:
					self.conflict = True
			elif 'W' in day:
				self.breaks = self.breaks - self.wednesday.getBreaks()
				self.wednesday.addClass(newsection)
				self.breaks = self.breaks + self.wednesday.getBreaks()
				if self.wednesday.conflict == True:
					self.conflict = True
			elif 'R' in day:
				self.breaks = self.breaks - self.thursday.getBreaks()
				self.thursday.addClass(newsection)
				self.breaks = self.breaks + self.thursday.getBreaks()
				if self.thursday.conflict == True:
					self.conflict = True
			elif 'F' in day:
				self.breaks = self.breaks - self.friday.getBreaks()
				self.friday.addClass(newsection)
				self.breaks = self.breaks + self.friday.getBreaks()
				if self.friday.conflict == True:
					self.conflict = True
	
	def getConflict(self):
		return self.conflict
		
	def getBreaks(self):
		return self.breaks
		
	# This method outputs the schedule, showing the total break time, conflict warning, and each class for each day
	def outputSchedule(self):
		print('Total break time: '+str(self.breaks*30)+' minutes')
		print('Conflicts: '+str(self.conflict)+'\n')
		for day in ['monday','tuesday','wednesday','thursday','friday']:
			print(day.capitalize())
			for section in getattr(self,day).sections:
				print(section.time+": "+section.courseCode+section.section)
			print('')

class Day:
	# This class has an attribute for sections, time slots, total breaks, and whether or not there is a conflict
	def __init__(self):
		self.sections = []
		self.conflict = False
		self.breaks = 0
		self.timeSlots = {'0835': 0,'0905': 0,'0935': 0,'1005': 0,'1035': 0,'1105': 0,'1135': 0,'1205': 0,'1235': 0,'1305': 0,'1335': 0,'1405': 0,'1435': 0,'1505': 0,'1535': 0,'1605': 0,'1635': 0,'1705': 0,'1735': 0,'1805': 0,'1835': 0,'1905': 0,'1935': 0,'2005': 0,'2035': 0}
	
	# This method adds a class section to the day, incrementing its corresponding time slots. If a time slot has more than one course in it, the conflict boolean is assigned True
	def addClass(self, section):
		times = section.time.split('-')
		startTime = int(times[0])
		endTime = int(times[1])
		# We go through each timeslot and increment ones where the current section overlaps
		for key in self.timeSlots:
			if (int(key) >= startTime and int(key) < endTime):
				self.timeSlots[key] = self.timeSlots[key] + 1
		# The conflict flag is raised if any timeslot has 2 courses at once
		if any(count > 1 for count in self.timeSlots.values()):
			self.conflict = True
		self.sections.append(section)
		self.calculateBreaks() # After appending a section, the total break time is calculated
	
	# This method counts up all the 30 minute block breaks in the day and stores it in the breaks attribute
	def calculateBreaks(self):
		values = ''
		for key in sorted(self.timeSlots):
			values = values+str(self.timeSlots[key])
		newvalues = ''
		for value in values:
			if value != '0':
				newvalues = newvalues + '1'
			else:
				newvalues = newvalues + '0'
		values = newvalues
		self.breaks = values.count('0') - len(values.split('1',1)[0]) - len(values[::-1].split('1',1)[0])
		
	def getBreaks(self):
		return self.breaks

	def getTimeSlots(self):
		return self.timeSlots
		
def getWebsiteData(term, subject, coursecode):
	url = 'https://central.carleton.ca/prod/bwckschd.p_get_crse_unsec'
	params = 'term_in='+term+'&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj='+subject+'&sel_crse='+coursecode+'&sel_title=&sel_schd=%25&sel_from_cred=&sel_to_cred=&sel_levl=%25&sel_instr=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a'
	r = requests.post(url, data=params)
	soup = BeautifulSoup(r.text, "html.parser", from_encoding='utf8')
	return soup

def getCourseData(data,courseCode):
	# These lists will contain all the sections of the corresponding type for the given course
	lectures = []
	labs = []
	tutorials = []
	
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
	
	# When the flag is true, we are grabbing the section title. When the flag is false, we are grabbing the section details. When the counter is at 2, we have all the data needed to record a sectioon
	sectionflag = True
	firstSectionGrab = True
	counter = 0

	for child in lis:
		child = str(child)
		sectionflag = not sectionflag
		
		# Here we gather the section letter and CRN for each section
		if sectionflag:
			crnAndSection = child[114:].strip('</a></th>').partition(' - ')[2]
			courseCRN = crnAndSection.partition(' - ')[0]
			courseSection = crnAndSection.partition(' - ')[2].partition(' - ')[2]
			
			# On the first pass we grab the course title
			if firstSectionGrab:
				courseTitle = child[114:].strip('</a></th>').partition(' - ')[0]
				firstSectionGrab = not firstSectionGrab
			else:
				counter = counter+1
			
		# Here we gather the details for the current section
		else:	
			j = 1
			typeIncrement = 0
			for thing in child.splitlines():
				if j == 11 :
					courseType = thing.replace('Schedule Type','').replace('Campus','').replace('Main','Lecture').strip('  ')
					# Here we check if we are dealing with a lecture or not (shown as 'Main')
					if 'Main' in thing:
						typeIncrement = 2
					else:
						typeIncrement = 0
				# The increment depends on the type of section we are looking at and is determined earlier
				if j == (28 + typeIncrement):
					time = thing[22:].strip('</td>').replace(' ','').replace(':','')
					time = time.split('-')
					# We translate the 12 hour time to 24 hour time
					if 'pm' in time[0] and ('12' not in time[0] or len(time[0]) < 6):
						time[0] = str(int(time[0].strip('pm'))+1200)
					elif 'pm' in time[0] and '12' in time[0]:
						time[0] = time[0].strip('pm')
					else:
						time[0] = str(int(time[0].strip('am')))
						if int(time[0]) < 1000:
							time[0] = '0'+time[0]					
					if 'pm' in time[1] and ('12' not in time[1] or len(time[1]) < 6):
						time[1] = str(int(time[1].strip('pm'))+1200)
					elif 'pm' in time[1] and '12' in time[1]:
						time[1] = time[1].strip('pm')					
					else:
						time[1] = str(int(time[1].strip('am')))
						if int(time[1]) < 1000:
							time[1] = '0'+time[1]	
					courseTime = time[0]+'-'+time[1]					
				if j == (29 + typeIncrement):
					courseDay = thing[22:].strip('</td>')
				if j == (30 + typeIncrement):
					courseLocation = thing[22:].strip('</td>')
				if j == (33 + typeIncrement):
					courseProf = thing[22:].replace(r1,'').replace(r2,'').replace(r3,'').replace('   ',' ').replace('  ',' ')
				j += 1	
			counter = counter+1

		# Here we make an instance of the section class and add it to the corresponding list			
		if counter == 2: 
			section = Section(courseTitle,courseCode,courseSection,courseCRN,courseTime,courseDay,courseLocation,courseProf)
			if any(i.isdigit() for i in courseSection): # Lecture sections don't have numbers
				if courseType == 'Laboratory':
					labs.append(section)
				else: # Here the section is a tutorial
					tutorials.append(section)
			else: # Here the section is a lecture
				lectures.append(section)
			counter = 0 # Reset the counter
			
	course = Course(courseTitle, lectures, labs, tutorials)
	return course

def getSemesterData(term, subject, coursecode):
	semesterData = []
	
	# We add each course's data to the semester data
	for i in range(1, len(subject)+1):
		soup = getWebsiteData(term, subject[str(i)], coursecode[str(i)])
		tag = soup.body.contents[5].contents[13]
		course = getCourseData(tag,subject[str(i)]+coursecode[str(i)])
		semesterData.append(course)
	return semesterData
	
def outputAllSectionData(semesterData):
	# We open an output text file
	text_file = open("Output.txt", "w")

	for course in semesterData:
		text_file.write('********************************************\n')
		text_file.write(course.title+'\n\n')
		
		if len(course.lectures) > 0:
			text_file.write('Lectures\n-------------------\n')
			for lecture in course.lectures:
				text_file.write('Section: '+lecture.section+'\n')
				text_file.write('CRN: '+lecture.CRN+'\n')
				text_file.write('Time: '+lecture.time+'\n')
				text_file.write('Days: '+lecture.day+'\n')
				text_file.write('Location: '+lecture.location+'\n')
				text_file.write('Professor: '+lecture.prof+'\n\n')
		if len(course.labs) > 1:
			text_file.write('Labs\n-------------------\n')
			for lab in course.labs:
				text_file.write('Section: '+lab.section+'\n')
				text_file.write('CRN: '+lab.CRN+'\n')
				text_file.write('Time: '+lab.time+'\n')
				text_file.write('Days: '+lab.day+'\n')
				text_file.write('Location: '+lab.location+'\n')
				text_file.write('Professor: '+lab.prof+'\n\n')
		if len(course.tutorials) > 1:
			text_file.write('Tutorials\n-------------------\n')
			for tutorial in course.tutorials:
				text_file.write('Section: '+tutorial.section+'\n')
				text_file.write('CRN: '+tutorial.CRN+'\n')
				text_file.write('Time: '+tutorial.time+'\n')
				text_file.write('Days: '+tutorial.day+'\n')
				text_file.write('Location: '+tutorial.location+'\n')
				text_file.write('Professor: '+tutorial.prof+'\n\n')
			
	text_file.close()

def getSemesterObject():
	# Check if the dump is present. If so, open the dump to get the data. If not we must produce the data and then dump it.
	if not os.path.isfile('data.dump'):
		# These variables determine the courses we use for the schedule
		term = '201530'
		subject = {'1': 'SYSC', '2': 'SYSC', '3': 'MATH', '4': 'ELEC', '5': 'CCDP', }
		coursecode = {'1': '2004', '2': '2001', '3': '2004', '4': '2501', '5': '2100', }

		semesterData = getSemesterData(term, subject, coursecode)
		outputAllSectionData(semesterData)
		# Here we dump the data
		with open('data.dump', 'wb') as output:
			pickle.dump(semesterData, output, pickle.HIGHEST_PROTOCOL)
	else:
		# Here we just load the data 
		with open('data.dump', 'rb') as input:
			semesterData = pickle.load(input) # protocol version is auto detected	
	return semesterData

def getCombinations(semesterData):
	combinations = 1
	for course in semesterData:
		combinations = combinations*len(course.lectures)
		if len(course.labs) != 0:
			combinations = combinations*len(course.labs)
	print ('Total combinations: '+str(combinations))
	
def getOptimizedSchedule(semesterData):
	firstpass = True
	schedule = Schedule()
	newschedule = Schedule()
	
	# The lectures, tutorials, and labs for all sections are checked
	for lecture0 in semesterData[0].lectures:
		for lab0 in semesterData[0].labs:
			for lecture1 in semesterData[1].lectures:
				for lab1 in semesterData[1].labs:
					for lecture2 in semesterData[2].lectures:
						for lab2 in semesterData[2].labs:
							for lecture3 in semesterData[3].lectures:
								for lab3 in semesterData[3].labs:
									for lecture4 in semesterData[4].lectures:
										for lab4 in semesterData[4].labs:
											newschedule.addSection(lecture0)
											newschedule.addSection(lab0)
											newschedule.addSection(lecture1)
											newschedule.addSection(lab1)
											newschedule.addSection(lecture2)
											newschedule.addSection(lab2)
											newschedule.addSection(lecture3)
											newschedule.addSection(lab3)
											newschedule.addSection(lecture4)
											newschedule.addSection(lab4)
											if firstpass and not newschedule.getConflict():
												schedule = newschedule
												firstpass = False
											elif (newschedule.getBreaks() < schedule.getBreaks()) and not newschedule.getConflict():
												schedule = newschedule
											newschedule = Schedule()
	if firstpass:
		print('There is no possible conflict-free schedule for the given courses')
		return newschedule
	else:
		schedule.outputSchedule()
		return schedule
	
def main():
	semesterData = getSemesterObject()
	for course in semesterData:
		course.CombineTutorials()
	outputAllSectionData(semesterData)
	schedule = getOptimizedSchedule(semesterData)
	
main()