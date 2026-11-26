"""Plain-Python NLP: tokenisation, stop-word removal, stemming, TF-IDF, cosine similarity."""
import math
import re
from collections import Counter

STOP_WORDS = set("""a an the and or but if then so of to in on at by for with about from as is am are was
were be been being do does did have has had i me my mine we our you your he she it they them their this
that these those what which who whom how when where why can could should would will shall may might must
not no yes please tell want need get got just also any some there here into out up over than too very
really him her his its let us""".split())

SUFFIXES = ("ational", "ations", "ation", "ingly", "ings", "ing", "ness", "ments", "ment",
            "ies", "ied", "ed", "ly", "s")

URGENT_RE = re.compile(
    r"\b(violen\w*|beat(?:ing|en|s)?|threat\w*|kill\w*|suicid\w*|abus\w*|rape\w*|assault\w*|acid|"
    r"molest\w*|harass\w*|trafficking|stalk\w*|hurt\w*|unsafe|danger\w*|end my life|want to die)\b")


def tokenize(text):
    """Lowercase -> split into words."""
    return re.findall(r"[a-z0-9]+", text.lower())


def stem(word):
    """Very small suffix-stripping stemmer (not the full Porter algorithm)."""
    if word.endswith("ss"):
        return word
    for suf in SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            return word[: -len(suf)] + ("y" if suf in ("ies", "ied") else "")
    return word


def preprocess(text):
    return [stem(t) for t in tokenize(text) if t not in STOP_WORDS]


def is_urgent(text):
    return bool(URGENT_RE.search(text.lower()))


class Engine:
    def __init__(self, kb):
        self.kb = kb
        docs = [Counter(preprocess(self._text(e))) for e in kb]
        n = len(kb)
        df = Counter()
        for d in docs:
            df.update(d.keys())
        self.idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
        self.unknown_idf = math.log(1 + n) + 1
        self.vectors = [self._vector(d) for d in docs]

    @staticmethod
    def _text(e):
        # title and keywords are repeated so they count for more than the long explanation
        return " ".join([e["title"]] * 2 + e["keywords"] * 2 + e["sample_questions"]
                        + [e["explanation"]])

    def _vector(self, counts):
        v = {t: (1 + math.log(c)) * self.idf.get(t, self.unknown_idf) for t, c in counts.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    def match(self, question):
        """Return (entry, confidence) or None if nothing matches well enough."""
        q = self._vector(Counter(preprocess(question)))
        if not q:
            return None
        scores = [sum(w * vec.get(t, 0.0) for t, w in q.items()) for vec in self.vectors]
        best = max(range(len(scores)), key=scores.__getitem__)
        s = scores[best]
        if s < 0.10:
            return None
        level = "High" if s >= 0.30 else "Medium" if s >= 0.18 else "Low"
        return self.kb[best], level
