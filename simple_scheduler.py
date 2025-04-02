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

cse_a_slots = [ClassSlots(cse_a, ind) for ind in range(1, 4)]
cse_b_slots = [ClassSlots(cse_b, ind) for ind in range(1, 4)]
cse_c_slots = [ClassSlots(cse_c, ind) for ind in range(1, 4)]

G.add_nodes_from(cse_a_slots)
G.add_nodes_from(cse_b_slots)
G.add_nodes_from(cse_c_slots)

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
                    G.add_edge(class_slot, cse_b_slots[class_slot.timeslot-1])
            break
        else:
            pass

print("CSE A Slots: ", [slot.faculty.name if slot != "free" else "free" for slot in cse_a_slots])
print("CSE B Slots: ", [slot.faculty.name if slot.faculty is not None else "free" for slot in cse_b_slots])
print("CSE C Slots: ", [slot.faculty.name if slot != "free" else "free" for slot in cse_c_slots])

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
