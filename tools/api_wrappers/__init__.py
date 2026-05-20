"""
API Wrappers
This module contains wrapper implementations for various external APIs.
"""

from .auth import MadadAuthAPI
from .common import MadadAPIClient, MadadAPIError

__all__ = ["MadadAPIClient", "MadadAPIError", "MadadAuthAPI"]
