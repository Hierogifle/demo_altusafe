"""
Menus - Menus interactifs

Module pour gérer les menus interactifs :
- Menu principal
- Menus de sélection
- Navigation menus
"""

from typing import Optional, Callable, Dict
from .display import Display


class Menus:
    """
    Gère les menus interactifs de l'application
    """
    
    @staticmethod
    def main_menu() -> str:
        """
        Afficher menu principal
        
        Returns:
            str: Choix utilisateur (0-5)
        
        Exemple:
            >>> choice = Menus.main_menu()
            >>> if choice == "1":
            ...     run_full_checklist()
        """
        Display.clear_screen()
        
        print("\n" + "="*60)
        print("  📋 MENU PRINCIPAL")
        print("="*60)
        print("\n  1️⃣  Exécuter la checklist complète")
        print("  2️⃣  Tester un item spécifique")
        print("  3️⃣  Changer de patient")
        print("  4️⃣  Voir infos patient")
        print("  5️⃣  À propos")
        print("  0️⃣  QUITTER\n")
        
        choice = input("  ➡️  Votre choix (0-5) : ").strip()
        return choice
    
    @staticmethod
    def patient_menu(patients: Dict[str, str]) -> Optional[str]:
        """
        Menu sélection patient
        
        Args:
            patients (dict): {patient_id: patient_name}
        
        Returns:
            str: Patient ID sélectionné ou None
        
        Exemple:
            >>> patients = {"P001": "Marie Dupont", "P002": "Jean Martin"}
            >>> selected = Menus.patient_menu(patients)
        """
        Display.clear_screen()
        
        print("\n" + "="*60)
        print("  👤 SÉLECTIONNER PATIENT")
        print("="*60 + "\n")
        
        patient_list = list(patients.items())
        
        for idx, (pid, name) in enumerate(patient_list, 1):
            print(f"  {idx}. {name} ({pid})")
        
        print(f"  0. Annuler\n")
        
        try:
            choice = int(input("  ➡️  Votre choix : "))
            
            if choice == 0:
                return None
            
            if 1 <= choice <= len(patient_list):
                return patient_list[choice - 1][0]
        
        except ValueError:
            pass
        
        return None
    
    @staticmethod
    def items_menu(items: list) -> Optional[int]:
        """
        Menu sélection item
        
        Args:
            items (list): Liste items avec id, type, question
        
        Returns:
            int: Item ID ou None
        """
        Display.clear_screen()
        
        print("\n" + "="*60)
        print("  🔧 TESTER UN ITEM")
        print("="*60)
        print("\n  Items disponibles :\n")
        
        for item in items:
            item_id = item.get("id")
            item_type = item.get("type")
            question = item.get("question", "?")[:50]
            
            print(f"  {item_id}. {item_type:15} - {question}...")
        
        print(f"  0. Retour au menu\n")
        
        try:
            choice = int(input("  ➡️  Votre choix : "))
            
            if choice == 0:
                return None
            
            if 1 <= choice <= len(items):
                return choice
        
        except ValueError:
            pass
        
        return None
    
    @staticmethod
    def confirm_menu(message: str, default: bool = True) -> bool:
        """
        Menu confirmation (oui/non)
        
        Args:
            message (str): Message confirmation
            default (bool): Réponse par défaut
        
        Returns:
            bool: Réponse utilisateur
        
        Exemple:
            >>> if Menus.confirm_menu("Êtes-vous sûr ?"):
            ...     do_something()
        """
        suffix = " [O/n] " if default else " [o/N] "
        response = input(f"\n  {message}{suffix}").strip().lower()
        
        if response == "":
            return default
        
        return response in ['o', 'oui', 'yes', 'y']
    
    @staticmethod
    def pause_menu(message: str = "Appuyez Entrée pour continuer..."):
        """
        Menu pause
        
        Args:
            message (str): Message affichage
        """
        input(f"\n  {message}")
    
    @staticmethod
    def settings_menu() -> Optional[str]:
        """
        Menu paramètres
        
        Returns:
            str: Option sélectionnée
        """
        Display.clear_screen()
        
        print("\n" + "="*60)
        print("  ⚙️  PARAMÈTRES")
        print("="*60)
        print("\n  1️⃣  Debug mode")
        print("  2️⃣  Logging level")
        print("  3️⃣  Timeout")
        print("  4️⃣  Fuzzy threshold")
        print("  0️⃣  Retour\n")
        
        choice = input("  ➡️  Votre choix (0-4) : ").strip()
        return choice
    
    @staticmethod
    def about_menu():
        """Afficher À propos"""
        Display.clear_screen()
        
        print("\n" + "="*60)
        print("  ℹ️  À PROPOS")
        print("="*60)
        
        print("""
  VERSION : 2.0
  
  Technologie :
    • Vosk (Reconnaissance vocale offline)
    • spaCy (Traitement NLP français)
    • rapidfuzz (Fuzzy matching)
    • Python 3.7+
  
  Fonctionnalités :
    ✓ Reconnaissance vocale 100% offline
    ✓ Micro activé uniquement lors des questions
    ✓ Validation fuzzy matching + NLP avancé
    ✓ Support vocabulaire médical français
    ✓ Conforme RGPD - données 100% locales
    ✓ 9 items checklist chirurgicale
  
  Architecture :
    • Données séparées du code
    • Configuration centralisée
    • Code modulaire et testable
    • Logging complet
        """)
        
        Menus.pause_menu()
    
    @staticmethod
    def error_menu(error_message: str):
        """
        Afficher erreur
        
        Args:
            error_message (str): Message erreur
        """
        Display.clear_screen()
        
        print("\n" + "="*60)
        print("  ❌ ERREUR")
        print("="*60)
        print(f"\n  {error_message}\n")
        print("="*60)
        
        Menus.pause_menu()
    
    @staticmethod
    def success_menu(message: str):
        """
        Afficher succès
        
        Args:
            message (str): Message succès
        """
        Display.clear_screen()
        
        print("\n" + "="*60)
        print("  ✅ SUCCÈS")
        print("="*60)
        print(f"\n  {message}\n")
        print("="*60)
        
        Menus.pause_menu()
    
    @staticmethod
    def loading_menu(title: str, steps: list):
        """
        Afficher écran loading
        
        Args:
            title (str): Titre loading
            steps (list): Étapes ["Chargement config", "Chargement patient", ...]
        """
        Display.clear_screen()
        
        print("\n" + "="*60)
        print(f"  ⏳ {title}")
        print("="*60 + "\n")
        
        for step in steps:
            print(f"  • {step}")
        
        print()
    
    @staticmethod
    def patient_info_menu(patient: dict):
        """
        Afficher informations patient
        
        Args:
            patient (dict): Données patient
        """
        Display.clear_screen()
        
        print("\n" + "="*60)
        print("  👤 INFORMATIONS PATIENT")
        print("="*60)
        
        print(f"\n  Identité :")
        print(f"    Nom : {patient.get('nom', '?')} {patient.get('prenom', '?')}")
        print(f"    ID : {patient.get('id', '?')}")
        print(f"    DPI : {patient.get('numero_dpi', '?')}")
        print(f"    Date naissance : {patient.get('date_naissance', '?')}")
        
        operation = patient.get('operation', {})
        print(f"\n  Intervention :")
        print(f"    Type : {operation.get('type_intervention', '?')}")
        print(f"    Site : {operation.get('site_operatoire', '?')}")
        print(f"    Côté : {operation.get('cote', '?')}")
        print(f"    Date prévue : {operation.get('date_prevue', '?')}")
        print(f"    Chirurgien : {operation.get('chirurgien', '?')}")
        print(f"    Anesthésiste : {operation.get('anesthesiste', '?')}")
        
        print("\n" + "="*60)
        Menus.pause_menu()


# Exemple d'utilisation
if __name__ == "__main__":
    print("=== Menus Tests ===\n")
    
    # Test menu principal
    # choice = Menus.main_menu()
    # print(f"Choix : {choice}")
    
    # Test menu patient
    patients = {
        "P001": "Marie Dupont",
        "P002": "Jean Martin",
        "P003": "Pierre Bernard"
    }
    # selected = Menus.patient_menu(patients)
    # print(f"Patient sélectionné : {selected}")
    
    # Test confirmation
    # if Menus.confirm_menu("Êtes-vous sûr ?"):
    #     print("Confirmé !")
    
    # Test À propos
    Menus.about_menu()
    
    print("✅ Tests terminés")
