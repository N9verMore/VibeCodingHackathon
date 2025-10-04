"""
Brand Name Normalization Utilities

Provides consistent brand name handling:
- For storage: lowercase with underscores (e.g., "tea_app")
- For search: Title Case with spaces (e.g., "Tea App")
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def normalize_brand_for_storage(brand: str) -> str:
    """
    Normalize brand name for database storage.
    
    Converts to lowercase with underscores.
    Examples:
        "Tea App" -> "tea_app"
        "TEA APP" -> "tea_app"
        "tea app" -> "tea_app"
        "tea-app" -> "tea_app"
    
    Args:
        brand: Raw brand name
        
    Returns:
        Normalized brand name for storage (lowercase with underscores)
    """
    if not brand:
        return ""
    
    # Replace common separators with underscores
    normalized = brand.replace(" ", "_").replace("-", "_")
    
    # Convert to lowercase
    normalized = normalized.lower()
    
    # Remove multiple consecutive underscores
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    
    # Strip leading/trailing underscores
    normalized = normalized.strip("_")
    
    logger.debug(f"Normalized '{brand}' -> '{normalized}' for storage")
    return normalized


def normalize_brand_for_search(brand: str) -> str:
    """
    Normalize brand name for external API searches (e.g., news).
    
    Converts underscores to spaces and capitalizes each word.
    Examples:
        "tea_app" -> "Tea App"
        "TEA_APP" -> "Tea App"
        "telegram" -> "Telegram"
    
    Args:
        brand: Raw brand name (typically from storage format)
        
    Returns:
        Normalized brand name for search (Title Case with spaces)
    """
    if not brand:
        return ""
    
    # Replace underscores with spaces
    normalized = brand.replace("_", " ")
    
    # Capitalize each word
    normalized = normalized.title()
    
    logger.debug(f"Normalized '{brand}' -> '{normalized}' for search")
    return normalized


def get_brand_names(brand: str) -> dict:
    """
    Get both storage and search versions of a brand name.
    
    Args:
        brand: Raw brand name
        
    Returns:
        Dict with 'storage' and 'search' keys
    """
    return {
        'storage': normalize_brand_for_storage(brand),
        'search': normalize_brand_for_search(brand)
    }

