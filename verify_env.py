import sys
import os

def test_imports():
    print("Checking dependencies...")
    try:
        import flask
        import importlib.metadata
        print(f"  [OK] Flask version: {importlib.metadata.version('flask')}")
    except Exception as e:
        print(f"  [FAIL] Flask: {e}")
        return False
        
    try:
        import numpy as np
        print(f"  [OK] NumPy version: {np.__version__}")
    except ImportError as e:
        print(f"  [FAIL] NumPy: {e}")
        return False

    try:
        import pandas as pd
        print(f"  [OK] Pandas version: {pd.__version__}")
    except ImportError as e:
        print(f"  [FAIL] Pandas: {e}")
        return False

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        print(f"  [OK] Matplotlib version: {matplotlib.__version__}")
    except ImportError as e:
        print(f"  [FAIL] Matplotlib: {e}")
        return False

    try:
        import seaborn as sns
        print(f"  [OK] Seaborn version: {sns.__version__}")
    except ImportError as e:
        print(f"  [FAIL] Seaborn: {e}")
        return False
        
    try:
        import werkzeug
        import importlib.metadata
        print(f"  [OK] Werkzeug version: {importlib.metadata.version('werkzeug')}")
    except Exception as e:
        print(f"  [FAIL] Werkzeug: {e}")
        return False
        
    return True

def test_backend_modules():
    print("\nVerifying database operations...")
    try:
        import database
        database.init_db()
        print("  [OK] SQLite DB initialized successfully.")
    except Exception as e:
        print(f"  [FAIL] database.py execution: {e}")
        return False
        
    print("\nVerifying analytics and data generation...")
    try:
        import analyzer
        df = analyzer.load_data()
        print(f"  [OK] Student dataset loaded. Total records: {len(df)}")
        analyzer.generate_plots()
        print("  [OK] Analysis plots successfully saved in static/images/.")
    except Exception as e:
        print(f"  [FAIL] analyzer.py execution: {e}")
        return False
        
    return True

if __name__ == '__main__':
    print("==================================================")
    print("STUDENT PERFORMANCE ANALYSIS OF AI: ENVIRONMENT TEST")
    print("==================================================")
    
    imports_ok = test_imports()
    if not imports_ok:
        print("\n[ERROR] One or more package imports failed. Please install dependencies.")
        sys.exit(1)
        
    modules_ok = test_backend_modules()
    if not modules_ok:
        print("\n[ERROR] Module verification failed. Please inspect logs.")
        sys.exit(1)
        
    print("\n==================================================")
    print("[SUCCESS] Environment and modules successfully verified!")
    print("You can run 'python app.py' to launch the web dashboard.")
    print("==================================================")
