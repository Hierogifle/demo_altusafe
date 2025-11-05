# 🎤 Checklist Vocale Chirurgicale

Application de validation vocale pour checklist chirurgicale utilisant Vosk (reconnaissance vocale offline) et NLP (traitement langage naturel).

## ✨ Fonctionnalités

- ✅ **Reconnaissance vocale 100% offline** - Pas de cloud, données 100% locales
- ✅ **Validation intelligente** - Fuzzy matching + NLP avancé pour items complexes
- ✅ **Architecture propre** - Données séparées du code, configuration centralisée
- ✅ **Interface claire** - Micro activé uniquement lors des questions
- ✅ **Conforme RGPD** - Données sensibles jamais envoyées au cloud

## 🏗️ Architecture

```
projet_checklist/
├── README.md                    ← Documentation
├── requirements.txt             ← Dépendances Python
├── data/                        ← DONNÉES PURES
│   ├── patients/                ← Données patients
│   ├── templates/               ← Questions et vocabulaire
│   ├── config/                  ← Configuration app
│   └── models/                  ← Modèles Vosk
├── src/                         ← CODE SOURCE
│   ├── main.py                  ← Point d'entrée
│   ├── core/                    ← Logique métier
│   ├── nlp/                     ← Traitement NLP
│   ├── io/                      ← Input/Output
│   └── ui/                      ← Interface utilisateur
├── tests/                       ← Tests unitaires
└── venv/                        ← Environnement Python
```

## 📥 Installation Rapide

### Prérequis

- Python 3.7+
- pip
- Microphone fonctionnel

### Étapes

**1. Cloner/Télécharger le projet**

```bash
cd projet_checklist
```

**2. Créer virtualenv**

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Installer dépendances**

```bash
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
```

**4. Télécharger modèle Vosk**

```bash
# Depuis https://alphacephei.com/vosk/models
# Placer dans : data/models/vosk-model-small-fr-0.22/
```

**5. Vérifier structure**

```bash
# Vérifier fichiers JSON existent
ls data/patients/P001.json
ls data/templates/checklist_template.json
ls data/config/app_config.json
```

**6. Lancer**

```bash
python src/main.py
```

## 🚀 Utilisation

### Menu Principal

```
📋 MENU PRINCIPAL
1️⃣  Exécuter la checklist complète
2️⃣  Tester un item spécifique
3️⃣  Voir les infos patient
4️⃣  À propos
0️⃣  QUITTER
```

### Option 1 : Checklist Complète

- Valide tous les 9 items
- Affiche résultats en temps réel
- Génère résumé final avec scores

### Option 2 : Item Spécifique

- Choisir un item à tester
- Voir détails de validation
- Tester plusieurs fois

### Option 3 : Infos Patient

- Affiche données patient chargées
- Intervention prévue
- Équipe médicale

## 📁 Structure Détaillée

### data/ - Données Pures

```
data/
├── patients/                      ← Données patients uniquement
│   ├── P001.json                  ✅ Patient 1 (Marie Dupont)
│   ├── P002.json                  ✅ Patient 2 (Jean Martin)
│   └── P003.json                  ✅ Patient 3 (Pierre Bernard)
│
├── templates/                     ← Templates réutilisables
│   ├── checklist_template.json    ✅ Questions (6 items)
│   ├── medical_vocabulary.json    ✅ Vocabulaire médical
│   └── patient_template.json      ✅ Template pour nouveaux patients
│
├── config/                        ← Configuration centralisée
│   ├── app_config.json            ✅ Configuration app
│   └── validation_rules.json      ⚪ (Optionnel)
│
└── models/                        ← Modèles ML
    └── vosk-model-small-fr-0.22/  ← Reconnaissance vocale
        ├── am/
        ├── conf/
        └── graph/
```

### src/ - Code Source

