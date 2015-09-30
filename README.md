# Carleton-Schedule-Optimizer
This python script finds all the sections for given Carleton University courses and sorts them into a class containing all the lectures, tutorials, and labs for each course. Each section has its own class detailing the time, day, location, professor, and CRN. The Course class has a method to combine tutorials that are common to one lecture. The Schedule class keeps track of the total amount of breaks in the schedule. The script then checks every combination of lectures/tutorials/labs for every class, finding a schedule that has no conflicts while minimizing the amount of breaks.

Things to do:
1) Make a better outputSchedule method for the Schedule class
2) Make the combine tutorials method work for combining labs and lectures as well
3) Refine the method used to check every combination of courses and sections
