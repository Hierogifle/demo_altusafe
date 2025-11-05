"""
DataLoader - Chargement des données JSON

Module pour charger tous les fichiers JSON :
- Configuration app
- Données patients
- Template checklist
- Vocabulaire médical
- Règles validation
"""

import json
import os
from pathlib import Path


class DataLoader:
    """
    Charge les fichiers JSON de configuration et données
    Gère les chemins relatifs et erreurs
    """
    
    # Chemins par défaut (relatifs à racine projet)
    DEFAULT_PATHS = {
        "config": "data/config/app_config.json",
        "config_complet": "data/config/app_config_COMPLET.json",
        "validation_rules": "data/config/validation_rules.json",
        "validation_rules_complet": "data/config/validation_rules_COMPLET.json",
        "checklist_template": "data/templates/checklist_template.json",
        "checklist_template_complet": "data/templates/checklist_template_COMPLET.json",
        "medical_vocabulary": "data/templates/medical_vocabulary.json",
        "medical_vocabulary_complet": "data/templates/medical_vocabulary_COMPLET.json",
        "patient_template": "data/templates/patient_template.json",
        "patients_dir": "data/patients/"
    }
    
    @staticmethod
    def _get_absolute_path(relative_path):
        """
        Convertir chemin relatif en absolu
        
        Args:
            relative_path (str): Chemin relatif depuis racine projet
        
        Returns:
            str: Chemin absolu
        """
        # Depuis racine projet
        project_root = Path(__file__).parent.parent.parent
        absolute_path = project_root / relative_path
        return str(absolute_path)
    
    @staticmethod
    def load_json(filepath):
        """
        Charger fichier JSON
        
        Args:
            filepath (str): Chemin fichier (relatif ou absolu)
        
        Returns:
            dict: Données JSON
        
        Raises:
            FileNotFoundError: Si fichier n'existe pas
            json.JSONDecodeError: Si JSON invalide
        
        Exemple:
            >>> data = DataLoader.load_json("data/config/app_config.json")
        """
        try:
            # Convertir en chemin absolu si relatif
            if not os.path.isabs(filepath):
                filepath = DataLoader._get_absolute_path(filepath)
            
            # Vérifier existence
            if not os.path.exists(filepath):
                raise FileNotFoundError(
                    f"Fichier non trouvé : {filepath}"
                )
            
            # Charger JSON
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
        
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Erreur JSON : {filepath}\n{e.msg}",
                e.doc,
                e.pos
            )
    
    @staticmethod
    def load_config(use_complet=True):
        """
        Charger configuration app
        
        Args:
            use_complet (bool): Utiliser version _COMPLET ?
        
        Returns:
            dict: Configuration app
        
        Raises:
            FileNotFoundError: Si fichier non trouvé
        """
        key = "config_complet" if use_complet else "config"
        path = DataLoader.DEFAULT_PATHS[key]
        
        return DataLoader.load_json(path)
    
    @staticmethod
    def load_validation_rules(use_complet=True):
        """
        Charger règles validation
        
        Args:
            use_complet (bool): Utiliser version _COMPLET ?
        
        Returns:
            dict: Règles validation
        """
        key = "validation_rules_complet" if use_complet else "validation_rules"
        path = DataLoader.DEFAULT_PATHS[key]
        
        return DataLoader.load_json(path)
    
    @staticmethod
    def load_checklist_template(use_complet=True):
        """
        Charger template checklist
        
        Args:
            use_complet (bool): Utiliser version _COMPLET ?
        
        Returns:
            dict: Template checklist
        
        Exemple:
            >>> checklist = DataLoader.load_checklist_template()
            >>> print(f"Items : {len(checklist['items'])}")
        """
        key = "checklist_template_complet" if use_complet else "checklist_template"
        path = DataLoader.DEFAULT_PATHS[key]
        
        return DataLoader.load_json(path)
    
    @staticmethod
    def load_medical_vocabulary(use_complet=True):
        """
        Charger vocabulaire médical
        
        Args:
            use_complet (bool): Utiliser version _COMPLET ?
        
        Returns:
            dict: Vocabulaire médical
        
        Exemple:
            >>> vocab = DataLoader.load_medical_vocabulary()
            >>> print(f"Concepts : {vocab['concepts'].keys()}")
        """
        key = "medical_vocabulary_complet" if use_complet else "medical_vocabulary"
        path = DataLoader.DEFAULT_PATHS[key]
        
        return DataLoader.load_json(path)
    
    @staticmethod
    def load_patient(patient_id):
        """
        Charger données patient
        
        Args:
            patient_id (str): ID patient (ex: "P001")
        
        Returns:
            dict: Données patient
        
        Raises:
            FileNotFoundError: Si patient n'existe pas
        
        Exemple:
            >>> patient = DataLoader.load_patient("P001")
            >>> print(f"Patient : {patient['nom']}")
        """
        patients_dir = DataLoader.DEFAULT_PATHS["patients_dir"]
        filepath = os.path.join(patients_dir, f"{patient_id}.json")
        
        return DataLoader.load_json(filepath)
    
    @staticmethod
    def load_patient_template():
        """
        Charger template patient vide
        
        Returns:
            dict: Template patient
        """
        path = DataLoader.DEFAULT_PATHS["patient_template"]
        return DataLoader.load_json(path)
    
    @staticmethod
    def list_patients():
        """
        Lister tous les patients disponibles
        
        Returns:
            list: Fichiers JSON trouvés
        
        Exemple:
            >>> patients = DataLoader.list_patients()
            >>> print(patients)
            ['P001.json', 'P002.json', 'P003.json']
        """
        patients_dir = DataLoader.DEFAULT_PATHS["patients_dir"]
        patients_abs = DataLoader._get_absolute_path(patients_dir)
        
        if not os.path.exists(patients_abs):
            return []
        
        patients = [
            f for f in os.listdir(patients_abs)
            if f.endswith('.json')
        ]
        
        return sorted(patients)
    
    @staticmethod
    def load_all_patients():
        """
        Charger tous les patients
        
        Returns:
            dict: {patient_id: données}
        
        Exemple:
            >>> all_patients = DataLoader.load_all_patients()
            >>> for pid, data in all_patients.items():
            ...     print(f"{pid}: {data['nom']}")
        """
        patients_files = DataLoader.list_patients()
        all_patients = {}
        
        for filename in patients_files:
            patient_id = filename.replace('.json', '')
            try:
                all_patients[patient_id] = DataLoader.load_patient(patient_id)
            except Exception as e:
                print(f"⚠️  Erreur chargement {patient_id} : {e}")
        
        return all_patients
    
    @staticmethod
    def save_json(filepath, data):
        """
        Sauvegarder données en JSON
        
        Args:
            filepath (str): Chemin fichier
            data (dict): Données à sauvegarder
        
        Raises:
            IOError: Si erreur écriture
        
        Exemple:
            >>> DataLoader.save_json("data/results.json", {"status": "ok"})
        """
        try:
            # Convertir en chemin absolu si relatif
            if not os.path.isabs(filepath):
                filepath = DataLoader._get_absolute_path(filepath)
            
            # Créer dossier si nécessaire
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Sauvegarder
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except IOError as e:
            raise IOError(f"Erreur écriture {filepath} : {e}")
    
    @staticmethod
    def verify_all_files():
        """
        Vérifier que tous les fichiers requis existent
        
        Returns:
            dict: {fichier: existe (bool)}
        
        Exemple:
            >>> status = DataLoader.verify_all_files()
            >>> for file, exists in status.items():
            ...     print(f"{'✅' if exists else '❌'} {file}")
        """
        status = {}
        
        for name, path in DataLoader.DEFAULT_PATHS.items():
            if name.endswith("_dir"):
                # Vérifier dossier
                abs_path = DataLoader._get_absolute_path(path)
                status[name] = os.path.isdir(abs_path)
            else:
                # Vérifier fichier
                abs_path = DataLoader._get_absolute_path(path)
                status[name] = os.path.isfile(abs_path)
        
        return status


# Exemple d'utilisation
if __name__ == "__main__":
    print("=== DataLoader Tests ===\n")
    
    try:
        # Test 1 - Vérifier tous les fichiers
        print("1️⃣  Vérification fichiers...")
        status = DataLoader.verify_all_files()
        for name, exists in status.items():
            icon = "✅" if exists else "❌"
            print(f"  {icon} {name}")
        
        # Test 2 - Charger config
        print("\n2️⃣  Chargement configuration...")
        config = DataLoader.load_config()
        print(f"  ✅ Config chargée : v{config.get('app', {}).get('version', '?')}")
        
        # Test 3 - Charger patient
        print("\n3️⃣  Chargement patient...")
        patient = DataLoader.load_patient("P001")
        print(f"  ✅ Patient : {patient.get('nom', '?')} {patient.get('prenom', '?')}")
        
        # Test 4 - Lister patients
        print("\n4️⃣  Patients disponibles...")
        patients = DataLoader.list_patients()
        for p in patients:
            print(f"  - {p}")
        
        print("\n✅ Tous les tests passés !")
    
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
