import argparse
import json
import os
from typing import Any
import difflib
import unicodedata

from speech_recognizer import SpeechRecognizer
from match import MatchEngine


def iter_fields(obj: Any, prefix: str = ""):
    """Yield (path, value) for simple fields in the JSON object (shallow + nested dicts)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)):
                # flatten one level for dicts, for lists join as string
                if isinstance(v, dict):
                    yield from iter_fields(v, prefix=path)
                else:
                    yield path, v
            else:
                yield path, v
    else:
        yield prefix or "value", obj


def _normalize(s: str) -> str:
    if s is None:
        return ""
    s = str(s).lower().strip()
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    # keep letters, numbers and spaces
    s = ''.join(ch if (ch.isalnum() or ch.isspace()) else ' ' for ch in s)
    s = ' '.join(s.split())
    return s


def _similarity(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def confirm_item(recognizer: SpeechRecognizer, prompt_text: str, expected: str | list, timeout: float = 7.0, match_engine: MatchEngine | None = None) -> dict:
    """Ask user to speak and compare the recognized text to expected.

    Loop until the information is validated (decision OK). On OK returns a dict with
    final status message 'information validé'. On user saying 'terminé' returns with status 'interrompu'.
    The returned dict contains attempts for debugging.
    """
    print("---")
    print("A valider:", prompt_text)

    expected_items = expected if isinstance(expected, list) else [expected]
    expected_norm = [_normalize(str(x)) for x in expected_items]

    attempts = []

    while True:
        print("Parlez maintenant (répondez avec la valeur attendue) ...")
        text = recognizer.listen_once(timeout=timeout)
        print("Reconnu :", repr(text))
        tnorm = _normalize(text)

        # check for explicit termination
        if tnorm and "termin" in tnorm:
            return {"status": "interrompu", "attempts": attempts}

        # If a MatchEngine is provided, prefer it for scoring/decision.
        best_score = 0.0
        best_expected = None
        decision = "KO"

        if match_engine is not None:
            try:
                # match_engine expects the utterance and a list of candidates
                # it will normalize internally. Use the raw recognized text.
                matches = match_engine.match_utterance_to_candidates(tnorm, expected_items, require_overlap_for_names=False)
                if matches:
                    best = matches[0]
                    best_expected = best[0]
                    best_score = float(best[1])
                    decision = best[3]
            except Exception:
                # if MatchEngine fails for any reason, fallback to difflib below
                match_engine = None

        if match_engine is None:
            # compute best similarity across expected variants using difflib fallback
            for exp, en in zip(expected_items, expected_norm):
                sim = _similarity(tnorm, en)
                if sim > best_score:
                    best_score = sim
                    best_expected = exp

            # decide thresholds (OK >= 0.88, INCERTAIN >= 0.70)
            if best_score >= 0.88:
                decision = "OK"
            elif best_score >= 0.70:
                decision = "INCERTAIN"
            else:
                decision = "KO"

        attempts.append({"recognized": text, "normalized": tnorm, "best_expected": best_expected, "score": best_score, "decision": decision})

        if decision == "OK":
            print("✅information validé")
            return {"status": "information validé", "attempts": attempts}
        else:
            print("🔁Veuillez répéter (statut:", decision, ")")
            # do not advance: loop again until OK or 'terminé'


def validate_fiche(fiche_path: str, model_path: str = "/vosk-model-fr-0.22"):
    if not os.path.exists(fiche_path):
        raise FileNotFoundError(f"Fiche not found: {fiche_path}")

    with open(fiche_path, "r", encoding="utf-8") as f:
        fiche = json.load(f)

    results = {}
    # try to initialize MatchEngine (optional). If it fails (no TF/tflite), we'll fallback to difflib.
    me = None

    # Check same folder (final) for encoder and vocab and notify (delete later)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tflite_path = os.path.join(script_dir, "encoder_embed.tflite")
    vocab_path = os.path.join(script_dir, "char_vocab_embed.txt")

    if os.path.exists(tflite_path) and os.path.exists(vocab_path):
        print(f"Found encoder and vocab in final folder: {script_dir} — will try to load them")
        try:
            me = MatchEngine(tflite_path=tflite_path, vocab_path=vocab_path)
            print("MatchEngine loaded successfully with provided encoder + vocab (final folder)")
        except Exception as e:
            print("Failed to initialize MatchEngine with final folder files, falling back:", e)
    else:
        print("encoder_embed.tflite and/or char_vocab_embed.txt not found in final folder; will try default MatchEngine init")
        try:
            me = MatchEngine()
            print("MatchEngine loaded successfully with default paths")
        except Exception as e:
            print("MatchEngine unavailable, falling back to simple string similarity:", e)

    with SpeechRecognizer(model_path=model_path) as sr:
        for path, value in iter_fields(fiche):
            # prepare a short string representation
            if isinstance(value, list):
                vstr = ", ".join(map(str, value))
            else:
                vstr = str(value)

            res = confirm_item(sr, f"{path}: {vstr}", expected=value, match_engine=me)
            results[path] = {"expected": vstr, "status": res.get("status"), "attempts": res.get("attempts", [])}

            # allow user to stop early by saying 'terminé' (status 'interrompu')
            if res.get("status") == "interrompu":
                print("Mot clé 'terminé' détecté — interruption de la validation.")
                break

    out_path = os.path.splitext(fiche_path)[0] + "_validated.json"
    with open(out_path, "w", encoding="utf-8") as fo:
        json.dump({"fiche": fiche, "validation": results}, fo, ensure_ascii=False, indent=2)

    print(f"Validation enregistrée dans: {out_path}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fiche", nargs="?", default="data/fiches/P1.json", help="Chemin du fichier fiche JSON à valider")
    p.add_argument("--model", default="vosk-model-fr-0.22", help="Chemin du modèle Vosk")
    args = p.parse_args()

    validate_fiche(args.fiche, model_path=args.model)


if __name__ == "__main__":
    main()
