# IonoFlux Python SDK v0.1.1

Documentation and package metadata patch for the official Python 3.11+ synchronous SDK. English/Korean READMEs now lead with `pip install ionoflux`, Server-key setup, a working basic example and explicit supported/unsupported API scope. GitHub/PyPI-safe absolute HTTPS links replace relative links. The header reuses the official service-hosted PNG logo with descriptive alt text, without creating a new brand asset.

Public API behavior is unchanged. PolyForm Noncommercial 1.0.0 and NOTICE are preserved byte-for-byte. Existing v0.1.0 release files/tag remain immutable. The independent optional smoke workflow in PR #8 is not included.

## Validation — 2026-10-20 KST

- Local: 135 offline tests, Ruff lint/format, mypy, actionlint, wheel/sdist builds, Twine, official license/NOTICE/SPDX checks and distribution file/credential-pattern checks passed.
- Both README documents passed the same Markdown renderer/sanitizer used for PyPI descriptions; all links are absolute HTTPS and the official logo survives sanitization. Added CI regression check `scripts/check_readme.py`.
- Chrome previews of both languages in light/dark mode loaded the official 512px PNG at 96px, with no horizontal overflow at 1100px. This previews sanitized content; actual PyPI presentation must still be inspected after approved publication.
- Official logo URL returned 200 image/png; SHA256 `ffd5d5dcfeb74e1eacdd6d90d040c1bba3e5ad173536046cee8166b0fa3bc9ae` matches the service repository's `frontend/public/brand/icon-512.png`.
- All 22 unique README link/image destinations were opened with HTTPS GET and returned 200 (table below). Existing published relative paths were also opened: PyPI returned a 200 client-challenge HTML page rather than the requested GitHub documents, so HTTP status alone is not evidence that those old links work. No false 404 claim is made.
- Prior v0.1.0 nine-request live API acceptance is historical evidence; this patch performs no new authenticated API calls. Secret-pattern scanning is a heuristic, not a guarantee of complete detection.

## Publication state and acceptance

Prepared candidate only. Check [reviewed checksums](release-artifacts.md) and [protected publication procedure](release-preparation.md). After merge approval, wait for exact main CI and reproduce both hashes. Then obtain separate tag/PyPI upload approval, keep TestPyPI disabled, require the owner's `pypi` Environment manual approval, and preserve Trusted Publishing. Stop on a CI/hash/index failure or partial upload; do not overwrite or retag v0.1.0.

After publication, restore the publishing flag to false, verify fresh PyPI installation/version/licenses and both public hashes/attestations, then open the latest PyPI page and inspect the logo, Korean link, API contract, license/NOTICE and all major links. The latest PyPI page remains v0.1.0 until that approved publication succeeds.

## Link checks

| URL | HTTP status |
|---|---|
| https://github.com/hongjunna/ionoflux-python | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/CHANGELOG.md | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/LICENSE | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/NOTICE | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/README.ko.md | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/README.md | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/docs/api-contract.md | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/docs/api-terms-preflight.ko.md | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/docs/api-terms-proposal.ko.md | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/docs/attribution-examples.md | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/docs/development-plan.md | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/docs/licensing-review.ko.md | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/docs/readme-usage-draft.md | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/docs/release-review.md | 200 |
| https://github.com/hongjunna/ionoflux-python/blob/main/docs/use-cases.ko.md | 200 |
| https://github.com/hongjunna/ionoflux-python/issues/2 | 200 |
| https://github.com/hongjunna/ionoflux-python/releases | 200 |
| https://github.com/hongjunna/ionoflux-python/releases/tag/python-v0.1.0 | 200 |
| https://ionoflux.runvia.app | 200 |
| https://ionoflux.runvia.app/account | 200 |
| https://ionoflux.runvia.app/brand/icon-512.png | 200 |
| https://pypi.org/project/ionoflux/ | 200 |
