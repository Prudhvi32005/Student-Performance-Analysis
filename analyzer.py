import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Set paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STATIC_IMAGES_DIR = os.path.join(BASE_DIR, 'static', 'images')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, 'student_ai_data.csv')

def generate_data(num_students=200):
    """
    Generates a realistic synthetic dataset representing student AI tool usage and grades.
    Incorporates a non-linear relationship: moderate usage improves grades,
    but excessive usage (over-reliance) results in a performance drop.
    """
    np.random.seed(42)
    
    student_ids = [f"STU{i:03d}" for i in range(1, num_students + 1)]
    
    first_names = ["Arjun", "Aditya", "Neha", "Priya", "Rahul", "Anjali", "Siddharth", "Ishita", "Vikram", "Rohan",
                   "Aarav", "Zara", "Kabir", "Diya", "Reyansh", "Kiara", "Vihaan", "Aanya", "Dev", "Meera"]
    last_names = ["Sharma", "Verma", "Gupta", "Patel", "Mehta", "Reddy", "Rao", "Nair", "Singh", "Joshi",
                  "Kumar", "Choudhury", "Bose", "Das", "Sen", "Iyer", "Kulkarni", "Deshmukh", "Nair", "Pillai"]
    
    names = [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(num_students)]
    
    # Generate study hours (normal distribution around 10 hours)
    study_hours = np.random.normal(10, 3, num_students).clip(2, 22)
    
    # Generate Prior GPA (normal distribution centered around 3.1)
    prior_gpa = np.random.normal(3.1, 0.4, num_students).clip(2.0, 4.0)
    
    # AI Tool Usage Hours (exponential or mixture: some don't use, some moderate, some high)
    ai_hours = np.random.exponential(6, num_students)
    ai_hours = np.clip(ai_hours, 0, 25) # Max 25 hours
    
    # AI Prompt count (correlated with AI hours)
    prompt_count = (ai_hours * np.random.normal(5, 1, num_students)).clip(0)
    
    # Attendance Rate (skewed towards higher values)
    attendance = np.random.beta(8, 2, num_students) * 100
    attendance = np.clip(attendance, 50, 100)
    
    # Categorize AI Usage Types
    usage_types = ["Coding Assistance", "Concept Explanations", "Summarization", "Grammar & Writing"]
    ai_usage_type = []
    for h in ai_hours:
        if h < 1.0:
            ai_usage_type.append("No Usage")
        else:
            ai_usage_type.append(np.random.choice(usage_types))
            
    # Calculate Subject Scores with custom dependencies
    math_scores = []
    science_scores = []
    english_scores = []
    coding_scores = []
    
    for i in range(num_students):
        attendance_mod = (attendance[i] - 75) * 0.2
        h = ai_hours[i]
        
        # AI effect: positive up to 12 hours, penalty after
        if h <= 12:
            ai_factor = h * 1.5
            ai_factor_coding = h * 2.0
            ai_factor_english = h * 1.2
        else:
            ai_factor = (12 * 1.5) - ((h - 12) * 1.6)
            ai_factor_coding = (12 * 2.0) - ((h - 12) * 2.2)
            ai_factor_english = (12 * 1.2) - ((h - 12) * 1.4)
            
        # Math Score
        m_noise = np.random.normal(0, 5)
        m_base = 40 + (prior_gpa[i] * 10) + (study_hours[i] * 0.6) + attendance_mod
        m_ai = ai_factor * 1.1 if ai_usage_type[i] in ["Concept Explanations", "Coding Assistance"] else ai_factor * 0.4
        math_scores.append(np.clip(m_base + m_ai + m_noise, 30, 100))
        
        # Science Score
        s_noise = np.random.normal(0, 4.5)
        s_base = 38 + (prior_gpa[i] * 11) + (study_hours[i] * 0.7) + attendance_mod
        s_ai = ai_factor * 1.2 if ai_usage_type[i] == "Concept Explanations" else ai_factor * 0.5
        science_scores.append(np.clip(s_base + s_ai + s_noise, 30, 100))
        
        # English Score
        e_noise = np.random.normal(0, 4)
        e_base = 45 + (prior_gpa[i] * 9) + (study_hours[i] * 0.5) + attendance_mod
        e_ai = ai_factor_english * 1.4 if ai_usage_type[i] in ["Grammar & Writing", "Summarization"] else ai_factor_english * 0.3
        english_scores.append(np.clip(e_base + e_ai + e_noise, 35, 100))
        
        # Coding Score
        c_noise = np.random.normal(0, 6)
        c_base = 32 + (prior_gpa[i] * 12) + (study_hours[i] * 0.8) + attendance_mod
        c_ai = ai_factor_coding * 1.5 if ai_usage_type[i] == "Coding Assistance" else ai_factor_coding * 0.3
        coding_scores.append(np.clip(c_base + c_ai + c_noise, 30, 100))
        
    math_scores = np.round(math_scores, 1)
    science_scores = np.round(science_scores, 1)
    english_scores = np.round(english_scores, 1)
    coding_scores = np.round(coding_scores, 1)
    
    # Calculate Overall Exam Score (Percentage)
    final_scores = np.round((math_scores + science_scores + english_scores + coding_scores) / 4, 1)
    
    # Calculate Grades
    grades = []
    for score in final_scores:
        if score >= 90:
            grades.append("A+")
        elif score >= 80:
            grades.append("A")
        elif score >= 70:
            grades.append("B")
        elif score >= 60:
            grades.append("C")
        elif score >= 50:
            grades.append("D")
        else:
            grades.append("F")
            
    df = pd.DataFrame({
        'Student_ID': student_ids,
        'Name': names,
        'Study_Hours_Weekly': np.round(study_hours, 1),
        'Prior_GPA': np.round(prior_gpa, 2),
        'Attendance_Rate': np.round(attendance, 1),
        'AI_Usage_Hours_Weekly': np.round(ai_hours, 1),
        'AI_Prompts_Count_Weekly': np.round(prompt_count, 0).astype(int),
        'AI_Usage_Type': ai_usage_type,
        'Math_Score': math_scores,
        'Science_Score': science_scores,
        'English_Score': english_scores,
        'Coding_Score': coding_scores,
        'Final_Exam_Score': final_scores,
        'Grade': grades
    })
    
    # Calculate Class Rank based on Final Exam Score descending
    df['Rank'] = df['Final_Exam_Score'].rank(ascending=False, method='min').astype(int)
    
    df.to_csv(CSV_PATH, index=False)
    return df

