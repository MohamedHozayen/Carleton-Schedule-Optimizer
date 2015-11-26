# Carleton-Schedule-Optimizer
This python script finds all the sections for given Carleton University courses and sorts them into a class containing all the lectures, tutorials, and labs for each course. Each section has its own class detailing the time, day, location, professor, and CRN. The Course class has a method to combine tutorials that are common to one lecture. The Schedule class keeps track of the total amount of breaks in the schedule. The script then checks every combination of lectures/tutorials/labs for every class, finding a schedule that has no conflicts while minimizing the amount of breaks. The schedules with the minimal amount of breaks are kept and one of them is displayed.

Things to do:
1) Properly account for biweekly labs
2) Take in the given courses as parameters
3) Maybe use a recursive function to build the schedules