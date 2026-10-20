# Published v0.1.0 artifacts

Built with fixed SOURCE_DATE_EPOCH1792479234 and the pinned release toolchain. PR#7 was integrated as841af55c18537cd46bd444e6160799afa7f773a9 and exact main CI passed9/9. These are the final hashes published by approved run39386641635 at tagpython-v0.1.0. Actual downloaded PyPI files match, both attestations passed cryptographic verification and fresh installation/offline checks passed. This document and the machine-readable manifest are excluded from both distributions. A later build must reproduce these bytes or stop for review.

| Artifact | SHA256 |
|---|---|
| `ionoflux-0.1.0-py3-none-any.whl` | `44a8e9a3fdad60499a7d0e70e7d53f5a6f204c3dbb93d6360d8433d04a856080` |
| `ionoflux-0.1.0.tar.gz` | `5652fee6c650af23d689f7f4df29492b9f5815f8db36fa507ed8c29e74f583c6` |

Wheel/sdist checks cover official LICENSE bytes, Required Notice, SPDX/License-File metadata, file allowlists and credential-like content. Installation uses an independent temporary venv for each artifact and runs offline examples. No live IonoFlux API request is performed here; reuse the nine successful 2026-10-20 smoke requests documented in release-review.md. Production PyPI accepted these files and OIDC publishing succeeded after the owner manually approved the pypi environment. TestPyPI was skipped. Future development builds/PR#8 are separate and must not overwrite these immutable files.
