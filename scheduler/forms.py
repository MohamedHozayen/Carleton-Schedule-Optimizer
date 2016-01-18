from django import forms
from scheduler.choices import *

class ScheduleForm(forms.Form):
	semester = forms.ChoiceField(choices = [('', '')]+SEMESTER_CHOICES, label = 'Semester', widget = forms.Select(), required = False)
	c1 = forms.CharField(label='Course 1', max_length=8, required = False)
	c2 = forms.CharField(label='Course 2', max_length=8, required = False)
	c3 = forms.CharField(label='Course 3', max_length=8, required = False)
	c4 = forms.CharField(label='Course 4', max_length=8, required = False)
	c5 = forms.CharField(label='Course 5', max_length=8, required = False)
	c6 = forms.CharField(label='Course 6', max_length=8, required = False)
	def is_valid(self):
		# Run the parent validation so django won't complain about not checking
		valid = super(ScheduleForm, self).is_valid()
		return True