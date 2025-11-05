"""
Module NLP - Traitement du langage naturel

Ce module contient la logique NLP avancée :
- Normalisation texte
- Détection mots-clés
- Extraction concepts médicaux
"""

from .normalizer import TextNormalizer
from .keyword_detector import KeywordDetector
from .concept_extractor import ConceptExtractor

__all__ = [
    'TextNormalizer',
    'KeywordDetector',
    'ConceptExtractor'
]
