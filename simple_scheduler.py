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

daa = Course("DAA", "CS101", 2)
coa = Course("COA", "CS102", 1)
pfl = Course("PFL", "CS103", 1)

ramu = Faculty("Ramu")
ramu.add_classes(classrooms={cse_a : daa, cse_b: pfl})
ash = Faculty("Ash")
ash.add_classes(classrooms={cse_a: pfl})
brock = Faculty("Brock")
brock.add_classes(classrooms={cse_b: coa})
delia = Faculty("Delia")
delia.add_classes(classrooms={cse_c: daa})   
oak = Faculty("Oak")
oak.add_classes(classrooms={cse_c: coa})

for class_slot in G.nodes():
    for faculty in class_slot.classroom.assigned_faculty.keys(): # For all faculty assigned to the classroom
        course_hours = faculty.assigned_classes[class_slot.classroom][1] > 0
        # If the faculty is not already assigned to the class slot and has course hours left
        if course_hours and faculty.name not in [key.faculty.name for key in G.neighbors(class_slot)]: 
            class_slot.allocate(faculty) # Allocate the class slot to the faculty
            faculty.assigned_classes[class_slot.classroom][1] -= 1 # Decrease the course hours of the faculty for that course
            for classroom in faculty.assigned_classes.keys(): # Where all that faculty is assigned
                if classroom.class_name != class_slot.classroom.class_name:
                    G.add_edge(class_slot, class_slots[classroom][class_slot.timeslot-1])
            break

for classroom in class_slots.keys():
    print(f"{str(classroom)} Slots : {[slot.faculty.name if slot.faculty else 'free' for slot in class_slots[classroom]]}")

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
