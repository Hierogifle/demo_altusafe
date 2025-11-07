import time
import vosk
import pyaudio


class SpeechRecognizer:
    """Lightweight wrapper around Vosk + PyAudio to listen once and return text.

    Usage:
        with SpeechRecognizer(model_path) as sr:
            text = sr.listen_once(timeout=5.0)

    Notes:
    - Uses exception_on_overflow=False to avoid raising OSError on input overflow.
    - listen_once reads frames until either Vosk reports a final result or until
      the timeout is reached. Returns the recognized text ('' if none).
    """

    def __init__(self, model_path: str = "vosk-model-fr-0.22/vosk-model-fr-0.22", rate: int = 16000, frames_per_buffer: int = 4096):
        self.model_path = model_path
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

        self.model = vosk.Model(self.model_path)
        self.rec = vosk.KaldiRecognizer(self.model, self.rate)

        self._p = pyaudio.PyAudio()
        self._stream = None

    def _open_stream(self):
        if self._stream is None:
            self._stream = self._p.open(format=pyaudio.paInt16,
                                        channels=1,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer)

    def listen_once(self, timeout: float = 5.0) -> str:
        """Listen for up to `timeout` seconds and return recognized text.

        Returns an empty string when nothing recognized.
        """
        self._open_stream()
        end = time.time() + timeout
        self.rec.Reset()
        accumulated = b""

        while time.time() < end:
            try:
                data = self._stream.read(self.frames_per_buffer, exception_on_overflow=False)
            except OSError:
                # Input overflow — skip this chunk and continue listening
                continue

            if not data:
                continue

            accumulated += data

            if self.rec.AcceptWaveform(data):
                res = self.rec.Result()
                try:
                    import json
                    j = json.loads(res)
                    return j.get("text", "")
                except Exception:
                    return ""

            # else keep collecting until timeout

        # try partial result once after timeout
        try:
            import json
            j = json.loads(self.rec.FinalResult())
            return j.get("text", "")
        except Exception:
            return ""

    def close(self):
        if self._stream is not None:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        try:
            self._p.terminate()
        except Exception:
            pass

    def __enter__(self):
        self._open_stream()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
