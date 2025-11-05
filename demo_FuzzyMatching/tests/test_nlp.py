"""
test_nlp.py - Tests unitaires du module NLP

Tests pour :
- TextNormalizer
- KeywordDetector
- ConceptExtractor
"""

import unittest
from src.nlp.normalizer import TextNormalizer
from src.nlp.keyword_detector import KeywordDetector
from src.nlp.concept_extractor import ConceptExtractor


class TestTextNormalizer(unittest.TestCase):
    """Tests TextNormalizer"""
    
    def test_normalize_basic(self):
        """Test normalisation basique"""
        result = TextNormalizer.normalize("MARIE DUPONT")
        self.assertEqual(result, "marie dupont")
    
    def test_normalize_accents(self):
        """Test suppression accents"""
        result = TextNormalizer.normalize("CHOLÉCYSTECTOMIE")
        self.assertEqual(result, "cholecystectomie")
    
    def test_normalize_punctuation(self):
        """Test suppression ponctuation"""
        result = TextNormalizer.normalize("Génou, GAUCHE!")
        self.assertEqual(result, "genou gauche")
    
    def test_normalize_spaces(self):
        """Test normalisation espaces"""
        result = TextNormalizer.normalize("  Multiple   Spaces  ")
        self.assertEqual(result, "multiple spaces")
    
    def test_normalize_combined(self):
        """Test normalisation combinée"""
        result = TextNormalizer.normalize("  CHOLÉCYSTECTOMIE, OUI!  ")
        self.assertEqual(result, "cholecystectomie oui")
    
    def test_remove_accents_only(self):
        """Test suppression accents uniquement"""
        result = TextNormalizer.remove_accents_only("Café")
        self.assertEqual(result, "Cafe")
    
    def test_to_lowercase(self):
        """Test minuscules"""
        result = TextNormalizer.to_lowercase("MARIE")
        self.assertEqual(result, "marie")
    
    def test_split_words(self):
        """Test division en mots"""
        result = TextNormalizer.split_words("hello world test")
        self.assertEqual(result, ["hello", "world", "test"])
    
    def test_get_tokens(self):
        """Test récupération tokens"""
        result = TextNormalizer.get_tokens("  MARIE   DUPONT  ")
        self.assertEqual(result, ["marie", "dupont"])


class TestKeywordDetector(unittest.TestCase):
    """Tests KeywordDetector"""
    
    def setUp(self):
        self.detector = KeywordDetector()
    
    def test_detect_single_keyword(self):
        """Test détection simple"""
        result = self.detector.detect_keywords(
            "oui confirmé",
            ["oui", "non"]
        )
        self.assertEqual(len(result["found"]), 1)
        self.assertIn("oui", result["found"])
    
    def test_detect_multiple_keywords(self):
        """Test détection multiple"""
        result = self.detector.detect_keywords(
            "oui et confirmé",
            ["oui", "confirmé", "ok"]
        )
        self.assertEqual(len(result["found"]), 2)
    
    def test_detect_no_keywords(self):
        """Test aucun mot-clé"""
        result = self.detector.detect_keywords(
            "peut-être",
            ["oui", "non", "ok"]
        )
        self.assertEqual(len(result["found"]), 0)
    
    def test_detect_any_keyword(self):
        """Test AU MOINS UN mot-clé"""
        result = self.detector.detect_any_keyword(
            "oui",
            ["oui", "non", "ok"]
        )
        self.assertTrue(result)
    
    def test_detect_all_keywords(self):
        """Test TOUS les mots-clés"""
        result = self.detector.detect_all_keywords(
            "oui et non",
            ["oui", "non"]
        )
        self.assertTrue(result)
    
    def test_count_keywords(self):
        """Test comptage mots-clés"""
        count = self.detector.count_keywords(
            "oui oui confirmé",
            ["oui", "confirmé"]
        )
        self.assertEqual(count, 2)
    
    def test_weighted_detection(self):
        """Test détection pondérée"""
        result = self.detector.weighted_detection(
            "oui confirmé",
            ["oui", "confirmé"],
            {"oui": 2, "confirmé": 1}
        )
        self.assertEqual(result["score"], 3)
    
    def test_case_insensitive(self):
        """Test case insensitive"""
        result = self.detector.detect_keywords(
            "OUI CONFIRMÉ",
            ["oui", "confirmé"]
        )
        self.assertEqual(len(result["found"]), 2)


