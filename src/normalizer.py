from __future__ import annotations

import unicodedata


def to_nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def needs_normalization(text: str) -> bool:
    return text != to_nfc(text)
