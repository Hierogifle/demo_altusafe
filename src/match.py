"""
Lightweight matching engine ported from the notebook `matching2.ipynb`.

Provides MatchEngine class with methods:
 - norm(text)
 - match_utterance_to_candidates(utterance, candidates, ...)

It embeds texts using a TFLite encoder (`encoder_embed.tflite`) and the
character vocabulary file `char_vocab_embed.txt` by default. Adjust paths
when instantiating the class.

Usage example:
	from match import MatchEngine
	m = MatchEngine(tflite_path='encoder_embed.tflite', vocab_path='char_vocab_embed.txt')
	res = m.match_utterance_to_candidates("Le patient Paul Dupont à 10:30", ["Paul Dupont","10:30","Salle 3"]) 

The result is a list of tuples (candidate, score, best_span, decision, embed_score, ng_score)
sorted by descending score.
"""

import os
import re
import unicodedata
import random
import math
from typing import List, Tuple

import numpy as np

try:
	import tensorflow as tf
except Exception as e:
	tf = None


class MatchEngine:
	def __init__(self, tflite_path: str = "encoder_embed.tflite", vocab_path: str = "char_vocab_embed.txt", seqlen: int = 200):
		self.seqlen = seqlen
		self.tflite_path = tflite_path
		self.vocab_path = vocab_path

		# load vocab
		if not os.path.exists(self.vocab_path):
			raise FileNotFoundError(f"Vocab file not found: {self.vocab_path}")
		with open(self.vocab_path, "r", encoding="utf-8") as f:
			self.vocab = [l.rstrip("\n") for l in f]
		self.tok2id = {t: i for i, t in enumerate(self.vocab)}
		self.UNK = self.tok2id.get("[UNK]", 1)

		# Notify that vocab was loaded and how many tokens
		# delete later
		try:
			print(f"MatchEngine: loaded vocab from '{self.vocab_path}' ({len(self.vocab)} tokens)")
		except Exception:
			print(f"MatchEngine: loaded vocab from '{self.vocab_path}'")
			# delete later

		# load tflite interpreter
		if tf is None:
			raise ImportError("TensorFlow is required for MatchEngine (tflite interpreter). Install tensorflow.")

		if not os.path.exists(self.tflite_path):
			raise FileNotFoundError(f"TFLite model not found: {self.tflite_path}")

		self.interpreter = tf.lite.Interpreter(model_path=self.tflite_path)
		self.interpreter.allocate_tensors()
		self._in = self.interpreter.get_input_details()
		self._out = self.interpreter.get_output_details()
		# delete later
		# Notify that the TFLite model was loaded
		print(f"MatchEngine: loaded TFLite model from '{self.tflite_path}'")
		# delete later
		# mark engine ready
		self.ready = True

	# ------------------------- text helpers -------------------------
	@staticmethod
	def strip_accents(s: str) -> str:
		return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

	def norm(self, s: str) -> str:
		if s is None:
			return ""
		s = str(s).lower().strip()
		s = self.strip_accents(s)
		s = re.sub(r"[^a-z0-9:/ \-]", " ", s)
		s = re.sub(r"\s+", " ", s).strip()
		return s

	# ------------------------- vectorize / embed -------------------------
	def vectorize_texts(self, texts: List[str], seqlen: int = None) -> np.ndarray:
		seqlen = seqlen or self.seqlen
		X = np.zeros((len(texts), seqlen), dtype=np.int32)
		for i, t in enumerate(texts):
			t = self.norm(t)
			for j, ch in enumerate(t[:seqlen]):
				X[i, j] = self.tok2id.get(ch, self.UNK)
		return X

	def embed_texts(self, texts: List[str]) -> np.ndarray:
		# produce [N, D] embeddings using the loaded tflite interpreter
		X = self.vectorize_texts(texts, self.seqlen)
		# resize input if needed
		self.interpreter.resize_tensor_input(self._in[0]['index'], [len(texts), self.seqlen])
		self.interpreter.allocate_tensors()
		in_d = self.interpreter.get_input_details()[0]
		out_d = self.interpreter.get_output_details()[0]
		self.interpreter.set_tensor(in_d['index'], X)
		self.interpreter.invoke()
		emb = self.interpreter.get_tensor(out_d['index'])
		return emb

	# ------------------------- n-gram similarity (auxiliary) -------------------------
	@staticmethod
	def char_ngrams(s: str, n: int = 3) -> dict:
		s = " " + s + " "
		out = {}
		for i in range(max(0, len(s) - n + 1)):
			g = s[i:i + n]
			out[g] = out.get(g, 0) + 1
		return out

	@staticmethod
	def cosine_counts(a: dict, b: dict) -> float:
		keys = set(a.keys()) | set(b.keys())
		dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
		na = math.sqrt(sum(v * v for v in a.values()))
		nb = math.sqrt(sum(v * v for v in b.values()))
		return 0.0 if na == 0 or nb == 0 else dot / (na * nb)

	def ngram_sim(self, u: str, v: str) -> float:
		u = self.norm(u); v = self.norm(v)
		return (self.cosine_counts(self.char_ngrams(u, 3), self.char_ngrams(v, 3)) +
				self.cosine_counts(self.char_ngrams(u, 4), self.char_ngrams(v, 4)) +
				self.cosine_counts(self.char_ngrams(u, 5), self.char_ngrams(v, 5))) / 3.0

	# ------------------------- span helpers & scoring -------------------------
	def word_windows(self, text: str, min_w: int = 2, max_w: int = 6) -> List[str]:
		toks = self.norm(text).split()
		if not toks:
			return [self.norm(text)]
		spans = []
		for w in range(min_w, min(max_w, len(toks)) + 1):
			for i in range(0, len(toks) - w + 1):
				spans.append(' '.join(toks[i:i + w]))
		return spans or [self.norm(text)]

	def best_cosine_over_spans_with_overlap(self, utterance: str, candidate: str, require_overlap_tokens: bool = True) -> Tuple[float, str, float, float]:
		spans = self.word_windows(utterance, 2, 6)
		cand_tokens = set(self.norm(candidate).split())
		filtered = []
		if require_overlap_tokens:
			for sp in spans:
				if len(cand_tokens & set(sp.split())) > 0:
					filtered.append(sp)
		spans_eval = filtered if filtered else spans

		E_spans = self.embed_texts(spans_eval)
		E_cand = self.embed_texts([candidate])[0]
		dots = (E_spans @ E_cand) / (np.linalg.norm(E_spans, axis=1) * np.linalg.norm(E_cand) + 1e-9)
		j = int(np.argmax(dots))
		best_span = spans_eval[j]
		embed_score = float(dots[j])

		ng = self.ngram_sim(best_span, candidate)
		final = 0.7 * embed_score + 0.3 * ng
		return final, best_span, embed_score, ng

	# ------------------------- API (decision + matching) -------------------------
	@staticmethod
	def decide(score: float, ok: float = 0.88, maybe: float = 0.70) -> str:
		return "OK" if score >= ok else ("INCERTAIN" if score >= maybe else "KO")

	def match_utterance_to_candidates(self, utterance: str, candidates: List[str], require_overlap_for_names: bool = True) -> List[Tuple[str, float, str, str, float, float]]:
		# Notify when this semantic matcher is used
		# delete later
		print(f"MatchEngine: matching utterance using encoder (ready={getattr(self, 'ready', False)}) against {len(candidates)} candidates")
		# delete later

		results = []
		for c in candidates:
			tokens = self.norm(c).split()
			is_name = len(tokens) >= 2 and all(t.isalpha() for t in tokens[:2])
			req = (require_overlap_for_names and is_name)
			s, span, s_embed, s_ng = self.best_cosine_over_spans_with_overlap(utterance, c, require_overlap_tokens=req)
			results.append((c, s, span, self.decide(s), s_embed, s_ng))
		results.sort(key=lambda x: -x[1])
		return results


if __name__ == "__main__":
	# Quick demo if run as script (requires the tflite model + vocab in cwd)
	try:
		me = MatchEngine()
	except Exception as e:
		print("MatchEngine initialization failed:", e)
	else:
		utt = "Le patient est Paul Dupont, opération à 10:30 en salle 4 avec le Dr. Bernard"
		cands = ["Bruno Romuald", "Romuald Bruno", "Paul Dupont", "Dupont Paul", "10:30", "Salle 4", "Dr. Bernard", "Appendicectomie"]
		res = me.match_utterance_to_candidates(utt, cands)
		for c, s, span, dec, s_embed, s_ng in res:
			print(f"{c:20s} | {s:.3f} | {dec} | span='{span}' | embed={s_embed:.3f} | ng={s_ng:.3f}")

