"""
Final working main.py with correct data path resolution.
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

# Simple working endpoints
@app.get("/")
def read_root():
    return {"message": "JEEVS-CBB API is running", "status": "healthy"}

@app.get("/years")
def get_years():
    """Get available years from real CSV data."""
    try:
        # Use absolute path to data directory
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        
        print(f"📂 Looking for data in: {data_dir}")
        
        if not os.path.exists(data_dir):
            return {"years": [], "error": f"Data directory not found: {data_dir}"}
        
        # Load all CSV files
        all_data = []
        years = []
        
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
            return {"years": sorted(years)}
        else:
            return {"years": [], "error": "No CSV files found"}
            
    except Exception as e:
        return {"years": [], "error": f"Failed to load years: {str(e)}"}
    
    return {"years": [2024, 2025, 2026]}

@app.get("/players")
def get_players(limit: int = 50, offset: int = 0, year: int = None):
    """Get players from real CSV data."""
    try:
        # Use absolute path to data directory
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        
        # Load all CSV files
        all_data = []
        years = []
        
        files = os.listdir(data_dir)
        
        for file in files:
            if file.endswith('-players_enriched.csv'):
                year = int(file.split('-')[0])
                years.append(year)
                
                csv_path = os.path.join(data_dir, file)
                df = pd.read_csv(csv_path)
                all_data.append(df)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Filter by year if specified
            if year is not None:
                combined_df = combined_df[combined_df['year'] == year]
            
            # Sort and paginate
            combined_df = combined_df.sort_values('adj_rapm_margin', ascending=False)
            total = len(combined_df)
            
            paginated_df = combined_df.iloc[offset:offset + limit]
            
            return {
                "count": total,
                "filtered_count": len(combined_df),
                "results": paginated_df.replace({pd.na: None}).to_dict('records')
            }
        else:
            return {"error": "No CSV files found", "results": []}
            
    except Exception as e:
        return {"error": f"Failed to load players: {str(e)}", "results": []}

@app.get("/health")
def health_check():
    """Basic health check."""
    return {"status": "healthy", "message": "JEEVS-CBB API is running"}

if __name__ == "__main__":
    import uvicorn
    print("🌐 Starting server on http://localhost:8000")
    print("📊 Using real CSV data files from backend/data/")
    uvicorn.run(app, host="0.0.0.0", port=8000)
