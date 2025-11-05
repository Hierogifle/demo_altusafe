"""
Validator - Logique de validation des réponses

Module pour :
- Normaliser texte
- Valider fuzzy matching
- Valider keyword matching
- Valider concept detection
"""

from rapidfuzz import fuzz


class Validator:
    """
    Valide les réponses vocales reconnues
    Supporte : fuzzy matching, keyword matching, concept detection
    """
    
    def __init__(self, fuzzy_threshold=80):
        """
        Initialiser le validator
        
        Args:
            fuzzy_threshold (int): Seuil de similitude (%) pour fuzzy matching
        """
        self.fuzzy_threshold = fuzzy_threshold
    
    def normalize_text(self, text):
        """
        Normaliser texte pour comparaison
        
        Args:
            text (str): Texte à normaliser
        
        Returns:
            str: Texte normalisé
        
        Normalisations appliquées :
            - Minuscules
            - Suppression accents
            - Suppression ponctuation
            - Suppression espaces multiples
        """
        if not text:
            return ""
        
        # Minuscules
        text = text.lower().strip()
        
        # Accents
        accents = {
            'à': 'a', 'ç': 'c', 'é': 'e', 'è': 'e', 'ê': 'e',
            'ô': 'o', 'ù': 'u', 'û': 'u', 'ü': 'u',
            'î': 'i', 'ï': 'i'
        }
        for old, new in accents.items():
            text = text.replace(old, new)
        
        # Espaces multiples
        text = ' '.join(text.split())
        
        # Ponctuation
        text = text.rstrip('.,;:!?')
        
        return text
    
    def validate_fuzzy_match(self, recognized, expected_values):
        """
        Validation fuzzy matching
        
        Args:
            recognized (str): Texte reconnu par Vosk
            expected_values (list): Valeurs attendues
        
        Returns:
            dict: Résultat validation
                - valid (bool): Est valide ?
                - score (int): Score similitude (%)
                - best_match (str): Meilleure correspondance trouvée
                - status (str): Message résultat
        
        Exemple:
            >>> validator = Validator(fuzzy_threshold=80)
            >>> result = validator.validate_fuzzy_match(
            ...     "marie dupont",
            ...     ["marie dupont", "jean martin"]
            ... )
            >>> result['valid']
            True
            >>> result['score']
            100
        """
        if not recognized:
            return {
                "valid": False,
                "recognized": "AUCUN TEXTE",
                "best_match": "---",
                "score": 0,
                "status": "❌ ÉCHOUÉ - Aucun texte"
            }
        
        # Normaliser
        recognized_norm = self.normalize_text(recognized)
        
        # Chercher meilleure correspondance
        best_score = 0
        best_match = None
        
        for expected in expected_values:
            expected_norm = self.normalize_text(expected)
            score = fuzz.ratio(recognized_norm, expected_norm)
            
            if score > best_score:
                best_score = score
                best_match = expected
        
        # Déterminer résultat
        is_valid = best_score >= self.fuzzy_threshold
        status = f"✅ VALIDÉ ({best_score}%)" if is_valid else f"❌ ÉCHOUÉ ({best_score}%)"
        
        return {
            "valid": is_valid,
            "recognized": recognized,
            "recognized_normalized": recognized_norm,
            "best_match": best_match,
            "score": best_score,
            "status": status
        }
    
    def validate_keyword_match(self, recognized, keywords, min_keywords=1):
        """
        Validation keyword matching
        
        Args:
            recognized (str): Texte reconnu
            keywords (list): Mots-clés à chercher
            min_keywords (int): Nombre minimum de mots-clés trouvés
        
        Returns:
            dict: Résultat validation
                - valid (bool): Est valide ?
                - found (list): Mots-clés trouvés
                - required (int): Nombre minimum requis
                - score (int): Nombre de mots-clés trouvés
                - status (str): Message résultat
        
        Exemple:
            >>> result = validator.validate_keyword_match(
            ...     "oui c'est confirmé",
            ...     ["oui", "non", "confirmé"],
            ...     min_keywords=2
            ... )
            >>> result['valid']
            True
            >>> result['found']
            ['oui', 'confirmé']
        """
        if not recognized:
            return {
                "valid": False,
                "found": [],
                "required": min_keywords,
                "score": 0,
                "status": f"❌ ÉCHOUÉ - Aucun texte"
            }
        
        # Normaliser
        text_norm = self.normalize_text(recognized)
        
        # Chercher mots-clés
        found = []
        for kw in keywords:
            kw_norm = self.normalize_text(kw)
            if kw_norm in text_norm:
                found.append(kw)
        
        # Valider
        is_valid = len(found) >= min_keywords
        status = f"✅ VALIDÉ ({len(found)}/{min_keywords})" if is_valid else f"❌ ÉCHOUÉ ({len(found)}/{min_keywords})"
        
        return {
            "valid": is_valid,
            "found": found,
            "required": min_keywords,
            "score": len(found),
            "status": status
        }
    
    def validate_concept_detection(self, recognized, concepts_dict, required_concepts, min_count=1):
        """
        Validation concept detection (NLP avancé)
        
        Args:
            recognized (str): Texte reconnu
            concepts_dict (dict): Dictionnaire concepts {"risques": [...], "traitements": [...]}
            required_concepts (list): Concepts recherchés ["risques", "traitements"]
            min_count (int): Nombre minimum de concepts trouvés
        
        Returns:
            dict: Résultat validation
                - valid (bool): Est valide ?
                - concepts (dict): Concepts trouvés avec termes
                - required (int): Nombre minimum requis
                - score (int): Nombre de concepts trouvés
                - status (str): Message résultat
        
        Exemple:
            >>> vocab = {
            ...     "risques": ["hypothermie", "allergie"],
            ...     "traitements": ["insuline"]
            ... }
            >>> result = validator.validate_concept_detection(
            ...     "hypothermie et traitement insuline",
            ...     vocab,
            ...     ["risques", "traitements"],
            ...     min_count=2
            ... )
            >>> result['valid']
            True
        """
        if not recognized:
            return {
                "valid": False,
                "concepts": {},
                "required": min_count,
                "score": 0,
                "status": f"❌ ÉCHOUÉ - Aucun texte"
            }
        
        # Normaliser
        text_norm = self.normalize_text(recognized)
        
        # Chercher concepts
        concepts_found = {}
        for concept_category in required_concepts:
            if concept_category in concepts_dict:
                found_terms = []
                for term in concepts_dict[concept_category]:
                    term_norm = self.normalize_text(term)
                    if term_norm in text_norm:
                        found_terms.append(term)
                if found_terms:
                    concepts_found[concept_category] = found_terms
        
        # Valider
        total_concepts = len(concepts_found)
        is_valid = total_concepts >= min_count
        status = f"✅ VALIDÉ ({total_concepts}/{min_count})" if is_valid else f"❌ ÉCHOUÉ ({total_concepts}/{min_count})"
        
        return {
            "valid": is_valid,
            "concepts": concepts_found,
            "required": min_count,
            "score": total_concepts,
            "status": status
        }
    
    def validate(self, recognized, validation_type, **kwargs):
        """
        Wrapper universal pour toute validation
        
        Args:
            recognized (str): Texte reconnu
            validation_type (str): Type validation
                - "fuzzy_match": Fuzzy matching
                - "keyword_match": Keyword matching
                - "concept_detection": Concept detection
            **kwargs: Arguments spécifiques au type
        
        Returns:
            dict: Résultat validation
        
        Exemples:
            >>> # Fuzzy matching
            >>> validator.validate(
            ...     "marie dupont",
            ...     "fuzzy_match",
            ...     expected_values=["marie dupont"],
            ...     threshold=80
            ... )
            
            >>> # Keyword matching
            >>> validator.validate(
            ...     "oui confirmé",
            ...     "keyword_match",
            ...     keywords=["oui", "confirmé"],
            ...     min_keywords=1
            ... )
            
            >>> # Concept detection
            >>> validator.validate(
            ...     "hypothermie insuline",
            ...     "concept_detection",
            ...     concepts_dict=vocab,
            ...     required_concepts=["risques", "traitements"],
            ...     min_count=1
            ... )
        """
        if validation_type == "fuzzy_match":
            return self.validate_fuzzy_match(
                recognized,
                kwargs.get("expected_values", [])
            )
        
        elif validation_type == "keyword_match":
            return self.validate_keyword_match(
                recognized,
                kwargs.get("keywords", []),
                kwargs.get("min_keywords", 1)
            )
        
        elif validation_type == "concept_detection":
            return self.validate_concept_detection(
                recognized,
                kwargs.get("concepts_dict", {}),
                kwargs.get("required_concepts", []),
                kwargs.get("min_count", 1)
            )
        
        else:
            raise ValueError(f"Type validation inconnu : {validation_type}")


# Exemple d'utilisation
if __name__ == "__main__":
    validator = Validator(fuzzy_threshold=80)
    
    # Test fuzzy matching
    print("=== Fuzzy Matching ===")
    result = validator.validate_fuzzy_match(
        "marie dupont",
        ["marie dupont", "jean martin"]
    )
    print(f"Résultat : {result}\n")
    
    # Test keyword matching
    print("=== Keyword Matching ===")
    result = validator.validate_keyword_match(
        "oui c'est confirmé",
        ["oui", "confirmé", "ok"],
        min_keywords=2
    )
    print(f"Résultat : {result}\n")
    
    # Test concept detection
    print("=== Concept Detection ===")
    vocab = {
        "risques": ["hypothermie", "allergie"],
        "traitements": ["insuline", "antibiotique"]
    }
    result = validator.validate_concept_detection(
        "hypothermie diabétique traitement insuline",
        vocab,
        ["risques", "traitements"],
        min_count=2
    )
    print(f"Résultat : {result}")
