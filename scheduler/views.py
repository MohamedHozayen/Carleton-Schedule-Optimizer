from django.shortcuts import render
from ScheduleOptimizer import *
from .forms import ScheduleForm

def scheduler(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ScheduleForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            term = form.cleaned_data['semester']
            c1 = form.cleaned_data['c1'].upper().replace(' ','')
            c2 = form.cleaned_data['c2'].upper().replace(' ','')
            c3 = form.cleaned_data['c3'].upper().replace(' ','')
            c4 = form.cleaned_data['c4'].upper().replace(' ','')
            c5 = form.cleaned_data['c5'].upper().replace(' ','')
            c6 = form.cleaned_data['c6'].upper().replace(' ','')
            subjects = [c1,c2,c3,c4,c5,c6]

            filters = form.cleaned_data['timeFilters']

            if len(filters) > 0:
                filters=filters[1:]
                filters = filters.split(',')

            if term == '201630' and c1=='' and c2=='' and c3=='' and c4=='' and c5=='' and c6=='':
                subjects = ['MATH2004','ELEC2501','SYSC2001','SYSC2004','CCDP2100','']
                data = {'semester': term, 'c1': subjects[0], 'c2': subjects[1], 'c3': subjects[2], 'c4': subjects[3], 'c5': subjects[4], 'c6': subjects[5], 'timeFilters': ''}
                form = ScheduleForm(data, initial=data)

            elif term == '201710' and c1=='' and c2=='' and c3=='' and c4=='' and c5=='' and c6=='':
                subjects = ['COMP1805','ELEC2607','SYSC2003','SYSC2100','STAT3502','']
                data = {'semester': term, 'c1': subjects[0], 'c2': subjects[1], 'c3': subjects[2], 'c4': subjects[3], 'c5': subjects[4], 'c6': subjects[5], 'timeFilters': ''}
                form = ScheduleForm(data, initial=data)

            # Here at least one course was entered incorrectly
            elif any( (len(y) < 8) for y in [x for x in [c1,c2,c3,c4,c5,c6] if x != '']):
                return render(request, 'scheduler/index.html', {
                    'form': form,
                    'error': 'Error: courses must be entered in the format XXXX1000, where XXXX is the department code and 1000 is the course code',
                })

            # Here one or more of the inputs were duplicates
            elif len(set([x for x in [c1,c2,c3,c4,c5,c6] if x != ''])) < len([x for x in [c1,c2,c3,c4,c5,c6] if x != '']):
                return render(request, 'scheduler/index.html', {
                    'form': form,
                    'error': 'Error: duplicate courses submitted',
                })

            # Result will be a string if there was an invalid course or a schedule could not be found
            result = scheduleOptimizer(subjects, term, filters)

            # If the result is a string, then one of the courses was invalid
            if isinstance(result, str):
                return render(request, 'scheduler/index.html', {
                    'form': form,
                    'error': result,
                })
            else:
                return render(request, 'scheduler/index.html', {
                    'form': form,
                    'result': result[0].outputBreakTime(), # This just outputs the break time for the schedules
                    'djangoJSON': getJSONData(result), # This returns a JSON object containing the data for all valid schedules
                })

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ScheduleForm()

    return render(request, 'scheduler/index.html', {'form': form})
