import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import networkx as nx
from reportlab.lib.pagesizes import A3, landscape
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

        # Set the window icon
        root.iconphoto(False, tk.PhotoImage(file="SchedulitLogo.png"))

        # Make the window full-screen
        self.root.geometry("1920x1080")
        self.root.attributes('-fullscreen', True)

        # Configure window layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Configure a style for consistent theming
        style = ttk.Style()
        style.configure("TLabel", font=("Perpetua", 16), background="#87CEEB")
        style.configure("TButton", font=("Candara", 12))
        style.configure("TCombobox", font=("Candara", 12))
        style.configure("TFrame", background="#87CEEB")

        # Main container frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # **Title Label at the Top**
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Schedulit", 
            font=("Perpetua", 28, "bold"),
            background="#87CEEB"
        )
        self.title_label.grid(row=0, column=0, pady=20, sticky="n")
        
        # Frames
        self.input_frame = ttk.Frame(self.main_frame, padding="10")
        self.input_frame.grid(row=1, column=0, sticky="nsew")
        self.button_frame = ttk.Frame(self.main_frame, padding="10")
        self.button_frame.grid(row=2, column=0, sticky="nsew")
        self.output_frame = ttk.Frame(self.main_frame, padding="10")
        self.output_frame.grid(row=3, column=0, sticky="nsew")

        # Center input fields in a sub-frame
        self.input_subframe = ttk.Frame(self.input_frame)
        self.input_subframe.grid(row=0, column=0, sticky="n")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Input Fields
        ttk.Label(self.input_subframe, text="Classroom:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.classroom_entry = ttk.Entry(self.input_subframe, width=30, font=("Candara", 12))
        self.classroom_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self.input_subframe, text="Add Classroom", command=self.add_classroom).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(self.input_subframe, text="Course Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.course_name_entry = ttk.Entry(self.input_subframe, width=30, font=("Candara", 12))
        self.course_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(self.input_subframe, text="Code:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.course_code_entry = ttk.Entry(self.input_subframe, width=10, font=("Candara", 12))
        self.course_code_entry.grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        ttk.Label(self.input_subframe, text="Hours:").grid(row=1, column=4, sticky="w", padx=5, pady=5)
        self.course_hours_entry = ttk.Entry(self.input_subframe, width=5, font=("Candara", 12))
        self.course_hours_entry.grid(row=1, column=5, sticky="ew", padx=5, pady=5)
        ttk.Button(self.input_subframe, text="Add Course", command=self.add_course).grid(row=1, column=6, padx=5, pady=5)

        ttk.Label(self.input_subframe, text="Faculty:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.faculty_entry = ttk.Entry(self.input_subframe, width=30, font=("Candara", 12))
        self.faculty_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self.input_subframe, text="Add Faculty", command=self.add_faculty).grid(row=2, column=2, padx=5, pady=5)

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

        # Buttons
        self.button_frame.grid_columnconfigure(0, weight=1)
        ttk.Button(self.button_frame, text="Generate Timetable", command=self.generate_timetable).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Save as PDF", command=self.save_pdf).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.button_frame, text="Clear Database", command=self.clear_database).grid(row=1, column=0, padx=5, pady=5)

        # Output Text
        self.output_text = tk.Text(self.output_frame, height=20, width=90, font=("Candara", 14), bg="#0000aa", fg="#ffffff")
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
        
        # Fetch and debug courses
        c.execute("SELECT code, name, hours FROM courses")
        self.courses = [Course(row[1], row[0], row[2]) for row in c.fetchall()]
        
        # Fetch and debug faculty
        c.execute("SELECT name FROM faculty")
        self.faculties = [Faculty(row[0]) for row in c.fetchall()]
        
        # Fetch and debug assignments
        c.execute("SELECT faculty_name, class_name, course_code FROM assignments")
        assignments = c.fetchall()
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
        doc = SimpleDocTemplate(pdf_file, pagesize=landscape(A3))  # Bigger Page Size
        elements = []
        
        slot_headers = ["Day", "1", "2", "Break", "3", "4", "Break", "5", "6", "7"]
        
        col_widths = [50, 135, 135, 50, 135, 135, 50, 135, 135, 135]  # Narrower Break Columns

        for class_index, class_name in enumerate(["CSEA", "CSEB", "CSEC"]):
            # Add class title
            elements.append(Table([[class_name]], colWidths=[sum(col_widths)], style=[
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 16),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))

            table_data = [slot_headers]
            merge_styles = []  # Store merging information

            for row_idx, day_entry in enumerate(self.timetable_data):
                day = day_entry[0]
                schedule = day_entry[class_index + 1].split(": ")[1].split(", ")

                # Insert "Break" slots
                formatted_schedule = schedule[:2] + ["Break"] + schedule[2:4] + ["Break"] + schedule[4:]

                while len(formatted_schedule) < 9:
                    formatted_schedule.append("")

                row = [day] + formatted_schedule
                table_data.append(row)

                # Handle merging
                col_start = 1  # Skip "Day" column
                while col_start < len(row):
                    col_end = col_start
                    while col_end + 1 < len(row) and row[col_end] == row[col_end + 1] and "Break" not in row[col_start]:  
                        col_end += 1  # Extend merge range

                    if col_end > col_start:  # If merge needed
                        merge_styles.append(('SPAN', (col_start, row_idx + 1), (col_end, row_idx + 1)))
                        merge_styles.append(('ALIGN', (col_start, row_idx + 1), (col_end, row_idx + 1), 'CENTER'))
                        merge_styles.append(('VALIGN', (col_start, row_idx + 1), (col_end, row_idx + 1), 'MIDDLE'))
                        for i in range(col_start + 1, col_end + 1):
                            row[i] = ""  # Remove redundant text in merged cells
                    
                    col_start = col_end + 1  # Move to next unmerged cell

            # Create Table
            t = Table(table_data, colWidths=col_widths)  
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),  # Bigger Font
                ('BOTTOMPADDING', (0, 0), (-1, 0), 14),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Default grid
            ] + merge_styles + [
                ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Ensure outer border
            ]))  

            elements.append(t)
            elements.append(Table([[""]], colWidths=[sum(col_widths)]))  # Spacer

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