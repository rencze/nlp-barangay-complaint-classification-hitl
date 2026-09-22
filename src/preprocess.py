"""Text preprocessing helpers for the TF-IDF + SVM complaint pipeline.

Complaint text arrives in Bisaya, Filipino, English, or code-switched
combinations. All of these use Latin script, so normalization is kept
deliberately simple: lowercase, remove URLs, strip punctuation, and
collapse whitespace. TF-IDF handles tokenization and n-grams from there.
"""

import re

_URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
_NON_ALPHANUMERIC = re.compile(r"[^a-z0-9\s]")
_WHITESPACE = re.compile(r"\s+")


def normalize_text(text):
    """Return a cleaned, lowercased version of a complaint narrative."""
    if text is None:
        return ""
    text = str(text).lower()
    text = _URL_PATTERN.sub(" ", text)
    text = _NON_ALPHANUMERIC.sub(" ", text)
    text = _WHITESPACE.sub(" ", text)
    return text.strip()
