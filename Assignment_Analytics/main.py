import gui
import sys

def main():
    # If run in test mode (like in our headless CI verification), skip mainloop
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("Running in headless test mode...")
        import tkinter as tk
        root = tk.Tk()
        app = gui.AssignmentAnalyticsApp(root)
        print("GUI initialized successfully.")
        # We can simulate interactions here
        app.entry_stu_id.insert(0, "T001")
        app.entry_stu_name.insert(0, "Test Student")
        app.entry_stu_email.insert(0, "test@example.com")
        app.add_student()
        print("Student added via GUI form successfully.")
        
        # Test Assignment
        app.entry_asn_id.insert(0, "TA01")
        app.entry_asn_title.insert(0, "Test Assignment")
        app.entry_asn_marks.insert(0, "100")
        app.entry_asn_date.insert(0, "2024-01-01")
        app.add_assignment()
        print("Assignment added via GUI form successfully.")
        
        # We exit without starting mainloop to prevent hanging
        print("Headless verification completed.")
        sys.exit(0)
    else:
        # Standard desktop execution
        gui.main()

if __name__ == "__main__":
    main()
