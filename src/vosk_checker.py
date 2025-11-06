"""vosk_checker.py

Listen to microphone (or read a WAV) with VOSK and check recognized text
against fields from a JSON record using MatchEngine (src/match.py).

Usage examples:
  # microphone (default)
  python src/vosk_checker.py --json ../data/P1.json

  # from WAV (useful for testing)
  python src/vosk_checker.py --json ../data/P1.json --wav samples/test.wav

Requirements:
  pip install vosk pyaudio numpy
  Place a VOSK french model in `models/vosk-fr` or set VOSK_MODEL env var
  Ensure `encoder_embed.tflite` and `char_vocab_embed.txt` are reachable (see MatchEngine)
"""

import argparse
import json
import os
import queue
import sys
import threading
import time
from datetime import datetime

try:
    from vosk import Model, KaldiRecognizer
except Exception:
    Model = None
    KaldiRecognizer = None

import wave

from match import MatchEngine


def build_candidates_from_record(record: dict) -> dict:
    """Return a dict field -> list[candidate strings]."""
    cand = {}
    # Patient name
    p = record.get("patient", {})
    prenom = p.get("prenom", "")
    nom = p.get("nom", "")
    if prenom or nom:
        name_variants = []
        if prenom and nom:
            name_variants.append(f"{prenom} {nom}")
            name_variants.append(f"{nom} {prenom}")
            name_variants.append(f"{prenom}")
            name_variants.append(f"{nom}")
        else:
            if prenom:
                name_variants.append(prenom)
            if nom:
                name_variants.append(nom)
        cand["name"] = list(dict.fromkeys(name_variants))

    # Date of birth
    dob = p.get("date_naissance") or p.get("date_de_naissance")
    dob_variants = []
    if dob:
        # Try parse ISO-like dates
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                dt = datetime.strptime(dob, fmt)
                break
            except Exception:
                dt = None
        # If ISO string like 1985-06-12, parse
        if dt is None:
            try:
                dt = datetime.fromisoformat(dob)
            except Exception:
                dt = None

        if dt:
            # common spoken/written variants
            dob_variants.append(dt.strftime("%d/%m/%Y"))
            dob_variants.append(dt.strftime("%d %B %Y"))
            dob_variants.append(dt.strftime("%d %b %Y"))
            dob_variants.append(dt.strftime("%Y-%m-%d"))
            dob_variants.append(dt.strftime("%d %m %Y"))
            # also include year-only and day-month
            dob_variants.append(dt.strftime("%Y"))
            dob_variants.append(dt.strftime("%d %B"))
        else:
            dob_variants.append(str(dob))
    if dob_variants:
        cand["dob"] = list(dict.fromkeys(dob_variants))

    # Intervention type
    intr = record.get("intervention", {})
    typ = intr.get("type") or intr.get("intervention")
    if typ:
        variants = [typ]
        # small normalizations
        variants.append(typ.replace("é", "e").replace("è", "e"))
        variants.append(typ.lower())
        cand["intervention_type"] = list(dict.fromkeys(variants))

    return cand


def transcribe_wav(wav_path, model_path, callback_final):
    """Transcribe a WAV file and call callback_final(text) for final results."""
    if Model is None:
        raise RuntimeError("VOSK library not available. Install with `pip install vosk`.")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"VOSK model not found: {model_path}")
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    wf = wave.open(wav_path, "rb")
    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = rec.Result()
            j = json.loads(res)
            text = j.get("text", "").strip()
            if text:
                callback_final(text)
    # final
    j = json.loads(rec.FinalResult())
    text = j.get("text", "").strip()
    if text:
        callback_final(text)


def run_mic_loop(model_path, callback_final, sample_rate=16000):
    """Run live microphone recognition; call callback_final(text) on final results."""
    try:
        import pyaudio
    except Exception:
        raise RuntimeError("pyaudio is required for microphone input. Install with `pip install pyaudio`.")

    if Model is None:
        raise RuntimeError("VOSK library not available. Install with `pip install vosk`.")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"VOSK model not found: {model_path}")

    model = Model(model_path)
    rec = KaldiRecognizer(model, sample_rate)
    rec.SetWords(True)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print("🎙️  Parlez… (Ctrl+C pour quitter)")
    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text = res.get("text", "").strip()
                if text:
                    callback_final(text)
            else:
                # partial = json.loads(rec.PartialResult()).get('partial','')
                pass
    except KeyboardInterrupt:
        print('\nInterrupted by user')
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True, help="Path to JSON file (e.g. ../data/P1.json)")
    ap.add_argument("--wav", help="Optional WAV file to transcribe instead of microphone")
    ap.add_argument("--vosk-model", default=os.environ.get("VOSK_MODEL", "vosk-model-small-fr-0.22/vosk-model-small-fr-0.22"), help="VOSK model path")
    ap.add_argument("--tflite", default=os.path.join('..','src','encoder_embed.tflite'), help="path to encoder tflite model for MatchEngine")
    ap.add_argument("--vocab", default=os.path.join('..','src','char_vocab_embed.txt'), help="path to char vocab for MatchEngine")
    args = ap.parse_args()

    # load JSON
    jpath = args.json
    if not os.path.exists(jpath):
        print(f"JSON file not found: {jpath}")
        sys.exit(1)
    with open(jpath, 'r', encoding='utf-8') as f:
        record = json.load(f)

    candidates = build_candidates_from_record(record)
    print("Candidates prepared:")
    for k, v in candidates.items():
        print(f" - {k}: {v}")

    # instantiate MatchEngine
    # try a few tflite/vocab fallback locations
    tfl = args.tflite
    vcb = args.vocab
    # fallback to cwd if provided paths don't exist
    if not os.path.exists(tfl):
        tfl_alt = os.path.join(os.getcwd(), 'encoder_embed.tflite')
        if os.path.exists(tfl_alt):
            tfl = tfl_alt
    if not os.path.exists(vcb):
        vcb_alt = os.path.join(os.getcwd(), 'char_vocab_embed.txt')
        if os.path.exists(vcb_alt):
            vcb = vcb_alt

    try:
        me = MatchEngine(tflite_path=tfl, vocab_path=vcb)
    except Exception as e:
        print("Failed to initialize MatchEngine:", e)
        print("You can still use VOSK for transcription, but matching will be disabled.")
        me = None

    def on_final(text: str):
        ts = text.strip()
        if not ts:
            return
        print('\n--- RECOGNIZED:', ts)
        # For each field, call match engine if available, otherwise do substring check
        for field, cand_list in candidates.items():
            print(f"\nField: {field}")
            if me is None:
                # simple substring check
                found = False
                for c in cand_list:
                    if c.lower() in ts.lower():
                        print(f"  MATCH (substring): {c}")
                        found = True
                if not found:
                    print("  No substring match")
            else:
                res = me.match_utterance_to_candidates(ts, cand_list)
                # print top-3
                for i, (c, score, span, dec, s_embed, s_ng) in enumerate(res[:3]):
                    print(f"  {i+1}. {c:30s} | {score:.3f} | {dec} | span='{span}' | embed={s_embed:.3f} | ng={s_ng:.3f}")

    # choose mode: wav or mic
    if args.wav:
        transcribe_wav(args.wav, args.vosk_model, on_final)
    else:
        run_mic_loop(args.vosk_model, on_final)


if __name__ == '__main__':
    main()
