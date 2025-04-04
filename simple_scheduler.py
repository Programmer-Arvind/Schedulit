import networkx as nx
import matplotlib.pyplot as plt

from ClassSlots import ClassSlots
from Faculty import Faculty
from Classroom import Classroom
from Course import Course

def is_valid_slot_for_faculty(faculty, class_slot, day, faculty_schedule, G):
    """
    Checks if a faculty member can be assigned to a given class slot.

    Args:
        faculty (Faculty): The faculty member to check.
        class_slot (ClassSlots): The class slot to check against.
        day (int): The current day being scheduled.
        faculty_schedule (dict): Tracks faculty assignments per day.
        G (nx.Graph): The graph representing the schedule.

    Returns:
        bool: True if the faculty member can be assigned, False otherwise.
    """
    course_hours = faculty.assigned_classes[class_slot.classroom][1] > 0
    faculty_not_going_other_class = faculty.name not in [key.faculty.name for key in G.neighbors(class_slot)]
    count_today = faculty_schedule[faculty][class_slot.classroom].count(day)
    had_two_classes_before = any(faculty_schedule[faculty][class_slot.classroom].count(i) > 1 for i in range(1, day))
    if count_today == 3:
        return False  # Already assigned two classes today
    if count_today == 1 and had_two_classes_before:
        return False  # Had two classes on a previous day
    
    return course_hours and faculty_not_going_other_class

def is_hours_remaining(faculties):
    """ Check if there are any hours remaining for any faculty member in the entire schedule."""
    for faculty in faculties:
        for classroom in faculty.assigned_classes.keys():
            if faculty.assigned_classes[classroom][1] > 0:
                return True
    return False

def save_graph(graph, day):
    """
    Saves the current graph `G` as a PNG image.

    Args:
        graph (nx.Graph): The NetworkX graph to visualize.
        day (int): The current day, used in filename.
    """
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(graph, seed=1, k = 1)  # Layout for consistent positioning

    # Draw nodes
    nx.draw_networkx_nodes(graph, pos, node_size=500, node_color="skyblue")

    # Draw edges with styling
    nx.draw_networkx_edges(graph, pos, edge_color="gray", width=2.5)

    # Draw labels: class name + timeslot
    node_labels = {
        node: f"{node.classroom.class_name}\nT{node.timeslot}"
        for node in graph.nodes
    }
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=8)

    plt.title(f"Graph - Day {day}")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f"graph_day_{day}.png", dpi=150)
    plt.close()

def generate_timetable(G, class_slots, faculties, faculty_schedule):
    """
    Generates a timetable based on the provided data structures.

    Args:
        G (nx.Graph): The graph representing the schedule.
        class_slots (dict): Dictionary mapping classrooms to lists of ClassSlots.
        faculties (list): List of Faculty objects.
        faculty_schedule (dict): Dictionary tracking faculty assignments per day.

    Returns:
        list: A list of daily schedules, where each schedule is a list of strings.
    """
    timetable = []
    day = 1

    while is_hours_remaining(faculties):
        day_schedule = [f"Day {day}"]
        for class_slot in G.nodes():
            for faculty in class_slot.classroom.assigned_faculty.keys():
                if is_valid_slot_for_faculty(faculty, class_slot, day, faculty_schedule, G):
                    class_slot.allocate(faculty)
                    faculty.assigned_classes[class_slot.classroom][1] -= 1
                    faculty_schedule[faculty][class_slot.classroom].append(day)
                    for classroom in faculty.assigned_classes.keys():
                        if classroom.class_name != class_slot.classroom.class_name:
                            G.add_edge(class_slot, class_slots[classroom][class_slot.timeslot - 1])
                    break

        # Collect timetable data for this day
        for classroom in class_slots.keys():
            slots = [slot.faculty.name if slot.faculty else 'free' for slot in class_slots[classroom]]
            day_schedule.append(f"{str(classroom)}: {', '.join(slots)}")
        timetable.append(day_schedule)

        # Reset for next day
        save_graph(G, day)
        G.clear()  # Clear the graph instead of reinitializing to preserve object reference
        for classroom in class_slots.keys():
            class_slots[classroom] = [ClassSlots(classroom, ind) for ind in range(1, 8)]
            G.add_nodes_from(class_slots[classroom])
        day += 1

    return timetable

# Example usage
if __name__ == "__main__":
    # Initialize classrooms
    cse_a = Classroom("CSE_A")
    cse_b = Classroom("CSE_B")
    cse_c = Classroom("CSE_C")

    # Initialize graph
    G = nx.Graph()

    # Create class slots for each classroom
    class_slots = {
        cse_a: [ClassSlots(cse_a, ind) for ind in range(1, 8)],
        cse_b: [ClassSlots(cse_b, ind) for ind in range(1, 8)],
        cse_c: [ClassSlots(cse_c, ind) for ind in range(1, 8)]
    }

    for classroom in class_slots.keys():
        G.add_nodes_from(class_slots[classroom])

    # Initialize courses
    daa = Course("DAA", "CSE101", 4)
    pfl = Course("PFL", "CSE102", 4)
    eee = Course("EEE", "EEE104", 3)
    os = Course("OS", "CSE104", 4)
    maths = Course("PRP", "MAT101", 3)

    # Initialize faculty and assign courses
    ramu = Faculty("Ramu")
    ramu.add_classes(classrooms={cse_a: pfl, cse_b: pfl})
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
    iris = Faculty("Iris")
    iris.add_classes(classrooms={cse_a: os, cse_b: os})
    blaine = Faculty("Blaine")
    blaine.add_classes(classrooms={cse_c: os})
    misty = Faculty("Misty")
    misty.add_classes(classrooms={cse_a: maths})
    max = Faculty("Max")
    max.add_classes(classrooms={cse_b: maths})
    tierno = Faculty("Tierno")
    tierno.add_classes(classrooms={cse_c: maths})

    courses = [daa, pfl, eee, os, maths]
    faculties = [ramu, ash, brock, delia, oak, harry, iris, blaine, misty, max, tierno]

    # Initialize faculty schedule
    faculty_schedule = {faculty: {classroom: [] for classroom in faculty.assigned_classes.keys()} for faculty in faculties}

    # Generate timetable
    timetable = generate_timetable(G, class_slots, faculties, faculty_schedule)

    print(timetable)
    # Print the timetable
    for day_data in timetable:
        for line in day_data:
            print(line)
        print()