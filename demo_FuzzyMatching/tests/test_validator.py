"""
test_validator.py - Tests unitaires du Validator

Tests pour :
- Normalisation texte
- Fuzzy matching
- Keyword matching
- Concept detection
"""

import unittest
from src.core.validator import Validator


class TestValidatorNormalization(unittest.TestCase):
    """Tests normalisation texte"""
    
    def setUp(self):
        """Initialiser validator avant chaque test"""
        self.validator = Validator(fuzzy_threshold=80)
    
    def test_normalize_simple(self):
        """Test normalisation simple"""
        result = self.validator.normalize_text("MARIE DUPONT")
        self.assertEqual(result, "marie dupont")
    
    def test_normalize_accents(self):
        """Test suppression accents"""
        result = self.validator.normalize_text("CHOLÉCYSTECTOMIE")
        self.assertEqual(result, "cholecystectomie")
    
    def test_normalize_punctuation(self):
        """Test suppression ponctuation"""
        result = self.validator.normalize_text("Génou, GAUCHE!")
        self.assertEqual(result, "genou gauche")
    
    def test_normalize_spaces(self):
        """Test normalisation espaces"""
        result = self.validator.normalize_text("  Génou   GAUCHE  ")
        self.assertEqual(result, "genou gauche")
    
    def test_normalize_complex(self):
        """Test normalisation complexe"""
        result = self.validator.normalize_text("  HYPOTHERMIE, ALLERGIE!  ")
        self.assertEqual(result, "hypothermie allergie")
    
    def test_normalize_empty(self):
        """Test normalisation texte vide"""
        result = self.validator.normalize_text("")
        self.assertEqual(result, "")


class TestValidatorFuzzyMatch(unittest.TestCase):
    """Tests fuzzy matching"""
    
    def setUp(self):
        self.validator = Validator(fuzzy_threshold=80)
    
    def test_fuzzy_exact_match(self):
        """Test match exact"""
        result = self.validator.validate_fuzzy_match(
            "marie dupont",
            ["marie dupont"]
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["score"], 100)
    
    def test_fuzzy_similar_match(self):
        """Test match similaire"""
        result = self.validator.validate_fuzzy_match(
            "marie dupon",  # Manque un 't'
            ["marie dupont"]
        )
        self.assertTrue(result["valid"])
        self.assertGreater(result["score"], 80)
    
    def test_fuzzy_no_match(self):
        """Test pas de match"""
        result = self.validator.validate_fuzzy_match(
            "jean martin",
            ["marie dupont"]
        )
        self.assertFalse(result["valid"])
        self.assertLess(result["score"], 80)
    
    def test_fuzzy_multiple_values(self):
        """Test avec plusieurs valeurs attendues"""
        result = self.validator.validate_fuzzy_match(
            "genou gauche",
            ["genou gauche", "epaule droite"]
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["best_match"], "genou gauche")
    
    def test_fuzzy_empty_text(self):
        """Test texte vide"""
        result = self.validator.validate_fuzzy_match(
            "",
            ["marie dupont"]
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["score"], 0)


class TestValidatorKeywordMatch(unittest.TestCase):
    """Tests keyword matching"""
    
    def setUp(self):
        self.validator = Validator()
    
    def test_keyword_found_single(self):
        """Test un mot-clé trouvé"""
        result = self.validator.validate_keyword_match(
            "oui confirmé",
            ["oui", "non", "ok"],
            min_keywords=1
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["score"], 1)
    
    def test_keyword_found_multiple(self):
        """Test plusieurs mots-clés trouvés"""
        result = self.validator.validate_keyword_match(
            "oui et confirmé",
            ["oui", "confirmé", "ok"],
            min_keywords=2
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["score"], 2)
    
    def test_keyword_not_found(self):
        """Test mot-clé non trouvé"""
        result = self.validator.validate_keyword_match(
            "peut-être",
            ["oui", "non", "confirmé"],
            min_keywords=1
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["score"], 0)
    
    def test_keyword_insufficient(self):
        """Test nombre insuffisant de mots-clés"""
        result = self.validator.validate_keyword_match(
            "oui",
            ["oui", "confirmé"],
            min_keywords=2
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["score"], 1)
    
    def test_keyword_case_insensitive(self):
        """Test case insensitivity"""
        result = self.validator.validate_keyword_match(
            "OUI CONFIRMÉ",
            ["oui", "confirmé"],
            min_keywords=2
        )
        self.assertTrue(result["valid"])


