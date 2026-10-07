import csv
import os
import student
import assignment

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'submissions.csv')

def initialize_file():
    """Create the CSV file with appropriate headers if it does not exist."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["submission_id", "assignment_id", "student_id", "submission_date", "score", "status"])

def add_submission(submission_id, assignment_id, student_id, submission_date, score, status="Submitted"):
    """Add a new submission. Validates relationships and inputs."""
    try:
        # Input validation
        if not submission_id or not assignment_id or not student_id or not status:
            raise ValueError("Submission ID, Assignment ID, Student ID, and status are required.")
            
        if status not in ["Submitted", "Missing"]:
            raise ValueError("Status must be either 'Submitted' or 'Missing'.")
            
        if score and score != "N/A":
            try:
                float(score)
            except ValueError:
                raise ValueError("Score must be a valid number or 'N/A'.")
                
        initialize_file()
        
        # Cross-validation: Check if student exists
        if not student.search_student(student_id):
            raise ValueError(f"Student ID {student_id} does not exist.")
            
        # Cross-validation: Check if assignment exists
        if not assignment.search_assignment(assignment_id):
            raise ValueError(f"Assignment ID {assignment_id} does not exist.")
            
        submissions = get_submissions()
        
        # Prevent duplicates
        for sub in submissions:
            if sub["submission_id"] == str(submission_id) and sub["submission_id"] != "N/A":
                raise ValueError(f"Submission ID {submission_id} already exists.")
                
        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([submission_id, assignment_id, student_id, submission_date, score, status])
        return True
    except Exception as e:
        print(f"Error adding submission: {e}")
        return False

def get_submissions():
    """Retrieve all submissions from the CSV file."""
    submissions = []
    try:
        initialize_file()
        with open(DATA_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                submissions.append(row)
    except Exception as e:
        print(f"Error getting submissions: {e}")
    return submissions

def get_pending_submissions():
    """Identify every student-assignment pair for which no submission record exists."""
    pending = []
    try:
        submissions = get_submissions()
                
        # Find missing submissions
        students = student.get_students()
        assignments = assignment.get_assignments()
        
        submitted_pairs = set((sub["student_id"], sub["assignment_id"]) for sub in submissions if sub["status"].lower() == "submitted")
        
        for stu in students:
            for assgn in assignments:
                if (stu["student_id"], assgn["assignment_id"]) not in submitted_pairs:
                    pending.append({
                        "submission_id": "N/A",
                        "assignment_id": assgn["assignment_id"],
                        "student_id": stu["student_id"],
                        "submission_date": "N/A",
                        "score": "N/A",
                        "status": "Missing"
                    })
    except Exception as e:
        print(f"Error getting pending submissions: {e}")
        
    return pending
