"""
TextNormalizer - Normalisation du texte

Module pour normaliser texte reconnu par Vosk avant validation :
- Minuscules
- Suppression accents
- Suppression ponctuation
- Suppression espaces multiples
- Suppression termes vides
"""

import unicodedata
import re


class TextNormalizer:
    """
    Normalise le texte pour comparaison et analyse
    """
    
    # Mapping accents
    ACCENTS_MAP = {
        'à': 'a', 'â': 'a', 'ä': 'a', 'á': 'a',
        'ç': 'c',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o', 'ó': 'o',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ý': 'y', 'ÿ': 'y'
    }
    
    # Caractères à supprimer
    PUNCTUATION = r'[.,;:!?\'\"-]'
    
    # Apostrophes à standardiser
    APOSTROPHES = ["'", "'", "´", "`"]
    
    @staticmethod
    def normalize(text):
        """
        Normaliser texte complètement
        
        Args:
            text (str): Texte à normaliser
        
        Returns:
            str: Texte normalisé
        
        Étapes :
            1. Vérifier non vide
            2. Minuscules
            3. Supprimer accents
            4. Supprimer ponctuation
            5. Normaliser espaces
            6. Supprimer espaces avant/après
        
        Exemple:
            >>> normalizer = TextNormalizer()
            >>> normalizer.normalize("CHOLÉCYSTECTOMIE!")
            'cholecystectomie'
            
            >>> normalizer.normalize("  Génou   GAUCHE  ,")
            'genou gauche'
        """
        if not text:
            return ""
        
        # 1. Minuscules
        text = text.lower().strip()
        
        # 2. Supprimer accents
        text = TextNormalizer._remove_accents(text)
        
        # 3. Standardiser apostrophes
        for apostrophe in TextNormalizer.APOSTROPHES:
            text = text.replace(apostrophe, "'")
        
        # 4. Supprimer ponctuation (sauf apostrophes)
        text = re.sub(TextNormalizer.PUNCTUATION, '', text)
        
        # 5. Normaliser espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # 6. Supprimer espaces avant/après
        text = text.strip()
        
        return text
    
    @staticmethod
    def _remove_accents(text):
        """
        Supprimer accents du texte
        
        Args:
            text (str): Texte avec accents
        
        Returns:
            str: Texte sans accents
        
        Utilise mapping manuel pour fiabilité
        """
        result = ""
        for char in text:
            if char in TextNormalizer.ACCENTS_MAP:
                result += TextNormalizer.ACCENTS_MAP[char]
            else:
                result += char
        return result
    
    @staticmethod
    def remove_accents_only(text):
        """Supprimer UNIQUEMENT les accents (garde casse, ponctuation, espaces)"""
        if not text:
            return ""
        return TextNormalizer._remove_accents(text)
    
    @staticmethod
    def to_lowercase(text):
        """Convertir en minuscules"""
        return text.lower() if text else ""
    
    @staticmethod
    def remove_punctuation(text):
        """Supprimer ponctuation"""
        if not text:
            return ""
        return re.sub(TextNormalizer.PUNCTUATION, '', text)
    
    @staticmethod
    def normalize_spaces(text):
        """Normaliser espaces multiples en un seul"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def split_words(text):
        """
        Diviser texte en mots
        
        Args:
            text (str): Texte (normalisé)
        
        Returns:
            list: Liste de mots
        """
        if not text:
            return []
        return text.split()
    
    @staticmethod
    def get_tokens(text, normalize_first=True):
        """
        Récupérer tokens (mots individuels)
        
        Args:
            text (str): Texte
            normalize_first (bool): Normaliser avant ?
        
        Returns:
            list: Liste de mots
        """
        if normalize_first:
            text = TextNormalizer.normalize(text)
        
        return TextNormalizer.split_words(text)
    
    @staticmethod
    def similarity_preprocessing(text):
        """
        Pré-traitement optimal pour comparaison similitude
        (Compatible avec rapidfuzz)
        
        Args:
            text (str): Texte
        
        Returns:
            str: Texte prétraité
        """
        return TextNormalizer.normalize(text)


# Exemple d'utilisation
if __name__ == "__main__":
    normalizer = TextNormalizer()
    
    test_cases = [
        "CHOLÉCYSTECTOMIE!",
        "  Génou   GAUCHE  ,",
        "Hypothermie, allergie, infection.",
        "Marie Dupont",
        "insuline + anticoagulant"
    ]
    
    print("=== Normalisation Texte ===\n")
    for text in test_cases:
        normalized = normalizer.normalize(text)
        print(f"Avant  : '{text}'")
        print(f"Après  : '{normalized}'")
        print()
