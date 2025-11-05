"""
ConfigLoader - Chargement et gestion de la configuration

Module pour gérer la configuration de l'application :
- Charger configuration app
- Charger règles validation
- Valider configuration
- Accéder aux valeurs de config
- Gérer valeurs par défaut
"""

import json
from typing import Any, Dict, Optional
from .data_loader import DataLoader


class ConfigLoader:
    """
    Charge et gère la configuration de l'application
    Centralise accès à tous les paramètres de config
    """
    
    # Configuration en cache (singleton)
    _config = None
    _validation_rules = None
    
    @staticmethod
    def load():
        """
        Charger la configuration complète
        
        Returns:
            dict: Configuration app + règles validation
        
        Raises:
            FileNotFoundError: Si fichiers config manquants
            ValueError: Si configuration invalide
        
        Exemple:
            >>> ConfigLoader.load()
            >>> app_name = ConfigLoader.get_app_name()
        """
        try:
            # Charger config app
            ConfigLoader._config = DataLoader.load_config(use_complet=True)
            
            # Charger règles validation
            ConfigLoader._validation_rules = DataLoader.load_validation_rules(use_complet=True)
            
            # Valider configuration
            ConfigLoader._validate_config()
            
            return {
                "config": ConfigLoader._config,
                "validation_rules": ConfigLoader._validation_rules
            }
        
        except Exception as e:
            raise ValueError(f"Erreur chargement configuration : {e}")
    
    @staticmethod
    def _validate_config():
        """Valider que la configuration est correcte"""
        if not ConfigLoader._config:
            raise ValueError("Configuration app non chargée")
        
        if not ConfigLoader._validation_rules:
            raise ValueError("Règles validation non chargées")
        
        # Vérifier clés essentielles
        required_keys = ["app", "vosk", "audio", "validation", "checklist"]
        for key in required_keys:
            if key not in ConfigLoader._config:
                raise ValueError(f"Clé config manquante : {key}")
    
    # =====================================================================
    # APP INFO
    # =====================================================================
    
    @staticmethod
    def get_app_name() -> str:
        """Récupérer nom application"""
        return ConfigLoader._get_safe("app", "name", "Checklist Chirurgicale")
    
    @staticmethod
    def get_app_version() -> str:
        """Récupérer version app"""
        return ConfigLoader._get_safe("app", "version", "2.0.0")
    
    @staticmethod
    def get_app_description() -> str:
        """Récupérer description app"""
        return ConfigLoader._get_safe("app", "description", "")
    
    # =====================================================================
    # VOSK CONFIGURATION
    # =====================================================================
    
    @staticmethod
    def get_vosk_model_path() -> str:
        """
        Récupérer chemin modèle Vosk
        
        Returns:
            str: Chemin modèle (ex: "data/models/vosk-model-small-fr-0.22")
        """
        return ConfigLoader._get_safe("vosk", "model_path", "data/models/vosk-model-small-fr-0.22")
    
    @staticmethod
    def get_vosk_sample_rate() -> int:
        """Récupérer sample rate Vosk"""
        return ConfigLoader._get_safe("vosk", "sample_rate", 16000)
    
    @staticmethod
    def get_vosk_blocksize() -> int:
        """Récupérer blocksize Vosk"""
        return ConfigLoader._get_safe("vosk", "blocksize", 4096)
    
    # =====================================================================
    # AUDIO CONFIGURATION
    # =====================================================================
    
    @staticmethod
    def get_listen_timeout() -> int:
        """
        Récupérer timeout d'écoute (secondes)
        
        Returns:
            int: Timeout en secondes (défaut: 10)
        """
        return ConfigLoader._get_safe("audio", "listen_timeout", 10)
    
    @staticmethod
    def get_listen_timeout_min() -> int:
        """Récupérer timeout minimum"""
        return ConfigLoader._get_safe("audio", "listen_timeout_min", 5)
    
    @staticmethod
    def get_listen_timeout_max() -> int:
        """Récupérer timeout maximum"""
        return ConfigLoader._get_safe("audio", "listen_timeout_max", 30)
    
    @staticmethod
    def is_partial_enabled() -> bool:
        """Récupérer si reconnaissance partielle activée"""
        return ConfigLoader._get_safe("audio", "enable_partial", True)
    
    @staticmethod
    def get_partial_interval() -> float:
        """Récupérer intervalle affichage reconnaissance partielle (sec)"""
        return ConfigLoader._get_safe("audio", "show_partial_interval", 0.5)
    
    # =====================================================================
    # VALIDATION CONFIGURATION
    # =====================================================================
    
    @staticmethod
    def get_fuzzy_threshold() -> int:
        """
        Récupérer seuil fuzzy matching par défaut
        
        Returns:
            int: Seuil (%) - défaut: 80
        """
        return ConfigLoader._get_safe("validation", "fuzzy_threshold", 80)
    
    @staticmethod
    def get_fuzzy_threshold_strict() -> int:
        """Récupérer seuil fuzzy strict"""
        return ConfigLoader._get_safe("validation", "fuzzy_threshold_strict", 90)
    
    @staticmethod
    def get_fuzzy_threshold_permissive() -> int:
        """Récupérer seuil fuzzy permissif"""
        return ConfigLoader._get_safe("validation", "fuzzy_threshold_permissive", 70)
    
    @staticmethod
    def get_keyword_min_default() -> int:
        """Récupérer minimum mots-clés par défaut"""
        return ConfigLoader._get_safe("validation", "keyword_min_default", 1)
    
    @staticmethod
    def get_concept_min_default() -> int:
        """Récupérer minimum concepts par défaut"""
        return ConfigLoader._get_safe("validation", "concept_min_default", 1)
    
    # =====================================================================
    # CHECKLIST CONFIGURATION
    # =====================================================================
    
    @staticmethod
    def get_checklist_template_file() -> str:
        """Récupérer chemin template checklist"""
        return ConfigLoader._get_safe("checklist", "template_file", "data/templates/checklist_template.json")
    
    @staticmethod
    def get_vocabulary_file() -> str:
        """Récupérer chemin vocabulaire médical"""
        return ConfigLoader._get_safe("checklist", "vocabulary_file", "data/templates/medical_vocabulary.json")
    
    @staticmethod
    def should_stop_on_first_failure() -> bool:
        """Récupérer si arrêt au premier échec"""
        return ConfigLoader._get_safe("checklist", "stop_on_first_failure", False)
    
    @staticmethod
    def requires_all_items() -> bool:
        """Récupérer si tous les items sont requis"""
        return ConfigLoader._get_safe("checklist", "require_all_items", True)
    
    # =====================================================================
    # LOGGING CONFIGURATION
    # =====================================================================
    
    @staticmethod
    def get_logging_level() -> str:
        """Récupérer niveau logging"""
        return ConfigLoader._get_safe("logging", "level", "INFO")
    
    @staticmethod
    def get_logging_file() -> str:
        """Récupérer chemin fichier logs"""
        return ConfigLoader._get_safe("logging", "file", "logs/checklist.log")
    
    @staticmethod
    def get_logging_format() -> str:
        """Récupérer format logging"""
        return ConfigLoader._get_safe("logging", "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # =====================================================================
    # UI CONFIGURATION
    # =====================================================================
    
    @staticmethod
    def should_clear_screen() -> bool:
        """Récupérer si effacer écran"""
        return ConfigLoader._get_safe("ui", "clear_screen", True)
    
    @staticmethod
    def should_show_progress_bar() -> bool:
        """Récupérer si afficher barre progression"""
        return ConfigLoader._get_safe("ui", "show_progress_bar", True)
    
    @staticmethod
    def should_show_timing() -> bool:
        """Récupérer si afficher temps"""
        return ConfigLoader._get_safe("ui", "show_timing", True)
    
    @staticmethod
    def should_use_colors() -> bool:
        """Récupérer si utiliser couleurs"""
        return ConfigLoader._get_safe("ui", "colors", True)
    
    # =====================================================================
    # ADVANCED CONFIGURATION
    # =====================================================================
    
    @staticmethod
    def is_debug_mode() -> bool:
        """Récupérer si mode debug activé"""
        return ConfigLoader._get_safe("advanced", "debug_mode", False)
    
    @staticmethod
    def is_test_mode() -> bool:
        """Récupérer si mode test activé"""
        return ConfigLoader._get_safe("advanced", "test_mode", False)
    
    @staticmethod
    def should_allow_retries() -> bool:
        """Récupérer si retries autorisées"""
        return ConfigLoader._get_safe("advanced", "allow_retry_failed_items", True)
    
    @staticmethod
    def get_max_retries() -> int:
        """Récupérer nombre maximum de retries"""
        return ConfigLoader._get_safe("advanced", "max_retries", 3)
    
    # =====================================================================
    # VALIDATION RULES
    # =====================================================================
    
    @staticmethod
    def get_item_rules(item_id: int) -> Optional[Dict]:
        """
        Récupérer règles d'un item spécifique
        
        Args:
            item_id (int): ID de l'item (1-9)
        
        Returns:
            dict: Règles de l'item ou None
        """
        if not ConfigLoader._validation_rules:
            return None
        
        items = ConfigLoader._validation_rules.get("items_complexes", {})
        item_key = f"item_{item_id}"
        
        return items.get(item_key)
    
    @staticmethod
    def get_scoring_system() -> Dict:
        """Récupérer système de scoring"""
        if not ConfigLoader._validation_rules:
            return {}
        
        return ConfigLoader._validation_rules.get("scoring_system", {})
    
    @staticmethod
    def get_error_handling() -> Dict:
        """Récupérer gestion des erreurs"""
        if not ConfigLoader._validation_rules:
            return {}
        
        return ConfigLoader._validation_rules.get("gestion_erreurs", {})
    
    # =====================================================================
    # UTILITIES
    # =====================================================================
    
    @staticmethod
    def _get_safe(section: str, key: str, default: Any = None) -> Any:
        """
        Récupérer valeur config en toute sécurité
        
        Args:
            section (str): Section config
            key (str): Clé
            default (Any): Valeur par défaut
        
        Returns:
            Any: Valeur ou défaut
        """
        if not ConfigLoader._config:
            return default
        
        section_data = ConfigLoader._config.get(section, {})
        return section_data.get(key, default)
    
    @staticmethod
    def get_all_config() -> Dict:
        """Récupérer toute la configuration"""
        return ConfigLoader._config or {}
    
    @staticmethod
    def get_all_rules() -> Dict:
        """Récupérer toutes les règles"""
        return ConfigLoader._validation_rules or {}
    
    @staticmethod
    def print_summary():
        """Afficher résumé configuration"""
        print("\n" + "="*60)
        print("  ⚙️  CONFIGURATION RÉSUMÉ")
        print("="*60)
        print(f"\n  Application: {ConfigLoader.get_app_name()} v{ConfigLoader.get_app_version()}")
        print(f"  Mode debug: {'✅' if ConfigLoader.is_debug_mode() else '❌'}")
        print(f"  Mode test: {'✅' if ConfigLoader.is_test_mode() else '❌'}")
        print(f"\n  Vosk:")
        print(f"    - Modèle: {ConfigLoader.get_vosk_model_path()}")
        print(f"    - Sample rate: {ConfigLoader.get_vosk_sample_rate()} Hz")
        print(f"\n  Audio:")
        print(f"    - Timeout: {ConfigLoader.get_listen_timeout()}s")
        print(f"    - Reconnaissance partielle: {'✅' if ConfigLoader.is_partial_enabled() else '❌'}")
        print(f"\n  Validation:")
        print(f"    - Seuil fuzzy: {ConfigLoader.get_fuzzy_threshold()}%")
        print(f"\n" + "="*60 + "\n")


# Exemple d'utilisation
if __name__ == "__main__":
    print("=== ConfigLoader Tests ===\n")
    
    try:
        # Charger config
        print("1️⃣  Chargement configuration...")
        ConfigLoader.load()
        print("✅ Configuration chargée\n")
        
        # Afficher résumé
        ConfigLoader.print_summary()
        
        # Test accès valeurs
        print("2️⃣  Test accès valeurs...")
        print(f"  App: {ConfigLoader.get_app_name()}")
        print(f"  Version: {ConfigLoader.get_app_version()}")
        print(f"  Timeout: {ConfigLoader.get_listen_timeout()}s")
        print(f"  Threshold: {ConfigLoader.get_fuzzy_threshold()}%")
        print(f"  Debug: {ConfigLoader.is_debug_mode()}\n")
        
        # Test règles
        print("3️⃣  Test règles validation...")
        item_6_rules = ConfigLoader.get_item_rules(6)
        if item_6_rules:
            print(f"  Item 6 type: {item_6_rules.get('type')}")
            print(f"  Item 6 validation: {item_6_rules.get('validation_type')}\n")
        
        print("✅ Tous les tests passés !")
    
    except Exception as e:
        print(f"❌ Erreur : {e}")
