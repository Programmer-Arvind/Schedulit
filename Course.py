class Course:
    """ Represents a course with a name, code, and number of class hours.
    Attributes:
        name (str): The name of the course.
        code (str): The code of the course.
        course_hours (int): The number of class hours for the course.
    """
    def __init__(self, name, code, class_hours):
        self.name = name
        self.code = code
        self.course_hours = class_hours
    
    def __str__(self):
        return f"{self.name} ({self.code})"