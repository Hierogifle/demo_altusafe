"""
KeywordDetector - Détection de mots-clés

Module pour détecter mots-clés et expressions dans le texte :
- Recherche simple (substring)
- Fuzzy matching optionnel
- Pondération des mots importants
- Détection phrases clés
"""

from .normalizer import TextNormalizer
from rapidfuzz import fuzz


class KeywordDetector:
    """
    Détecte mots-clés et expressions dans le texte
    """
    
    def __init__(self, use_fuzzy=False, fuzzy_threshold=80):
        """
        Initialiser le détecteur
        
        Args:
            use_fuzzy (bool): Utiliser fuzzy matching optionnel
            fuzzy_threshold (int): Seuil fuzzy matching (%)
        """
        self.use_fuzzy = use_fuzzy
        self.fuzzy_threshold = fuzzy_threshold
        self.normalizer = TextNormalizer()
    
    def detect_keywords(self, text, keywords, fuzzy=None):
        """
        Détecter mots-clés dans le texte
        
        Args:
            text (str): Texte à analyser
            keywords (list): Liste de mots-clés à chercher
            fuzzy (bool): Utiliser fuzzy matching (override)
        
        Returns:
            dict:
                - found (list): Mots-clés trouvés
                - count (int): Nombre de mots-clés trouvés
                - missing (list): Mots-clés non trouvés
        
        Exemple:
            >>> detector = KeywordDetector()
            >>> result = detector.detect_keywords(
            ...     "oui c'est confirmé",
            ...     ["oui", "confirmé", "ok"]
            ... )
            >>> result['found']
            ['oui', 'confirmé']
            >>> result['count']
            2
        """
        if not text or not keywords:
            return {
                "found": [],
                "count": 0,
                "missing": keywords,
                "text": text,
                "text_normalized": self.normalizer.normalize(text)
            }
        
        # Normaliser texte
        text_norm = self.normalizer.normalize(text)
        
        # Déterminer méthode
        use_fuzzy = fuzzy if fuzzy is not None else self.use_fuzzy
        
        # Chercher mots-clés
        found = []
        missing = []
        
        for keyword in keywords:
            keyword_norm = self.normalizer.normalize(keyword)
            
            if use_fuzzy:
                # Fuzzy matching
                score = fuzz.partial_ratio(text_norm, keyword_norm)
                if score >= self.fuzzy_threshold:
                    found.append(keyword)
                else:
                    missing.append(keyword)
            else:
                # Substring matching (exact après normalisation)
                if keyword_norm in text_norm:
                    found.append(keyword)
                else:
                    missing.append(keyword)
        
        return {
            "found": found,
            "count": len(found),
            "missing": missing,
            "text": text,
            "text_normalized": text_norm
        }
    
    def detect_any_keyword(self, text, keywords):
        """
        Détecter AU MOINS UN mot-clé
        
        Args:
            text (str): Texte à analyser
            keywords (list): Liste de mots-clés
        
        Returns:
            bool: Au moins un keyword trouvé ?
        
        Exemple:
            >>> detector.detect_any_keyword(
            ...     "oui confirmé",
            ...     ["oui", "non", "ok"]
            ... )
            True
        """
        result = self.detect_keywords(text, keywords)
        return len(result["found"]) > 0
    
    def detect_all_keywords(self, text, keywords):
        """
        Détecter TOUS les mots-clés
        
        Args:
            text (str): Texte à analyser
            keywords (list): Liste de mots-clés
        
        Returns:
            bool: Tous les keywords trouvés ?
        
        Exemple:
            >>> detector.detect_all_keywords(
            ...     "oui et confirmé",
            ...     ["oui", "confirmé"]
            ... )
            True
        """
        result = self.detect_keywords(text, keywords)
        return len(result["missing"]) == 0
    
    def count_keywords(self, text, keywords):
        """
        Compter nombre de mots-clés trouvés
        
        Args:
            text (str): Texte
            keywords (list): Mots-clés
        
        Returns:
            int: Nombre trouvé
        """
        result = self.detect_keywords(text, keywords)
        return result["count"]
    
    def detect_phrases(self, text, phrases):
        """
        Détecter phrases/expressions
        
        Args:
            text (str): Texte à analyser
            phrases (list): Liste de phrases
        
        Returns:
            dict:
                - found (list): Phrases trouvées
                - count (int): Nombre trouvé
                - text_normalized (str): Texte normalisé
        
        Exemple:
            >>> detector.detect_phrases(
            ...     "antibioprophylaxie effectuée",
            ...     ["antibio", "effectuée", "selon protocole"]
            ... )
            >>> result['found']
            ['antibio', 'effectuée']
        """
        return self.detect_keywords(text, phrases, fuzzy=False)
    
    def weighted_detection(self, text, keywords, weights=None):
        """
        Détection avec pondération
        Certains mots sont plus importants que d'autres
        
        Args:
            text (str): Texte
            keywords (list): Mots-clés
            weights (dict): Poids par mot-clé
                           {"oui": 2, "confirmé": 1}
        
        Returns:
            dict:
                - found (list): Mots-clés trouvés
                - score (float): Score total (somme des poids)
                - details (dict): Détails par mot-clé
        
        Exemple:
            >>> result = detector.weighted_detection(
            ...     "oui confirmé",
            ...     ["oui", "confirmé"],
            ...     {"oui": 2, "confirmé": 1}
            ... )
            >>> result['score']
            3
        """
        if weights is None:
            weights = {kw: 1 for kw in keywords}
        
        result = self.detect_keywords(text, keywords)
        
        # Calculer score pondéré
        score = 0
        details = {}
        
        for keyword in result["found"]:
            weight = weights.get(keyword, 1)
            score += weight
            details[keyword] = {"found": True, "weight": weight}
        
        for keyword in result["missing"]:
            weight = weights.get(keyword, 1)
            details[keyword] = {"found": False, "weight": weight}
        
        return {
            "found": result["found"],
            "score": score,
            "details": details,
            "text_normalized": result["text_normalized"]
        }


# Exemple d'utilisation
if __name__ == "__main__":
    detector = KeywordDetector()
    
    print("=== Détection Mots-Clés ===\n")
    
    # Test 1
    result = detector.detect_keywords(
        "oui c'est confirmé",
        ["oui", "confirmé", "ok"]
    )
    print(f"Test 1 - Oui/Confirmé")
    print(f"  Trouvés : {result['found']}")
    print(f"  Count : {result['count']}\n")
    
    # Test 2
    result = detector.detect_keywords(
        "hypothermie allergie infection",
        ["hypothermie", "allergie", "infection", "saignement"]
    )
    print(f"Test 2 - Risques")
    print(f"  Trouvés : {result['found']}")
    print(f"  Manquants : {result['missing']}\n")
    
    # Test 3 - Pondération
    result = detector.weighted_detection(
        "oui et confirmé",
        ["oui", "confirmé"],
        {"oui": 2, "confirmé": 1}
    )
    print(f"Test 3 - Pondération")
    print(f"  Score : {result['score']}")
    print(f"  Détails : {result['details']}")
