#!/usr/bin/env python3

from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import copy

# This class is used for each section of a given course, and contains all the
# corresponding lectures and labs/tutorials
class Section:
	def __init__(self, title, courseCode, section, CRN, time, day, room, prof, courseType, full):
		self.title = title
		self.courseCode = courseCode
		self.section = section
		self.CRN = CRN
		self.time = time
		self.day = day
		self.room = room
		self.prof = prof
		self.courseType = courseType
		self.specialFlag = False
		self.full = full

	# This adds a list of all the lab and tutorial sections for the given
	# lecture section
	def addLabsOrTuts(self, labstuts):
		self.labstuts = labstuts

	# This adds extra lecture sections that are separate from the regular lectures
	# This applies mainly to ECOR1010 with its TSE lectures
	def addSpecial(self, special):
		self.special = special
		self.specialFlag = True

	def __str__(self):
		return self.courseCode+self.section+'\n'+self.courseType+'\n'+self.day+self.time+'\n'

# This class keeps track of sections, time slots, total breaks, and conflict
# for a given day
class Day:
	def __init__(self):
		self.sections = []
		self.breaks = 0
		self.timeSlots = {'0835': 0,'0905': 0,'0935': 0,'1005': 0,'1035': 0,'1105': 0,'1135': 0,'1205': 0,'1235': 0,'1305': 0,'1335': 0,'1405': 0,'1435': 0,'1505': 0,'1535': 0,'1605': 0,'1635': 0,'1705': 0,'1735': 0,'1805': 0,'1835': 0,'1905': 0,'1935': 0,'2005': 0,'2035': 0}

	# This method adds a course section to the day, incrementing its corresponding
	# time slots.
	def addSection(self, section):
		if section.courseType == 'Online Course':
			self.sections.append(section)
			return
		times = section.time.split('-')
		startTime = int(times[0])
		endTime = int(times[1])
		# We go through each timeslot and increment section overlaps
		for key in self.timeSlots:
			if (int(key) >= startTime and int(key) < endTime):
				self.timeSlots[key] += 1
		self.sections.append(section)

	# This method removes a given course section from the day, decrementing its
	# time slots
	def removeSection(self, section):
		times = section.time.split('-')
		startTime = int(times[0])
		endTime = int(times[1])
		# We go through each timeslot and increment section overlaps
		for key in self.timeSlots:
			if (int(key) >= startTime and int(key) < endTime):
				self.timeSlots[key] -= 1
		self.sections.remove(section)

	# The conflict flag is raised if any timeslot has 2 courses at once
	def checkForConflicts(self):
		if any(count > 1 for count in self.timeSlots.values()):
			return True
		return False

	# This method counts up all the 30 minute block breaks in the day and stores it in the breaks attribute
	def calculateBreaks(self):
		# If there is one course or two courses for the day, then there are no breaks
		if len(self.sections) - sum(x.courseType == 'Online Course' for x in self.sections	) < 2:
			self.breaks = 0
			return 0
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
		return self.breaks

	# This method adds one time filter in the format ########, with the first
	# four numbers indicating the start and the last four indicating the end
	def addFilter(self, filter):
		start = filter[0:4]
		end = filter[4:8]
		while int(start) < int(end):
			self.timeSlots[start] += 1
			start = sorted(self.timeSlots.keys())[sorted(self.timeSlots.keys()).index(start)+1]

	# This method checks if there are any sections in the day that are full
	def checkForFullSections(self):
		for section in self.sections:
			if section.full:
				return True

