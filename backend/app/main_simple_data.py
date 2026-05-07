"""
Simple working main.py that uses actual CSV data files.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pandas as pd
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for startup/shutdown."""
    print("🚀 Starting JEEVS-CBB API with real data...")
    yield
    print("👋 Shutting down JEEVS-CBB API")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple data loading
def load_real_data():
    """Load real data from CSV files."""
    try:
        # Get absolute path to data directory  
        current_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(current_dir, 'data')
        
        print(f"📂 Looking for data in: {data_dir}")
        
        # Load all CSV files
        all_data = []
        years = []
        
        if os.path.exists(data_dir):
            files = os.listdir(data_dir)
            print(f"📁 Found files: {files}")
            
            for file in files:
                if file.endswith('-players_enriched.csv'):
                    year = int(file.split('-')[0])
                    years.append(year)
                    
                    csv_path = os.path.join(data_dir, file)
                    print(f"📖 Loading: {csv_path}")
                    df = pd.read_csv(csv_path)
                    all_data.append(df)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            print(f"📊 Loaded {len(combined_df)} rows from {len(years)} years")
            return combined_df, years
        else:
            print(f"❌ Data directory not found: {data_dir}")
            return pd.DataFrame(), []
    
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return pd.DataFrame(), []

# Basic endpoints
@app.get("/")
def read_root():
    return {"message": "JEEVS-CBB API is running", "status": "healthy"}

@app.get("/years")
def get_years():
    """Get available years from real data."""
    try:
        df, years = load_real_data()
        return {"years": years}
    except Exception as e:
        return {"error": f"Failed to load years: {str(e)}", "years": []}

@app.get("/players")
def get_players(limit: int = 50, offset: int = 0, year: int = None):
    """Get players from real data."""
    try:
        df, _ = load_real_data()
        
        # Filter by year if specified
        if year is not None:
            df = df[df['year'] == year]
        
        # Sort and paginate
        df = df.sort_values('adj_rapm_margin', ascending=False)
        total = len(df)
        
        paginated_df = df.iloc[offset:offset + limit]
        
        return {
            "count": total,
            "filtered_count": len(df),
            "results": paginated_df.replace({pd.na: None}).to_dict('records')
        }
    except Exception as e:
        return {"error": f"Failed to load players: {str(e)}", "results": []}

@app.get("/health")
def health_check():
    """Basic health check."""
    return {"status": "healthy", "message": "JEEVS-CBB API is running"}

if __name__ == "__main__":
    import uvicorn
    print("🌐 Starting server on http://localhost:8000")
    print("📊 Using real CSV data files")
    uvicorn.run(app, host="0.0.0.0", port=8000)
