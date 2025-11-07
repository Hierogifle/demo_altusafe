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
                frames_per_buffer=4096)
				
# Chemin d'export du fichier text
output_file_path = "recognized_text.txt"

with open(output_file_path, "w") as output_file:
    print("Listening for speech. Say 'Terminate' to stop.")
    # démarrage du streamin audio
    while True:
        # Lecture protégée contre les input overflow (arrive si l'OS remplit
        # le buffer audio avant qu'on ne lise). On passe
        # exception_on_overflow=False pour éviter que PyAudio lève une
        # exception et on attrape OSError au cas où.
        try:
            data = stream.read(4096, exception_on_overflow=False)
        except OSError as e:
            # Input overflow occurred — on le signale et on continue la
            # boucle. Cela évite que le script plante si le système audio
            # n'arrive pas à fournir les frames assez vite.
            print(f"Warning: audio input overflow: {e}")
            continue

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