def load_data(filepath=None):
    """Loads student data, generating it first if missing. Resolves path from session if available."""
    if filepath is None:
        try:
            from flask import session as flask_session
            if flask_session and 'data_file' in flask_session:
                filepath = flask_session['data_file']
        except Exception:
            pass
            
    if filepath is None or not os.path.exists(filepath):
        filepath = CSV_PATH
        
    if not os.path.exists(filepath):
        return generate_data()
    return pd.read_csv(filepath)

def get_default_statistics():
    """Returns a default stats dictionary to prevent template rendering crashes."""
    return {
        'total_students': 0,
        'avg_gpa': 0.0,
        'avg_exam_score': 0.0,
        'avg_ai_hours': 0.0,
        'correlation_score_ai': 0.0,
        'correlation_score_study': 0.0,
        'category_counts': {},
        'cat_avg_scores': {},
        'subject_averages': {'Math': 0.0, 'Science': 0.0, 'English': 0.0, 'Coding': 0.0},
        'highest_scorers': {
            'Math': {'name': 'N/A', 'score': 0.0, 'id': 'N/A'},
            'Science': {'name': 'N/A', 'score': 0.0, 'id': 'N/A'},
            'English': {'name': 'N/A', 'score': 0.0, 'id': 'N/A'},
            'Coding': {'name': 'N/A', 'score': 0.0, 'id': 'N/A'}
        },
        'difficult_subject': {'name': 'N/A', 'average': 0.0},
        'top_performers': [],
        'weak_performers': []
    }

