import csv
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'assignments.csv')

def initialize_file():
    """Create the CSV file with appropriate headers if it does not exist."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["assignment_id", "title", "total_marks", "due_date"])

def add_assignment(assignment_id, title, total_marks, due_date):
    """Add a new assignment. Validates inputs and prevents duplicate IDs."""
    try:
        # Input validation
        if not assignment_id or not title or not total_marks or not due_date:
            raise ValueError("All fields are required.")
            
        try:
            float(total_marks)
        except ValueError:
            raise ValueError("Total marks must be a number.")
            
        initialize_file()
        assignments = get_assignments()
        
        # Prevent duplicates
        for assignment in assignments:
            if assignment["assignment_id"] == str(assignment_id):
                raise ValueError(f"Assignment ID {assignment_id} already exists.")
                
        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([assignment_id, title, total_marks, due_date])
        return True
    except Exception as e:
        print(f"Error adding assignment: {e}")
        return False

def get_assignments():
    """Retrieve all assignments from the CSV file."""
    assignments = []
    try:
        initialize_file()
        with open(DATA_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                assignments.append(row)
    except Exception as e:
        print(f"Error getting assignments: {e}")
    return assignments

def search_assignment(assignment_id):
    """Search for an assignment by its ID."""
    try:
        assignments = get_assignments()
        for assignment in assignments:
            if assignment["assignment_id"] == str(assignment_id):
                return assignment
    except Exception as e:
        print(f"Error searching assignment: {e}")
    return None