# This class keeps track of every section for day of the week
class Schedule:
	def __init__(self):
		self.monday = Day()
		self.tuesday = Day()
		self.wednesday = Day()
		self.thursday = Day()
		self.friday = Day()
		self.breaks = 0
		self.noFullSectionsAllowed = False

	# This method adds a section to the schedule. It checks which days to add
	# the section to and then adds them using the Day addSection() method
	def addSection(self, newsection):
		if newsection.day == 'Online':
			self.monday.addSection(newsection)
			return
		for day in newsection.day: # section.day is a string storing the days the class is held
			if 'M' in day:
				self.monday.addSection(newsection)
			elif 'T' in day:
				self.tuesday.addSection(newsection)
			elif 'W' in day:
				self.wednesday.addSection(newsection)
			elif 'R' in day:
				self.thursday.addSection(newsection)
			elif 'F' in day:
				self.friday.addSection(newsection)
		if newsection.specialFlag:
			self.addSection(newsection.special)

	# This method removes a section from the schedule.
	def removeSection(self, newsection):
		for day in newsection.day: # section.day is a string storing the days the class is held
			if 'M' in day:
				self.monday.removeSection(newsection)
			elif 'T' in day:
				self.tuesday.removeSection(newsection)
			elif 'W' in day:
				self.wednesday.removeSection(newsection)
			elif 'R' in day:
				self.thursday.removeSection(newsection)
			elif 'F' in day:
				self.friday.removeSection(newsection)
		if newsection.specialFlag:
			self.removeSection(newsection.special)

	# This method iterates over every day, calling their own checkForConflicts methods
	# If the no full sections are allowed, then we check for those as well
	def checkForConflicts(self):
		for day in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
			if day.checkForConflicts():
				return True
			if self.noFullSectionsAllowed:
				if day.checkForFullSections():
					return True
		return False

	# This method iterates over every day, calculating their total break times
	def calculateBreaks(self):
		self.breaks = 0
		for day in [self.monday, self.tuesday, self.wednesday, self.thursday, self.friday]:
			self.breaks += day.calculateBreaks()

	def __str__(self):
		c = []
		s = ''
		for day in ['monday','tuesday','wednesday','thursday','friday']:
			for section in getattr(self,day).sections:
				course = section.courseCode
				title = section.title
				if course not in c:
					if section.courseType == 'Online Course':
						c.append(title+' '+course+' '+section.section+' (Online Course) ('+section.CRN+')\n')
					else:
						c.append(title+' '+course+' '+section.section+' ('+section.CRN+')\n')

		for x in sorted(set(c)):
			s += x
		return s[:-1]

	# This method returns the break time for the given schedule
	def outputBreakTime(self):
		hours = int(self.breaks/2)
		minutes = self.breaks*30%60
		s = 'The minimum break time for these courses with the given time filters is '+str(hours)+' hours'
		if minutes:
			s += ' and '+str(minutes)+' minutes'
		return s

	# This method gathers all the sections for the schedule into a JSON object
	def getJSON(self):
		data = []
		i = 1
		for day in ['monday','tuesday','wednesday','thursday','friday']:
			for section in getattr(self,day).sections:
				sectionData = {}
				sectionData['title'] = section.title
				sectionData['courseCode'] = section.courseCode+' '+section.section
				sectionData['CRN'] = section.CRN
				sectionData['courseType'] = section.courseType
				sectionData['day'] = i
				sectionData['start'] = section.time[:2]+':'+section.time[2:4]
				sectionData['end'] = section.time[-4:-2]+':'+section.time[-2:]
				sectionData['prof'] = section.prof
				sectionData['room'] = section.room
				sectionData['full'] = section.full
				data.append(sectionData)
			i+=1
		return data

	# This method goes through each filter, adding it as a dummy section to each corresponding day
	# Each filter is of the form X########, with X being the day and #### the 30 minute time blocks at the start and end
	def addFilters(self, filters):
		for fil in filters:
			if 'M' in fil[0]:
				self.monday.addFilter(fil[1:])
			elif 'T' in fil[0]:
				self.tuesday.addFilter(fil[1:])
			elif 'W' in fil[0]:
				self.wednesday.addFilter(fil[1:])
			elif 'R' in fil[0]:
				self.thursday.addFilter(fil[1:])
			elif 'F' in fil[0]:
				self.friday.addFilter(fil[1:])

# This function goes through a list of schedules, consolidating the data into a JSON object
def getJSONData(schedules):
	data = []
	for schedule in schedules:
		data.append(schedule.getJSON())
	return json.dumps(data)

