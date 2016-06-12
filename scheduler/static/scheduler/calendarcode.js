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

// Colour > color
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

// // 5 minutes are added to the end time of a section. The end time always ends in 5
// function addFiveMinutes(time) {
//     if (time.substring(3,5) == '25') {
//       time = time.substring(0,3)+'30';
//     }
//     else { // Here the end time is XX:55
//       time = time.
//     }
//     return time;
//     // var value = '16:00';
//     return '17:00';
// }
