# app/core/year_utils.py
# Legacy module - use app.core.utils.years instead

from app.core.utils.years import normalize_year

# Re-export for backward compatibility
__all__ = ['normalize_year']