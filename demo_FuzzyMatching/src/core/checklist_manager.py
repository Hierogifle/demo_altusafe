"""
Checklist Manager - Gestion complète de la checklist

Module pour :
- Charger données patient et checklist
- Gérer flux validation
- Afficher résultats
- Générer résumé final
"""

from .recognizer import ChecklistRecognizer
from .validator import Validator


class ChecklistManager:
    """
    Gère l'exécution complète de la checklist
    Orchestre : reconnaissance vocale + validation + affichage
    """
    
    def __init__(self, checklist_template, patient_data, config):
        """
        Initialiser le manager
        
        Args:
            checklist_template (dict): Template checklist depuis JSON
            patient_data (dict): Données patient depuis JSON
            config (dict): Configuration app depuis JSON
        """
        self.checklist = checklist_template.get("items", [])
        self.patient = patient_data
        self.config = config
        
        # Initialiser composants
        model_path = config.get("vosk", {}).get("model_path")
        self.recognizer = ChecklistRecognizer(model_path)
        
        fuzzy_threshold = config.get("validation", {}).get("fuzzy_threshold", 80)
        self.validator = Validator(fuzzy_threshold=fuzzy_threshold)
        
        # Résultats
        self.results = []
    
    def run_full_checklist(self):
        """
        Exécuter la checklist complète
        
        Returns:
            list: Liste des résultats
        """
        print("\n" + "="*60)
        print("🚀 DÉMARRAGE CHECKLIST COMPLÈTE")
        print("="*60)
        print(f"\n👤 Patient : {self.patient.get('nom', '?')} {self.patient.get('prenom', '?')}")
        print(f"🏥 Intervention : {self.patient.get('operation', {}).get('type_intervention', '?')}")
        print(f"📍 Site : {self.patient.get('operation', {}).get('site_operatoire', '?')}\n")
        
        input("⏸️  Appuyez Entrée pour commencer... ")
        
        self.results = []
        
        try:
            for idx, item in enumerate(self.checklist, 1):
                # Header item
                self._display_item_header(item, idx)
                
                # Écouter
                print("  ⏳ Veuillez répondre...\n")
                recognized = self.recognizer.listen_for_answer(
                    timeout=item.get("timeout", 10)
                )
                
                # Valider
                result = self._validate_item(item, recognized)
                self.results.append(result)
                
                # Afficher résultat
                self._display_result(result)
                
                # Continuer vers suivant
                if idx < len(self.checklist):
                    input("\n  ⏸️  Appuyez Entrée pour l'item suivant... ")
                else:
                    print("\n  ✅ Tous les items sont testés !")
        
        except KeyboardInterrupt:
            print("\n\n  ⏹️  Programme interrompu par l'utilisateur")
        
        # Résumé
        self._display_summary()
        
        return self.results
    
    def run_single_item(self, item_id):
        """
        Exécuter un item spécifique
        
        Args:
            item_id (int): ID de l'item (1-9)
        
        Returns:
            dict: Résultat validation
        """
        # Chercher item
        item = None
        for i in self.checklist:
            if i.get("id") == item_id:
                item = i
                break
        
        if not item:
            print(f"❌ Item {item_id} non trouvé")
            return None
        
        # Header
        self._display_item_header(item, item_id)
        
        # Écouter
        print("  ⏳ Veuillez répondre...\n")
        recognized = self.recognizer.listen_for_answer(
            timeout=item.get("timeout", 10)
        )
        
        # Valider
        result = self._validate_item(item, recognized)
        
        # Afficher
        self._display_result(result)
        
        return result
    
    def _validate_item(self, item, recognized):
        """
        Valider un item selon son type
        
        Args:
            item (dict): Configuration de l'item
            recognized (str): Texte reconnu
        
        Returns:
            dict: Résultat validation
        """
        validation_type = item.get("validation_type")
        item_type = item.get("type")
        
        result = {"item": item, "recognized": recognized}
        
        if validation_type == "fuzzy_match":
            # Items 1-3 : fuzzy matching contre données patient
            if item_type == "NOM":
                expected = [self.patient.get("nom", "")]
            elif item_type == "LIEU":
                expected = [self.patient.get("operation", {}).get("site_operatoire", "")]
            elif item_type == "INTERVENTION":
                expected = [self.patient.get("operation", {}).get("type_intervention", "")]
            else:
                expected = item.get("expected_values", [])
            
            validation = self.validator.validate_fuzzy_match(recognized, expected)
        
        elif validation_type == "keyword_match":
            # Items 4-5, 9 : keyword matching
            validation = self.validator.validate_keyword_match(
                recognized,
                item.get("keywords", []),
                item.get("min_keywords", 1)
            )
        
        elif validation_type == "concept_detection":
            # Items 6, 8 : concept detection (NLP avancé)
            # TODO: Charger medical_vocabulary.json
            # validation = self.validator.validate_concept_detection(...)
            validation = {
                "valid": True,  # Placeholder
                "concepts": {},
                "required": item.get("min_count", 1),
                "score": 1,
                "status": "⚠️ CONCEPT DETECTION (À IMPLÉMENTER)"
            }
        
        else:
            validation = {"valid": False, "status": "❌ Type validation inconnu"}
        
        result.update(validation)
        return result
    
    def _display_item_header(self, item, numero):
        """Afficher header d'un item"""
        print("\n" + "="*60)
        print(f"  📋 ITEM {numero}/{len(self.checklist)} - {item.get('type', '')}")
        print("="*60)
        print(f"\n  ❓ {item.get('question', '')}")
        print(f"  💡 {item.get('hint', '')}")
        print()
    
    def _display_result(self, result):
        """Afficher résultat validation"""
        print("\n" + "="*60)
        print("  📊 RÉSULTAT VALIDATION")
        print("="*60)
        print()
        print(f"  Texte reconnu : '{result.get('recognized', '')}'")
        print(f"  Score : {result.get('score', 0)}%")
        print()
        print(f"  {result.get('status', '???')}")
        print()
        print("="*60)
    
    def _display_summary(self):
        """Afficher résumé final"""
        print("\n" + "="*60)
        print("  📊 RÉSUMÉ FINAL")
        print("="*60)
        
        valid_count = sum(1 for r in self.results if r.get('valid', False))
        total_count = len(self.results)
        
        print(f"\n  Items testés : {len(self.results)}/{len(self.checklist)}")
        print(f"  Items validés : {valid_count}/{total_count}")
        
        if total_count > 0:
            percentage = (valid_count / total_count) * 100
            print(f"  Taux de réussite : {percentage:.0f}%")
        
        print(f"\n  Détail :")
        for i, result in enumerate(self.results, 1):
            status_icon = "✅" if result.get('valid') else "❌"
            item_type = result.get('item', {}).get('type', '?')
            score = result.get('score', 0)
            print(f"    {i}. {status_icon} {item_type:15} - Score: {score:3}%")
        
        print()
        print("="*60)
        input("  ⏸️  Appuyez Entrée pour revenir au menu... ")


# Exemple d'utilisation
if __name__ == "__main__":
    from src.io.data_loader import DataLoader
    
    try:
        # Charger données
        config = DataLoader.load_config()
        patient = DataLoader.load_patient("P001")
        checklist = DataLoader.load_checklist()
        
        # Créer manager
        manager = ChecklistManager(checklist, patient, config)
        
        # Exécuter
        results = manager.run_full_checklist()
        
        # Résultats
        print(f"\n✅ Checklist terminée : {len(results)} items")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
