"""
Data Integrity Module
Handles data validation, assertions, and consistency checks.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataIntegrityError(Exception):
    """Custom exception for data integrity violations."""
    pass


class DataValidator:
    """
    Comprehensive data validation and integrity checking.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.errors = []
        self.warnings = []
    
    def validate_primary_keys(self) -> bool:
        """
        Validate primary key constraints.
        
        Returns:
            True if valid, False otherwise
        """
        is_valid = True
        
        # Check for null player_id
        null_player_ids = self.df[self.df['player_id'].isna()]
        if not null_player_ids.empty:
            self.errors.append(f"Found {len(null_player_ids)} rows with null player_id")
            is_valid = False
        
        # Check for null year
        null_years = self.df[self.df['year'].isna()]
        if not null_years.empty:
            self.errors.append(f"Found {len(null_years)} rows with null year")
            is_valid = False
        
        # Check for duplicate (player_id, year) pairs
        duplicates = self.df.duplicated(subset=['player_id', 'year'], keep=False)
        if duplicates.any():
            dup_count = duplicates.sum()
            dup_pairs = self.df[duplicates][['player_id', 'year']].drop_duplicates()
            self.errors.append(f"Found {dup_count} duplicate (player_id, year) pairs")
            self.errors.append(f"Sample duplicates: {dup_pairs.head().to_dict('records')}")
            is_valid = False
        
        return is_valid
    
    def validate_schema_consistency(self) -> bool:
        """
        Validate schema consistency.
        
        Returns:
            True if valid, False otherwise
        """
        is_valid = True
        
        # Required columns
        required_columns = [
            'player_id', 'year', 'player_name', 'player_code', 
            'team', 'conf', 'posClass'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            self.errors.append(f"Missing required columns: {missing_columns}")
            is_valid = False
        
        # Type validation
        if 'year' in self.df.columns:
            if not pd.api.types.is_numeric_dtype(self.df['year']):
                self.errors.append("year column must be numeric")
                is_valid = False
        
        # Check for empty critical fields
        critical_fields = ['player_name', 'player_id']
        for field in critical_fields:
            if field in self.df.columns:
                empty_count = self.df[field].isna().sum() + (self.df[field] == '').sum()
                if empty_count > 0:
                    self.errors.append(f"Found {empty_count} rows with empty {field}")
                    is_valid = False
        
        return is_valid
    
    def validate_data_ranges(self) -> bool:
        """
        Validate data value ranges.
        
        Returns:
            True if valid, False otherwise
        """
        is_valid = True
        
        # Year ranges
        if 'year' in self.df.columns:
            invalid_years = self.df[~self.df['year'].isin([2024, 2025, 2026, 'career'])]
            if not invalid_years.empty:
                self.errors.append(f"Found {len(invalid_years)} rows with invalid years")
                is_valid = False
        
        # Percentage ranges (should be 0-1 or 0-100)
        percentage_fields = [
            'off_usage', 'off_assist', 'off_to', 'off_orb', 'def_orb',
            'off_ftr', 'def_stl', 'def_blk', 'off_threepr'
        ]
        
        for field in percentage_fields:
            if field in self.df.columns:
                # Check for values outside reasonable range
                invalid_pct = self.df[(self.df[field] < -1) | (self.df[field] > 200)]
                if not invalid_pct.empty:
                    self.warnings.append(f"Found {len(invalid_pct)} rows with unusual {field} values")
        
        return is_valid
    
    def validate_relationships(self) -> bool:
        """
        Validate data relationships and referential integrity.
        
        Returns:
            True if valid, False otherwise
        """
        is_valid = True
        
        # Check that player_code and player_id are consistent
        if 'player_code' in self.df.columns and 'player_id' in self.df.columns:
            # Each player_code should map to exactly one player_id
            code_to_id = self.df.groupby('player_code')['player_id'].nunique()
            inconsistent_codes = code_to_id[code_to_id > 1]
            
            if not inconsistent_codes.empty:
                self.errors.append(f"Found {len(inconsistent_codes)} player_codes mapping to multiple player_ids")
                is_valid = False
        
        return is_valid
    
    def run_all_validations(self) -> Dict[str, Any]:
        """
        Run all validation checks.
        
        Returns:
            Validation report
        """
        self.errors = []
        self.warnings = []
        
        # Run all validations
        pk_valid = self.validate_primary_keys()
        schema_valid = self.validate_schema_consistency()
        range_valid = self.validate_data_ranges()
        rel_valid = self.validate_relationships()
        
        is_valid = pk_valid and schema_valid and range_valid and rel_valid
        
        return {
            'is_valid': is_valid,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings,
            'summary': {
                'total_rows': len(self.df),
                'unique_players': self.df['player_id'].nunique() if 'player_id' in self.df.columns else 0,
                'year_range': {
                    'min': int(self.df['year'].min()) if 'year' in self.df.columns and not self.df['year'].empty else None,
                    'max': int(self.df['year'].max()) if 'year' in self.df.columns and not self.df['year'].empty else None,
                },
                'columns': list(self.df.columns)
            }
        }


def assert_data_integrity(df: pd.DataFrame, strict: bool = False) -> bool:
    """
    Assert data integrity with optional strict mode.
    
    Args:
        df: DataFrame to validate
        strict: If True, raises exception on validation failure
        
    Returns:
        True if data passes integrity checks
        
    Raises:
        DataIntegrityError: If strict=True and validation fails
    """
    validator = DataValidator(df)
    result = validator.run_all_validations()
    
    if not result['is_valid']:
        error_msg = f"Data integrity validation failed: {result['errors']}"
        
        if strict:
            raise DataIntegrityError(error_msg)
        else:
            logger.error(error_msg)
            for error in result['errors']:
                logger.error(f"  - {error}")
    
    if result['warnings']:
        for warning in result['warnings']:
            logger.warning(f"Data integrity warning: {warning}")
    
    return result['is_valid']


def validate_player_record(player_data: Dict[str, Any]) -> List[str]:
    """
    Validate a single player record.
    
    Args:
        player_data: Player data dictionary
        
    Returns:
        List of validation errors
    """
    errors = []
    
    # Required fields
    required_fields = ['player_id', 'player_name', 'year']
    for field in required_fields:
        if field not in player_data or player_data[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Field validations
    if 'player_id' in player_data:
        if not isinstance(player_data['player_id'], str) or not player_data['player_id'].strip():
            errors.append("player_id must be a non-empty string")
    
    if 'year' in player_data:
        year = player_data['year']
        if year not in [2024, 2025, 2026, 'career']:
            errors.append(f"Invalid year: {year}")
    
    return errors


def create_data_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create comprehensive data quality report.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Data quality report
    """
    report = {
        'basic_stats': {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
        },
        'completeness': {},
        'uniqueness': {},
        'distributions': {}
    }
    
    # Completeness analysis
    for col in df.columns:
        null_count = df[col].isna().sum()
        completeness = (len(df) - null_count) / len(df) * 100
        report['completeness'][col] = {
            'null_count': int(null_count),
            'completeness_pct': round(completeness, 2)
        }
    
    # Uniqueness analysis
    for col in df.select_dtypes(include=['object']).columns:
        unique_count = df[col].nunique()
        uniqueness_pct = unique_count / len(df) * 100
        report['uniqueness'][col] = {
            'unique_count': int(unique_count),
            'uniqueness_pct': round(uniqueness_pct, 2)
        }
    
    # Distribution analysis for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        col_data = df[col].dropna()
        if not col_data.empty:
            report['distributions'][col] = {
                'mean': float(col_data.mean()),
                'median': float(col_data.median()),
                'std': float(col_data.std()),
                'min': float(col_data.min()),
                'max': float(col_data.max()),
                'q25': float(col_data.quantile(0.25)),
                'q75': float(col_data.quantile(0.75))
            }
    
    return report


def log_data_validation_results(validation_result: Dict[str, Any]):
    """
    Log validation results in a structured format.
    
    Args:
        validation_result: Result from DataValidator.run_all_validations()
    """
    logger.info("=== Data Validation Results ===")
    logger.info(f"Valid: {validation_result['is_valid']}")
    logger.info(f"Errors: {validation_result['error_count']}")
    logger.info(f"Warnings: {validation_result['warning_count']}")
    
    if validation_result['errors']:
        logger.error("Errors found:")
        for error in validation_result['errors']:
            logger.error(f"  - {error}")
    
    if validation_result['warnings']:
        logger.warning("Warnings found:")
        for warning in validation_result['warnings']:
            logger.warning(f"  - {warning}")
    
    logger.info("Summary:")
    for key, value in validation_result['summary'].items():
        logger.info(f"  {key}: {value}")
    
    logger.info("=== End Validation Results ===")
