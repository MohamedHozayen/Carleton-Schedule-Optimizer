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
              placement:'left',
              //placement: placem,
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
        }});

    $('#addFilterBtn').click(function(e){
      //ask them to choose a day
      var days = [
        'Mon',
        'Tues',
        'Wed',
        'Thurs',
        'Fri'
      ]
      var formGroup =$('<div class="form-group">');
      var buttonToolBar = $('<div class="btn-toolbar"></div>');
      var buttonGroup = $('<div class="btn-group"></div>');
      var filter =$('<div class="filter"></div>');
      var daysObj = $('<div class="days"></div>')

      formGroup.append(buttonToolBar)
      buttonToolBar.append(buttonGroup);
      daysObj.append(formGroup);
      filter.append(daysObj);
      $('.filters').append(filter);
      for (var day in days){
        var individualDayButton = '<button type="button" class="btn btn-default dayBtn">'+days[day]+'</button>';
        buttonGroup.append(individualDayButton);
      };
    });
    var filters=[];
    $('body').on('click', '.dayBtn', function(e) {
      var day = $(this).text();
      $(this).siblings().css("display","none");

      var filter = $(this).parent().parent().parent().parent();
      var index = $(this).closest(".filter").index();
      filter.append("<div class=\"form-group\"><div class=\"slider-range-"+index+"\"></div></div>");
      var onslideFunction = function(event,ui){
        var startHour = Math.floor(ui.values[0]/60)
        var endHour = Math.floor(ui.values[1]/60)
        var startMinute = ui.values[0] - (startHour * 60);
        var endMinute = ui.values[1] - (endHour * 60);
        var filterTime = getTimeAsString(day, startHour, startMinute, endHour, endMinute);
        filters[index]=filterTime
        addPreviousFilterToHiddenInput(filters);
      };
      $( ".slider-range-"+index).slider({
        animate:true,
        range: true,
        min: 515,
        max: 1235,
        step:30,
        values: [ 515, 545 ],
        slide: onslideFunction,
      });
    });

    // This ensures no filters are applied after each post request
    changeFilters('');
});

// This enum is used to convert the days to a usable format
var DayEnum = {
  'Mon' : 'M',
  'Tues' : 'T',
  'Wed' : 'W',
  'Thurs' : 'R',
  'Fri' : 'F',
};

function addPreviousFilterToHiddenInput(filters) {
  var filterElement = document.getElementsByName('timeFilters')[0];
  filterElement.value="";
  filters.forEach(function(filter){
    filterElement.value+=','+filter;
  });
  console.log(filterElement.value);
}

function changeFilters(newTime,index) {
  // This is the element containing all the filters
  var filterElement = document.getElementsByName('timeFilters')[0];
  filterElement.value=newTime;
  //console.log(index+":"+filterElement.value);
}

// This function returns a start or end time in the correct string format
function getTimeAsString(day, startHour, startMinute, endHour, endMinute) {
  if (startHour < 10) {
    startHour = '0'+startHour.toString();
  }
  if (startMinute < 10) {
    startMinute = '0'+startMinute.toString();
  }
  if (endHour < 10) {
    endHour = '0'+endHour.toString();
  }
  if (endMinute < 10) {
    endMinute = '0'+endMinute.toString();
  }
  return DayEnum[day]+startHour.toString()+startMinute.toString()+endHour.toString()+endMinute.toString();
}

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
function padStartTime(time) {
  if (time.substring(3,5) == '05') {
    time = time.substring(0,3)+'00';
  }
  else { // Here the start time is XX:35
    time = time.substring(0,3)+'30';
  }
  return time;
}

// This function pads the end time, making it five minutes later
function padEndTime(time) {
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
    start = padStartTime(sections[section].start);
    end = padEndTime(sections[section].end);
    day = sections[section].day;
    courseType = sections[section].courseType;
    room = sections[section].room;
    prof = sections[section].prof;
    full = sections[section].full;

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
    details = courseCode+"<br>"+title+"<br>"+prof+"<br>Room: "+room+"<br>CRN: "+courseCRN;

    // This code block assigns different colours to each course instead of to each section type
    if (!(titles.includes(title))) {
      titles[count] = title;
      count++;
    }
    if(full) {
      colour = "black"
      details += "<br><b>THIS SECTION IS FULL<b>"
    } else {
      colour = ColourEnum[titles.indexOf(title)];
    }

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
