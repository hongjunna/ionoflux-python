# Reviewed v0.1.0 artifacts (not published)

Built with the fixed SOURCE_DATE_EPOCH 1792479234 and pinned release toolchain from the publishing-preparation branch based on merged main b446319. These are the final candidate hashes; the branch must be reviewed/integrated and its exact main CI must pass before the release tag. This document and the machine-readable manifest are excluded from both distributions. A later build must reproduce these bytes or stop for review.

| Artifact | SHA256 |
|---|---|
| `ionoflux-0.1.0-py3-none-any.whl` | `44a8e9a3fdad60499a7d0e70e7d53f5a6f204c3dbb93d6360d8433d04a856080` |
| `ionoflux-0.1.0.tar.gz` | `5652fee6c650af23d689f7f4df29492b9f5815f8db36fa507ed8c29e74f583c6` |

Wheel/sdist checks cover official LICENSE bytes, Required Notice, SPDX/License-File metadata, file allowlists and credential-like content. Installation uses an independent temporary venv for each artifact and runs offline examples. No live IonoFlux API request is performed here; reuse the nine successful 2026-10-20 smoke requests documented in release-review.md. These hashes do not claim either index has accepted the package. PyPI name allocation and OIDC exchange can only be confirmed at an approved publish.
