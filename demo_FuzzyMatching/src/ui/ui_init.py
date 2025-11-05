"""
Module UI - Interface Utilisateur

Ce module contient la logique de l'interface :
- Affichage console (Display)
- Menus interactifs (Menus)
"""

from .display import Display
from .menus import Menus

__all__ = [
    'Display',
    'Menus'
]
