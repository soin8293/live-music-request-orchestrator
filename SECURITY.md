# Security policy

## Supported version

Security fixes are applied to the latest release on `main`.

## Report a vulnerability

Please use GitHub's private vulnerability-reporting feature. Do not open a
public issue containing credentials, private event payloads, or personal data.

## Security model

- The server binds to `127.0.0.1` by default.
- A non-loopback bind is refused unless `ORCHESTRATOR_INGEST_TOKEN` is set.
- Mutating endpoints accept loopback requests only unless the configured token
  is supplied in `X-Ingest-Token`.
- Request bodies and user-controlled strings are bounded.
- The overlay renders user-controlled values with DOM text APIs, not HTML.
- Raw event payloads, chat text, and usernames are not written to logs.
- State is in memory by default; this public edition does not persist viewer
  identities or request history.

This is a local demonstration, not an internet-facing multi-tenant service.
Putting it behind a reverse proxy requires authentication, TLS, rate limiting,
origin restrictions, a privacy review, and a separate threat model.
