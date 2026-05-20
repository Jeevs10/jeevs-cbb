from typing import List
from fastapi import APIRouter, HTTPException
from app.core.player_resolver import get_player_history
from app.middleware.error_handler import logger
import numpy as np
import pandas as pd

router = APIRouter()

@router.get("/players/{ncaa_id}/history")
def player_history(ncaa_id: str):
    """Get player history across all years."""
    try:
        history = get_player_history(ncaa_id)
        
        if history.empty:
            logger.warning(f"No history found for player: {ncaa_id}")
            return {"history": []}
        
        # Convert to list of dicts, replacing out-of-range float values
        history_list = []
        for _, row in history.iterrows():
            row_dict = {}
            for key, value in row.items():
                # Replace NaN and infinity with None
                if isinstance(value, float):
                    if np.isnan(value) or np.isinf(value):
                        row_dict[key] = None
                    else:
                        row_dict[key] = value
                elif pd.isna(value):
                    row_dict[key] = None
                else:
                    row_dict[key] = value
            history_list.append(row_dict)
        
        return {"history": history_list}
        
    except Exception as e:
        logger.error(f"Error fetching player history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
