"""
__init__.py - Package src

Initialise le package src et expose les modules principaux
"""

# Imports des modules principaux
from .core import (
    ChecklistRecognizer,
    Validator,
    ChecklistManager
)

from .io import DataLoader

__version__ = "2.0.0"
__author__ = "Medical Team"

__all__ = [
    'ChecklistRecognizer',
    'Validator',
    'ChecklistManager',
    'DataLoader'
]