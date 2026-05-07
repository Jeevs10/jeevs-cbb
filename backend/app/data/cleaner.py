"""
Data Cleaner Module
Handles data normalization, ID cleaning, and consistency enforcement.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

from .schema import (
    COLUMN_MAPPINGS, 
    CATEGORICAL_FIELDS,
    PERCENTAGE_COLUMNS,
    SchemaValidator
)


class DataCleaner:
    """
    Handles data cleaning and normalization.
    """
    
    @staticmethod
    def clean_player_id(x: Any) -> Optional[str]:
        """
        Clean player ID (roster.ncaa_id) to ensure consistency.
        
        Args:
            x: Raw player ID value
            
        Returns:
            Cleaned player ID as string, or None if invalid
        """
        if pd.isna(x):
            return None
        
        # Convert to string and clean
        cleaned = str(x).replace(".0", "").strip()
        
        # Return None if empty after cleaning
        if not cleaned:
            return None
        
        return cleaned
    
    @staticmethod
    def clean_year(x: Any) -> Optional[int]:
        """
        Clean year values to ensure consistency.
        
        Args:
            x: Raw year value
            
        Returns:
            Cleaned year as integer, or None if invalid
        """
        if pd.isna(x):
            return None
        
        try:
            x = str(x)
            
            # Handle format like "2023/2024" -> 2024
            if "/" in x:
                return int(x.split("/")[-1]) + 2000
            
            # Handle numeric strings
            return int(float(x))
            
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names according to the data contract.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with normalized column names
        """
        df = df.copy()
        
        # Apply column mappings
        df = df.rename(columns=COLUMN_MAPPINGS)
        
        return df
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all cleaning operations to a DataFrame.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        
        # Normalize column names first
        df = DataCleaner.normalize_column_names(df)
        
        # Clean player_id
        if 'player_id' in df.columns:
            df['player_id'] = df['player_id'].apply(DataCleaner.clean_player_id)
        
        # Clean year
        if 'year' in df.columns:
            df['year'] = df['year'].apply(DataCleaner.clean_year)
        
        # Remove rows with null primary keys
        if 'player_id' in df.columns and 'year' in df.columns:
            df = df.dropna(subset=['player_id', 'year'])
        
        # Ensure proper data types
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)
        
        # Remove duplicate (player_id, year) pairs
        if 'player_id' in df.columns and 'year' in df.columns:
            df = df.drop_duplicates(subset=['player_id', 'year'], keep='last')
        
        return df
    
    @staticmethod
    def validate_and_report(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate DataFrame against schema and return validation report.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Validation report with errors and statistics
        """
        validator = SchemaValidator()
        
        # Run all validations
        primary_key_errors = validator.validate_primary_keys(df)
        schema_errors = validator.validate_schema_consistency(df)
        integrity_errors = validator.validate_data_integrity(df)
        
        all_errors = primary_key_errors + schema_errors + integrity_errors
        
        return {
            'is_valid': len(all_errors) == 0,
            'error_count': len(all_errors),
            'errors': all_errors,
            'row_count': len(df),
            'unique_players': df['player_id'].nunique() if 'player_id' in df.columns else 0,
            'year_range': {
                'min': int(df['year'].min()) if 'year' in df.columns and not df['year'].empty else None,
                'max': int(df['year'].max()) if 'year' in df.columns and not df['year'].empty else None,
            }
        }
    
    @staticmethod
    def prepare_for_display(df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare DataFrame for frontend display (convert percentages, etc.).
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame prepared for display
        """
        df = df.copy()
        
        # Convert percentage columns to percentages (multiply by 100)
        for col in PERCENTAGE_COLUMNS:
            if col in df.columns:
                df[col] = df[col] * 100
        
        # Replace NaN with None for JSON serialization
        df = df.replace({np.nan: None})
        
        return df


# Global cleaner instance
_cleaner = DataCleaner()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function to clean data.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    return _cleaner.clean_dataframe(df)


def validate_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to validate data.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Validation report
    """
    return _cleaner.validate_and_report(df)


def prepare_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function to prepare data for display.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame prepared for display
    """
    return _cleaner.prepare_for_display(df)
