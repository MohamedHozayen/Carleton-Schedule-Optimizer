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
        // contentWidth: 'auto',
        timeFormat: '',
        eventRender: function(event, element) {
          if(event.start._d.getDate() > 3) {
            placem = "left";
          }else {
            placem = "right";
          }
          $(element).tooltip(
            {
              title: event.id,
              container: "body",
              placement: placem,
              html: true,
            }
          );
        },
        eventMouseover:function(event){
          if(event.color=="green"){
            $(this).css("background","#556B2F");
          }else if(event.color=="blue"){
            $(this).css("background","#191970");
          }else if(event.color=="red"){
            $(this).css("background","#8B0000");
          }else if (event.color=="purple") {
            $(this).css("background","#663399");
          }else if (event.color=="DarkOrange") {
            $(this).css("background","#B8860B");
          }else if (event.color=="SaddleBrown") {
            $(this).css("background","#592720");
          }
        },
        eventMouseout: function(event){
          $(this).css("background",event.color);
        }
    })
});

// This enum is used to manage the colours
var ColourEnum = {
  0 : "red",
  1 : "green",
  2 : "blue",
  3 : "DarkOrange",
  4 : "purple",
  5 : "SaddleBrown"
}

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
function addCalanderEvent(title, start, end, days, colour, id) {
		var eventObject = {
		title: title,
		start: start,
		end: end,
		dow: days,
    color: colour,
    id: id,
		};

		$('#calendar').fullCalendar('renderEvent', eventObject, true);
		return eventObject;
}

// This function takes a JSON list of sections, adding them one by one to the calendar
function addSectionsToCalendar(sections) {
  var section;
  var titles = ["","","","","",""];
  count = 0;
  courseText = "";

  for (section in sections) {
    title = sections[section].title;
    courseCode = sections[section].courseCode;
    courseCRN = sections[section].CRN;
    start = getStartTime(sections[section].start);
    end = getEndTime(sections[section].end);
    // start = sections[section].start;
    // end = sections[section].end;
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

    // Here we collect the event text and assign colours to the sections based on their type
    if (courseType == 'Lecture') {
      courseText = courseCode+' '+courseType+'\n'+prof+'\n'+room;
    }
    else if (courseType == 'Lab') {
      courseText = courseCode+' '+courseType+'\n'+prof+'\n'+room;
    }
    else { // Here we have a tutorial
      courseText = courseCode+' '+courseType+'\n'+room;
    }

    // This code block assigns different colours to each course instead of to each section type
    if (!(titles.includes(title))) {
      titles[count] = title;
      count++;
    }
    colour = ColourEnum[titles.indexOf(title)];

    details = courseCode+"<br>"+title+"<br>"+prof+"<br>Room: "+room+"<br>CRN: "+courseCRN;
    addCalanderEvent(courseText, start, end, [day], colour, details);
  }
}

// This function refreshes the schedule on the calendar, showing the new schedule
function displayNewSchedule(scheduleNumber) {
  $('#calendar').fullCalendar('removeEvents');
  currentSchedule.Value += 1;
  addSectionsToCalendar(schedules[currentSchedule.Value]);
}

// This function updates the display showing the current schedule numnber
function updateCurrentSchedule(schedules, currentSchedule) {
  scheduleNumber.innerHTML = '<p><strong>Current optimal schedule: '+(currentSchedule+1)+' of '+schedules.length+'</strong><p>';
}

// This function displays the previous schedule in the list of schedules
function previousClick(schedules, currentSchedule) {
  if (currentSchedule > 0) {
    currentSchedule -= 1;
  }
  else {
    currentSchedule = schedules.length - 1;
  }
  $('#calendar').fullCalendar('removeEvents');
  addSectionsToCalendar(schedules[currentSchedule]);
  updateCurrentSchedule(schedules, currentSchedule);
  return currentSchedule;
}

// This function displays the next schedule in the list of schedules
function nextClick(schedules, currentSchedule) {
  if (currentSchedule < schedules.length - 1) {
    currentSchedule += 1;
  }
  else {
    currentSchedule = 0;
  }
  $('#calendar').fullCalendar('removeEvents');
  addSectionsToCalendar(schedules[currentSchedule]);
  updateCurrentSchedule(schedules, currentSchedule);
  return currentSchedule;
}

//Function To Display Popup
function div_show() {
document.getElementById('abc').style.display = "block";
}