# This function uses the Carleton API to grab all the section data for the given
# course, returning a list of every available section
def getCourseData(course, term, noFullCoursesFlag):
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

	# This fixes receiving unwanted data in the JSON
	text = text.split('\n')[0]

	# Check if the given course is valid
	if len(text) < 10:
		return 'invalid'

	# Here we grab the course data from the JSON data
	courseData = json.loads(text)[1][0]

	for section in courseData:
		# This flag keeps track of sections with extra lectures (e.g. ECOR1010)
		specialFlag = False

		# Here we grab the lecture info from the JSON data and instantiate the section
		courseTitle = section['title']
		courseSection = section['section']
		courseCRN = section['crn']
		courseProf = section['timeslots'][0]['prof']
		courseFull = section['space'] == 0

		if not noFullCoursesFlag or not courseFull:
			# Here we have an online course
			if section['link_id'] == 'AV':
				currentSection = Section(courseTitle, course, courseSection, courseCRN, '', 'Online', '', courseProf, 'Online Course', courseFull)
			else:
				# For some reason, the JSON started showing days twice for sections with tutorials or labs
				# This chunk of code handles that case while still taking care of "special" sections
				days = section['days']
				if len(set(days.split(','))) == 1:
					days = days[:2]

				# If there is a comma, then we have the special extra lecture
				if ',' in days:
					days = days.split(',')
					# The special and regular days are not consistently in order
					if len(days[0]) > len(days[1]):
						courseDays = days[0]
						specialDays = days[1]
					else:
						courseDays = days[1]
						specialDays = days[0]
					specialTime = section['start'].replace(':','').split(',')[1][:4]+'-'+section['end'].replace(':','').split(',')[1][:4]
					specialFlag = True
				else:
					courseDays = days
				courseTime = section['start'].replace(':','')[:4]+'-'+section['end'].replace(':','')[:4]
				courseRoom = section['room']
				currentSection = Section(courseTitle, course, courseSection, courseCRN, courseTime, courseDays, courseRoom, courseProf, 'Lecture', courseFull)
			if specialFlag:
				currentSection.addSpecial(Section(courseTitle, course, courseSection, courseCRN, specialTime, specialDays, courseRoom, courseProf, 'Lecture', courseFull))

			# If there are no labs or tutorials, we are done with the current course
			numberOfLabsOrTutorials = len(section['labs'])
			if numberOfLabsOrTutorials == 0 or len(section['labs'][0]) == 0:
				labstuts = [Section('', '', '', '', '', '', '', '', '', False)]

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

				# Here we gather the data for each lab/tutorial section and add them
				# to the list labstuts. This list will be added to the course section
				labstuts = []
				for labtut in section['labs'][0]:
					ltSection = labtut['section']
					ltCRN = labtut['crn']
					ltDay = labtut['days']
					ltDay = list(set(ltDay.split(',')))[0] # tutorial days and start/end times started showing up twice
					ltstart = list(set(labtut['start'].split(',')))[0]
					ltend = list(set(labtut['end'].split(',')))[0]
					ltTime = ltstart[:-3]+'-'+ltend[:-3]
					ltTime = ltTime.replace(':','')
					ltRoom = labtut['room']
					ltFull = labtut['space'] == 0
					labstuts.append(Section(courseTitle, course, ltSection, ltCRN, ltTime, ltDay, ltRoom, courseProf, labOrTutorial, ltFull))

			currentSection.addLabsOrTuts(labstuts)
			# The current section of the course is added to the list of sections
			sections.append(currentSection)

	if len(sections) == 0:
		sections = 'full'

	# We return the list of all the sections for the given course
	return sections

# This function goes through the list of courses and gathers all the data for
# all of them, returning the data in a list of lists of course sections
def getSemesterData(courses, term, noFullCoursesFlag):
	# Each element in semesterData is a list of course sections. Each course section
	# has its own list of the available tutorials or labs
	semesterData = []
	for course in courses:
		if course != '':
			courseData = getCourseData(course, term, noFullCoursesFlag)
			if isinstance(courseData, str):
				if term[-2:] == '10':
					season = 'winter'
				elif term[-2:] == '20':
					season = 'summer'
				else:
					season = 'fall'
				if courseData == 'invalid':
					return 'Error: '+course+' is not offered in the '+season+' of '+term[:4]
				if courseData == 'full':
					return 'Error: '+course+' is completely full in the '+season+' of '+term[:4]
			semesterData.append(courseData)

	# We fill up the list with dummy courses to make the huge scheduleOptimizer work
	while(len(semesterData) < 6):
		dummy = Section('', '', '', '', '', '', '', '', '', False)
		dummy.addLabsOrTuts([Section('', '', '', '', '', '', '', '', '', False)])
		semesterData.append([dummy])
	return semesterData

