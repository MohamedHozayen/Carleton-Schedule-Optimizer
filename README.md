# Carleton-Schedule-Optimizer
This python script finds all the sections for given Carleton University courses and sorts them into a class containing all the lectures, tutorials, and labs for each course. Each section has its own class detailing the time, day, location, professor, and CRN. The Course class has a method to combine tutorials that are common to one lecture. The Schedule class keeps track of the total amount of breaks in the schedule. The script then checks every combination of lectures/tutorials/labs for every class, finding a schedule that has no conflicts while minimizing the amount of breaks.

Things to do:
1) Make the combineTutorials method work for combining labs and lectures as well
2) Make the getOptimizedSchedule function keep a list of all schedules with the minimal break time and display the number of schedules with the minimal break time
3) Make the schedule optimizer work for labs that are biweekly
4) Make the combineTutorials method only combine if the sections are at the same time
