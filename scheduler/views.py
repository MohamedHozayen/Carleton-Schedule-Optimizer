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
            c1 = form.cleaned_data['c1'].upper()
            c2 = form.cleaned_data['c2'].upper()
            c3 = form.cleaned_data['c3'].upper()
            c4 = form.cleaned_data['c4'].upper()
            c5 = form.cleaned_data['c5'].upper()
            c6 = form.cleaned_data['c6'].upper()
            subjects = [c1,c2,c3,c4,c5,c6]

            if term=='' and c1=='' and c2=='' and c3=='' and c4=='' and c5=='' and c6=='':
                term = '201630'
                subjects = ['ECOR3800','COMP3005','SYSC4001','SYSC3110','SYSC3303','']
                data = {'semester': term, 'c1': subjects[0], 'c2': subjects[1], 'c3': subjects[2], 'c4': subjects[3], 'c5': subjects[4], 'c6': subjects[5]}
                form = ScheduleForm(data, initial=data)

            result = scheduleOptimizer(term,subjects)
            return render(request, 'scheduler/index.html', {
                'form': form,
                'result': result,
            })

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ScheduleForm()

    return render(request, 'scheduler/index.html', {'form': form})
