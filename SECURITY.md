# Security

## Reporting a vulnerability

Please report security issues via GitHub's **private vulnerability reporting** on this repo (Security tab → Report a vulnerability). Do not open a public issue.

I aim to respond within 7 days.

## Threat model

This tool is designed to run **locally only**, with no authentication. It binds to `127.0.0.1` and refuses to start on non-loopback addresses. Exposing it to the public internet is a misconfiguration and is explicitly unsupported.

In scope:
- CSRF, XSS, SQL injection, markdown sanitisation bypass, SSRF.
- Dependency vulnerabilities (Dependabot covers these).

Out of scope:
- Any scenario assuming the tool is exposed to untrusted networks or multiple users -- that is not a supported deployment.