```
src/
├── __init__.py
├── main.py                        ← Point d'entrée application
│
├── core/                          ← Logique métier
│   ├── __init__.py
│   ├── recognizer.py              ← Wrapper Vosk
│   ├── validator.py               ← Logique validation
│   └── checklist_manager.py       ← Gestion checklist
│
├── nlp/                           ← Traitement NLP
│   ├── __init__.py
│   ├── normalizer.py              ← Normalisation texte
│   ├── keyword_detector.py        ← Détection mots-clés
│   └── concept_extractor.py       ← Extraction concepts
│
├── io/                            ← Input/Output
│   ├── __init__.py
│   ├── data_loader.py             ← Charger JSON
│   ├── config_loader.py           ← Charger config
│   └── logger.py                  ← Logging
│
└── ui/                            ← Interface utilisateur
    ├── __init__.py
    ├── display.py                 ← Affichage console
    └── menus.py                   ← Menus interactifs
```

### tests/ - Tests Unitaires

```
tests/
├── test_validator.py              ← Tests validation
├── test_nlp.py                    ← Tests NLP
└── test_recognizer.py             ← Tests reconnaissance
```

## 📊 Items Checklist

### Items Simples (Fuzzy Matching)

```
1. Identité patient confirmée
   → Vérifier : nom reconnu == nom enregistré

2. Intervention prévue confirmée
   → Vérifier : intervention reconnue == intervention attendue

3. Site opératoire confirmé
   → Vérifier : site reconnu == site attendu

4. Installation correcte confirmée
   → Simple oui/non

5. Documents nécessaires disponibles
   → Simple oui/non
```

### Items Complexes (NLP Avancé)

```
6. Partage infos risques/étapes critiques
   → Détection concepts médicaux

7. Plan chirurgical (temps, matériels, points)
   → Détection mots-clés chirurgicaux

8. Plan anesthésique (risques, traitements)
   → Détection concepts anesthésie

9. Antibioprophylaxie selon protocole
   → Détection mots-clés antibioprophylaxie
```

## 🔧 Configuration

### app_config.json

```json
{
  "app": {
    "name": "Checklist Chirurgicale",
    "version": "2.0"
  },
  "vosk": {
    "model_path": "data/models/vosk-model-small-fr-0.22",
    "sample_rate": 16000,
    "blocksize": 4096
  },
  "audio": {
    "listen_timeout": 10,
    "enable_partial": true
  },
  "validation": {
    "fuzzy_threshold": 80,
    "fuzzy_threshold_strict": 90,
    "fuzzy_threshold_permissive": 70
  },
  "checklist": {
    "template_file": "data/templates/checklist_template.json",
    "vocabulary_file": "data/templates/medical_vocabulary.json",
    "stop_on_first_failure": false
  }
}
```

**À personnaliser :**
- `fuzzy_threshold` : Seuil de validation (%)
- `listen_timeout` : Durée d'écoute par item (sec)

## 📝 Données Patients

### Structure P001.json

```json
{
  "id": "P001",
  "nom": "marie dupont",
  "prenom": "marie",
  "date_naissance": "1965-05-15",
  "numero_dpi": "123456789",
  "operation": {
    "id": "OP001",
    "type_intervention": "cholecystectomie",
    "site_operatoire": "genou gauche",
    "date_prevue": "2025-11-06",
    "chirurgien": "Dr. Jean Martin",
    "anesthesiste": "Dr. Marie Durand"
  }
}
```

## 🧪 Tests

### Lancer tous les tests

```bash
pytest tests/
```

### Tests disponibles

| Fichier | Teste |
|---------|-------|
| `test_validator.py` | Validation fuzzy matching |
| `test_nlp.py` | Normalisation et NLP |
| `test_recognizer.py` | Wrapper Vosk |

### Exemple

```bash
# Tester validation
pytest tests/test_validator.py -v

# Tester avec couverture
pytest tests/ --cov=src
```

## 🔄 Workflows

### Ajouter un Nouveau Patient

**Étape 1 :** Créer `data/patients/P002.json`

```json
{
  "id": "P002",
  "nom": "jean martin",
  "prenom": "jean",
  "operation": {
    "type_intervention": "arthroplastie genou",
    "site_operatoire": "genou gauche"
  }
}
```

