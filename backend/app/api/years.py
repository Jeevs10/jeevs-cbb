from fastapi import APIRouter
from app.core.data_loader import df

router = APIRouter()

@router.get("/years")
def get_years():
    years = sorted(df["year"].dropna().astype(int).unique().tolist())
    return years