class TestConceptExtractor(unittest.TestCase):
    """Tests ConceptExtractor"""
    
    def setUp(self):
        self.extractor = ConceptExtractor()
        self.vocab = {
            "risques": ["hypothermie", "allergie", "infection"],
            "traitements": ["insuline", "antibiotique"]
        }
    
    def test_extract_single_concept(self):
        """Test extraction simple"""
        result = self.extractor.extract_concepts(
            "hypothermie",
            self.vocab,
            ["risques"]
        )
        self.assertEqual(result["score"], 1)
        self.assertIn("risques", result["concepts"])
    
    def test_extract_multiple_concepts(self):
        """Test extraction multiple"""
        result = self.extractor.extract_concepts(
            "hypothermie et allergie",
            self.vocab,
            ["risques"]
        )
        self.assertEqual(result["score"], 2)
    
    def test_extract_no_concepts(self):
        """Test aucun concept"""
        result = self.extractor.extract_concepts(
            "patient normal",
            self.vocab,
            ["risques"]
        )
        self.assertEqual(result["score"], 0)
    
    def test_extract_multi_category(self):
        """Test extraction multi-catégories"""
        result = self.extractor.extract_concepts(
            "hypothermie et insuline",
            self.vocab,
            ["risques", "traitements"]
        )
        self.assertEqual(result["score"], 2)
        self.assertIn("risques", result["concepts"])
        self.assertIn("traitements", result["concepts"])
    
    def test_extract_category(self):
        """Test extraction une catégorie"""
        result = self.extractor.extract_category(
            "hypothermie allergie",
            self.vocab["risques"]
        )
        self.assertEqual(result["count"], 2)
    
    def test_validate_multi_category(self):
        """Test validation multi-catégories"""
        result = self.extractor.validate_multi_category(
            "hypothermie et insuline",
            self.vocab,
            {
                "required_categories": ["risques", "traitements"],
                "min_per_category": {"risques": 1, "traitements": 1},
                "total_min": 2
            }
        )
        self.assertTrue(result["valid"])
    
    def test_validate_multi_category_fail(self):
        """Test validation multi-catégories échouée"""
        result = self.extractor.validate_multi_category(
            "hypothermie",
            self.vocab,
            {
                "required_categories": ["risques", "traitements"],
                "min_per_category": {"risques": 1, "traitements": 1},
                "total_min": 2
            }
        )
        self.assertFalse(result["valid"])


class TestNLPIntegration(unittest.TestCase):
    """Tests d'intégration NLP complets"""
    
    def test_full_pipeline(self):
        """Test pipeline NLP complet"""
        # Étape 1 : Normalisation
        text = "  HYPOTHERMIE, ALLERGIE!  "
        normalized = TextNormalizer.normalize(text)
        self.assertEqual(normalized, "hypothermie allergie")
        
        # Étape 2 : Détection mots-clés
        detector = KeywordDetector()
        keywords_result = detector.detect_keywords(
            normalized,
            ["hypothermie", "allergie"]
        )
        self.assertEqual(len(keywords_result["found"]), 2)
        
        # Étape 3 : Extraction concepts
        extractor = ConceptExtractor()
        vocab = {"risques": ["hypothermie", "allergie"]}
        concepts_result = extractor.extract_concepts(
            normalized,
            vocab,
            ["risques"]
        )
        self.assertEqual(concepts_result["score"], 2)
    
    def test_medical_workflow(self):
        """Test workflow médical réaliste"""
        # Cas : Patient dit les risques
        recognized = "Risque hypothermie, allergie aux antibiotiques"
        
        # Normaliser
        normalized = TextNormalizer.normalize(recognized)
        
        # Détecter mots-clés
        detector = KeywordDetector()
        keywords = detector.detect_keywords(
            normalized,
            ["risque", "hypothermie", "allergie", "antibiotique"]
        )
        
        # Extraire concepts
        extractor = ConceptExtractor()
        vocab = {"risques": ["hypothermie", "allergie"]}
        concepts = extractor.extract_concepts(
            normalized,
            vocab,
            ["risques"]
        )
        
        # Vérifier résultats
        self.assertGreater(len(keywords["found"]), 0)
        self.assertGreater(concepts["score"], 0)


if __name__ == "__main__":
    unittest.main()
