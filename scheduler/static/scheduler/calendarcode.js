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
				color: 'red',
    })
});

function addCalanderEvent(title, start, end, days)
{
		var eventObject = {
		title: title,
		start: start,
		end: end,
		dow: days,
		};

		$('#calendar').fullCalendar('renderEvent', eventObject, true);
		return eventObject;
}
