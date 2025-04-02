import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import matplotlib.pyplot as plt
from ClassSlots import ClassSlots
from Faculty import Faculty
from Classroom import Classroom
from Course import Course

# GUI Application
class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Scheduler")
        self.root.geometry("800x600")

        # Data storage
        self.classrooms = []
        self.courses = []
        self.faculties = []
        self.class_slots = {}
        self.G = nx.Graph()
        self.timetable_data = []

        # Frames
        self.input_frame = ttk.Frame(root, padding="10")
        self.input_frame.grid(row=0, column=0, sticky="nsew")
        self.button_frame = ttk.Frame(root, padding="10")
        self.button_frame.grid(row=1, column=0, sticky="nsew")
        self.output_frame = ttk.Frame(root, padding="10")
        self.output_frame.grid(row=2, column=0, sticky="nsew")

        # Input Fields
        ttk.Label(self.input_frame, text="Classroom:").grid(row=0, column=0, sticky="w")
        self.classroom_entry = ttk.Entry(self.input_frame)
        self.classroom_entry.grid(row=0, column=1, sticky="ew")
        ttk.Button(self.input_frame, text="Add Classroom", command=self.add_classroom).grid(row=0, column=2, padx=5)

        ttk.Label(self.input_frame, text="Course Name:").grid(row=1, column=0, sticky="w")
        self.course_name_entry = ttk.Entry(self.input_frame)
        self.course_name_entry.grid(row=1, column=1, sticky="ew")
        ttk.Label(self.input_frame, text="Code:").grid(row=1, column=2, sticky="w")
        self.course_code_entry = ttk.Entry(self.input_frame, width=10)
        self.course_code_entry.grid(row=1, column=3, sticky="ew")
        ttk.Label(self.input_frame, text="Hours:").grid(row=1, column=4, sticky="w")
        self.course_hours_entry = ttk.Entry(self.input_frame, width=5)
        self.course_hours_entry.grid(row=1, column=5, sticky="ew")
        ttk.Button(self.input_frame, text="Add Course", command=self.add_course).grid(row=1, column=6, padx=5)

        ttk.Label(self.input_frame, text="Faculty:").grid(row=2, column=0, sticky="w")
        self.faculty_entry = ttk.Entry(self.input_frame)
        self.faculty_entry.grid(row=2, column=1, sticky="ew")
        ttk.Button(self.input_frame, text="Add Faculty", command=self.add_faculty).grid(row=2, column=2, padx=5)

        ttk.Label(self.input_frame, text="Assign Faculty:").grid(row=3, column=0, sticky="w")
        self.assign_faculty_entry = ttk.Entry(self.input_frame)
        self.assign_faculty_entry.grid(row=3, column=1, sticky="ew")
        ttk.Label(self.input_frame, text="Classroom:").grid(row=3, column=2, sticky="w")
        self.assign_classroom_entry = ttk.Entry(self.input_frame)
        self.assign_classroom_entry.grid(row=3, column=3, sticky="ew")
        ttk.Label(self.input_frame, text="Course Code:").grid(row=3, column=4, sticky="w")
        self.assign_course_entry = ttk.Entry(self.input_frame)
        self.assign_course_entry.grid(row=3, column=5, sticky="ew")
        ttk.Button(self.input_frame, text="Assign", command=self.assign_faculty).grid(row=3, column=6, padx=5)

        # Buttons
        ttk.Button(self.button_frame, text="Generate Schedule", command=self.generate_schedule).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Save as PDF", command=self.save_pdf).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Show Graph", command=self.show_graph).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Clear Data", command=self.clear_data).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Exit", command=root.quit).grid(row=0, column=4, padx=5, pady=5)

        # Output Text
        self.output_text = tk.Text(self.output_frame, height=20, width=90)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)

    def add_classroom(self):
        class_name = self.classroom_entry.get().strip()
        if class_name and class_name not in [c.class_name for c in self.classrooms]:
            classroom = Classroom(class_name)
            self.classrooms.append(classroom)
            self.classroom_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added classroom: {class_name}\n")
        else:
            messagebox.showwarning("Input Error", "Please enter a unique classroom name.")

    def add_course(self):
        name = self.course_name_entry.get().strip()
        code = self.course_code_entry.get().strip()
        hours = self.course_hours_entry.get().strip()
        if name and code and hours.isdigit() and code not in [c.code for c in self.courses]:
            course = Course(name, code, int(hours))
            self.courses.append(course)
            self.course_name_entry.delete(0, tk.END)
            self.course_code_entry.delete(0, tk.END)
            self.course_hours_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added course: {name} ({code}, {hours} hours)\n")
        else:
            messagebox.showwarning("Input Error", "Please enter valid and unique course details.")

    def add_faculty(self):
        name = self.faculty_entry.get().strip()
        if name and name not in [f.name for f in self.faculties]:
            faculty = Faculty(name)
            self.faculties.append(faculty)
            self.faculty_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added faculty: {name}\n")
        else:
            messagebox.showwarning("Input Error", "Please enter a unique faculty name.")

    def assign_faculty(self):
        faculty_name = self.assign_faculty_entry.get().strip()
        class_name = self.assign_classroom_entry.get().strip()
        course_code = self.assign_course_entry.get().strip()
        if faculty_name and class_name and course_code:
            faculty = next((f for f in self.faculties if f.name == faculty_name), None)
            classroom = next((c for c in self.classrooms if c.class_name == class_name), None)
            course = next((c for c in self.courses if c.code == course_code), None)
            if not faculty:
                messagebox.showwarning("Input Error", "Faculty not found.")
                return
            if not classroom:
                messagebox.showwarning("Input Error", "Classroom not found.")
                return
            if not course:
                messagebox.showwarning("Input Error", "Course not found.")
                return
            faculty.add_classes(classrooms={classroom: course})
            self.assign_faculty_entry.delete(0, tk.END)
            self.assign_classroom_entry.delete(0, tk.END)
            self.assign_course_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Assigned {faculty_name} to {class_name} for {course_code}\n")
        else:
            messagebox.showwarning("Input Error", "Please enter all assignment details.")

    def is_valid_slot_for_faculty(self, faculty, class_slot):
        course_hours = faculty.assigned_classes[class_slot.classroom][1] > 0
        faculty_not_going_other_class = faculty.name not in [key.faculty.name for key in self.G.neighbors(class_slot)]
        prev_faculty = self.class_slots[class_slot.classroom][class_slot.timeslot - 2].faculty if class_slot.timeslot > 1 else None
        last_class_different_faculty = prev_faculty.name != faculty.name if prev_faculty else True
        count = sum(1 for slot in self.class_slots[class_slot.classroom] if slot.faculty == faculty)
        return course_hours and faculty_not_going_other_class and last_class_different_faculty and count <= 2

    def is_hours_remaining(self):
        for faculty in self.faculties:
            for classroom in faculty.assigned_classes.keys():
                if faculty.assigned_classes[classroom][1] > 0:
                    return True
        return False

    def generate_schedule(self):
        if not self.classrooms or not self.faculties:
            messagebox.showwarning("Data Error", "Add classrooms and faculty first!")
            return
        
        self.G = nx.Graph()
        self.class_slots = {room: [ClassSlots(room, ind) for ind in range(1, 4)] for room in self.classrooms}
        for classroom in self.class_slots.keys():
            self.G.add_nodes_from(self.class_slots[classroom])

        day = 1
        self.timetable_data = []
        while self.is_hours_remaining():
            for class_slot in self.G.nodes():
                for faculty in class_slot.classroom.assigned_faculty.keys():
                    if self.is_valid_slot_for_faculty(faculty, class_slot):
                        class_slot.allocate(faculty)
                        faculty.assigned_classes[class_slot.classroom][1] -= 1
                        for classroom in faculty.assigned_classes.keys():
                            if classroom.class_name != class_slot.classroom.class_name:
                                self.G.add_edge(class_slot, self.class_slots[classroom][class_slot.timeslot-1])
                        break
            
            # Collect timetable data for this day
            day_schedule = [f"Day {day}"]
            for classroom in self.class_slots.keys():
                slots = [slot.faculty.name if slot.faculty else 'free' for slot in self.class_slots[classroom]]
                day_schedule.append(f"{classroom.class_name}: {', '.join(slots)}")
            self.timetable_data.append(day_schedule)
            
            # Reset for next day
            self.G = nx.Graph()
            self.class_slots = {room: [ClassSlots(room, ind) for ind in range(1, 4)] for room in self.classrooms}
            for classroom in self.class_slots.keys():
                self.G.add_nodes_from(self.class_slots[classroom])
            day += 1
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=== Timetable ===\n")
        for day_data in self.timetable_data:
            for line in day_data:
                self.output_text.insert(tk.END, f"{line}\n")
            self.output_text.insert(tk.END, "\n")

    def save_pdf(self):
        if not self.timetable_data:
            messagebox.showwarning("No Data", "Please generate the schedule first!")
            return
        pdf_file = "timetable.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        elements = []
        header = ["Day"] + [c.class_name for c in self.classrooms]
        table_data = [header]
        for day_data in self.timetable_data:
            day = day_data[0]
            slots = [day]
            for entry in day_data[1:]:
                slots.append(entry.split(": ")[1])
            table_data.append(slots)
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)
        doc.build(elements)
        self.output_text.insert(tk.END, f"Timetable saved as {pdf_file}\n")

    def show_graph(self):
        pos = nx.spring_layout(self.G, seed=20, k=1.5)
        nx.draw(
            self.G,
            pos,
            with_labels=True,
            node_size=4000,
            edge_color="grey",
            font_size=12,
            font_color="#ffffff",
            width=2,
        )
        plt.show()

    def clear_data(self):
        self.classrooms = []
        self.courses = []
        self.faculties = []
        self.class_slots = {}
        self.G = nx.Graph()
        self.timetable_data = []
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Data cleared successfully.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()