**Étape 2 :** Modifier `src/main.py`

```python
patient = DataLoader.load_patient("P002")
```

**Étape 3 :** Lancer

```bash
python src/main.py
```

### Ajouter une Question

Éditer `data/templates/checklist_template.json` :

```json
{
  "id": 7,
  "question": "Nouvelle question ?",
  "type": "NOUVEAU",
  "validation_type": "keyword_match",
  "keywords": ["oui", "yes"],
  "hint": "Répondez oui",
  "required": true,
  "timeout": 10
}
```

### Ajouter Vocabulaire Médical

Éditer `data/templates/medical_vocabulary.json` :

```json
{
  "concepts": {
    "risques": [
      "hypothermie", "allergie", "infection"
    ]
  }
}
```

## 🐛 Dépannage

### "Modèle Vosk non trouvé"

```bash
# Vérifier chemin
ls data/models/vosk-model-small-fr-0.22/
# Doit afficher : am/, conf/, graph/

# Si absent :
# 1. Télécharger depuis https://alphacephei.com/vosk/models
# 2. Placer dans data/models/
# 3. Renommer en vosk-model-small-fr-0.22
```

### "Fichier JSON non trouvé"

```bash
# Vérifier structure
ls -la data/patients/
ls -la data/templates/
ls -la data/config/

# Vérifier fichiers manquants et les télécharger
```

### "Aucun texte reconnu"

```bash
# Solutions :
1. Testez microphone avec autre app d'abord
2. Parlez plus fort et proche du microphone
3. Éliminez bruit ambiant
4. Augmentez listen_timeout dans config :
   "listen_timeout": 15
```

### "JSON invalide"

```bash
# Valider JSON
python -m json.tool data/patients/P001.json

# Si erreur :
# Vérifier virgules, guillemets, accolades
# Utiliser https://jsonlint.com/
```

## 📚 Documentation

| Fichier | Contenu |
|---------|---------|
| `STRUCTURE_FINALE.md` | Architecture détaillée |
| `bonnes_pratiques.md` | Best practices |
| `DOWNLOAD_SETUP.md` | Guide installation |
| `INSTALLATION_COMPLETE.md` | Setup complet |

## 🔗 Ressources

- **Vosk** : https://alphacephei.com/vosk/
- **spaCy** : https://spacy.io/
- **rapidfuzz** : https://github.com/maxbachmann/RapidFuzz
- **Python** : https://www.python.org/

## 📊 Technologies

| Tech | Utilisation |
|------|-------------|
| **Python 3.7+** | Langage principal |
| **Vosk** | Reconnaissance vocale offline |
| **spaCy** | Traitement NLP français |
| **rapidfuzz** | Fuzzy matching |
| **sounddevice** | Capture audio |
| **JSON** | Configuration et données |

## ✅ Checklist Avant Lancement

- [ ] Structure dossiers créée
- [ ] Fichiers JSON téléchargés
- [ ] `requirements.txt` installé
- [ ] Modèle Vosk téléchargé
- [ ] Modèle spaCy téléchargé
- [ ] Virtualenv activé
- [ ] Tests passent (`pytest tests/`)
- [ ] Microphone détecté

## 🚀 Première Exécution

```bash
# Activer virtualenv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Lancer application
python src/main.py

# Vous devez voir :
# 🎤 CHECKLIST VOCALE - RECONNAISSANCE + VALIDATION NLP
# 📋 MENU PRINCIPAL
# ...
```

## 📄 Licence

Développé pour application checklist chirurgicale.
À adapter selon vos besoins.

## 👨‍💼 Support

Pour questions ou problèmes :

1. Vérifier structure des dossiers
2. Consulter section Dépannage
3. Vérifier fichiers JSON valides
4. Vérifier imports Python

---

**Version 2.0 - Architecture Cleancode** 🏆

Données séparées | Configuration centralisée | Code modulaire | 100% Offline
