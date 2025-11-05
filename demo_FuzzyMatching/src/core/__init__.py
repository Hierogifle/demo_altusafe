"""
Module Core - Logique métier de l'application

Ce module contient la logique principale :
- Reconnaissance vocale (Vosk)
- Validation des réponses
- Gestion de la checklist
"""

# __init__.py
from .recognizer import ChecklistRecognizer
from .validator import Validator
from .checklist_manager import ChecklistManager

__all__ = [
    'ChecklistRecognizer',
    'Validator',
    'ChecklistManager'
]
