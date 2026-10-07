import pandas as pd
import numpy as np
import os
import submission
import student
import assignment

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'submissions.csv')

def load_submissions():
    """Load submissions data using Pandas."""
    try:
        if not os.path.exists(DATA_FILE):
            submission.initialize_file()
        df = pd.read_csv(DATA_FILE)
        
        # Convert score column to numeric, forcing errors to NaN
        if 'score' in df.columns:
            df['score'] = pd.to_numeric(df['score'], errors='coerce')
        return df
    except Exception as e:
        print(f"Error loading submissions in Pandas: {e}")
        return None

def completion_statistics():
    """Calculate overall submission completion statistics."""
    try:
        # Calculate expected total submissions
        students_count = len(student.get_students())
        assignments_count = len(assignment.get_assignments())
        total_expected = students_count * assignments_count
        
        df = load_submissions()
        if df is None or df.empty:
            completed = 0
            df_scored = pd.DataFrame()
        else:
            completed = len(df[df['status'].str.lower() == 'submitted'])
            df_scored = df.dropna(subset=['score'])
            
        missing_count = total_expected - completed
        completion_rate = (completed / total_expected) * 100 if total_expected > 0 else 0
        
        # Meaningful use of numpy to get overall median score
        overall_median = np.median(df_scored['score']) if not df_scored.empty else 0
        
        stats = {
            "Total Expected Submissions": total_expected,
            "Completed": completed,
            "Missing": missing_count,
            "Completion Rate (%)": round(completion_rate, 2),
            "Overall Median Score": round(float(overall_median), 1)
        }
        return stats
    except Exception as e:
        print(f"Error calculating completion statistics: {e}")
        return None

def assignment_statistics():
    """Calculate statistical metrics (average, highest, lowest) for each assignment."""
    try:
        df = load_submissions()
        if df is None or df.empty:
            print("No submissions data available.")
            return None
            
        # Filter rows with valid scores
        df_scored = df.dropna(subset=['score'])
        if df_scored.empty:
            print("No valid scores available for statistics.")
            return None
            
        # Use pandas groupby with string identifiers to avoid FutureWarnings
        stats_df = df_scored.groupby('assignment_id')['score'].agg(
            Average='mean',
            Highest='max',
            Lowest='min',
            Count='count'
        )
        
        return stats_df.to_dict('index')
    except Exception as e:
        print(f"Error calculating assignment statistics: {e}")
        return None

def get_assignment_completion_data():
    """Returns data for Assignment-wise Completion Rate bar chart."""
    try:
        students = student.get_students()
        assignments = assignment.get_assignments()
        
        if not students or not assignments:
            return None
            
        total_students = len(students)
        df = load_submissions()
        
        completion_data = {}
        for a in assignments:
            a_id = a['assignment_id']
            title = a['title']
            
            if df is not None and not df.empty:
                submitted = len(df[(df['assignment_id'] == a_id) & (df['status'].str.lower() == 'submitted')])
            else:
                submitted = 0
                
            rate = (submitted / total_students) * 100 if total_students > 0 else 0
            label = f"{title}"
            completion_data[label] = rate
            
        return completion_data
    except Exception as e:
        print(f"Error getting assignment completion data: {e}")
        return None

def get_submission_timeline_data():
    """Returns data for Submission Pattern Over Time line chart."""
    try:
        df = load_submissions()
        if df is None or df.empty:
            return None
            
        df_sub = df[(df['status'].str.lower() == 'submitted') & (df['submission_date'] != 'N/A')].copy()
        
        if df_sub.empty:
            return None
            
        timeline = df_sub.groupby('submission_date').size().reset_index(name='count')
        timeline['submission_date'] = pd.to_datetime(timeline['submission_date'], errors='coerce')
        timeline = timeline.dropna(subset=['submission_date']).sort_values('submission_date')
        timeline['submission_date_str'] = timeline['submission_date'].dt.strftime('%Y-%m-%d')
        
        if timeline.empty:
            return None
            
        return {
            'dates': timeline['submission_date_str'].tolist(),
            'counts': timeline['count'].tolist()
        }
    except Exception as e:
        print(f"Error getting submission timeline data: {e}")
        return None
        
def get_status_distribution_data():
    """Returns data for Status Distribution pie chart."""
    try:
        stats = completion_statistics()
        if stats and stats.get("Total Expected Submissions", 0) > 0:
            return {
                "Submitted": stats["Completed"],
                "Missing": stats["Missing"]
            }
        return None
    except Exception as e:
        print(f"Error getting status distribution data: {e}")
        return None
