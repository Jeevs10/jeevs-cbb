"""
Core Utilities Package
Centralized utility functions for common operations.

This package provides:
- ids: Player ID handling and conversion
- years: Year normalization and validation  
- filters: Data filtering and pandas operations

Usage:
    from app.core.utils import normalize_year, clean_player_id, apply_filters
    from app.core.utils.ids import resolve_player_identifier
    from app.core.utils.years import get_available_years
    from app.core.utils.filters import search_columns, paginate_dataframe
"""

from .ids import (
    clean_player_id,
    clean_year,
    resolve_player_identifier,
    validate_player_id_format,
    create_id_mapping,
    get_player_id_from_code,
    get_player_code_from_id
)

from .years import (
    normalize_year,
    validate_year,
    get_year_range,
    filter_by_years,
    get_available_years,
    create_year_labels,
    sort_by_year
)

from .filters import (
    apply_filters,
    filter_by_numeric_range,
    search_columns,
    sort_dataframe,
    paginate_dataframe,
    clean_numeric_columns,
    convert_percentages,
    replace_nan_with_none,
    get_unique_values,
    create_filter_summary
)
