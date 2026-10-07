import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import student
import assignment
import submission
import analytics

def setup_test_environment():
    """Setup temporary data files for testing without altering real data."""
    temp_dir = tempfile.mkdtemp()
    
    student.DATA_FILE = os.path.join(temp_dir, 'students.csv')
    assignment.DATA_FILE = os.path.join(temp_dir, 'assignments.csv')
    submission.DATA_FILE = os.path.join(temp_dir, 'submissions.csv')
    analytics.DATA_FILE = submission.DATA_FILE
    
    return temp_dir

def teardown_test_environment(temp_dir):
    """Clean up temporary test files."""
    shutil.rmtree(temp_dir)

def run_tests():
    temp_dir = setup_test_environment()
    print("Testing Environment Initialized...\n")
    
    try:
        # A. Student Tests
        print("Testing Students...")
        assert student.add_student("S001", "Alice Smith", "alice@example.com") == True
        assert student.add_student("S002", "Bob Jones", "bob@example.com") == True
        assert student.add_student("", "Empty ID", "empty@example.com") == False # Reject empty student
        assert student.add_student("S001", "Duplicate ID", "dup@example.com") == False # Reject duplicate ID
        
        # B. Assignment Tests
        print("Testing Assignments...")
        assert assignment.add_assignment("A001", "Math Homework", "100", "2023-11-01") == True
        assert assignment.add_assignment("A002", "Science Project", "50", "2023-11-05") == True
        assert assignment.add_assignment("A003", "Invalid Marks", "abc", "2023-11-05") == False # Reject invalid marks
        assert assignment.add_assignment("A001", "Duplicate ID", "100", "2023-11-01") == False # Reject duplicate ID
        
        # C. Submission Tests
        print("Testing Submissions...")
        assert submission.add_submission("SUB001", "A001", "S001", "2023-10-30", "95", "Submitted") == True
        assert submission.add_submission("SUB002", "A001", "INVALID_STU", "2023-10-30", "90", "Submitted") == False # Reject invalid student
        assert submission.add_submission("SUB003", "INVALID_ASN", "S002", "2023-10-30", "90", "Submitted") == False # Reject invalid assignment
        assert submission.add_submission("SUB004", "A002", "S001", "2023-10-30", "abc", "Submitted") == False # Reject invalid score
        assert submission.add_submission("SUB001", "A002", "S002", "2023-10-30", "90", "Submitted") == False # Reject duplicate submission ID
        assert submission.add_submission("SUB005", "A002", "S001", "2023-10-30", "90", "InvalidStatus") == False # Validate status
        
        # D. Missing submissions
        print("Testing Missing Submissions...")
        missing = submission.get_pending_submissions()
        # S001 has A001. A002 is missing.
        # S002 has nothing. A001, A002 are missing.
        # Total expected missing = 3
        assert len(missing) == 3
        
        # E. Analytics Tests
        print("Testing Analytics...")
        stats = analytics.completion_statistics()
        assert stats["Total Expected Submissions"] == 4
        assert stats["Completed"] == 1
        assert stats["Missing"] == 3
        assert stats["Completion Rate (%)"] == 25.0
        
        # Assignment stats
        astats = analytics.assignment_statistics()
        assert "A001" in astats
        assert astats["A001"]["Count"] == 1
        assert astats["A001"]["Highest"] == 95.0
        
        # Chart Data
        comp_data = analytics.get_assignment_completion_data()
        assert "Math Homework" in comp_data
        assert comp_data["Math Homework"] == 50.0  # 1 out of 2 students
        
        time_data = analytics.get_submission_timeline_data()
        assert "2023-10-30" in time_data["dates"]
        
        print("\nAll tests completed and passed successfully!")
    except AssertionError as e:
        print(f"\nTest failed due to an assertion error. Check test assertions.")
        sys.exit(1)
    finally:
        teardown_test_environment(temp_dir)
        print("Cleaned up temporary testing environment.")

if __name__ == "__main__":
    run_tests()
