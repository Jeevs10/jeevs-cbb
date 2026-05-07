"""
Data Loader Module
Handles reading raw data files and initial data loading.
"""

import os
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

from .schema import DataContract, COLUMN_MAPPINGS


class DataLoader:
    """
    Handles loading of raw CSV data files.
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the data loader.
        
        Args:
            base_dir: Base directory for data files. If None, uses default.
        """
        if base_dir is None:
            # Default to backend/data directory
            current_dir = os.path.dirname(os.path.dirname(__file__))
            self.base_dir = os.path.join(current_dir, '..', 'data')
        else:
            self.base_dir = base_dir
    
    def load_year_data(self, year: int) -> pd.DataFrame:
        """
        Load data for a specific year.
        
        Args:
            year: Year to load (2024, 2025, 2026)
            
        Returns:
            DataFrame with raw data for the specified year
        """
        csv_path = os.path.join(self.base_dir, f"{year}-players_enriched.csv")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Data file not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        
        # Add year column if not present
        if 'year' not in df.columns:
            df['year'] = year
        
        return df
    
    def load_all_years(self, years: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Load data for multiple years.
        
        Args:
            years: List of years to load. If None, loads all available years.
            
        Returns:
            Combined DataFrame with data for all specified years
        """
        if years is None:
            years = [2024, 2025, 2026]
        
        dataframes = []
        
        for year in years:
            try:
                df = self.load_year_data(year)
                dataframes.append(df)
            except FileNotFoundError:
                print(f"Warning: Data file for year {year} not found, skipping...")
                continue
        
        if not dataframes:
            raise ValueError("No data files found for any year")
        
        # Combine all dataframes
        combined_df = pd.concat(dataframes, ignore_index=True)
        
        return combined_df
    
    def get_available_years(self) -> List[int]:
        """
        Get list of available years based on existing files.
        
        Returns:
            List of available years
        """
        available_years = []
        
        for year in [2024, 2025, 2026]:
            csv_path = os.path.join(self.base_dir, f"{year}-players_enriched.csv")
            if os.path.exists(csv_path):
                available_years.append(year)
        
        return available_years
    
    def validate_data_files(self) -> Dict[int, bool]:
        """
        Check which data files exist and are readable.
        
        Returns:
            Dictionary mapping year to file status
        """
        status = {}
        
        for year in [2024, 2025, 2026]:
            csv_path = os.path.join(self.base_dir, f"{year}-players_enriched.csv")
            
            if os.path.exists(csv_path):
                try:
                    # Try to read first few rows to verify file integrity
                    pd.read_csv(csv_path, nrows=5)
                    status[year] = True
                except Exception:
                    status[year] = False
            else:
                status[year] = False
        
        return status


# Global loader instance
_loader = DataLoader()


def load_players(years: Optional[List[int]] = None) -> pd.DataFrame:
    """
    Convenience function to load player data.
    
    Args:
        years: List of years to load. If None, loads all available years.
        
    Returns:
        Combined DataFrame with player data
    """
    return _loader.load_all_years(years)


def get_available_years() -> List[int]:
    """
    Convenience function to get available years.
    
    Returns:
        List of available years
    """
    return _loader.get_available_years()


def validate_data_files() -> Dict[int, bool]:
    """
    Convenience function to validate data files.
    
    Returns:
        Dictionary mapping year to file status
    """
    return _loader.validate_data_files()
