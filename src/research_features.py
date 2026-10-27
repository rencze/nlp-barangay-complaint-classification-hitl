"""Importable, versioned preprocessing for the separate development candidate."""
import unicodedata


def candidate_normalize(text):
    """NFKC, casefold and whitespace; preserve negations and Unicode characters."""
    return ' '.join(unicodedata.normalize('NFKC', text).casefold().split())
