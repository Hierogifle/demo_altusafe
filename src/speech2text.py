import vosk
import pyaudio
import json


# Télécharger le modèle depuis ce lien
# dezipper le
# et définissez le chemin d'accés au modèle
model_path = "vosk-model-fr-0.22/vosk-model-fr-0.22"
# Initialisation du modèle
model = vosk.Model(model_path)


# création de notre object de reconnaissance vocale
rec = vosk.KaldiRecognizer(model, 16000)

# On ouvre le microphone
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192)
				
# Chemin d'export du fichier text
output_file_path = "recognized_text.txt"

with open(output_file_path, "w") as output_file:
    print("Listening for speech. Say 'Terminate' to stop.")
    # démarrage du streamin audio
    while True:
        data = stream.read(4096)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            recognized_text = result['text']
            
            #ecriture dans le fichier de sortie
            output_file.write(recognized_text + "\n")
            print(recognized_text)
            
            # On vérifie sur la personne dit "terminé" pour clore le stream
            if "terminé" in recognized_text.lower():
                print("Termination keyword detected. Stopping...")
                break

stream.stop_stream()
stream.close()


p.terminate()