def get_statistics():
    """Computes high-level descriptive statistics from the dataset."""
    df = load_data()
    
    stats = {
        'total_students': len(df),
        'avg_gpa': round(df['Prior_GPA'].mean(), 2),
        'avg_exam_score': round(df['Final_Exam_Score'].mean(), 1),
        'avg_ai_hours': round(df['AI_Usage_Hours_Weekly'].mean(), 1),
        'correlation_score_ai': round(df['Final_Exam_Score'].corr(df['AI_Usage_Hours_Weekly']), 3),
        'correlation_score_study': round(df['Final_Exam_Score'].corr(df['Study_Hours_Weekly']), 3),
    }
    
    # AI usage categories distribution
    category_counts = df['AI_Usage_Type'].value_counts().to_dict()
    stats['category_counts'] = category_counts
    
    # Average score per category
    cat_avg_scores = df.groupby('AI_Usage_Type')['Final_Exam_Score'].mean().round(1).to_dict()
    stats['cat_avg_scores'] = cat_avg_scores
    
    # Subject-wise Averages
    subject_averages = {
        'Math': round(df['Math_Score'].mean(), 1),
        'Science': round(df['Science_Score'].mean(), 1),
        'English': round(df['English_Score'].mean(), 1),
        'Coding': round(df['Coding_Score'].mean(), 1)
    }
    stats['subject_averages'] = subject_averages
    
    # Highest Scorer in each subject
    stats['highest_scorers'] = {
        'Math': {
            'name': df.loc[df['Math_Score'].idxmax()]['Name'],
            'score': df['Math_Score'].max(),
            'id': df.loc[df['Math_Score'].idxmax()]['Student_ID']
        },
        'Science': {
            'name': df.loc[df['Science_Score'].idxmax()]['Name'],
            'score': df['Science_Score'].max(),
            'id': df.loc[df['Science_Score'].idxmax()]['Student_ID']
        },
        'English': {
            'name': df.loc[df['English_Score'].idxmax()]['Name'],
            'score': df['English_Score'].max(),
            'id': df.loc[df['English_Score'].idxmax()]['Student_ID']
        },
        'Coding': {
            'name': df.loc[df['Coding_Score'].idxmax()]['Name'],
            'score': df['Coding_Score'].max(),
            'id': df.loc[df['Coding_Score'].idxmax()]['Student_ID']
        }
    }
    
    # Difficult Subject identification (the subject with lowest average)
    difficult_subject = min(subject_averages, key=subject_averages.get)
    stats['difficult_subject'] = {
        'name': difficult_subject,
        'average': subject_averages[difficult_subject]
    }
    
    # Class Performance: Top 5 and Bottom 5 performers
    top_5 = df.sort_values(by='Final_Exam_Score', ascending=False).head(5)
    bottom_5 = df.sort_values(by='Final_Exam_Score', ascending=True).head(5)
    
    stats['top_performers'] = top_5[['Student_ID', 'Name', 'Final_Exam_Score', 'Grade', 'Rank']].to_dict(orient='records')
    stats['weak_performers'] = bottom_5[['Student_ID', 'Name', 'Final_Exam_Score', 'Grade', 'Rank']].to_dict(orient='records')
    
    return stats