class TestValidatorConceptDetection(unittest.TestCase):
    """Tests concept detection"""
    
    def setUp(self):
        self.validator = Validator()
        self.vocab = {
            "risques": ["hypothermie", "allergie", "infection"],
            "traitements": ["insuline", "antibiotique"]
        }
    
    def test_concept_found_single(self):
        """Test un concept trouvé"""
        result = self.validator.validate_concept_detection(
            "hypothermie",
            self.vocab,
            ["risques"],
            min_count=1
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["score"], 1)
    
    def test_concept_found_multiple(self):
        """Test plusieurs concepts trouvés"""
        result = self.validator.validate_concept_detection(
            "hypothermie et allergie",
            self.vocab,
            ["risques"],
            min_count=2
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["score"], 2)
    
    def test_concept_multi_category(self):
        """Test concepts multi-catégories"""
        result = self.validator.validate_concept_detection(
            "hypothermie traitement insuline",
            self.vocab,
            ["risques", "traitements"],
            min_count=2
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["score"], 2)
        self.assertIn("risques", result["concepts"])
        self.assertIn("traitements", result["concepts"])
    
    def test_concept_not_found(self):
        """Test concept non trouvé"""
        result = self.validator.validate_concept_detection(
            "patient normal",
            self.vocab,
            ["risques"],
            min_count=1
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["score"], 0)
    
    def test_concept_empty_text(self):
        """Test texte vide"""
        result = self.validator.validate_concept_detection(
            "",
            self.vocab,
            ["risques"],
            min_count=1
        )
        self.assertFalse(result["valid"])


class TestValidatorUniversal(unittest.TestCase):
    """Tests wrapper universel validate()"""
    
    def setUp(self):
        self.validator = Validator(fuzzy_threshold=80)
    
    def test_validate_fuzzy(self):
        """Test validate() fuzzy"""
        result = self.validator.validate(
            "marie dupont",
            "fuzzy_match",
            expected_values=["marie dupont"]
        )
        self.assertTrue(result["valid"])
    
    def test_validate_keyword(self):
        """Test validate() keyword"""
        result = self.validator.validate(
            "oui confirmé",
            "keyword_match",
            keywords=["oui", "confirmé"],
            min_keywords=2
        )
        self.assertTrue(result["valid"])
    
    def test_validate_concept(self):
        """Test validate() concept"""
        vocab = {"risques": ["hypothermie"]}
        result = self.validator.validate(
            "hypothermie",
            "concept_detection",
            concepts_dict=vocab,
            required_concepts=["risques"],
            min_count=1
        )
        self.assertTrue(result["valid"])
    
    def test_validate_invalid_type(self):
        """Test type validation invalide"""
        with self.assertRaises(ValueError):
            self.validator.validate(
                "test",
                "invalid_type"
            )


class TestValidatorIntegration(unittest.TestCase):
    """Tests d'intégration complets"""
    
    def setUp(self):
        self.validator = Validator(fuzzy_threshold=80)
    
    def test_full_workflow_item_1(self):
        """Test workflow complet Item 1 (nom patient)"""
        result = self.validator.validate_fuzzy_match(
            "marie dupont",
            ["marie dupont"]
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["score"], 100)
    
    def test_full_workflow_item_4(self):
        """Test workflow complet Item 4 (confirmation)"""
        result = self.validator.validate_keyword_match(
            "oui c'est confirmé",
            ["oui", "confirmé", "ok"],
            min_keywords=1
        )
        self.assertTrue(result["valid"])
        self.assertGreaterEqual(result["score"], 1)
    
    def test_full_workflow_item_6(self):
        """Test workflow complet Item 6 (risques)"""
        vocab = {
            "risques": ["hypothermie", "allergie", "infection"]
        }
        result = self.validator.validate_concept_detection(
            "hypothermie et allergie",
            vocab,
            ["risques"],
            min_count=1
        )
        self.assertTrue(result["valid"])


if __name__ == "__main__":
    unittest.main()
