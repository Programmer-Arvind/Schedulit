class Faculty:
    """ Represents a faculty member."""
    def __init__(self, name):
        self.name = name
        self.assigned_classes = {}

    def add_classes(self, classrooms):
        """ Assigns classrooms to the faculty member and updates the classroom's assigned faculty.
        Args:
            classrooms (dict): A dictionary mapping classrooms to courses (Classroom object : Course Object).
        """
        self.assigned_classes.update(classrooms)
        for classroom, course in classrooms.items():
            classroom.add_faculty(self, course)

    def __str__(self):
        return self.name