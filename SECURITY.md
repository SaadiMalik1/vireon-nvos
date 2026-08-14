# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in VIREON, please report it responsibly:

1. **Do NOT open a public GitHub issue.**
2. Email: security@vireon.org (or open a private security advisory on GitHub)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Response Timeline

- **Acknowledgment:** within 48 hours
- **Initial assessment:** within 1 week
- **Fix or mitigation:** within 30 days (severity-dependent)

## Supported Versions

Only the latest release (v1.2.x) receives security updates.

## Known Security Considerations

- VIREON uses SQLite for evidence storage. SQLite is not designed for concurrent write access — do not deploy multiple API instances against the same `.db` file without external locking.
- The MCP server (stdio transport) does not encrypt data in transit — it is intended for local use only. For remote deployments, use the HTTP transport (v1.3+) with TLS.
- Evidence bundles are hashed (SHA-256) but not encrypted. Do not store PII in evidence bundles.
- The API uses API key authentication (set `VIREON_API_KEY` env var). Without this, the API runs in unauthenticated development mode.
