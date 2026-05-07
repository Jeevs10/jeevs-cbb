"""
Minimal test version to check if basic setup works.
"""

# Test basic imports first
try:
    import fastapi
    import pandas
    import numpy
    print("✅ Basic imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

# Test data layer imports
try:
    from app.data import load_clean_data
    print("✅ Data layer import successful")
except ImportError as e:
    print(f"❌ Data layer import error: {e}")
    exit(1)

# Test if data loads
try:
    df = load_clean_data()
    print(f"✅ Data loaded successfully: {len(df)} rows")
except Exception as e:
    print(f"❌ Data loading error: {e}")
    exit(1)

print("🎉 All tests passed! Ready to start server.")
