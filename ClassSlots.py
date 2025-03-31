class ClassSlots:
    """ Represents a class slot in a classroom.
    Attributes:
        classroom (Classroom): The classroom to which the slot belongs.
        timeslot (int): The time slot number.
        faculty (Faculty): The faculty member assigned to the slot (if any).
    """
    def __init__(self, classroom, timeslot):
        self.classroom = classroom
        self.timeslot = timeslot
        self.faculty = None

    def allocate(self, faculty):
        """ Allocates a faculty member to the class slot.
        Args:
            faculty (Faculty): The faculty member to be allocated.
        """
        self.faculty = faculty
        self.classroom.add_class_slots(self.timeslot, faculty)

    def __str__(self):
        return f"{self.classroom}_P{self.timeslot}"