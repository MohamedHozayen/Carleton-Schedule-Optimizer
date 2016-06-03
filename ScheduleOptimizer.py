#!/usr/bin/env python3

from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

# This class is used for each section of a given course, and contains all the
# corresponding lectures and labs/tutorials
class Section:
	def __init__(self, title, courseCode, section, CRN, time, day, room, prof, courseType):
		self.title = title
		self.courseCode = courseCode
		self.section = section
		self.CRN = CRN
		self.time = time
		self.day = day
		self.room = room
		self.prof = prof
		self.courseType = courseType

	# This adds a list of all the lab and tutorial sections for the given
	# lecture section
	def addLabsOrTuts(self, labstuts):
		self.labstuts = labstuts

# This class keeps track of sections, time slots, total breaks, and conflict
# for a given day
class Day:
	def __init__(self):
		self.sections = []
		self.conflict = False
		self.breaks = 0
		self.timeSlots = {'0835': 0,'0905': 0,'0935': 0,'1005': 0,'1035': 0,'1105': 0,'1135': 0,'1205': 0,'1235': 0,'1305': 0,'1335': 0,'1405': 0,'1435': 0,'1505': 0,'1535': 0,'1605': 0,'1635': 0,'1705': 0,'1735': 0,'1805': 0,'1835': 0,'1905': 0,'1935': 0,'2005': 0,'2035': 0}

	# This method adds a class section to the day, incrementing its corresponding
	#time slots. If a time slot contains more than one course, the conflict is set
	def addClass(self, section):
		times = section.time.split('-')
		startTime = int(times[0])
		endTime = int(times[1])
		# We go through each timeslot and increment section overlaps
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

# This class keeps track of every section for day of the week
class Schedule:
	def __init__(self):
		self.monday = Day()
		self.tuesday = Day()
		self.wednesday = Day()
		self.thursday = Day()
		self.friday = Day()
		self.breaks = 10000
		self.conflict = False

	# This method adds a section to the schedule. It checks which days to add
	# the section to and then adds them using the addClass method. After adding,
	# we check if the day has a conflict
	def addSection(self, newsection):
		if self.breaks == 10000: # The break time is reinitialized to 0 when we initially add a section
			self.breaks = 0
		for day in newsection.day: # section.day is a string storing the days the class is held
			if 'M' in day:
				self.breaks = self.breaks - self.monday.breaks
				self.monday.addClass(newsection)
				self.breaks = self.breaks + self.monday.breaks
				if self.monday.conflict == True:
					self.conflict = True
			elif 'T' in day:
				self.breaks = self.breaks - self.tuesday.breaks
				self.tuesday.addClass(newsection)
				self.breaks = self.breaks + self.tuesday.breaks
				if self.tuesday.conflict == True:
					self.conflict = True
			elif 'W' in day:
				self.breaks = self.breaks - self.wednesday.breaks
				self.wednesday.addClass(newsection)
				self.breaks = self.breaks + self.wednesday.breaks
				if self.wednesday.conflict == True:
					self.conflict = True
			elif 'R' in day:
				self.breaks = self.breaks - self.thursday.breaks
				self.thursday.addClass(newsection)
				self.breaks = self.breaks + self.thursday.breaks
				if self.thursday.conflict == True:
					self.conflict = True
			elif 'F' in day:
				self.breaks = self.breaks - self.friday.breaks
				self.friday.addClass(newsection)
				self.breaks = self.breaks + self.friday.breaks
				if self.friday.conflict == True:
					self.conflict = True
			elif day == 'O': # This means the section is an online course
				self.online.append(newsection.courseCode)

	def __str__(self):
		c = []
		s = 'Courses and sections for optimal schedule:\n'
		for day in ['monday','tuesday','wednesday','thursday','friday']:
			for section in getattr(self,day).sections:
				course = section.courseCode
				title = section.title
				if course not in c:
					c.append(title+' '+course+' '+section.section+' ('+section.CRN+')\n')
		# for course in self.online:
		# 	c.append(course+'(online)')
		for x in sorted(set(c)):
			# s += x+', '
			s += x
		return s[:-1]

	# This method returns the schedule as a string. It shows the total break time
	# and each class for each day
	def outputSchedule(self, numschedules):
		s = 'Minimal break time for the given courses: '+str(self.breaks*30)+' minutes'+'\n'
		s += 'Number of schedules with minimal break time: '+str(numschedules)+'\n\n'
		s += str(self)+'\n'+'\n'
		for day in ['monday','tuesday','wednesday','thursday','friday']:
			s += day.capitalize()+'\n'
			daylist = []
			for section in getattr(self,day).sections:
				daylist.append(section.time+": "+section.courseCode+' '+section.section+' '+section.courseType)
			if len(daylist) == 0:
				s += 'No courses today!\n'
			for section in sorted(daylist):
				s += section+'\n'
			s += '\n'
		s = s[:-2] # We want to remove the excess newline characters

		return s

