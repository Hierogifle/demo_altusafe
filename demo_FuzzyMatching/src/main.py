"""
main.py - Point d'entrée de l'application

Orchestre l'exécution complète de l'application checklist vocale
"""

import sys
import time
from io.data_loader import DataLoader
from core import ChecklistRecognizer, Validator, ChecklistManager
from ui.display import Display
from ui.menus import MainMenu


class Application:
    """
    Application principale pour checklist chirurgicale
    Gère : menu principal, chargement données, exécution checklist
    """
    
    def __init__(self):
        """Initialiser l'application"""
        self.config = None
        self.patient = None
        self.checklist_template = None
        self.medical_vocabulary = None
        self.manager = None
    
    def load_configuration(self):
        """
        Charger toute la configuration et données
        
        Raises:
            FileNotFoundError: Si fichiers manquants
            RuntimeError: Si erreur configuration
        """
        try:
            print("⚙️  Chargement configuration...\n")
            
            # Charger config app
            self.config = DataLoader.load_config()
            print("✅ Configuration app")
            
            # Charger template checklist
            self.checklist_template = DataLoader.load_checklist_template()
            print("✅ Template checklist")
            
            # Charger vocabulaire médical
            self.medical_vocabulary = DataLoader.load_medical_vocabulary()
            print("✅ Vocabulaire médical")
            
            # Charger patient par défaut
            self.patient = DataLoader.load_patient("P001")
            print("✅ Données patient\n")
            
        except FileNotFoundError as e:
            print(f"❌ ERREUR : Fichier non trouvé\n{e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ ERREUR : {e}")
            sys.exit(1)
    
    def initialize_manager(self):
        """Initialiser le manager checklist"""
        try:
            self.manager = ChecklistManager(
                self.checklist_template,
                self.patient,
                self.config
            )
        except Exception as e:
            print(f"❌ ERREUR initialisation : {e}")
            sys.exit(1)
    
    def display_banner(self):
        """Afficher bannière de démarrage"""
        Display.print_banner(
            "🎤 CHECKLIST VOCALE CHIRURGICALE",
            "Reconnaissance Vocale + NLP + Validation"
        )
    
    def show_main_menu(self):
        """Afficher et gérer le menu principal"""
        while True:
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
            
            if choice == "0":
                self.exit_application()
            
            elif choice == "1":
                self.run_full_checklist()
            
            elif choice == "2":
                self.run_single_item()
            
            elif choice == "3":
                self.change_patient()
            
            elif choice == "4":
                self.show_patient_info()
            
            elif choice == "5":
                self.show_about()
            
            else:
                print("  ❌ Choix invalide, réessayez")
                time.sleep(1)
    
    def run_full_checklist(self):
        """Exécuter la checklist complète"""
        try:
            results = self.manager.run_full_checklist()
            print("\n✅ Checklist terminée")
            input("Appuyez Entrée pour continuer...")
        except KeyboardInterrupt:
            print("\n\n⏹️  Programme interrompu")
        except Exception as e:
            print(f"\n❌ Erreur : {e}")
            input("Appuyez Entrée pour continuer...")
    
    def run_single_item(self):
        """Exécuter un item spécifique"""
        Display.clear_screen()
        
        print("\n" + "="*60)
        print("  🔧 TESTER UN ITEM SPÉCIFIQUE")
        print("="*60)
        print("\n  Items disponibles :")
        
        for item in self.checklist_template.get("items", []):
            item_id = item.get("id")
            item_type = item.get("type")
            question = item.get("question", "?")[:40]
            print(f"  {item_id}. {item_type:15} - {question}...")
        
        print(f"  0. Retour au menu\n")
        
        choice = input("  ➡️  Votre choix : ").strip()
        
        if choice == "0":
            return
        
        try:
            item_id = int(choice)
            result = self.manager.run_single_item(item_id)
            
            if result:
                print("\n✅ Item testé")
            
            input("\nAppuyez Entrée pour continuer...")
        
        except ValueError:
            print("  ❌ Entrée invalide")
            time.sleep(1)
        except Exception as e:
            print(f"  ❌ Erreur : {e}")
            time.sleep(1)
    
    def change_patient(self):
        """Changer de patient"""
        Display.clear_screen()
        
        print("\n" + "="*60)
        print("  👤 CHANGER DE PATIENT")
        print("="*60)
        print("\n  Patients disponibles :")
        print("  1. P001 - Marie Dupont")
        print("  2. P002 - Jean Martin")
        print("  3. P003 - Pierre Bernard")
        print("  0. Annuler\n")
        
        choice = input("  ➡️  Votre choix : ").strip()
        
        if choice == "0":
            return
        
        try:
            if choice == "1":
                patient_id = "P001"
            elif choice == "2":
                patient_id = "P002"
            elif choice == "3":
                patient_id = "P003"
            else:
                print("  ❌ Choix invalide")
                time.sleep(1)
                return
            
            # Charger patient
            self.patient = DataLoader.load_patient(patient_id)
            
            # Réinitialiser manager
            self.initialize_manager()
            
            print(f"  ✅ Patient changé : {self.patient.get('nom', '?')}")
            time.sleep(1)
        
        except Exception as e:
            print(f"  ❌ Erreur : {e}")
            time.sleep(1)
    
    def show_patient_info(self):
        """Afficher infos patient"""
        Display.clear_screen()
        
        print("\n" + "="*60)
        print("  👤 INFORMATIONS PATIENT")
        print("="*60)
        
        print(f"\n  Nom : {self.patient.get('nom', '?')} {self.patient.get('prenom', '?')}")
        print(f"  ID Patient : {self.patient.get('id', '?')}")
        print(f"  DPI : {self.patient.get('numero_dpi', '?')}")
        print(f"  Date naissance : {self.patient.get('date_naissance', '?')}")
        
        print(f"\n  Intervention : {self.patient.get('operation', {}).get('type_intervention', '?')}")
        print(f"  Site : {self.patient.get('operation', {}).get('site_operatoire', '?')}")
        print(f"  Côté : {self.patient.get('operation', {}).get('cote', '?')}")
        print(f"  Date prévue : {self.patient.get('operation', {}).get('date_prevue', '?')}")
        print(f"  Chirurgien : {self.patient.get('operation', {}).get('chirurgien', '?')}")
        print(f"  Anesthésiste : {self.patient.get('operation', {}).get('anesthesiste', '?')}")
        
        print()
        input("Appuyez Entrée pour continuer...")
    
    def show_about(self):
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
  
  Auteur : Développé pour application médicale
  
  Dépendances :
    • sounddevice
    • vosk
    • rapidfuzz
    • spacy
  
  Architecture :
    • Données séparées du code
    • Configuration centralisée
    • Code modulaire et testable
        """)
        
        input("Appuyez Entrée pour continuer...")
    
    def exit_application(self):
        """Quitter l'application"""
        Display.clear_screen()
        print("\n  👋 Au revoir !\n")
        sys.exit(0)
    
    def run(self):
        """
        Lancer l'application complètement
        Workflow principal
        """
        try:
            # Bannière
            self.display_banner()
            
            # Charger configuration
            self.load_configuration()
            
            # Initialiser manager
            self.initialize_manager()
            
            # Menu principal
            self.show_main_menu()
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Application interrompue")
            sys.exit(0)
        
        except Exception as e:
            print(f"\n❌ ERREUR NON GÉRÉE : {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    app = Application()
    app.run()