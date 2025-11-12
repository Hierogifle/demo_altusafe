# Altusafe – Validation vocale des fiches opératoires

Ce dépôt rassemble tout le nécessaire pour valider oralement les fiches patient/intervention **en français** : données synthétiques, notebooks d’entraînement, moteur de rapprochement texte/voix et scripts temps réel basés sur **Vosk (modèle large fr 0.22)**. L’objectif est de lire chaque champ d’une fiche, écouter la confirmation vocale, puis décider automatiquement si l’information entendue correspond à la référence.

## Organisation du dépôt

```
data/
  fiches/                 # Fiches JSON sources et sorties *_validated.json
  new_ pairs.tsv          # Corpus augmenté (4091 lignes) texte ↔ cible ↔ label
  pairs_checklist_180k.tsv# Corpus historique (mêmes colonnes)
final/
  match.py                # Moteur de matching empaqueté pour les scripts finaux
  validate_fiche.py       # Orchestrateur de validation vocale
  encoder_embed.tflite    # (à placer ici) encodeur TFLite exporté depuis matching2.ipynb
  char_vocab_embed.txt    # (à placer ici) vocabulaire caractères pour l’encodeur
notebook/
  matching.ipynb          # Exploration des paires & prototypage de règles
  matching2.ipynb         # Entraînement du modèle caractère et export TFLite + vocab
src/
  match.py                # Implémentation principale du MatchEngine
  speech_recognizer.py    # Wrapper Vosk + PyAudio (écoute bloquante)
  speech2text.py          # Petit utilitaire de dictée continue
  vosk_checker.py         # Vérifie un enregistrement/micro vs une fiche JSON
```

## Jeux de données

- `data/fiches/*.json` décrit les dossiers patients (civilité, identité, intervention, salle, bloc, chirurgien, etc.). Les fichiers `*_validated.json` sont produits par `final/validate_fiche.py` après une session de validation.
- `data/new_ pairs.tsv` et `data/pairs_checklist_180k.tsv` contiennent les phrases d’entraînement utilisées par les notebooks. Chaque ligne suit `texte\tcible\tlabel` où `label` vaut `1.0` (appartenance) ou `0.0` (négatif). Les corpus incluent des variantes d’identité, d’horaires, de salles/blocs (« bloc trois = salle trois »), de rôles (chirurgien/anesthésiste) et d’actes opératoires afin de couvrir les formulations naturelles en lettres.

## Notebooks d’entraînement

1. **`notebook/matching.ipynb`** : nettoie et inspecte les paires TSV, teste des règles simples (normalisation, trigrammes) et construit les premiers seuils OK / INCERTAIN / KO.
2. **`notebook/matching2.ipynb`** : entraîne un encodeur caractère (tf.keras) sur les mêmes paires, fusionne scores embedding + n‑grammes puis exporte :
   - `encoder_embed.tflite` (modèle léger pour l’inférence locale) ;
   - `char_vocab_embed.txt` (alphabet trié par fréquence).
   Ces artefacts sont consommés par `MatchEngine` côté `src/` et copiés dans `final/` pour les démos hors-notebook.

## MatchEngine (src/match.py & final/match.py)

- Normalise les textes (minuscules, retrait des accents, filtrage chars).
- Vectorise via le vocabulaire caractères puis :
  - encode les fenêtres de mots de l’énoncé avec le modèle TFLite,
  - calcule un score cosine embedding + un score n-grammes,
  - agrège les deux (70 % embedding, 30 % n-grammes) et applique les seuils (`OK ≥ 0.88`, `INCERTAIN ≥ 0.70`).
- Fournit `match_utterance_to_candidates(utterance, candidates, require_overlap_for_names)` qui retourne une liste triée `(candidat, score, meilleur_span, décision, score_embed, score_ngram)`.

Cette classe est utilisée partout où un texte reconnu doit être rapproché d’une liste de valeurs attendues (noms, heures, salles, opérations…).

## Validation interactive (`final/validate_fiche.py`)

1. Charge la fiche JSON (`data/fiches/P*.json`).
2. Essaie d’instancier `MatchEngine` en priorité avec `final/encoder_embed.tflite` et `final/char_vocab_embed.txt` (sinon chemins par défaut).
3. Ouvre un micro via `SpeechRecognizer` (Vosk Large FR) et itère sur chaque champ de la fiche (chemin JSON → valeur).
4. Pour chaque champ :
   - invite l’utilisateur à prononcer la valeur,
   - compare la transcription normalisée aux variantes attendues via `MatchEngine` (fallback `difflib` si indisponible),
   - boucle tant que la décision n’est pas `OK` ou que l’utilisateur ne dit pas “terminé”.
5. Écrit `*_validated.json` contenant la fiche originale et l’historique des tentatives.

Exemple :

```bash
python final/validate_fiche.py data/fiches/P1.json --model /chemin/vers/vosk-model-fr-0.22
```

> ⚠️ Le script attend le **modèle Vosk large français 0.22** (≈1,8 Go). Téléchargez-le depuis https://alphacephei.com/vosk/models et placez-le, par exemple, dans `vosk-model-fr-0.22/`. Spécifiez le chemin via `--model` ou `VOSK_MODEL`.

## Autres scripts voix

- `src/vosk_checker.py` : lit une fiche JSON, prépare les candidats (noms, dates, type d’intervention), transcrit un micro ou un WAV via Vosk Large, puis score chaque champ avec `MatchEngine`. Utile pour tester rapidement des enregistrements ou ajuster les seuils.
- `src/speech2text.py` : boucle minimale de dictée (Vosk Large + PyAudio) qui écrit chaque résultat dans `recognized_text.txt`. Sert de check matériel/audio.
- `src/speech_recognizer.py` : contexte `with` simplifiant l’accès micro + modèle Vosk (utilisé par `validate_fiche.py`).

## Pré-requis & installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install vosk==0.3.45 pyaudio numpy tensorflow==2.13.0
# + autres dépendances éventuelles (jupyter, notebook, pandas) pour relancer les notebooks
```

Placez ensuite les fichiers suivants :

- `vosk-model-fr-0.22` (modèle large) dans un dossier accessible, ou définissez `VOSK_MODEL`.
- `encoder_embed.tflite` et `char_vocab_embed.txt` à la racine du repo ou dans `final/` suivant vos chemins de lancement.

## Relancer l’entraînement

1. Mettre à jour `data/new_ pairs.tsv` / `pairs_checklist_180k.tsv` avec les nouvelles formulations (toutes lettres, variations de salles/blocs, etc.).
2. Ouvrir `notebook/matching2.ipynb`, ré-exécuter les cellules d’entraînement/export ; récupérer les nouveaux artefacts `.tflite` + vocab.
3. Copier ces artefacts dans `src/` (pour les scripts) et `final/` (pour les livrables), puis re-tester `final/validate_fiche.py` ou `src/vosk_checker.py`.

Ainsi, les fiches JSON, les textes d’apprentissage, les notebooks et les scripts de validation restent alignés et exploitent la même logique de reconnaissance vocale basée sur **Vosk Large FR**.
