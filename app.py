from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
import database
import analyzer

app = Flask(__name__)
app.secret_key = 'super_secret_key_student_performance_ai_project'

# Configure file uploads
UPLOAD_FOLDER = os.path.join(app.root_path, 'data', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.before_request
def ensure_session_uuid():
    """Generates unique session ID for isolating uploaded files."""
    if 'session_uuid' not in session:
        session['session_uuid'] = str(uuid.uuid4())

# Ensure database and base files are initialized
database.init_db()

# Generate initial dataset and plots
try:
    df = analyzer.load_data()
    analyzer.generate_plots()
    print("Initial student dataset and analytical plots prepared successfully.")
except Exception as e:
    print(f"Error during initial data setup: {e}")

@app.context_processor
def inject_user():
    """Injects user information into templates automatically if logged in."""
    return dict(
        logged_in='user_id' in session,
        current_username=session.get('username')
    )

def login_required(f):
    """Decorator to require login on specific endpoints."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def dashboard():
    """Main dashboard showing overview metrics and a data grid of student performance."""
    try:
        stats = analyzer.get_statistics()
        df = analyzer.load_data()
        
        # Paginate or list students
        students = df.to_dict(orient='records')
    except Exception as e:
        flash(f"Error reading dashboard data: {e}", "error")
        stats = analyzer.get_default_statistics()
        students = []
        
    return render_template('dashboard.html', stats=stats, students=students)

@app.route('/analysis')
@login_required
def analysis():
    """Visualizations page containing analytical charts and summaries."""
    try:
        stats = analyzer.get_statistics()
    except Exception as e:
        flash(f"Error loading analysis metrics: {e}", "error")
        stats = analyzer.get_default_statistics()
        
    return render_template('analysis.html', stats=stats)

@app.route('/internship')
@login_required
def internship():
    """Timeline and syllabus log for the 45-day internship."""
    return render_template('internship.html')

@app.route('/run-analysis', methods=['POST'])
@login_required
def run_analysis():
    """Triggers dataset regeneration and plot updates."""
    try:
        analyzer.generate_data(num_students=200)
        analyzer.generate_plots()
        return jsonify({"status": "success", "message": "Dataset and plots successfully regenerated."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles new user registration."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if password != confirm_password:
            flash("Passwords do not match.", "error")
        else:
            success, message = database.register_user(username, email, password)
            if success:
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for('login'))
            else:
                flash(message, "error")
            
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user authentication."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = database.authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "error")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs out user and invalidates session."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/custom-plot', methods=['GET', 'POST'])
@login_required
def custom_plot():
    """Custom plotting view allowing users to select columns and plot types dynamically."""
    columns_numeric = [
        'Study_Hours_Weekly', 'Prior_GPA', 'Attendance_Rate', 
        'AI_Usage_Hours_Weekly', 'AI_Prompts_Count_Weekly', 'Final_Exam_Score'
    ]
    columns_categorical = ['AI_Usage_Type']
    plot_types = ['scatter', 'bar', 'box', 'hist']
    
    plot_data = None
    selected_x = None
    selected_y = None
    selected_type = None
    
    if request.method == 'POST':
        selected_x = request.form.get('x_column')
        selected_y = request.form.get('y_column')
        selected_type = request.form.get('plot_type')
        
        # y_column is ignored for histogram plots
        y_val = selected_y if selected_type != 'hist' else None
        
        try:
            plot_data = analyzer.generate_custom_plot(
                x_col=selected_x, 
                y_col=y_val, 
                plot_type=selected_type
            )
        except Exception as e:
            flash(f"Error generating customized plot: {e}", "error")
            
    return render_template(
        'custom_plot.html', 
        columns_numeric=columns_numeric,
        columns_categorical=columns_categorical,
        plot_types=plot_types,
        plot_data=plot_data,
        selected_x=selected_x,
        selected_y=selected_y,
        selected_type=selected_type
    )

@app.route('/performance-analytics', methods=['GET', 'POST'])
@login_required
def performance_analytics():
    """Performance analytics dashboard showcasing individual, subject, and class performance metrics."""
    try:
        stats = analyzer.get_statistics()
        df = analyzer.load_data()
        
        # Sort student names alphabetically for the dropdown selection
        students_list = df.sort_values(by='Name')[['Student_ID', 'Name']].to_dict(orient='records')
        
        selected_student_id = request.form.get('student_id') or request.args.get('student_id')
        if not selected_student_id and students_list:
            selected_student_id = students_list[0]['Student_ID']
            
        student_data = None
        student_chart = None
        
        if selected_student_id:
            row = df[df['Student_ID'] == selected_student_id]
            if not row.empty:
                student_data = row.iloc[0].to_dict()
                student_chart = analyzer.generate_student_comparison_chart(selected_student_id)
                
    except Exception as e:
        flash(f"Error loading performance analytics: {e}", "error")
        stats = analyzer.get_default_statistics()
        students_list = []
        student_data = None
        student_chart = None
        selected_student_id = None
        
    return render_template(
        'performance_analytics.html',
        stats=stats,
        students_list=students_list,
        selected_student_id=selected_student_id,
        student_data=student_data,
        student_chart=student_chart
    )

@app.route('/dynamic-analysis', methods=['GET', 'POST'])
@login_required
def dynamic_analysis():
    """Handles arbitrary CSV uploads, displays stats/previews, and enables dynamic plotting."""
    # Resolve paths
    session_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], session.get('session_uuid', 'default'))
    os.makedirs(session_upload_dir, exist_ok=True)
    
    # Handle GET quick load demo parameters
    demo_type = request.args.get('demo') or request.args.get('load_test')
    if demo_type:
        if demo_type == 'custom':
            test_path = os.path.join(app.root_path, 'test_data.csv')
            if os.path.exists(test_path):
                session['dynamic_data_file'] = test_path
                session['dynamic_dataset_name'] = 'test_data.csv'
                session['is_student_schema'] = False
                flash("Demo custom dataset loaded successfully!", "success")
            else:
                flash("Demo custom dataset file not found.", "error")
        elif demo_type == 'student':
            test_path = os.path.join(app.root_path, 'test_student.csv')
            if os.path.exists(test_path):
                session['dynamic_data_file'] = test_path
                session['dynamic_dataset_name'] = 'test_student.csv'
                session['is_student_schema'] = True
                flash("Demo student cohort dataset loaded successfully!", "success")
            else:
                flash("Demo student cohort dataset file not found.", "error")
                
    action = request.form.get('action')
    
    if request.method == 'POST' and 'file' in request.files:
        # Handle file upload
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(session_upload_dir, f"upload_{filename}")
            try:
                file.save(filepath)
                # Parse to verify
                import pandas as pd
                df = pd.read_csv(filepath)
                
                # Check shape
                if df.empty:
                    flash("The uploaded CSV file is empty.", "error")
                    if os.path.exists(filepath):
                        os.remove(filepath)
                else:
                    # Successfully parsed
                    session['dynamic_data_file'] = filepath
                    session['dynamic_dataset_name'] = filename
                    
                    # Validate schema
                    is_student = analyzer.validate_student_schema(df)
                    session['is_student_schema'] = is_student
                    
                    flash(f"Dataset '{filename}' successfully uploaded! Detected {df.shape[0]} rows and {df.shape[1]} columns.", "success")
            except Exception as e:
                flash(f"Error reading CSV file: {str(e)}", "error")
                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            flash("Please upload a valid CSV file (.csv).", "error")
            
        return redirect(url_for('dynamic_analysis'))
        
    elif request.method == 'POST' and action == 'set_cohort':
        # User wants to set the uploaded file as the active student cohort dataset
        dynamic_file = session.get('dynamic_data_file')
        if dynamic_file and os.path.exists(dynamic_file):
            session['data_file'] = dynamic_file
            session['dataset_name'] = session.get('dynamic_dataset_name')
            
            # Regenerate plots for dashboard using the custom cohort!
            try:
                analyzer.generate_plots()
                flash("Active Cohort Dataset overridden. The main dashboard and analysis page are now using your custom data!", "success")
            except Exception as e:
                flash(f"Error building analytics for cohort: {str(e)}. Reverting override.", "error")
                session.pop('data_file', None)
                session.pop('dataset_name', None)
        else:
            flash("No uploaded dataset found to set as cohort.", "error")
        return redirect(url_for('dynamic_analysis'))
        
    elif request.method == 'POST' and action == 'reset':
        # Reset everything to default synthetic data
        session.pop('data_file', None)
        session.pop('dataset_name', None)
        session.pop('dynamic_data_file', None)
        session.pop('dynamic_dataset_name', None)
        session.pop('is_student_schema', None)
        
        # Regenerate standard plots
        try:
            analyzer.generate_plots()
            flash("Successfully reset to the default synthetic student cohort.", "success")
        except Exception as e:
            flash(f"Error resetting plots: {str(e)}", "error")
            
        return redirect(url_for('dynamic_analysis'))
        
    # Analysis & Plotting workspace variables
    plot_data = None
    selected_x = request.form.get('x_column')
    selected_y = request.form.get('y_column')
    selected_type = request.form.get('plot_type')
    
    # Retrieve current dataset details if available
    metadata = None
    preview_rows = None
    columns_list = []
    columns_numeric = []
    columns_categorical = []
    summary_stats = None
    
    # Check what file to inspect for GET/POST plotter
    inspect_file = session.get('dynamic_data_file') or session.get('data_file')
    
    if inspect_file and os.path.exists(inspect_file):
        try:
            import pandas as pd
            import numpy as np
            df = pd.read_csv(inspect_file)
            
            # Metadata
            metadata = {
                'name': session.get('dynamic_dataset_name') or session.get('dataset_name', 'Custom Dataset'),
                'rows': df.shape[0],
                'cols': df.shape[1],
                'is_cohort_active': 'data_file' in session and session['data_file'] == inspect_file,
                'is_student': session.get('is_student_schema', False)
            }
            
            columns_list = list(df.columns)
            
            # Divide columns into numerical and categorical
            for col in df.columns:
                if np.issubdtype(df[col].dtype, np.number):
                    columns_numeric.append(col)
                else:
                    columns_categorical.append(col)
                    
            # Generate first 10 rows for preview (converting nan to None for JSON template friendliness)
            df_cleaned = df.replace({np.nan: None})
            preview_rows = df_cleaned.head(10).to_dict(orient='records')
            
            # Generate summary statistics
            desc = df.describe(include='all')
            summary_stats = []
            for col in df.columns:
                col_type = str(df[col].dtype)
                null_count = int(df[col].isnull().sum())
                
                mean_val = round(desc[col].get('mean'), 2) if 'mean' in desc.index and pd.notnull(desc[col].get('mean')) else 'N/A'
                min_val = round(desc[col].get('min'), 2) if 'min' in desc.index and pd.notnull(desc[col].get('min')) else 'N/A'
                max_val = round(desc[col].get('max'), 2) if 'max' in desc.index and pd.notnull(desc[col].get('max')) else 'N/A'
                unique_val = int(desc[col].get('unique')) if 'unique' in desc.index and pd.notnull(desc[col].get('unique')) else 'N/A'
                
                summary_stats.append({
                    'name': col,
                    'type': col_type,
                    'nulls': null_count,
                    'mean': mean_val,
                    'min': min_val,
                    'max': max_val,
                    'unique': unique_val
                })
                
            # If plotting form was submitted
            if request.method == 'POST' and selected_x and selected_type and action != 'set_cohort' and action != 'reset':
                y_val = selected_y if selected_type != 'hist' else None
                try:
                    plot_data = analyzer.generate_dynamic_plot(
                        filepath=inspect_file,
                        x_col=selected_x,
                        y_col=y_val,
                        plot_type=selected_type
                    )
                except Exception as e:
                    flash(f"Error rendering dynamic plot: {str(e)}", "error")
                    
        except Exception as e:
            flash(f"Error loading uploaded file: {str(e)}", "error")
            
    return render_template(
        'dynamic_analysis.html',
        metadata=metadata,
        columns_list=columns_list,
        columns_numeric=columns_numeric,
        columns_categorical=columns_categorical,
        preview_rows=preview_rows,
        summary_stats=summary_stats,
        plot_data=plot_data,
        selected_x=selected_x,
        selected_y=selected_y,
        selected_type=selected_type
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