# This function goes through the list of courses and gathers all the data for
# all of them, returning the data in a list of lists of course sections
def getSemesterData(courses, term):
	# Each element in semesterData is a course, whose first element is a list of the lectures
	# and whose second element is a list of the tutorials or labs
	semesterData = []
	for course in courses:
		if course != '':
			courseData = getCourseData(course, term)
			if courseData == 'invalid':
				return ''+course+' was an invalid course'
			semesterData.append(courseData)

	# We fill up the list with dummy courses to make the huge scheduleOptimizer work
	while(len(semesterData) < 6):
		dummy = Section('', '', '', '', '', '', '', '', '')
		dummy.addLabsOrTuts([Section('', '', '', '', '', '', '', '', '')])
		semesterData.append([dummy])
	return semesterData

# This function uses the Carleton API to grab all the section data for the given
# course, returning a list of every available section
def getCourseData(course, term):
	# The sections will be defined as tutorials or labs when they are constructed
	# Each course can only have either tutorials or labs
	sections = []

	# Here we get the json data from the Carleton course API and clean it up a bit
	url = 'http://at.eng.carleton.ca/engsched/wishlist.php?&courses='+course+'&term='+term+'&list='
	html = urlopen(url).read()
	soup = BeautifulSoup(html, 'html.parser')
	for script in soup(["script", "style"]):
		script.extract()
		text = soup.get_text()
		lines = (line.strip() for line in text.splitlines())
		chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
		text = '\n'.join(chunk for chunk in chunks if chunk)[:-37]

	# Check if the given course is valid
	if len(text) < 10:
		return 'invalid'

	# Here we grab the course data from the JSON data
	courseData = json.loads(text)[1][0]

	# We go through each section of the given course
	numberOfSections = len(json.loads(text)[1][0])
	# print('Number of sections: '+str(numberOfSections))
	for section in courseData:
		# Here we grab the lecture info from the JSON data and instantiate the section
		courseTitle = section['title']
		courseSection = section['section']
		courseCRN = section['crn']
		courseDays = section['days']
		courseTime = section['start'][:-3]+'-'+section['end'][:-3]
		courseTime = courseTime.replace(':','')
		courseRoom = section['room']
		courseProf = section['timeslots'][0]['prof']
		# print('\n'+courseTitle+'\n'+course+' '+courseSection+'\nCRN: '+courseCRN)
		# print('Days: '+courseDays+'\nTime: '+courseTime+'\nRoom: '+courseRoom)
		# print('Prof: '+courseProf)
		currentSection = Section(courseTitle, course, courseSection, courseCRN, courseTime, courseDays, courseRoom, courseProf, 'Lecture')

		# If there are no labs or tutorials, we are done with the current course
		numberOfLabsOrTutorials = len(section['labs'])
		if numberOfLabsOrTutorials == 0:
			labstuts = [Section('', '', '', '', '', '', '', '', '')]
			# print('There were no labs or tutorials for this course')
		# Here we have labs or tutorials, so we deal with all of them
		else:
			# I am assuming that all tutorials have the link_id T# and all labs have the link_id L#
			# This might cause errors in the future if a tutorial does not have the assumed ID
			labOrTutorial = section['labs'][0][0]['link_id']
			if labOrTutorial[0] == 'T':
				labOrTutorial = 'Tutorial'
			elif labOrTutorial[0] == 'L':
				labOrTutorial = 'Lab'
			# If we end up here then my link_id assumption is wrong
			else:
				pass

			# print('Lab or Tutorial: '+labOrTutorial)
			# print('Number of labs/tutorials: '+str(len(section['labs'][0])))

			# Here we gather the data for each lab/tutorial section and add them
			# to the list labstuts. This list will be added to the course section
			labstuts = []
			for labtut in section['labs'][0]:
				# print(labtut.keys())
				ltSection = labtut['section']
				ltCRN = labtut['crn']
				ltDay = labtut['days']
				ltTime = labtut['start'][:-3]+'-'+labtut['end'][:-3]
				ltTime = ltTime.replace(':','')
				ltRoom = labtut['room']
				# print('Lab/Tutorial Section: '+ltSection)
				# print('CRN: '+ltCRN)
				# print('Day: '+ltDay)
				# print('Time: '+ltTime)
				# print('Room: '+ltRoom)
				labstuts.append(Section(courseTitle, course, ltSection, ltCRN, ltTime, ltDay, ltRoom, courseProf, labOrTutorial))

		currentSection.addLabsOrTuts(labstuts)
		# The current section of the course is added to the list of sections
		sections.append(currentSection)

	# We return the list of all the sections for the given course
	return sections

