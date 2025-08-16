# ModuleNotFoundError Troubleshooting Guide

## Problem Description
The metrics service script is encountering a `ModuleNotFoundError` when trying to import `MetricsService` from `services.metrics_service`. This is a common Python import issue that can have several root causes.

## Root Cause Analysis

### 1. Python Path Issues
The current script uses complex path manipulation that may not work correctly:
```python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'fastapi_backend')))
```

### 2. Import Statement Problems
The script tries to import directly from `services.metrics_service` without properly setting up the module path relative to the analytics-backend directory.

### 3. Missing Dependencies
The script may be missing required dependencies like `schedule` for periodic execution.

## Comprehensive Solution

### Step 1: Fix Python Path Configuration
The script should add the analytics-backend directory to the Python path, not the parent directories:

```python
# Add the analytics-backend directory to Python path
analytics_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, analytics_backend_dir)

# Add fastapi_backend directory for cross-service imports
fastapi_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'fastapi_backend'))
sys.path.insert(0, fastapi_backend_dir)
```

### Step 2: Verify Project Structure
Ensure all directories have proper `__init__.py` files:
```
analytics-service/
└── analytics-backend/
    ├── __init__.py  # May be missing
    ├── services/
    │   ├── __init__.py  # Should exist
    │   └── metrics_service.py
    └── scripts/
        ├── __init__.py  # Should exist
        └── run_metrics_service.py
```

### Step 3: Fix Import Statements
Use relative imports or ensure the module path is correctly configured:

```python
# Option 1: Direct import after fixing path
from services.metrics_service import MetricsService

# Option 2: Absolute import with package name
from analytics_backend.services.metrics_service import MetricsService
```

### Step 4: Install Missing Dependencies
Ensure all required packages are installed:

```bash
pip install schedule sqlalchemy psycopg2-binary python-dotenv
```

### Step 5: Environment Configuration
Create proper environment configuration files and ensure database connections are properly set up.

### Step 6: Virtual Environment Setup
Ensure the script is running in the correct virtual environment with all dependencies installed.

## Testing Steps

1. **Test Python Path Resolution**:
   ```python
   import sys
   print("Python path:", sys.path)
   print("Current working directory:", os.getcwd())
   ```

2. **Test Module Import**:
   ```python
   try:
       from services.metrics_service import MetricsService
       print("Import successful")
   except ImportError as e:
       print(f"Import failed: {e}")
   ```

3. **Test Database Connections**:
   ```python
   # Test both database connections
   metrics_service = MetricsService()
   print("Database connections established")
   ```

## Alternative Solutions

### Option 1: Use setuptools for Package Installation
Create a `setup.py` file to install the analytics-backend as a proper Python package.

### Option 2: Use PYTHONPATH Environment Variable
Set the PYTHONPATH environment variable to include the analytics-backend directory:
```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/analytics-service/analytics-backend"
```

### Option 3: Use Relative Imports
Restructure the code to use relative imports within the package.

## Implementation Plan

1. **Fix the run_metrics_service.py script** with correct path configuration
2. **Add missing __init__.py files** if needed
3. **Update the metrics_service.py** to handle imports correctly
4. **Create a requirements.txt** with all dependencies
5. **Test the implementation** step by step
6. **Update documentation** with correct setup instructions

## Next Steps

Switch to Code mode to implement these fixes in the actual Python files.