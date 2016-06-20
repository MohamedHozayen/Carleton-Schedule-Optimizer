// This function initializes the calendar
$(document).ready(function() {
    var calendar = $('#calendar').fullCalendar({
				header: {
					left:   '',
			    center: '',
			    right:  '',
				},
				columnFormat: {
			    month: 'ddd',
			    week: 'ddd',
			    day: 'dddd M/d'
				},
				defaultView: 'agendaWeek',
				weekends: false,
				allDaySlot: false,
				minTime: "8:00",
				maxTime: "22:00",
				contentHeight: 'auto',
        timeFormat: '',
    })
});

// This function pads the start time, making it five minutes earlier
function getStartTime(time) {
  if (time.substring(3,5) == '05') {
    time = time.substring(0,3)+'00';
  }
  else { // Here the start time is XX:35
    time = time.substring(0,3)+'30';
  }
  return time;
}

// This function pads the end time, making it five minutes later
function getEndTime(time) {
  if (time.substring(3,5) == '25') {
    time = time.substring(0,3)+'30';
  }
  else { // Here the end time is XX:55
    time = ''+(parseInt(time.substring(0,2))+1)+':00';
  }
  return time;
}

// Colour > color.
function addCalanderEvent(title, start, end, days, colour) {
		var eventObject = {
		title: title,
		start: start,
		end: end,
		dow: days,
    color: colour,
		};

		$('#calendar').fullCalendar('renderEvent', eventObject, true);
		return eventObject;
}

// This function takes a JSON list of sections, adding them one by one to the calendar
function addSectionsToCalendar(sections) {
  var section;

  for (section in sections) {
    title = sections[section].title;
    courseCode = sections[section].courseCode;
    courseCRN = sections[section].CRN;
    start = getStartTime(sections[section].start);
    end = getEndTime(sections[section].end);
    day = sections[section].day;
    courseType = sections[section].courseType;
    room = sections[section].room;
    prof = sections[section].prof;

    if (prof === '') {
      prof = 'Prof TBA'
    }
    if (room === '') {
      room = 'Room TBA'
    }

    if (courseType == 'Lecture') {
      colour = 'blue';
      courseCode = courseCode+' '+courseType+'\n'+prof+'\n'+room+'\nCRN: '+courseCRN;
    }
    else if (courseType == 'Lab') {
      colour = 'red';
      courseCode = courseCode+' '+courseType+'\n'+prof+'\n'+room+'\nCRN: '+courseCRN;
    }
    else { // Here we have a tutorial
      colour = 'green';
      courseCode = courseCode+' '+courseType+'\n'+room+'\nCRN: '+courseCRN;
    }
    addCalanderEvent(courseCode, start, end, [day], colour);
  }
}

function displayNewSchedule(scheduleNumber) {
  $('#calendar').fullCalendar('removeEvents');
  currentSchedule.Value += 1;
  addSectionsToCalendar(schedules[currentSchedule.Value]);
}
