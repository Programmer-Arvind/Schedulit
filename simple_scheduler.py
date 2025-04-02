import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
from ClassSlots import ClassSlots
from Faculty import Faculty
from Classroom import Classroom
from Course import Course
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import tkinter as tk
from tkinter import ttk, messagebox

# Database setup
def init_db():
    conn = sqlite3.connect('scheduler.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS classrooms (class_name TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS courses (code TEXT PRIMARY KEY, name TEXT, hours INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS faculty (name TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS assignments (faculty_name TEXT, class_name TEXT, course_code TEXT, 
                 FOREIGN KEY(faculty_name) REFERENCES faculty(name), 
                 FOREIGN KEY(class_name) REFERENCES classrooms(class_name), 
                 FOREIGN KEY(course_code) REFERENCES courses(code))''')
    c.execute('''CREATE TABLE IF NOT EXISTS schedule (class_name TEXT, timeslot INTEGER, faculty_name TEXT)''')
    conn.commit()
    conn.close()

# Clear database
def clear_db():
    conn = sqlite3.connect('scheduler.db')
    c = conn.cursor()
    c.execute("DELETE FROM schedule")
    c.execute("DELETE FROM assignments")
    c.execute("DELETE FROM faculty")
    c.execute("DELETE FROM courses")
    c.execute("DELETE FROM classrooms")
    conn.commit()
    conn.close()

# Load data from database
def load_data():
    conn = sqlite3.connect('scheduler.db')
    c = conn.cursor()
    
    c.execute("SELECT class_name FROM classrooms")
    classrooms = [Classroom(row[0]) for row in c.fetchall()]
    
    c.execute("SELECT code, name, hours FROM courses")
    courses = [Course(row[1], row[0], row[2]) for row in c.fetchall()]
    
    c.execute("SELECT name FROM faculty")
    faculty = [Faculty(row[0]) for row in c.fetchall()]
    
    c.execute("SELECT faculty_name, class_name, course_code FROM assignments")
    for row in c.fetchall():
        fac = next(f for f in faculty if f.name == row[0])
        clas = next(c for c in classrooms if c.class_name == row[1])
        cour = next(c for c in courses if c.code == row[2])
        fac.add_classes(classrooms={clas: cour})
    
    conn.close()
    return classrooms, courses, faculty

# Save timetable to PDF
def save_timetable_to_pdf(header, table):
    pdf_file = "timetable.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []
    data = [header] + table
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    doc.build(elements)
    return pdf_file

# GUI Application
class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Scheduler")
        self.root.geometry("600x400")

        # Frames
        self.input_frame = ttk.Frame(root, padding="10")
        self.input_frame.grid(row=0, column=0, sticky="nsew")
        self.output_frame = ttk.Frame(root, padding="10")
        self.output_frame.grid(row=1, column=0, sticky="nsew")

        # Input Fields
        ttk.Label(self.input_frame, text="Classroom:").grid(row=0, column=0, sticky="w")
        self.classroom_entry = ttk.Entry(self.input_frame)
        self.classroom_entry.grid(row=0, column=1, sticky="ew")
        ttk.Button(self.input_frame, text="Add Classroom", command=self.add_classroom).grid(row=0, column=2)

        ttk.Label(self.input_frame, text="Course Name:").grid(row=1, column=0, sticky="w")
        self.course_name_entry = ttk.Entry(self.input_frame)
        self.course_name_entry.grid(row=1, column=1, sticky="ew")
        ttk.Label(self.input_frame, text="Code:").grid(row=1, column=2, sticky="w")
        self.course_code_entry = ttk.Entry(self.input_frame, width=10)
        self.course_code_entry.grid(row=1, column=3, sticky="ew")
        ttk.Label(self.input_frame, text="Hours:").grid(row=1, column=4, sticky="w")
        self.course_hours_entry = ttk.Entry(self.input_frame, width=5)
        self.course_hours_entry.grid(row=1, column=5, sticky="ew")
        ttk.Button(self.input_frame, text="Add Course", command=self.add_course).grid(row=1, column=6)

        ttk.Label(self.input_frame, text="Faculty:").grid(row=2, column=0, sticky="w")
        self.faculty_entry = ttk.Entry(self.input_frame)
        self.faculty_entry.grid(row=2, column=1, sticky="ew")
        ttk.Button(self.input_frame, text="Add Faculty", command=self.add_faculty).grid(row=2, column=2)

        ttk.Label(self.input_frame, text="Assign Faculty:").grid(row=3, column=0, sticky="w")
        self.assign_faculty_entry = ttk.Entry(self.input_frame)
        self.assign_faculty_entry.grid(row=3, column=1, sticky="ew")
        ttk.Label(self.input_frame, text="Classroom:").grid(row=3, column=2, sticky="w")
        self.assign_classroom_entry = ttk.Entry(self.input_frame)
        self.assign_classroom_entry.grid(row=3, column=3, sticky="ew")
        ttk.Label(self.input_frame, text="Course Code:").grid(row=3, column=4, sticky="w")
        self.assign_course_entry = ttk.Entry(self.input_frame)
        self.assign_course_entry.grid(row=3, column=5, sticky="ew")
        ttk.Button(self.input_frame, text="Assign", command=self.assign_faculty).grid(row=3, column=6)

        # Buttons
        ttk.Button(self.input_frame, text="Generate Schedule", command=self.generate_schedule).grid(row=4, column=0, columnspan=3, pady=10)
        ttk.Button(self.input_frame, text="Clear Database", command=self.clear_database).grid(row=4, column=3, columnspan=2, pady=10)
        ttk.Button(self.input_frame, text="Exit", command=root.quit).grid(row=4, column=5, columnspan=2, pady=10)

        # Output Text
        self.output_text = tk.Text(self.output_frame, height=10, width=70)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)

        # Initialize database
        init_db()

    def add_classroom(self):
        class_name = self.classroom_entry.get().strip()
        if class_name:
            conn = sqlite3.connect('scheduler.db')
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO classrooms (class_name) VALUES (?)", (class_name,))
            conn.commit()
            conn.close()
            self.classroom_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added classroom: {class_name}\n")
        else:
            messagebox.showwarning("Input Error", "Please enter a classroom name.")

    def add_course(self):
        name = self.course_name_entry.get().strip()
        code = self.course_code_entry.get().strip()
        hours = self.course_hours_entry.get().strip()
        if name and code and hours.isdigit():
            conn = sqlite3.connect('scheduler.db')
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO courses (code, name, hours) VALUES (?, ?, ?)", (code, name, int(hours)))
            conn.commit()
            conn.close()
            self.course_name_entry.delete(0, tk.END)
            self.course_code_entry.delete(0, tk.END)
            self.course_hours_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added course: {name} ({code}, {hours} hours)\n")
        else:
            messagebox.showwarning("Input Error", "Please enter valid course details.")

    def add_faculty(self):
        name = self.faculty_entry.get().strip()
        if name:
            conn = sqlite3.connect('scheduler.db')
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO faculty (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            self.faculty_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added faculty: {name}\n")
        else:
            messagebox.showwarning("Input Error", "Please enter a faculty name.")

    def assign_faculty(self):
        faculty_name = self.assign_faculty_entry.get().strip()
        class_name = self.assign_classroom_entry.get().strip()
        course_code = self.assign_course_entry.get().strip()
        if faculty_name and class_name and course_code:
            conn = sqlite3.connect('scheduler.db')
            c = conn.cursor()
            c.execute("SELECT name FROM faculty WHERE name=?", (faculty_name,))
            if not c.fetchone():
                messagebox.showwarning("Input Error", "Faculty not found.")
                return
            c.execute("SELECT class_name FROM classrooms WHERE class_name=?", (class_name,))
            if not c.fetchone():
                messagebox.showwarning("Input Error", "Classroom not found.")
                return
            c.execute("SELECT code FROM courses WHERE code=?", (course_code,))
            if not c.fetchone():
                messagebox.showwarning("Input Error", "Course not found.")
                return
            c.execute("INSERT INTO assignments (faculty_name, class_name, course_code) VALUES (?, ?, ?)", 
                      (faculty_name, class_name, course_code))
            conn.commit()
            conn.close()
            self.assign_faculty_entry.delete(0, tk.END)
            self.assign_classroom_entry.delete(0, tk.END)
            self.assign_course_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Assigned {faculty_name} to {class_name} for {course_code}\n")
        else:
            messagebox.showwarning("Input Error", "Please enter all assignment details.")

    def generate_schedule(self):
        classrooms, courses, faculty = load_data()
        if not classrooms or not faculty:
            messagebox.showwarning("Data Error", "Add classrooms and faculty first!")
            return

        G = nx.Graph()
        class_slots = {room: [ClassSlots(room, ind) for ind in range(1, 4)] for room in classrooms}
        for classroom in class_slots.keys():
            G.add_nodes_from(class_slots[classroom])

        conn = sqlite3.connect('scheduler.db')
        c = conn.cursor()
        for class_slot in G.nodes():
            for faculty in class_slot.classroom.assigned_faculty.keys():
                course_hours = faculty.assigned_classes[class_slot.classroom][1] > 0
                if (course_hours and 
                    faculty.name not in [key.faculty.name for key in G.neighbors(class_slot)]):
                    class_slot.allocate(faculty)
                    faculty.assigned_classes[class_slot.classroom][1] -= 1
                    c.execute("INSERT INTO schedule (class_name, timeslot, faculty_name) VALUES (?, ?, ?)",
                             (class_slot.classroom.class_name, class_slot.timeslot, faculty.name))
                    for classroom in faculty.assigned_classes.keys():
                        if classroom.class_name != class_slot.classroom.class_name:
                            G.add_edge(class_slot, class_slots[classroom][class_slot.timeslot-1])
                    break
        conn.commit()
        conn.close()

        # Generate timetable
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=== Timetable ===\n")
        header = ["Classroom", "Slot 1", "Slot 2", "Slot 3"]
        table = []
        for classroom in class_slots.keys():
            row = [classroom.class_name]
            for slot in class_slots[classroom]:
                entry = slot.faculty.name if slot.faculty else "Free"
                row.append(entry)
            table.append(row)
        self.output_text.insert(tk.END, " ".join(f"{h:<15}" for h in header) + "\n")
        self.output_text.insert(tk.END, "-" * (15 * len(header)) + "\n")
        for row in table:
            self.output_text.insert(tk.END, " ".join(f"{r:<15}" for r in row) + "\n")

        # Save to PDF
        pdf_file = save_timetable_to_pdf(header, table)
        self.output_text.insert(tk.END, f"\nTimetable saved as {pdf_file}\n")

        # Visualize graph
        pos = nx.spring_layout(G, seed=20, k=1.5)
        nx.draw(G, pos, with_labels=True, node_size=4000, edge_color="grey", font_size=12, font_color="#ffffff", width=2)
        plt.show()

    def clear_database(self):
        clear_db()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Database cleared successfully.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()