def getOptimizedSchedules(semesterData, filters, noFullCoursesFlag):
	maxschedules = 50
	firstpass = True
	schedules = []
	schedule = Schedule()
	newschedule = Schedule()

	if(noFullCoursesFlag):
		newschedule.noFullSectionsAllowed = True

	newschedule.addFilters(filters)

	# The lectures and tutorials/labs for all sections are added in for each loops,
	# and we check for conflicts after each addition. If a conflict is found, then
	# we do not proceed deeper into the loop.
	for lec1 in semesterData[0]:
		newschedule.addSection(lec1)
		if newschedule.checkForConflicts():
			newschedule.removeSection(lec1)
		else:
			for lt1 in lec1.labstuts:
				newschedule.addSection(lt1)
				if newschedule.checkForConflicts():
					newschedule.removeSection(lt1)
				else:
					for lec2 in semesterData[1]:
						newschedule.addSection(lec2)
						if newschedule.checkForConflicts():
							newschedule.removeSection(lec2)
						else:
							for lt2 in lec2.labstuts:
								newschedule.addSection(lt2)
								if newschedule.checkForConflicts():
									newschedule.removeSection(lt2)
								else:
									for lec3 in semesterData[2]:
										newschedule.addSection(lec3)
										if newschedule.checkForConflicts():
											newschedule.removeSection(lec3)
										else:
											for lt3 in lec3.labstuts:
												newschedule.addSection(lt3)
												if newschedule.checkForConflicts():
													newschedule.removeSection(lt3)
												else:
													for lec4 in semesterData[3]:
														newschedule.addSection(lec4)
														if newschedule.checkForConflicts():
															newschedule.removeSection(lec4)
														else:
															for lt4 in lec4.labstuts:
																newschedule.addSection(lt4)
																if newschedule.checkForConflicts():
																	newschedule.removeSection(lt4)
																else:
																	for lec5 in semesterData[4]:
																		newschedule.addSection(lec5)
																		if newschedule.checkForConflicts():
																			newschedule.removeSection(lec5)
																		else:
																			for lt5 in lec5.labstuts:
																				newschedule.addSection(lt5)
																				if newschedule.checkForConflicts():
																					newschedule.removeSection(lt5)
																				else:
																					for lec6 in semesterData[5]:
																						newschedule.addSection(lec6)
																						if newschedule.checkForConflicts():
																							newschedule.removeSection(lec6)
																						else:
																							for lt6 in lec6.labstuts:
																								newschedule.addSection(lt6)
																								if newschedule.checkForConflicts():
																									newschedule.removeSection(lt6)
																								else:
																									newschedule.calculateBreaks()
																									# Here we found the first conflict-free schedule
																									if firstpass:
																										schedule = copy.deepcopy(newschedule)
																										schedules = [schedule]
																										firstpass = False
																									# Here we found a schedule with smaller breaks than the previous best schedule
																									elif newschedule.breaks < schedule.breaks:
																										schedule = copy.deepcopy(newschedule)
																										schedules = [schedule]
																									# Here we found a schedule with the same amount of breaks as the previous best
																									elif newschedule.breaks == schedule.breaks:
																										if len(schedules) < maxschedules:
																											schedules.append(copy.deepcopy(newschedule))
																									newschedule.removeSection(lt6)
																							newschedule.removeSection(lec6)
																					newschedule.removeSection(lt5)
																			newschedule.removeSection(lec5)
																	newschedule.removeSection(lt4)
															newschedule.removeSection(lec4)
													newschedule.removeSection(lt3)
											newschedule.removeSection(lec3)
									newschedule.removeSection(lt2)
							newschedule.removeSection(lec2)
					newschedule.removeSection(lt1)
			newschedule.removeSection(lec1)

	if firstpass:
		if len(filters) > 0:
			return 'There is no possible conflict-free schedule for the given courses. Try using fewer filters.'
		return 'There is no possible conflict-free schedule for the given courses.'
	else:
		return schedules

# This function collects the semester data, ensures the courses were valid,
# and then runs the getOptimizedSchedules function
def scheduleOptimizer(subjects, term, filters, noFullCoursesFlag):
	semesterData = getSemesterData(subjects, term, noFullCoursesFlag)
	if isinstance(semesterData, str): # Here one or more of the given courses was invalid
		return semesterData
	return getOptimizedSchedules(semesterData, filters, noFullCoursesFlag)

# term = '201630'
# term = '201710'
# courses = ['COMP3005','ECOR3800','SYSC3110','SYSC3303','SYSC4001']
# courses = ['SYSC2004','SYSC2001','CCDP2100','MATH2004','ELEC2501']
# courses = ['ECOR1010','MATH1104','MATH1004']
# courses = ['TSES3001']
# getCourseData('MATH1104',term)
# filters = ['M0835','T0835','W0835','R1805','F1435']
# filters = ['M08351735']
# filters = []
# schedules = scheduleOptimizer(courses,term, filters)
# print(schedules)
# print(json.dumps(schedules[0].getJSON(), indent=4, sort_keys=True))
# schedules[0].getJSON()
