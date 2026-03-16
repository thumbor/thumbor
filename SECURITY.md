# Security Policy

## Reporting a Vulnerability

The thumbor team takes security vulnerabilities seriously. If you discover a
security issue in thumbor, please report it responsibly.

Please **DO NOT open a public GitHub issue** for security vulnerabilities.

Instead, please report the vulnerability privately using GitHub's
**Private Vulnerability Reporting** feature:

- Go to the repository's **Security** tab
- Click **Report a vulnerability**
- Submit the details through the GitHub Security Advisory form

Include as much information as possible to help us reproduce the issue:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- A proof of concept (PoC), if available
- Your environment (thumbor version, configuration, deployment model)

We will acknowledge receipt of your report as soon as possible and work with
you to understand and resolve the issue.

## Responsible Disclosure

We ask that you follow responsible disclosure practices:

- Do not publicly disclose the vulnerability before it has been addressed.
- Allow the maintainers reasonable time to investigate and fix the issue.
- Coordinate with us before publishing advisories, blog posts, or CVEs.

Once the issue is fixed, we will publicly acknowledge your contribution unless
you prefer to remain anonymous.

## Supported Versions

Security fixes are typically provided for the most recent stable versions of
thumbor.

| Version                 | Supported      |
| ----------------------- | -------------- |
| Latest release          | ✅             |
| Previous minor versions | ⚠️ Best effort |
| Older versions          | ❌             |

Users are strongly encouraged to keep their thumbor installations up to date.

## Security Considerations When Running Thumbor

When deploying thumbor in production, please consider the following:

- Use a strong `SECURITY_KEY` to sign URLs.
- Disable `/unsafe` endpoints (`ALLOW_UNSAFE_URL = False`) when possible.
- Restrict allowed image sources using `ALLOWED_SOURCES`.
- Place thumbor behind a reverse proxy or CDN when exposed to the internet.
- Monitor and rate-limit incoming requests to prevent abuse.

Proper configuration helps prevent issues such as URL tampering, which could
otherwise allow attackers to generate arbitrary image processing requests.

## Acknowledgements

We appreciate the efforts of security researchers and the open-source community
in responsibly reporting vulnerabilities and helping improve the security of
thumbor.
