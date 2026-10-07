import csv
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'students.csv')

def initialize_file():
    """Create the CSV file with appropriate headers if it does not exist."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["student_id", "name", "email"])

def add_student(student_id, name, email):
    """Add a new student. Validates inputs and prevents duplicate IDs."""
    try:
        # Input validation
        if not student_id or not name or not email:
            raise ValueError("All fields (student_id, name, email) are required.")
            
        initialize_file()
        students = get_students()
        
        # Prevent duplicates
        for student in students:
            if student["student_id"] == str(student_id):
                raise ValueError(f"Student ID {student_id} already exists.")
                
        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([student_id, name, email])
        return True
    except Exception as e:
        print(f"Error adding student: {e}")
        return False

def get_students():
    """Retrieve all students from the CSV file."""
    students = []
    try:
        initialize_file()
        with open(DATA_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                students.append(row)
    except Exception as e:
        print(f"Error getting students: {e}")
    return students

def search_student(student_id):
    """Search for a student by their ID."""
    try:
        students = get_students()
        for student in students:
            if student["student_id"] == str(student_id):
                return student
    except Exception as e:
        print(f"Error searching student: {e}")
    return None