def generate_plots():
    """Generates analytical charts using Matplotlib/Seaborn and saves them in static/images."""
    df = load_data()
    
    # Set aesthetics styling
    sns.set_theme(style="darkgrid")
    plt.rcParams['figure.facecolor'] = '#151c2c'
    plt.rcParams['axes.facecolor'] = '#1b253b'
    plt.rcParams['text.color'] = '#e2e8f0'
    plt.rcParams['axes.labelcolor'] = '#cbd5e1'
    plt.rcParams['xtick.color'] = '#94a3b8'
    plt.rcParams['ytick.color'] = '#94a3b8'
    plt.rcParams['grid.color'] = '#334155'
    
    # 1. Distribution of Final Exam Scores
    plt.figure(figsize=(8, 5))
    sns.histplot(df['Final_Exam_Score'], kde=True, color='#6366f1', edgecolor='#1e1b4b', linewidth=1.5)
    plt.title('Distribution of Student Final Exam Scores', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
    plt.xlabel('Final Exam Score', fontsize=12)
    plt.ylabel('Count of Students', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_IMAGES_DIR, 'grade_distribution.png'), dpi=150, facecolor='#151c2c')
    plt.close()
    
    # 2. AI Usage Hours vs Final Exam Score (Non-linear Scatter + Trendline)
    plt.figure(figsize=(9, 5.5))
    # Draw scatter with color coding usage type
    sns.scatterplot(
        data=df, 
        x='AI_Usage_Hours_Weekly', 
        y='Final_Exam_Score', 
        hue='AI_Usage_Type', 
        palette='hls',
        s=70, 
        alpha=0.85,
        edgecolor='#0f172a',
        linewidth=0.8
    )
    # Fit a 2nd-degree polynomial line to show the non-linear trend (boost then drop)
    x_sorted = np.sort(df['AI_Usage_Hours_Weekly'].values)
    poly_fit = np.polyfit(df['AI_Usage_Hours_Weekly'], df['Final_Exam_Score'], 2)
    poly_val = np.polyval(poly_fit, x_sorted)
    plt.plot(x_sorted, poly_val, color='#f43f5e', linewidth=2.5, label='Performance Trendline (Quadratic)')
    
    plt.title('AI Tool Usage vs Final Exam Score', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
    plt.xlabel('AI Tool Usage (Hours/Week)', fontsize=12)
    plt.ylabel('Final Exam Score', fontsize=12)
    plt.legend(facecolor='#1e293b', edgecolor='#475569', labelcolor='#e2e8f0')
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_IMAGES_DIR, 'ai_usage_vs_score.png'), dpi=150, facecolor='#151c2c')
    plt.close()
    
    # 3. Correlation Heatmap
    plt.figure(figsize=(7, 5))
    numeric_cols = ['Study_Hours_Weekly', 'Prior_GPA', 'Attendance_Rate', 'AI_Usage_Hours_Weekly', 'AI_Prompts_Count_Weekly', 'Final_Exam_Score']
    corr_matrix = df[numeric_cols].corr()
    
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool)) # Mask upper triangle
    
    sns.heatmap(
        corr_matrix, 
        mask=mask,
        annot=True, 
        fmt='.2f', 
        cmap='coolwarm', 
        center=0,
        cbar_kws={'shrink': .8},
        square=True,
        linewidths=.5,
        annot_kws={"size": 10}
    )
    plt.title('Correlation Matrix of Student Metrics', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_IMAGES_DIR, 'correlation_heatmap.png'), dpi=150, facecolor='#151c2c')
    plt.close()
    
    # 4. Boxplot: Performance across AI Usage Categories
    plt.figure(figsize=(9, 5))
    # Order categories
    cat_order = ["No Usage", "Summarization", "Grammar & Writing", "Concept Explanations", "Coding Assistance"]
    # Filter only available ones to prevent key errors
    available_cats = [c for c in cat_order if c in df['AI_Usage_Type'].unique()]
    
    sns.boxplot(
        data=df, 
        x='AI_Usage_Type', 
        y='Final_Exam_Score', 
        hue='AI_Usage_Type',
        order=available_cats,
        palette='Set2',
        legend=False,
        linewidth=1.5
    )
    # Add swarmplot overlay to show points
    sns.swarmplot(
        data=df, 
        x='AI_Usage_Type', 
        y='Final_Exam_Score', 
        order=available_cats,
        color='#ffffff', 
        size=4, 
        alpha=0.6
    )
    
    plt.title('Student Performance Distribution by AI Tool Category', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
    plt.xlabel('Primary AI Usage Type', fontsize=12)
    plt.ylabel('Final Exam Score', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(STATIC_IMAGES_DIR, 'ai_type_performance.png'), dpi=150, facecolor='#151c2c')
    plt.close()
    
    print("Analytics charts successfully generated and saved to static/images/.")

def generate_custom_plot(x_col, y_col=None, plot_type='scatter'):
    """
    Generates a user-configured plot dynamically and returns it as a Base64-encoded PNG string.
    """
    import io
    import base64
    
    df = load_data()
    
    # Set aesthetics styling to match the site design
    sns.set_theme(style="darkgrid")
    plt.figure(figsize=(9, 5.5))
    plt.rcParams['figure.facecolor'] = '#151c2c'
    plt.rcParams['axes.facecolor'] = '#1b253b'
    plt.rcParams['text.color'] = '#e2e8f0'
    plt.rcParams['axes.labelcolor'] = '#cbd5e1'
    plt.rcParams['xtick.color'] = '#94a3b8'
    plt.rcParams['ytick.color'] = '#94a3b8'
    plt.rcParams['grid.color'] = '#334155'
    
    title_x = x_col.replace('_', ' ')
    title_y = y_col.replace('_', ' ') if y_col else ''
    
    if plot_type == 'scatter' and y_col:
        # Check if we should color by AI category
        hue_col = 'AI_Usage_Type' if 'AI_Usage_Type' in df.columns and x_col != 'AI_Usage_Type' and y_col != 'AI_Usage_Type' else None
        sns.scatterplot(
            data=df, 
            x=x_col, 
            y=y_col, 
            hue=hue_col, 
            palette='hls' if hue_col else None,
            s=70, 
            alpha=0.85,
            edgecolor='#0f172a',
            linewidth=0.8
        )
        plt.title(f'{title_y} vs {title_x}', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
        if hue_col:
            plt.legend(facecolor='#1e293b', edgecolor='#475569', labelcolor='#e2e8f0')
            
    elif plot_type == 'bar' and y_col:
        # Compute mean value for clean bar plots
        if df[x_col].dtype == object or len(df[x_col].unique()) < 10:
            grouped = df.groupby(x_col)[y_col].mean().reset_index()
            sns.barplot(
                data=grouped, 
                x=x_col, 
                y=y_col, 
                hue=x_col,
                palette='Set2', 
                legend=False
            )
            plt.title(f'Average {title_y} by {title_x}', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
        else:
            sns.barplot(
                data=df, 
                x=x_col, 
                y=y_col, 
                hue=x_col,
                palette='coolwarm', 
                legend=False
            )
            plt.title(f'{title_y} by {title_x}', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
            
    elif plot_type == 'box' and y_col:
        sns.boxplot(
            data=df, 
            x=x_col, 
            y=y_col, 
            hue=x_col,
            palette='Set2',
            legend=False,
            linewidth=1.5
        )
        plt.title(f'Distribution of {title_y} across {title_x}', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
        
    elif plot_type == 'hist':
        sns.histplot(df[x_col], kde=True, color='#6366f1', edgecolor='#1e1b4b', linewidth=1.5)
        plt.title(f'Distribution of {title_x}', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
        plt.ylabel('Frequency')
        
    else:
        # Fallback empty plot with error message
        plt.text(0.5, 0.5, "Invalid Plot Configuration\nSelect correct columns & plot types", 
                 ha='center', va='center', color='#f43f5e', fontsize=14, fontweight='bold')
        plt.title('Plot Configuration Error', fontsize=14, color='#f43f5e', pad=15)
        
    plt.xlabel(title_x, fontsize=12)
    if y_col and plot_type != 'hist':
        plt.ylabel(title_y, fontsize=12)
        
    plt.tight_layout()
    
    # Save to dynamic buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='#151c2c', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64

def generate_student_comparison_chart(student_id):
    """
    Generates a bar plot comparing a specific student's scores in Math, Science, English, 
    and Coding with the overall class averages. Returns the plot as a Base64 string.
    """
    import io
    import base64
    
    df = load_data()
    student_row = df[df['Student_ID'] == student_id]
    
    if student_row.empty:
        return None
        
    student_data = student_row.iloc[0]
    
    # Define subjects and collect scores
    subjects = ['Math', 'Science', 'English', 'Coding']
    student_scores = [
        student_data['Math_Score'],
        student_data['Science_Score'],
        student_data['English_Score'],
        student_data['Coding_Score']
    ]
    
    class_averages = [
        df['Math_Score'].mean(),
        df['Science_Score'].mean(),
        df['English_Score'].mean(),
        df['Coding_Score'].mean()
    ]
    
    # Build data structure for plotting
    plot_df = pd.DataFrame({
        'Subject': subjects * 2,
        'Score': student_scores + class_averages,
        'Group': ["Student's Score"] * 4 + ["Class Average"] * 4
    })
    
    # Set aesthetics styling to match the site design
    sns.set_theme(style="darkgrid")
    plt.figure(figsize=(7, 4.5))
    plt.rcParams['figure.facecolor'] = '#151c2c'
    plt.rcParams['axes.facecolor'] = '#1b253b'
    plt.rcParams['text.color'] = '#e2e8f0'
    plt.rcParams['axes.labelcolor'] = '#cbd5e1'
    plt.rcParams['xtick.color'] = '#94a3b8'
    plt.rcParams['ytick.color'] = '#94a3b8'
    plt.rcParams['grid.color'] = '#334155'
    
    sns.barplot(
        data=plot_df,
        x='Subject',
        y='Score',
        hue='Group',
        palette=['#6366f1', '#a855f7']
    )
    
    plt.title(f"{student_data['Name']}'s Performance vs Class Average", fontsize=12, color='#f8fafc', pad=15, fontweight='bold')
    plt.xlabel('Subjects', fontsize=10)
    plt.ylabel('Score (%)', fontsize=10)
    plt.ylim(0, 105)
    plt.legend(facecolor='#1e293b', edgecolor='#475569', labelcolor='#e2e8f0')
    
    plt.tight_layout()
    
    # Save to dynamic buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='#151c2c', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64

def validate_student_schema(df):
    """
    Checks if an uploaded DataFrame has the required columns to function as the cohort dataset.
    """
    required_columns = ['Student_ID', 'Name', 'Final_Exam_Score', 'AI_Usage_Hours_Weekly', 'Prior_GPA', 'Grade', 'Rank']
    # Let's check for a subset of essential columns to be flexible, but let them all exist if possible
    # We can also compute Rank and Grade if they are missing! Let's check for:
    essential_columns = ['Student_ID', 'Name', 'Final_Exam_Score', 'AI_Usage_Hours_Weekly']
    return all(col in df.columns for col in essential_columns)

def generate_dynamic_plot(filepath, x_col, y_col=None, plot_type='scatter'):
    """
    Generates a Seaborn visualization plot dynamically from any CSV filepath and column names.
    Returns a Base64-encoded PNG string.
    """
    import io
    import base64
    
    df = pd.read_csv(filepath)
    
    # Set aesthetics styling to match the site design
    sns.set_theme(style="darkgrid")
    plt.figure(figsize=(9, 5.5))
    plt.rcParams['figure.facecolor'] = '#151c2c'
    plt.rcParams['axes.facecolor'] = '#1b253b'
    plt.rcParams['text.color'] = '#e2e8f0'
    plt.rcParams['axes.labelcolor'] = '#cbd5e1'
    plt.rcParams['xtick.color'] = '#94a3b8'
    plt.rcParams['ytick.color'] = '#94a3b8'
    plt.rcParams['grid.color'] = '#334155'
    
    title_x = str(x_col).replace('_', ' ')
    title_y = str(y_col).replace('_', ' ') if y_col else ''
    
    try:
        if plot_type == 'scatter' and y_col:
            sns.scatterplot(
                data=df, 
                x=x_col, 
                y=y_col, 
                s=70, 
                alpha=0.85,
                color='#6366f1',
                edgecolor='#0f172a',
                linewidth=0.8
            )
            plt.title(f'{title_y} vs {title_x}', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
                
        elif plot_type == 'line' and y_col:
            # Sort X axis for clean line drawing if it's numeric
            if np.issubdtype(df[x_col].dtype, np.number):
                sorted_df = df.sort_values(by=x_col)
            else:
                sorted_df = df
            sns.lineplot(
                data=sorted_df, 
                x=x_col, 
                y=y_col, 
                color='#a855f7',
                linewidth=2.5
            )
            plt.title(f'{title_y} over {title_x}', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
                
        elif plot_type == 'bar' and y_col:
            if df[x_col].nunique() < 25:
                # If category count is small, draw average grouped bar plot
                grouped = df.groupby(x_col)[y_col].mean().reset_index()
                sns.barplot(
                    data=grouped, 
                    x=x_col, 
                    y=y_col, 
                    hue=x_col,
                    palette='Set2', 
                    legend=False
                )
                plt.title(f'Average {title_y} by {title_x}', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
            else:
                sns.barplot(
                    data=df, 
                    x=x_col, 
                    y=y_col, 
                    palette='coolwarm',
                    legend=False
                )
                plt.title(f'{title_y} by {title_x}', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
                
        elif plot_type == 'box' and y_col:
            sns.boxplot(
                data=df, 
                x=x_col, 
                y=y_col, 
                hue=x_col,
                palette='Set2',
                legend=False,
                linewidth=1.5
            )
            plt.title(f'Distribution of {title_y} across {title_x}', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            
        elif plot_type == 'hist':
            sns.histplot(df[x_col], kde=True, color='#6366f1', edgecolor='#1e1b4b', linewidth=1.5)
            plt.title(f'Distribution of {title_x}', fontsize=14, color='#f8fafc', pad=15, fontweight='bold')
            plt.ylabel('Frequency')
            
        else:
            plt.text(0.5, 0.5, "Invalid Plot Configuration\nSelect valid columns & plot types", 
                     ha='center', va='center', color='#f43f5e', fontsize=14, fontweight='bold')
            plt.title('Plot Configuration Error', fontsize=14, color='#f43f5e', pad=15)
            
    except Exception as e:
        plt.text(0.5, 0.5, f"Error rendering plot:\n{str(e)}", 
                 ha='center', va='center', color='#f43f5e', fontsize=10, fontweight='bold')
        plt.title('Plotting Error', fontsize=14, color='#f43f5e', pad=15)
        
    plt.xlabel(title_x, fontsize=12)
    if y_col and plot_type != 'hist':
        plt.ylabel(title_y, fontsize=12)
        
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='#151c2c', bbox_inches='tight', dpi=150)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64


if __name__ == '__main__':
    # Test block
    generate_data()
    generate_plots()
    print("Module ran successfully. High-level stats:")
    print(get_statistics())
