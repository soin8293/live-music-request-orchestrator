# Provenance and scope notice

This repository contains a credential-free reference implementation of a system
designed and built by Sorbarikor Inene for a live-stream music-request workflow.

It preserves the original engineering ideas that are useful to reviewers:

- normalization of multiple live-event payload shapes;
- bounded request parsing and validation;
- duplicate suppression and queue-capacity controls;
- requester attribution;
- same-origin REST and live event-stream state delivery; and
- a browser-source overlay suitable for local OBS-style composition.

The release history was intentionally started from a clean tree. It excludes
private account identifiers, OAuth credentials, tokens, event logs, real user
data, copyrighted media, provider-specific playback code, archived experiments,
and machine-specific operational notes.

TikTok, TikFinity, OBS, Spotify, and other product names are trademarks of their
respective owners. This project is not affiliated with or endorsed by them.
