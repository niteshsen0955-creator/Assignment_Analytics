import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import student
import assignment
import submission
import analytics

class AssignmentAnalyticsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Assignment Submission & Analytics System")
        self.root.geometry("1100x750")
        
        # Configure style
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 11))
        style.configure("TButton", font=("Arial", 10))
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create Tabs
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_students = ttk.Frame(self.notebook)
        self.tab_assignments = ttk.Frame(self.notebook)
        self.tab_submissions = ttk.Frame(self.notebook)
        self.tab_missing = ttk.Frame(self.notebook)
        self.tab_analytics = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_dashboard, text="Dashboard")
        self.notebook.add(self.tab_students, text="Students")
        self.notebook.add(self.tab_assignments, text="Assignments")
        self.notebook.add(self.tab_submissions, text="Submissions")
        self.notebook.add(self.tab_missing, text="Missing Work")
        self.notebook.add(self.tab_analytics, text="Analytics")
        
        # Setup UIs
        self.setup_dashboard()
        self.setup_students()
        self.setup_assignments()
        self.setup_submissions()
        self.setup_missing()
        self.setup_analytics()
        
        # Bind tab change event to refresh data
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Initial data load
        self.refresh_all_data()

    def on_tab_changed(self, event):
        self.refresh_all_data()

    def refresh_all_data(self):
        """Refresh all treeviews, dashboard stats, and dropdowns."""
        self.refresh_dashboard()
        self.refresh_students_tree()
        self.refresh_assignments_tree()
        self.refresh_submissions_tree()
        self.refresh_missing_tree()
        self.refresh_analytics()
        self.update_dropdowns()

    # ==========================
    # 1. DASHBOARD
    # ==========================
    def setup_dashboard(self):
        title = tk.Label(self.tab_dashboard, text="System Dashboard", font=("Arial", 24, "bold"))
        title.pack(pady=30)
        
        self.dash_frame = ttk.Frame(self.tab_dashboard)
        self.dash_frame.pack(pady=20)
        
        self.dash_labels = {}
        fields = [
            "Total Students", 
            "Total Assignments", 
            "Total Expected Submissions",
            "Completed Submissions", 
            "Missing Submissions", 
            "Completion Rate", 
            "Average Score"
        ]
        for i, field in enumerate(fields):
            lbl = tk.Label(self.dash_frame, text=f"{field}:", font=("Arial", 14))
            lbl.grid(row=i, column=0, sticky='e', padx=20, pady=10)
            val = tk.Label(self.dash_frame, text="0", font=("Arial", 16, "bold"), fg="#0052cc")
            val.grid(row=i, column=1, sticky='w', padx=20, pady=10)
            self.dash_labels[field] = val
            
        btn_refresh = ttk.Button(self.tab_dashboard, text="Refresh Dashboard", command=self.refresh_all_data)
        btn_refresh.pack(pady=30)

    def refresh_dashboard(self):
        try:
            students = student.get_students()
            assignments = assignment.get_assignments()
            stats = analytics.completion_statistics()
            
            self.dash_labels["Total Students"].config(text=str(len(students)))
            self.dash_labels["Total Assignments"].config(text=str(len(assignments)))
            
            if stats:
                self.dash_labels["Total Expected Submissions"].config(text=str(stats.get("Total Expected Submissions", 0)))
                self.dash_labels["Completed Submissions"].config(text=str(stats.get("Completed", 0)))
                self.dash_labels["Missing Submissions"].config(text=str(stats.get("Missing", 0)))
                self.dash_labels["Completion Rate"].config(text=f"{stats.get('Completion Rate (%)', 0)}%")
                
            # Average score calculation using Pandas
            df = analytics.load_submissions()
            if df is not None and not df.empty:
                df_scored = df.dropna(subset=['score'])
                avg_score = df_scored['score'].mean() if not df_scored.empty else 0
                self.dash_labels["Average Score"].config(text=f"{avg_score:.2f}")
            else:
                self.dash_labels["Average Score"].config(text="0")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh dashboard: {str(e)}")

    # ==========================
    # 2. STUDENT MANAGEMENT
    # ==========================
    def setup_students(self):
        form_frame = ttk.LabelFrame(self.tab_students, text="Manage Student")
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_stu_id = ttk.Entry(form_frame)
        self.entry_stu_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Name:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_stu_name = ttk.Entry(form_frame)
        self.entry_stu_name.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_stu_email = ttk.Entry(form_frame)
        self.entry_stu_email.grid(row=0, column=5, padx=5, pady=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=1, column=0, columnspan=6, pady=10)
        
        ttk.Button(btn_frame, text="Add Student", command=self.add_student).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_student_form).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Search", command=self.search_student).pack(side='left', padx=5)
        
        # Search filter
        search_frame = ttk.Frame(self.tab_students)
        search_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(search_frame, text="Live Search (ID or Name):").pack(side='left', padx=5)
        self.entry_search_stu = ttk.Entry(search_frame)
        self.entry_search_stu.pack(side='left', padx=5)
        self.entry_search_stu.bind("<KeyRelease>", self.filter_students)
        
        self.tree_stu = ttk.Treeview(self.tab_students, columns=("ID", "Name", "Email"), show='headings')
        self.tree_stu.heading("ID", text="Student ID")
        self.tree_stu.heading("Name", text="Name")
        self.tree_stu.heading("Email", text="Email")
        self.tree_stu.pack(fill='both', expand=True, padx=10, pady=10)
        
    def add_student(self):
        try:
            s_id = self.entry_stu_id.get().strip()
            name = self.entry_stu_name.get().strip()
            email = self.entry_stu_email.get().strip()
            
            if not s_id or not name or not email:
                messagebox.showerror("Validation Error", "All fields are required.")
                return
                
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messagebox.showerror("Validation Error", "Invalid email format.")
                return
                
            if student.search_student(s_id):
                messagebox.showerror("Validation Error", "Student ID already exists.")
                return
                
            success = student.add_student(s_id, name, email)
            if success:
                messagebox.showinfo("Success", "Student added successfully.")
                self.clear_student_form()
                self.refresh_all_data()
            else:
                messagebox.showerror("Error", "Failed to add student due to a data layer error.")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def clear_student_form(self):
        self.entry_stu_id.delete(0, tk.END)
        self.entry_stu_name.delete(0, tk.END)
        self.entry_stu_email.delete(0, tk.END)
        
    def search_student(self):
        try:
            s_id = self.entry_stu_id.get().strip()
            if not s_id:
                messagebox.showinfo("Info", "Please enter a Student ID in the form to search.")
                return
                
            s = student.search_student(s_id)
            if s:
                self.clear_student_form()
                self.entry_stu_id.insert(0, s["student_id"])
                self.entry_stu_name.insert(0, s["name"])
                self.entry_stu_email.insert(0, s["email"])
            else:
                messagebox.showinfo("Info", "Student not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def filter_students(self, event=None):
        query = self.entry_search_stu.get().strip().lower()
        self.tree_stu.delete(*self.tree_stu.get_children())
        for s in student.get_students():
            if query in s["student_id"].lower() or query in s["name"].lower():
                self.tree_stu.insert('', tk.END, values=(s["student_id"], s["name"], s["email"]))

    def refresh_students_tree(self):
        self.entry_search_stu.delete(0, tk.END)
        self.tree_stu.delete(*self.tree_stu.get_children())
        for s in student.get_students():
            self.tree_stu.insert('', tk.END, values=(s["student_id"], s["name"], s["email"]))

    # ==========================
    # 3. ASSIGNMENT MANAGEMENT
    # ==========================
    def setup_assignments(self):
        form_frame = ttk.LabelFrame(self.tab_assignments, text="Manage Assignment")
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="Assignment ID:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_asn_id = ttk.Entry(form_frame)
        self.entry_asn_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Title:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_asn_title = ttk.Entry(form_frame)
        self.entry_asn_title.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Total Marks:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_asn_marks = ttk.Entry(form_frame)
        self.entry_asn_marks.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Due Date (YYYY-MM-DD):").grid(row=1, column=2, padx=5, pady=5)
        self.entry_asn_date = ttk.Entry(form_frame)
        self.entry_asn_date.grid(row=1, column=3, padx=5, pady=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Add Assignment", command=self.add_assignment).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_assignment_form).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Search", command=self.search_assignment).pack(side='left', padx=5)
        
        search_frame = ttk.Frame(self.tab_assignments)
        search_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(search_frame, text="Live Search (ID or Title):").pack(side='left', padx=5)
        self.entry_search_asn = ttk.Entry(search_frame)
        self.entry_search_asn.pack(side='left', padx=5)
        self.entry_search_asn.bind("<KeyRelease>", self.filter_assignments)
        
        self.tree_asn = ttk.Treeview(self.tab_assignments, columns=("ID", "Title", "Marks", "Due Date"), show='headings')
        self.tree_asn.heading("ID", text="Assignment ID")
        self.tree_asn.heading("Title", text="Title")
        self.tree_asn.heading("Marks", text="Total Marks")
        self.tree_asn.heading("Due Date", text="Due Date")
        self.tree_asn.pack(fill='both', expand=True, padx=10, pady=10)
        
    def add_assignment(self):
        try:
            a_id = self.entry_asn_id.get().strip()
            title = self.entry_asn_title.get().strip()
            marks = self.entry_asn_marks.get().strip()
            due_date = self.entry_asn_date.get().strip()
            
            if not a_id or not title or not marks or not due_date:
                messagebox.showerror("Validation Error", "All fields are required.")
                return
                
            try:
                m = float(marks)
                if m <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation Error", "Total marks must be a numeric value greater than 0.")
                return
                
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Validation Error", "Due date must be in YYYY-MM-DD format.")
                return
                
            if assignment.search_assignment(a_id):
                messagebox.showerror("Validation Error", "Assignment ID already exists.")
                return
                
            success = assignment.add_assignment(a_id, title, marks, due_date)
            if success:
                messagebox.showinfo("Success", "Assignment added successfully.")
                self.clear_assignment_form()
                self.refresh_all_data()
            else:
                messagebox.showerror("Error", "Failed to add assignment in data layer.")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def clear_assignment_form(self):
        self.entry_asn_id.delete(0, tk.END)
        self.entry_asn_title.delete(0, tk.END)
        self.entry_asn_marks.delete(0, tk.END)
        self.entry_asn_date.delete(0, tk.END)

    def search_assignment(self):
        try:
            a_id = self.entry_asn_id.get().strip()
            if not a_id:
                messagebox.showinfo("Info", "Please enter an Assignment ID to search.")
                return
                
            a = assignment.search_assignment(a_id)
            if a:
                self.clear_assignment_form()
                self.entry_asn_id.insert(0, a["assignment_id"])
                self.entry_asn_title.insert(0, a["title"])
                self.entry_asn_marks.insert(0, a["total_marks"])
                self.entry_asn_date.insert(0, a["due_date"])
            else:
                messagebox.showinfo("Info", "Assignment not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
            
    def filter_assignments(self, event=None):
        query = self.entry_search_asn.get().strip().lower()
        self.tree_asn.delete(*self.tree_asn.get_children())
        for a in assignment.get_assignments():
            if query in a["assignment_id"].lower() or query in a["title"].lower():
                self.tree_asn.insert('', tk.END, values=(a["assignment_id"], a["title"], a["total_marks"], a["due_date"]))

    def refresh_assignments_tree(self):
        self.entry_search_asn.delete(0, tk.END)
        self.tree_asn.delete(*self.tree_asn.get_children())
        for a in assignment.get_assignments():
            self.tree_asn.insert('', tk.END, values=(a["assignment_id"], a["title"], a["total_marks"], a["due_date"]))

    # ==========================
    # 4. SUBMISSION MANAGEMENT
    # ==========================
    def setup_submissions(self):
        form_frame = ttk.LabelFrame(self.tab_submissions, text="Record Submission")
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="Submission ID:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_sub_id = ttk.Entry(form_frame)
        self.entry_sub_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=2, padx=5, pady=5)
        self.combo_sub_stu = ttk.Combobox(form_frame, state="readonly")
        self.combo_sub_stu.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Assignment ID:").grid(row=1, column=0, padx=5, pady=5)
        self.combo_sub_asn = ttk.Combobox(form_frame, state="readonly")
        self.combo_sub_asn.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Submission Date (YYYY-MM-DD):").grid(row=1, column=2, padx=5, pady=5)
        self.entry_sub_date = ttk.Entry(form_frame)
        self.entry_sub_date.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Score:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_sub_score = ttk.Entry(form_frame)
        self.entry_sub_score.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Status:").grid(row=2, column=2, padx=5, pady=5)
        self.combo_sub_status = ttk.Combobox(form_frame, values=["Submitted", "Missing"], state="readonly")
        self.combo_sub_status.current(0)
        self.combo_sub_status.grid(row=2, column=3, padx=5, pady=5)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(btn_frame, text="Record Submission", command=self.add_submission).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_submission_form).pack(side='left', padx=5)
        
        # Filters
        filter_frame = ttk.Frame(self.tab_submissions)
        filter_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(filter_frame, text="Filter By Student ID:").pack(side='left', padx=5)
        self.entry_filter_sub_stu = ttk.Entry(filter_frame, width=10)
        self.entry_filter_sub_stu.pack(side='left', padx=5)
        self.entry_filter_sub_stu.bind("<KeyRelease>", self.filter_submissions)
        
        ttk.Label(filter_frame, text="Filter By Assignment ID:").pack(side='left', padx=5)
        self.entry_filter_sub_asn = ttk.Entry(filter_frame, width=10)
        self.entry_filter_sub_asn.pack(side='left', padx=5)
        self.entry_filter_sub_asn.bind("<KeyRelease>", self.filter_submissions)
        
        ttk.Label(filter_frame, text="Filter By Status:").pack(side='left', padx=5)
        self.combo_filter_status = ttk.Combobox(filter_frame, values=["All", "Submitted", "Missing"], state="readonly", width=12)
        self.combo_filter_status.current(0)
        self.combo_filter_status.pack(side='left', padx=5)
        self.combo_filter_status.bind("<<ComboboxSelected>>", self.filter_submissions)
        
        self.tree_sub = ttk.Treeview(self.tab_submissions, columns=("SubID", "AsnID", "StuID", "Date", "Score", "Status"), show='headings')
        self.tree_sub.heading("SubID", text="Submission ID")
        self.tree_sub.heading("AsnID", text="Assignment ID")
        self.tree_sub.heading("StuID", text="Student ID")
        self.tree_sub.heading("Date", text="Date")
        self.tree_sub.heading("Score", text="Score")
        self.tree_sub.heading("Status", text="Status")
        self.tree_sub.pack(fill='both', expand=True, padx=10, pady=10)

    def update_dropdowns(self):
        try:
            students = student.get_students()
            assignments = assignment.get_assignments()
            self.combo_sub_stu['values'] = [s['student_id'] for s in students]
            self.combo_sub_asn['values'] = [a['assignment_id'] for a in assignments]
        except Exception as e:
            print(f"Error updating dropdowns: {e}")

    def add_submission(self):
        try:
            sub_id = self.entry_sub_id.get().strip()
            stu_id = self.combo_sub_stu.get().strip()
            asn_id = self.combo_sub_asn.get().strip()
            sub_date = self.entry_sub_date.get().strip()
            score = self.entry_sub_score.get().strip()
            status = self.combo_sub_status.get().strip()
            
            if not sub_id or not stu_id or not asn_id or not status:
                messagebox.showerror("Validation Error", "Submission ID, Student ID, Assignment ID, and Status are required.")
                return
                
            if status == "Submitted":
                if not sub_date or not score:
                    messagebox.showerror("Validation Error", "Date and Score are required for 'Submitted' status.")
                    return
                    
                try:
                    datetime.strptime(sub_date, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Validation Error", "Submission date must be in YYYY-MM-DD format.")
                    return
                    
                try:
                    s_val = float(score)
                    a = assignment.search_assignment(asn_id)
                    if a:
                        max_score = float(a["total_marks"])
                        if s_val < 0 or s_val > max_score:
                            messagebox.showerror("Validation Error", f"Score must be between 0 and {max_score}.")
                            return
                except ValueError:
                    messagebox.showerror("Validation Error", "Score must be a valid number.")
                    return
            else:
                # Force missing defaults if status is Missing
                if not score: score = "N/A"
                if not sub_date: sub_date = "N/A"
                
            subs = submission.get_submissions()
            
            # Ensure unique submission ID
            for sub in subs:
                if sub["submission_id"] == sub_id and sub_id != "N/A":
                    messagebox.showerror("Validation Error", "Submission ID already exists.")
                    return
                    
            # Prevent duplicate submission for the same student + assignment
            for sub in subs:
                if sub["student_id"] == stu_id and sub["assignment_id"] == asn_id:
                    messagebox.showerror("Validation Error", "A submission already exists for this Student and Assignment.")
                    return
                    
            success = submission.add_submission(sub_id, asn_id, stu_id, sub_date, score, status)
            if success:
                messagebox.showinfo("Success", "Submission recorded successfully.")
                self.clear_submission_form()
                self.refresh_all_data()
            else:
                messagebox.showerror("Error", "Failed to record submission.")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def clear_submission_form(self):
        self.entry_sub_id.delete(0, tk.END)
        self.combo_sub_stu.set('')
        self.combo_sub_asn.set('')
        self.entry_sub_date.delete(0, tk.END)
        self.entry_sub_score.delete(0, tk.END)
        self.combo_sub_status.current(0)
        
    def filter_submissions(self, event=None):
        try:
            stu_q = self.entry_filter_sub_stu.get().strip().lower()
            asn_q = self.entry_filter_sub_asn.get().strip().lower()
            stat_q = self.combo_filter_status.get().strip()
            
            self.tree_sub.delete(*self.tree_sub.get_children())
            for s in submission.get_submissions():
                match_stu = (stu_q in s["student_id"].lower())
                match_asn = (asn_q in s["assignment_id"].lower())
                match_stat = (stat_q == "All" or stat_q.lower() == s["status"].lower())
                
                if match_stu and match_asn and match_stat:
                    self.tree_sub.insert('', tk.END, values=(s["submission_id"], s["assignment_id"], s["student_id"], s["submission_date"], s["score"], s["status"]))
        except Exception as e:
            pass

    def refresh_submissions_tree(self):
        self.entry_filter_sub_stu.delete(0, tk.END)
        self.entry_filter_sub_asn.delete(0, tk.END)
        self.combo_filter_status.current(0)
        self.tree_sub.delete(*self.tree_sub.get_children())
        for s in submission.get_submissions():
            self.tree_sub.insert('', tk.END, values=(s["submission_id"], s["assignment_id"], s["student_id"], s["submission_date"], s["score"], s["status"]))

    # ==========================
    # 5. MISSING SUBMISSIONS
    # ==========================
    def setup_missing(self):
        title = tk.Label(self.tab_missing, text="Missing Submissions List", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        btn_refresh = ttk.Button(self.tab_missing, text="Refresh List", command=self.refresh_missing_tree)
        btn_refresh.pack(pady=5)
        
        self.tree_miss = ttk.Treeview(self.tab_missing, columns=("SubID", "AsnID", "StuID", "Date", "Score", "Status"), show='headings')
        self.tree_miss.heading("SubID", text="Submission ID")
        self.tree_miss.heading("AsnID", text="Assignment ID")
        self.tree_miss.heading("StuID", text="Student ID")
        self.tree_miss.heading("Date", text="Date")
        self.tree_miss.heading("Score", text="Score")
        self.tree_miss.heading("Status", text="Status")
        self.tree_miss.pack(fill='both', expand=True, padx=10, pady=10)

    def refresh_missing_tree(self):
        self.tree_miss.delete(*self.tree_miss.get_children())
        try:
            missing = submission.get_pending_submissions()
            for m in missing:
                self.tree_miss.insert('', tk.END, values=(m["submission_id"], m["assignment_id"], m["student_id"], m["submission_date"], m["score"], m["status"]))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load missing submissions: {str(e)}")

    # ==========================
    # 6. ANALYTICS TAB
    # ==========================
    def setup_analytics(self):
        top_frame = ttk.Frame(self.tab_analytics)
        top_frame.pack(fill='x', padx=10, pady=5)
        
        title = tk.Label(top_frame, text="Data Analytics & Visualizations", font=("Arial", 16, "bold"))
        title.pack(pady=5)
        
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Refresh Analytics & Charts", command=self.refresh_analytics).pack(side='left')
        
        self.lbl_stats = tk.Label(top_frame, text="", font=("Arial", 12), justify='left')
        self.lbl_stats.pack(pady=5)
        
        # Charts frame
        self.charts_frame = ttk.Frame(self.tab_analytics)
        self.charts_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.canvas_widget = None
        
        table_frame = ttk.Frame(self.tab_analytics)
        table_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(table_frame, text="Assignment Statistics:", font=("Arial", 12, "bold")).pack(anchor='w', pady=2)
        
        self.tree_astats = ttk.Treeview(table_frame, columns=("AsnID", "Average", "Highest", "Lowest", "Count"), show='headings', height=4)
        self.tree_astats.heading("AsnID", text="Assignment ID")
        self.tree_astats.heading("Average", text="Average Score")
        self.tree_astats.heading("Highest", text="Highest Score")
        self.tree_astats.heading("Lowest", text="Lowest Score")
        self.tree_astats.heading("Count", text="Submissions Count")
        self.tree_astats.pack(fill='x')

    def refresh_charts(self):
        # Clear existing canvas
        if self.canvas_widget:
            self.canvas_widget.destroy()
            self.canvas_widget = None
            
        comp_data = analytics.get_assignment_completion_data()
        time_data = analytics.get_submission_timeline_data()
        status_data = analytics.get_status_distribution_data()
        
        if not comp_data and not time_data and not status_data:
            lbl = tk.Label(self.charts_frame, text="No submission data available for visualization.", font=("Arial", 12, "italic"))
            lbl.pack(pady=20)
            self.canvas_widget = lbl
            return
            
        # Create Figure
        fig = Figure(figsize=(10, 3.5), dpi=100)
        
        plot_count = 0
        if comp_data: plot_count += 1
        if time_data: plot_count += 1
        if status_data: plot_count += 1
        
        if plot_count == 0:
            return
            
        idx = 1
        
        # Graph 1: Bar Chart
        if comp_data:
            ax1 = fig.add_subplot(1, plot_count, idx)
            idx += 1
            labels = list(comp_data.keys())
            values = list(comp_data.values())
            
            short_labels = [l[:12]+"..." if len(l)>12 else l for l in labels]
            
            bars = ax1.bar(short_labels, values, color='#4c72b0')
            ax1.set_ylim(0, 100)
            ax1.set_title("Assignment-wise Completion Rate")
            ax1.set_xlabel("Assignment")
            ax1.set_ylabel("Completion Percentage (%)")
            ax1.tick_params(axis='x', rotation=15)
            
            for bar in bars:
                height = bar.get_height()
                ax1.annotate(f'{height:.0f}%',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9)
                            
        # Graph 2: Line Chart
        from matplotlib.ticker import MaxNLocator
        if time_data:
            ax2 = fig.add_subplot(1, plot_count, idx)
            idx += 1
            ax2.plot(time_data['dates'], time_data['counts'], marker='o', linestyle='-', color='#55a868')
            ax2.set_title("Submission Pattern Over Time")
            ax2.set_xlabel("Submission Date")
            ax2.set_ylabel("Number of Submissions")
            ax2.tick_params(axis='x', rotation=15)
            ax2.grid(True, linestyle='--', alpha=0.7)
            # Ensure integer ticks on y axis
            ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
            
        # Graph 3: Pie Chart
        if status_data:
            ax3 = fig.add_subplot(1, plot_count, idx)
            idx += 1
            labels = list(status_data.keys())
            sizes = list(status_data.values())
            if sum(sizes) > 0:
                ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#55a868', '#c44e52'])
                ax3.set_title("Overall Submission Status")
            
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill='both', expand=True)

    def refresh_analytics(self):
        try:
            comp_stats = analytics.completion_statistics()
            if comp_stats:
                stat_text = (
                    f"Total Expected Submissions: {comp_stats.get('Total Expected Submissions', 0)}  |  "
                    f"Completed: {comp_stats.get('Completed', 0)}  |  "
                    f"Missing: {comp_stats.get('Missing', 0)}\n"
                    f"Completion Rate: {comp_stats.get('Completion Rate (%)', 0)}%  |  "
                    f"Overall Median Score: {comp_stats.get('Overall Median Score', 0)}"
                )
                self.lbl_stats.config(text=stat_text)
            else:
                self.lbl_stats.config(text="No completion statistics available.")
                
            self.tree_astats.delete(*self.tree_astats.get_children())
            asn_stats = analytics.assignment_statistics()
            if asn_stats:
                for a_id, s in asn_stats.items():
                    # Format strictly for display
                    self.tree_astats.insert('', tk.END, values=(
                        a_id, 
                        f"{s['Average']:.2f}", 
                        f"{s['Highest']:.1f}", 
                        f"{s['Lowest']:.1f}", 
                        s['Count']
                    ))
                    
            # Refresh matplotlib charts
            self.refresh_charts()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load analytics: {str(e)}")

def main():
    root = tk.Tk()
    app = AssignmentAnalyticsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
