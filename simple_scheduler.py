import networkx as nx
import matplotlib.pyplot as plt

from ClassSlots import ClassSlots
from Faculty import Faculty
from Classroom import Classroom
from Course import Course

cse_a = Classroom("CSE_A")
cse_b = Classroom("CSE_B")
cse_c = Classroom("CSE_C")

G = nx.Graph()

# Create class slots for each classroom
class_slots = { cse_a : [ClassSlots(cse_a, ind) for ind in range(1, 4)], 
                cse_b : [ClassSlots(cse_b, ind) for ind in range(1, 4)], 
                cse_c : [ClassSlots(cse_c, ind) for ind in range(1, 4)] }

for clasroom in class_slots.keys():
    G.add_nodes_from(class_slots[clasroom])

daa = Course("DAA", "CSE101", 3)
pfl = Course("PFL", "CSE103", 2)
eee = Course("EEE", "EEE104", 1)

ramu = Faculty("Ramu")
ramu.add_classes(classrooms={cse_a : pfl, cse_b: pfl})
ash = Faculty("Ash")
ash.add_classes(classrooms={cse_a: daa})
brock = Faculty("Brock")
brock.add_classes(classrooms={cse_b: daa})
delia = Faculty("Delia")
delia.add_classes(classrooms={cse_c: pfl})   
oak = Faculty("Oak")
oak.add_classes(classrooms={cse_c: daa})
harry = Faculty("Harry")
harry.add_classes(classrooms={cse_a: eee, cse_b: eee, cse_c: eee})

faculties = [ramu, ash, brock, delia, oak, harry]

def is_valid_slot_for_faculty(faculty, class_slot):
    """
    Checks if a faculty member can be assigned to a given class slot.

    Args:
        faculty (Faculty): The faculty member to check.
        class_slot (ClassSlots): The class slot to check against.

    Returns:
        bool: True if the faculty member can be assigned, False otherwise.

    Notes:
        This function checks four conditions to determine validity:

            1. The course is still scheduled for the given classroom.
            2. The faculty member is not already teaching another course at this time slot.
            3. The previous class in the same room was taught by a different faculty member.
            4. The faculty member has at most one class assigned to them in this time slot.

    """
    course_hours = faculty.assigned_classes[class_slot.classroom][1] > 0
    faculty_not_going_other_class = faculty.name not in [key.faculty.name for key in G.neighbors(class_slot)]
    prev_faculty = class_slots[class_slot.classroom][class_slot.timeslot - 2].faculty
    last_class_different_faculty = prev_faculty.name != faculty.name if prev_faculty else True
    
    count = 1
    for slot in class_slots[class_slot.classroom]:
        if slot.faculty == faculty:
            count += 1

    return course_hours and faculty_not_going_other_class and last_class_different_faculty and count <= 2

def is_hours_remaining():
    """ Check if there are any hours remaining for any faculty member in the entire schedule."""
    for faculty in faculties:
        for classroom in faculty.assigned_classes.keys():
            if faculty.assigned_classes[classroom][1] > 0:
                return True
    return False

day = 1
while is_hours_remaining():
    print("Day ", day)
    for class_slot in G.nodes():
        for faculty in class_slot.classroom.assigned_faculty.keys(): # For all faculty assigned to the classroom
            # If the faculty is not already assigned to the class slot and has course hours left
            if is_valid_slot_for_faculty(faculty, class_slot): 
                class_slot.allocate(faculty) # Allocate the class slot to the faculty
                faculty.assigned_classes[class_slot.classroom][1] -= 1 # Decrease the course hours of the faculty for that course
                for classroom in faculty.assigned_classes.keys(): # Where all that faculty is assigned
                    if classroom.class_name != class_slot.classroom.class_name:
                        G.add_edge(class_slot, class_slots[classroom][class_slot.timeslot-1])
                break

    for classroom in class_slots.keys():
        print(f"{str(classroom)} Slots : {[slot.faculty.name if slot.faculty else 'free' for slot in class_slots[classroom]]}")

    G = nx.Graph()
    class_slots = { cse_a : [ClassSlots(cse_a, ind) for ind in range(1, 4)], 
                cse_b : [ClassSlots(cse_b, ind) for ind in range(1, 4)], 
                cse_c : [ClassSlots(cse_c, ind) for ind in range(1, 4)] }
    for clasroom in class_slots.keys():
        G.add_nodes_from(class_slots[clasroom])
    day += 1

pos = nx.spring_layout(G, seed=20, k=1.5)  # positions for all nodes
nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=4000,
    edge_color="grey",
    font_size=12,
    font_color="#ffffff",
    width=2,
)
plt.show()