def getOptimizedSchedules(semesterData):
	maxschedules = 10
	firstpass = True
	schedules = []
	schedule = Schedule()
	newschedule = Schedule()

	# The lectures and tutorials/labs for all sections are checked.
	for lec1 in semesterData[0]:
		for lt1 in lec1.labstuts:
			for lec2 in semesterData[1]:
				for lt2 in lec2.labstuts:
					for lec3 in semesterData[2]:
						for lt3 in lec3.labstuts:
							for lec4 in semesterData[3]:
								for lt4 in lec4.labstuts:
									for lec5 in semesterData[4]:
										for lt5 in lec5.labstuts:
											for lec6 in semesterData[5]:
												for lt6 in lec6.labstuts:
													newschedule.addSection(lec1)
													newschedule.addSection(lt1)
													newschedule.addSection(lec2)
													newschedule.addSection(lt2)
													newschedule.addSection(lec3)
													newschedule.addSection(lt3)
													newschedule.addSection(lec4)
													newschedule.addSection(lt4)
													newschedule.addSection(lec5)
													newschedule.addSection(lt5)
													newschedule.addSection(lec6)
													newschedule.addSection(lt6)
													if firstpass and not newschedule.conflict:
														schedule = newschedule
														schedules.append(newschedule)
														firstpass = False
													elif (newschedule.breaks < schedule.breaks) and not newschedule.conflict:
														schedule = newschedule
														schedules = []
														schedules.append(newschedule)
													elif (newschedule.breaks == schedule.breaks) and not newschedule.conflict:
														if len(schedules) <= maxschedules:
															schedules.append(newschedule)
													newschedule = Schedule()

	if firstpass:
		return 'There is no possible conflict-free schedule for the given courses'
		# print('There is no possible conflict-free schedule for the given courses')
		# return schedules
	else:
		return schedule.outputSchedule(len(schedules))
		# schedule.outputSchedule(len(schedules))
		# return schedules

# This function collects the semester data, ensures the courses were valid,
# and then runs the getOptimizedSchedules function
def scheduleOptimizer(subjects, term):
	if term == '':
		return 'Error:\nNo term selected'

	semesterData = getSemesterData(subjects, term)
	if isinstance(semesterData, str): # Here one or more of the given courses was invalid
		return semesterData
	# outputSectionDataToText(semesterData)
	return getOptimizedSchedules(semesterData)

term = '201630'
courses = ['COMP3005','ECOR3800','SYSC3110','SYSC3303','SYSC4001']
# courses = ['MATH2004']
print(scheduleOptimizer(courses,term))
