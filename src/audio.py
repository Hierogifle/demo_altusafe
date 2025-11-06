# pip install vosk pyaudio
import json, sys, queue, threading
from vosk import Model, KaldiRecognizer
import pyaudio

# --- 1) Vosk ---
SAMPLE_RATE = 16000
model = Model("models/vosk-fr")   # dossier du modèle FR offline
rec   = KaldiRecognizer(model, SAMPLE_RATE)
rec.SetWords(True)

# --- 2) Audio ---
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLE_RATE,
                input=True, frames_per_buffer=8000)
stream.start_stream()

# --- 3) Ton matcher (exemple d’interface) ---
class MyMatcher:
    def __init__(self, encoder_tflite_path, char_vocab_path, candidates_by_field):
        # charge ton TFLite encoder + vocab + pré-calcul des embeddings candidats
        ...
    def match(self, text):
        # retourne une liste de résultats (field, candidate, score, decision, best_span)
        ...
matcher = MyMatcher("encoder_embed.tflite", "char_vocab_embed.txt", candidates_by_field={...})

# --- 4) Boucle reco → matching sur résultats finaux ---
print("🎙️  Parlez… (Ctrl+C pour quitter)")
buffered_partial = ""
while True:
    data = stream.read(4000, exception_on_overflow=False)
    if rec.AcceptWaveform(data):
        res = json.loads(rec.Result())
        text = res.get("text","").strip()
        if not text: 
            continue
        # normalise comme à l’entraînement (IMPORTANT)
        print("Final:", text)
        results = matcher.match(text)      # ton code
        for r in results:
            print(r)
    else:
        pres = json.loads(rec.PartialResult())
        partial = pres.get("partial","")
        # -> si tu veux déclencher sur partials stables: debouncing 600–800 ms, sinon ignore
