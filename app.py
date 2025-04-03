import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import networkx as nx
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from ClassSlots import ClassSlots
from Faculty import Faculty
from Classroom import Classroom
from Course import Course
from simple_scheduler import generate_timetable

# GUI Application
class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Scheduler")
        
        root.iconphoto(False, tk.PhotoImage(file="SchedulitLogo.png"))
        # Make the window full-screen
        self.root.state('zoomed')  # Maximizes window on Windows
        
        # Center the content dynamically
        self.root.grid_rowconfigure(0, weight=1)  # Allow row 0 to expand
        self.root.grid_columnconfigure(0, weight=1)  # Allow column 0 to expand

        # Main container frame to center content
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure main_frame to center its contents
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Data storage (in-memory for current session)
        self.classrooms = []
        self.courses = []
        self.faculties = []
        self.class_slots = {}
        self.faculty_schedule = {}
        self.timetable_data = []

        # Initialize database
        self.init_db()

        # Frames (inside main_frame instead of root)
        self.input_frame = ttk.Frame(self.main_frame, padding="10")
        self.input_frame.grid(row=0, column=0, sticky="nsew")
        self.button_frame = ttk.Frame(self.main_frame, padding="10")
        self.button_frame.grid(row=1, column=0, sticky="nsew")
        self.output_frame = ttk.Frame(self.main_frame, padding="10")
        self.output_frame.grid(row=2, column=0, sticky="nsew")

        # Center input fields by creating a sub-frame
        self.input_subframe = ttk.Frame(self.input_frame)
        self.input_subframe.grid(row=0, column=0, sticky="n")  # Center vertically, not stretching
        self.input_frame.grid_columnconfigure(0, weight=1)  # Center the subframe horizontally

        # Input Fields (inside input_subframe)
        # Classroom Row
        ttk.Label(self.input_subframe, text="Classroom:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.classroom_entry = ttk.Entry(self.input_subframe, width=30)
        self.classroom_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self.input_subframe, text="Add Classroom", command=self.add_classroom).grid(row=0, column=2, padx=5, pady=5)

        # Course Row
        ttk.Label(self.input_subframe, text="Course Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.course_name_entry = ttk.Entry(self.input_subframe, width=30)
        self.course_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(self.input_subframe, text="Code:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.course_code_entry = ttk.Entry(self.input_subframe, width=10)
        self.course_code_entry.grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        ttk.Label(self.input_subframe, text="Hours:").grid(row=1, column=4, sticky="w", padx=5, pady=5)
        self.course_hours_entry = ttk.Entry(self.input_subframe, width=5)
        self.course_hours_entry.grid(row=1, column=5, sticky="ew", padx=5, pady=5)
        ttk.Button(self.input_subframe, text="Add Course", command=self.add_course).grid(row=1, column=6, padx=5, pady=5)

        # Faculty Row
        ttk.Label(self.input_subframe, text="Faculty:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.faculty_entry = ttk.Entry(self.input_subframe, width=30)
        self.faculty_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self.input_subframe, text="Add Faculty", command=self.add_faculty).grid(row=2, column=2, padx=5, pady=5)

        # Assignment Row
        ttk.Label(self.input_subframe, text="Assign Faculty:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.assign_faculty_combo = ttk.Combobox(self.input_subframe, state="readonly", width=27)
        self.assign_faculty_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(self.input_subframe, text="Classroom:").grid(row=3, column=2, sticky="w", padx=5, pady=5)
        self.assign_classroom_combo = ttk.Combobox(self.input_subframe, state="readonly", width=27)
        self.assign_classroom_combo.grid(row=3, column=3, sticky="ew", padx=5, pady=5)
        ttk.Label(self.input_subframe, text="Course Code:").grid(row=3, column=4, sticky="w", padx=5, pady=5)
        self.assign_course_combo = ttk.Combobox(self.input_subframe, state="readonly", width=27)
        self.assign_course_combo.grid(row=3, column=5, sticky="ew", padx=5, pady=5)
        ttk.Button(self.input_subframe, text="Assign", command=self.assign_faculty).grid(row=3, column=6, padx=5, pady=5)

        # Buttons (center them in button_frame)
        self.button_frame.grid_columnconfigure(0, weight=1)  # Center buttons horizontally
        ttk.Button(self.button_frame, text="Generate Timetable", command=self.generate_timetable).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Save as PDF", command=self.save_pdf).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Clear Database", command=self.clear_database).grid(row=1, column=0, padx=5, pady=5)

        # Output Text   
        self.output_text = tk.Text(self.output_frame, height=20, width=90)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)

        # Load initial data from database
        self.load_data()

    def init_db(self):
        conn = sqlite3.connect('scheduler.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS classrooms (class_name TEXT PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS courses (code TEXT PRIMARY KEY, name TEXT, hours INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS faculty (name TEXT PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS assignments (faculty_name TEXT, class_name TEXT, course_code TEXT, 
                    FOREIGN KEY(faculty_name) REFERENCES faculty(name), 
                    FOREIGN KEY(class_name) REFERENCES classrooms(class_name), 
                    FOREIGN KEY(course_code) REFERENCES courses(code))''')
        conn.commit()
        conn.close()

    def load_data(self):
        conn = sqlite3.connect('scheduler.db')
        c = conn.cursor()
        
        # Fetch and debug classrooms
        c.execute("SELECT class_name FROM classrooms")
        self.classrooms = [Classroom(row[0]) for row in c.fetchall()]
        print(f"Loaded classrooms: {[c.class_name for c in self.classrooms]}")
        
        # Fetch and debug courses
        c.execute("SELECT code, name, hours FROM courses")
        self.courses = [Course(row[1], row[0], row[2]) for row in c.fetchall()]
        print(f"Loaded courses: {[(c.code, c.name, c.course_hours) for c in self.courses]}")
        
        # Fetch and debug faculty
        c.execute("SELECT name FROM faculty")
        self.faculties = [Faculty(row[0]) for row in c.fetchall()]
        print(f"Loaded faculty: {[f.name for f in self.faculties]}")
        
        # Fetch and debug assignments
        c.execute("SELECT faculty_name, class_name, course_code FROM assignments")
        assignments = c.fetchall()
        print(f"Loaded assignments: {assignments}")
        for row in assignments:
            faculty = next(f for f in self.faculties if f.name == row[0])
            classroom = next(c for c in self.classrooms if c.class_name == row[1])
            course = next(c for c in self.courses if c.code == row[2])
            faculty.add_classes(classrooms={classroom: course})
        
        self.update_combos()
        conn.close()

    def add_classroom(self):
        class_name = self.classroom_entry.get().strip()
        if class_name and class_name not in [c.class_name for c in self.classrooms]:
            conn = sqlite3.connect('scheduler.db')
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO classrooms (class_name) VALUES (?)", (class_name,))
            conn.commit()
            conn.close()
            self.load_data()
            self.classroom_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added classroom: {class_name}\n")
        else:
            messagebox.showwarning("Input Error", "Please enter a unique classroom name.")

    def add_course(self):
        name = self.course_name_entry.get().strip()
        code = self.course_code_entry.get().strip()
        hours = self.course_hours_entry.get().strip()
        if name and code and hours.isdigit() and code not in [c.code for c in self.courses]:
            conn = sqlite3.connect('scheduler.db')
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO courses (code, name, hours) VALUES (?, ?, ?)", (code, name, int(hours)))
            conn.commit()
            conn.close()
            self.load_data()
            self.course_name_entry.delete(0, tk.END)
            self.course_code_entry.delete(0, tk.END)
            self.course_hours_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added course: {name} ({code}, {hours} hours)\n")
        else:
            messagebox.showwarning("Input Error", "Please enter valid and unique course details.")

    def add_faculty(self):
        name = self.faculty_entry.get().strip()
        if name and name not in [f.name for f in self.faculties]:
            conn = sqlite3.connect('scheduler.db')
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO faculty (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            self.load_data()
            self.faculty_entry.delete(0, tk.END)
            self.output_text.insert(tk.END, f"Added faculty: {name}\n")
        else:
            messagebox.showwarning("Input Error", "Please enter a unique faculty name.")

    def update_combos(self):
        self.assign_faculty_combo['values'] = [f.name for f in self.faculties]
        self.assign_classroom_combo['values'] = [c.class_name for c in self.classrooms]
        self.assign_course_combo['values'] = [c.code for c in self.courses]
        print(f"Updated dropdowns - Faculty: {self.assign_faculty_combo['values']}, "
              f"Classrooms: {self.assign_classroom_combo['values']}, "
              f"Courses: {self.assign_course_combo['values']}")

    def assign_faculty(self):
        faculty_name = self.assign_faculty_combo.get()
        class_name = self.assign_classroom_combo.get()
        course_code = self.assign_course_combo.get()
        if faculty_name and class_name and course_code:
            conn = sqlite3.connect('scheduler.db')
            c = conn.cursor()
            c.execute("SELECT name FROM faculty WHERE name=?", (faculty_name,))
            if not c.fetchone():
                messagebox.showwarning("Input Error", "Faculty not found.")
                conn.close()
                return
            c.execute("SELECT class_name FROM classrooms WHERE class_name=?", (class_name,))
            if not c.fetchone():
                messagebox.showwarning("Input Error", "Classroom not found.")
                conn.close()
                return
            c.execute("SELECT code FROM courses WHERE code=?", (course_code,))
            if not c.fetchone():
                messagebox.showwarning("Input Error", "Course not found.")
                conn.close()
                return
            c.execute("INSERT INTO assignments (faculty_name, class_name, course_code) VALUES (?, ?, ?)", 
                      (faculty_name, class_name, course_code))
            conn.commit()
            conn.close()
            self.load_data()
            self.output_text.insert(tk.END, f"Assigned {faculty_name} to {class_name} for {course_code}\n")
        else:
            messagebox.showwarning("Input Error", "Please select all assignment details.")

    def generate_timetable(self):
        if not self.classrooms or not self.faculties:
            messagebox.showwarning("Data Error", "Add classrooms and faculty first!")
            return
        
        self.G = nx.Graph()
        self.class_slots = {room: [ClassSlots(room, ind) for ind in range(1, 8)] for room in self.classrooms}
        for classroom in self.class_slots.keys():
            self.G.add_nodes_from(self.class_slots[classroom])
        
        self.faculty_schedule = {faculty: {classroom: [] for classroom in faculty.assigned_classes.keys()} for faculty in self.faculties}
        
        self.timetable_data = generate_timetable(self.G, self.class_slots, self.faculties, self.faculty_schedule)
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "=== Timetable ===\n")
        for day_data in self.timetable_data:
            for line in day_data:
                self.output_text.insert(tk.END, f"{line}\n")
            self.output_text.insert(tk.END, "\n")

    def save_pdf(self):
        if not self.timetable_data:
            messagebox.showwarning("No Data", "Please generate the timetable first!")
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
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)
        doc.build(elements)
        self.output_text.insert(tk.END, f"Timetable saved as {pdf_file}\n")

    def clear_database(self):
        conn = sqlite3.connect('scheduler.db')
        c = conn.cursor()
        c.execute("DELETE FROM assignments")
        c.execute("DELETE FROM faculty")
        c.execute("DELETE FROM courses")
        c.execute("DELETE FROM classrooms")
        conn.commit()
        conn.close()
        self.classrooms = []
        self.courses = []
        self.faculties = []
        self.class_slots = {}
        self.faculty_schedule = {}
        self.timetable_data = []
        self.update_combos()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Database cleared successfully.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()