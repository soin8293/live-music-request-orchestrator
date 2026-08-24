# Engineering case study

## Problem

A live music-request experience has several independently unreliable surfaces:
chat connectors change payload shapes, webhook retries create duplicates,
playback state changes out of band, and browser overlays must recover without
operator intervention. Debugging all of this while live is substantially harder
than building a static queue UI.

## My contribution

I designed and implemented the original private system end to end:

- compared and reconciled multiple ingress paths;
- created a canonical request contract;
- fixed repeated-event behavior with debounce and queue-level deduplication;
- carried requester identity into now-playing and queue state;
- exposed canonical state over REST and live push updates;
- built the browser-source overlay and its reconnect behavior;
- integrated and debugged a private playback-provider experiment; and
- wrote operational handoffs, smoke checks, and failure matrices.

This implementation is a clean reconstruction of those verified design
ideas. It is not a dump of the private working directory.

## What made it difficult

- Different integrations represented the same command with different field
  names and action values.
- A single chat action could be delivered zero, one, or several times depending
  on connector state.
- The queue, current track, requester label, and overlay could drift unless one
  component owned canonical state.
- Live troubleshooting required graceful degradation: HTTP polling remains a
  fallback when the live event stream reconnects.
- Credentials, chat logs, and account-specific configuration could not be
  included in the released source.

## Portfolio adaptation decisions

- Synthetic metadata replaces private provider calls.
- State is memory-only and starts empty.
- No raw live payload is logged.
- The overlay uses text nodes for untrusted values.
- Network exposure is default-deny.
- Tests focus on normalization, queue invariants, access control, and API shape.

## Limitations

- The optional bridge depends on a locally installed third-party application.
- CI does not exercise a real live-chat session.
- The mock catalog does not play audio.
- This repository does not claim a production multi-tenant security boundary.
