"""
Wrapper Vosk - Reconnaissance vocale offline

Module pour :
- Initialiser modèle Vosk
- Capturer audio du microphone
- Retourner texte reconnu
- Gérer timeouts et erreurs
"""

import json
import queue
import os
import sys
import time
from vosk import Model, KaldiRecognizer, SetLogLevel
import sounddevice as sd

# Silencer logs Vosk
SetLogLevel(-1)


class ChecklistRecognizer:
    """
    Wrapper Vosk pour reconnaissance vocale
    Gère : initialisation, capture audio, timeout
    """
    
    def __init__(self, model_path, sample_rate=16000, blocksize=4096):
        """
        Initialiser le modèle Vosk
        
        Args:
            model_path (str): Chemin vers modèle Vosk
            sample_rate (int): Fréquence d'échantillonnage (Hz)
            blocksize (int): Taille du buffer audio
        
        Raises:
            FileNotFoundError: Si modèle non trouvé
            RuntimeError: Si erreur chargement modèle
        """
        self.sample_rate = sample_rate
        self.blocksize = blocksize
        self.audio_queue = queue.Queue()
        
        # Vérifier modèle existe
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"❌ Modèle Vosk non trouvé\n"
                f"   Recherché : {os.path.abspath(model_path)}\n"
                f"   Télécharger depuis : https://alphacephei.com/vosk/models"
            )
        
        # Charger modèle
        try:
            print(f"📦 Chargement modèle Vosk...")
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            print(f"✅ Modèle chargé\n")
        except Exception as e:
            raise RuntimeError(f"❌ Erreur chargement modèle : {e}")
    
    def audio_callback(self, indata, frames, time_info, status):
        """
        Callback pour capturer l'audio
        Appelé automatiquement par sounddevice
        """
        if status:
            pass  # Ignorer status messages
        self.audio_queue.put(bytes(indata))
    
    def listen_for_answer(self, timeout=10, show_partial=True):
        """
        Écouter une réponse vocale
        
        Args:
            timeout (int): Durée d'écoute max (sec)
            show_partial (bool): Afficher reconnaissance partielle
        
        Returns:
            str: Texte reconnu
        
        Note:
            - Micro activé UNIQUEMENT pendant cette fonction
            - Micro fermé après (économie ressources)
        """
        recognized = ""
        start_time = time.time()
        
        try:
            # OUVERTURE MICRO
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=self.blocksize,
                dtype='int16',
                channels=1,
                callback=self.audio_callback,
                latency='low'
            ):
                print("   🎤 Micro ACTIF - Parlez maintenant...")
                print("   " + "-" * 50)
                
                # Boucle d'écoute
                while time.time() - start_time < timeout:
                    try:
                        data = self.audio_queue.get(timeout=0.3)
                        
                        # Traiter audio
                        if self.recognizer.AcceptWaveform(data):
                            # RÉSULTAT FINAL
                            result = json.loads(self.recognizer.Result())
                            recognized = result.get('text', '')
                            
                            if recognized:
                                print(f"   ✅ Phrase reconnue : '{recognized}'")
                                print("   " + "-" * 50)
                                break
                        else:
                            # Affichage partiel (temps réel)
                            if show_partial:
                                partial = json.loads(self.recognizer.PartialResult())
                                partial_text = partial.get('partial', '')
                                if partial_text:
                                    elapsed = time.time() - start_time
                                    print(f"   💬 [{elapsed:.1f}s] {partial_text}", end='\r', flush=True)
                    
                    except queue.Empty:
                        continue
                
                # Vérifier timeout
                if not recognized:
                    print("\n   ⏱️  TIMEOUT - Aucun texte reconnu")
                    print("   " + "-" * 50)
        
        except Exception as e:
            print(f"   ❌ Erreur microphone : {e}")
            print("   Vérifiez que votre microphone fonctionne correctement")
            print("   " + "-" * 50)
        
        # FERMETURE MICRO (hors du bloc with)
        return recognized
    
    def reset_recognizer(self):
        """Réinitialiser le recognizer pour nouvel audio"""
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)


# Exemple d'utilisation
if __name__ == "__main__":
    try:
        # Initialiser
        recognizer = ChecklistRecognizer("data/models/vosk-model-small-fr-0.22")
        
        # Écouter
        text = recognizer.listen_for_answer(timeout=10)
        print(f"\nRésultat final : '{text}'")
        
    except Exception as e:
        print(f"Erreur : {e}")
