# AI-Assisted Student Performance Analytics Dashboard

A premium, dark-themed glassmorphic web dashboard built with Flask and Python data science packages. It simulates and analyzes student academic outcomes in relation to their weekly Generative AI tools utilization patterns (coding assistance, concepts explanation, summaries, etc.), and includes a generic dynamic dataset upload/analysis workspace.

---

## 🌟 Key Features

### 1. Cohort Overview Dashboard
- High-level KPI indicators showing class averages, total cohort size, and AI engagement metrics.
- Correlation coefficients (Pearson's r) mapping study time and AI hours against final exam grades.
- Interactive paginated data grid showing detailed cohort rankings.

### 2. Dynamic Dataset Analyzer & Visual Plotter
- **Arbitrary CSV Ingestion**: Upload *any* tabular CSV file, and view its shape and metadata immediately.
- **Descriptive Statistics**: Auto-detects columns and lists data types, null counts, unique values, mean, min, and max.
- **Interactive Data Preview**: Displays the first 10 rows of the active dataset.
- **Custom Seaborn Charts**: Build dynamic visualizations (Scatter, Line, Bar, Box, and Histograms) on any of the resolved columns.

### 3. Student Cohort Override
- Checks uploaded datasets for a student schema match.
- Toggle **Apply to Global Cohort** to update all dashboards, charts, and metrics with your uploaded dataset.
- Clear/Reset at any time to return to default synthetic data.

### 4. Internship Roadmap
- Interactive 45-day internship planner logging timeline structures, milestones, and documentation logs week-by-week.

### 5. Secure Authentication
- SQLite user DB with password hashing protection.
- Eye visibility toggle for password fields and double-entry validation on registration.
- Smooth top-right sliding toast notifications.

---

## 🛠️ Technology Stack

- **Backend**: Python, Flask, SQLite3, Werkzeug
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Matplotlib, Seaborn
- **Frontend**: HTML5, Vanilla JavaScript, Custom CSS (Glassmorphism & dark gradients)

---

## 🚀 Setup & Execution

### 1. Install Dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 2. Verify Environment & Data Setup
Run the verify script to test packages, build the local SQLite database, and pre-render analytical charts:
```bash
python verify_env.py
```

### 3. Launch Web Server
Start the Flask development server:
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your web browser to explore the dashboard.

---

## 📁 Repository Structure

```text
├── app.py                  # Flask router and route handlers
├── analyzer.py             # Data simulation, stats calculations, and plot renderers
├── database.py             # SQLite user registration/auth database management
├── verify_env.py           # Verification script for dependencies and modules
├── requirements.txt        # Package configuration list
├── data/
│   └── uploads/            # Location for session-isolated uploaded user CSVs
├── static/
│   ├── css/
│   │   └── style.css       # Custom stylesheets (glassmorphism layouts)
│   ├── js/
│   │   └── dashboard.js    # Front-end AJAX interactions and toast animations
│   └── images/             # Rendered analysis charts
└── templates/              # Jinja2 HTML page templates
```
