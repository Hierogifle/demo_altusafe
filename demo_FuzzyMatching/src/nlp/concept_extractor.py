"""
ConceptExtractor - Extraction de concepts médicaux

Module pour extraire concepts médicaux du texte :
- Détection concepts (risques, traitements, etc.)
- Extraction termes par catégorie
- Scoring concepts
- Validation multi-catégories
"""

from .normalizer import TextNormalizer
from .keyword_detector import KeywordDetector


class ConceptExtractor:
    """
    Extrait concepts médicaux du texte
    Utilise vocabulaire médical pour identifier termes importants
    """
    
    def __init__(self):
        """Initialiser l'extracteur"""
        self.normalizer = TextNormalizer()
        self.keyword_detector = KeywordDetector()
    
    def extract_concepts(self, text, concepts_dict, required_concepts=None):
        """
        Extraire concepts du texte
        
        Args:
            text (str): Texte à analyser
            concepts_dict (dict): Dictionnaire concepts
                                  {"risques": [...], "traitements": [...]}
            required_concepts (list): Concepts à chercher (optionnel)
                                     Si None, cherche tous les concepts
        
        Returns:
            dict:
                - concepts (dict): Concepts trouvés avec termes
                - score (int): Nombre total de concepts trouvés
                - details (dict): Détails par catégorie
        
        Exemple:
            >>> vocab = {
            ...     "risques": ["hypothermie", "allergie"],
            ...     "traitements": ["insuline", "antibiotique"]
            ... }
            >>> extractor = ConceptExtractor()
            >>> result = extractor.extract_concepts(
            ...     "hypothermie patient insuline",
            ...     vocab,
            ...     ["risques", "traitements"]
            ... )
            >>> result['concepts']
            {'risques': ['hypothermie'], 'traitements': ['insuline']}
            >>> result['score']
            2
        """
        if not text or not concepts_dict:
            return {
                "concepts": {},
                "score": 0,
                "details": {},
                "text": text
            }
        
        # Normaliser texte
        text_norm = self.normalizer.normalize(text)
        
        # Déterminer quels concepts chercher
        if required_concepts is None:
            required_concepts = list(concepts_dict.keys())
        
        # Extraire concepts
        concepts_found = {}
        details = {}
        total_score = 0
        
        for concept_category in required_concepts:
            if concept_category not in concepts_dict:
                continue
            
            # Chercher termes de cette catégorie
            terms = concepts_dict[concept_category]
            
            if isinstance(terms, dict):
                # Cas où les termes sont dans une structure {'termes': [...]}
                terms = terms.get("termes", [])
            
            found_terms = []
            for term in terms:
                term_norm = self.normalizer.normalize(term)
                if term_norm in text_norm:
                    found_terms.append(term)
            
            if found_terms:
                concepts_found[concept_category] = found_terms
                total_score += len(found_terms)
            
            details[concept_category] = {
                "found": len(found_terms),
                "total": len(terms),
                "terms": found_terms
            }
        
        return {
            "concepts": concepts_found,
            "score": total_score,
            "details": details,
            "text": text,
            "text_normalized": text_norm
        }
    
    def extract_category(self, text, category_terms):
        """
        Extraire termes d'une catégorie spécifique
        
        Args:
            text (str): Texte
            category_terms (list): Termes de la catégorie
        
        Returns:
            dict:
                - found (list): Termes trouvés
                - count (int): Nombre de termes trouvés
        
        Exemple:
            >>> result = extractor.extract_category(
            ...     "hypothermie allergie infection",
            ...     ["hypothermie", "allergie", "saignement"]
            ... )
            >>> result['found']
            ['hypothermie', 'allergie']
        """
        text_norm = self.normalizer.normalize(text)
        found = []
        
        for term in category_terms:
            term_norm = self.normalizer.normalize(term)
            if term_norm in text_norm:
                found.append(term)
        
        return {
            "found": found,
            "count": len(found),
            "category_total": len(category_terms)
        }
    
    def validate_multi_category(self, text, concepts_dict, requirements):
        """
        Valider réponse avec exigences multi-catégories
        
        Args:
            text (str): Texte à analyser
            concepts_dict (dict): Dictionnaire concepts
            requirements (dict): Exigences
                                {
                                  "required_categories": ["risques", "traitements"],
                                  "min_per_category": {"risques": 1, "traitements": 1},
                                  "total_min": 2
                                }
        
        Returns:
            dict:
                - valid (bool): Requête satisfaite ?
                - concepts (dict): Concepts trouvés
                - analysis (dict): Analyse détaillée
        
        Exemple:
            >>> result = extractor.validate_multi_category(
            ...     "hypothermie diabétique insuline",
            ...     vocab,
            ...     {
            ...       "required_categories": ["risques", "traitements"],
            ...       "min_per_category": {"risques": 1, "traitements": 1},
            ...       "total_min": 2
            ...     }
            ... )
            >>> result['valid']
            True
        """
        extraction = self.extract_concepts(
            text,
            concepts_dict,
            requirements.get("required_categories", [])
        )
        
        # Vérifier exigences
        min_per_category = requirements.get("min_per_category", {})
        total_min = requirements.get("total_min", 1)
        
        # Vérifier par catégorie
        per_category_ok = True
        for category, min_required in min_per_category.items():
            found = len(extraction["concepts"].get(category, []))
            if found < min_required:
                per_category_ok = False
                break
        
        # Vérifier total
        total_ok = extraction["score"] >= total_min
        
        # Résultat
        is_valid = per_category_ok and total_ok
        
        return {
            "valid": is_valid,
            "concepts": extraction["concepts"],
            "analysis": {
                "total_found": extraction["score"],
                "total_min": total_min,
                "per_category_ok": per_category_ok,
                "total_ok": total_ok,
                "details": extraction["details"]
            }
        }
    
    def get_concept_score(self, concepts_found, weight_by_importance=False):
        """
        Calculer score pour concepts trouvés
        
        Args:
            concepts_found (dict): Concepts trouvés
                                  {"risques": ["hypothermie", "allergie"]}
            weight_by_importance (bool): Pondérer par importance ?
        
        Returns:
            int: Score
        """
        if weight_by_importance:
            # Pondération : 1ère occurrence d'une catégorie = 1pt
            return len(concepts_found)
        else:
            # Simple : nombre total de termes trouvés
            count = 0
            for terms in concepts_found.values():
                count += len(terms)
            return count
    
    def summary(self, extraction_result):
        """
        Générer résumé d'extraction
        
        Args:
            extraction_result (dict): Résultat d'extraction
        
        Returns:
            str: Résumé texte
        
        Exemple:
            >>> result = extractor.extract_concepts(...)
            >>> print(extractor.summary(result))
            "Concepts détectés: 3 (risques: 2, traitements: 1)"
        """
        concepts = extraction_result.get("concepts", {})
        
        if not concepts:
            return "Aucun concept détecté"
        
        parts = [f"Concepts détectés: {extraction_result['score']}"]
        
        for category, terms in concepts.items():
            parts.append(f"{category}: {len(terms)}")
        
        return f"{parts[0]} ({', '.join(parts[1:])})"


# Exemple d'utilisation
if __name__ == "__main__":
    extractor = ConceptExtractor()
    
    vocab = {
        "risques": {
            "description": "Risques potentiels",
            "termes": ["hypothermie", "allergie", "infection", "saignement"]
        },
        "traitements": {
            "description": "Traitements",
            "termes": ["insuline", "antibiotique", "anticoagulant"]
        }
    }
    
    print("=== Extraction Concepts ===\n")
    
    # Test 1
    result = extractor.extract_concepts(
        "hypothermie allergie et traitement insuline",
        vocab,
        ["risques", "traitements"]
    )
    print(f"Test 1 - Simple extraction")
    print(f"  Concepts : {result['concepts']}")
    print(f"  Score : {result['score']}")
    print(f"  Résumé : {extractor.summary(result)}\n")
    
    # Test 2 - Validation multi-catégorie
    result = extractor.validate_multi_category(
        "hypothermie et diabétique avec insuline",
        vocab,
        {
            "required_categories": ["risques", "traitements"],
            "min_per_category": {"risques": 1, "traitements": 1},
            "total_min": 2
        }
    )
    print(f"Test 2 - Multi-catégorie")
    print(f"  Valid : {result['valid']}")
    print(f"  Concepts : {result['concepts']}\n")
