class Classroom:
    """ Represents a classroom.
    Attributes:
        class_name (str): The name of the classroom.
    """
    def __init__(self, class_name):
        self.class_name = class_name
        self.assigned_faculty = {}
        self.class_slots = ["free"] * 3
    
    def add_faculty(self, faculty, course):
        """ Assigns a faculty member to a course in the classroom.
        Args:
            faculty (Faculty): The faculty member to be assigned.
            course (Course): The course being taught.
        """
        self.assigned_faculty[faculty] = course

    def add_class_slots(self, class_number, faculty):
       self.class_slots[class_number - 1] = faculty

    def __str__(self):
        return self.class_name