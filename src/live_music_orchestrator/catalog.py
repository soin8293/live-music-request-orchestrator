"""Deterministic synthetic track metadata for credential-free demos."""

from __future__ import annotations

import hashlib
import re

from .models import ResolvedTrack

_WHITESPACE = re.compile(r"\s+")
_HEX_PALETTE = (
    "#6d5dfc",
    "#ff4fa3",
    "#00c2a8",
    "#ff9f1c",
    "#2ec4ff",
    "#8b5cf6",
    "#ef476f",
    "#06d6a0",
)


class SyntheticCatalog:
    """Resolve a request without network calls or copyrighted media."""

    def resolve(self, query: str) -> ResolvedTrack:
        cleaned = _WHITESPACE.sub(" ", query).strip()
        title, artist = self._split(cleaned)
        digest = hashlib.sha256(cleaned.casefold().encode("utf-8")).hexdigest()
        first = int(digest[:2], 16) % len(_HEX_PALETTE)
        second = int(digest[2:4], 16) % len(_HEX_PALETTE)
        if first == second:
            second = (second + 3) % len(_HEX_PALETTE)
        return ResolvedTrack(
            track_id=f"demo_{digest[:16]}",
            title=title,
            artist=artist,
            duration_ms=180_000 + (int(digest[4:8], 16) % 90_000),
            color_start=_HEX_PALETTE[first],
            color_end=_HEX_PALETTE[second],
        )

    @staticmethod
    def _split(query: str) -> tuple[str, str]:
        if " - " in query:
            title, artist = query.split(" - ", 1)
            if title.strip():
                return title.strip(), artist.strip() or "Demo Artist"
        return query or "Untitled Request", "Demo Artist"
