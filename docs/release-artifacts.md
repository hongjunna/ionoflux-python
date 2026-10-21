# Reviewed release artifacts

## v0.1.2 candidate

Reproduce using `SOURCE_DATE_EPOCH=1792540800` and the pinned `.github/release/requirements.txt` toolchain. `.github/release/0.1.2.json` is the strict machine-readable manifest. Two consecutive local builds produced identical hashes. Exact main CI, the `python-v0.1.2` tag and the owner's manual `pypi` environment approval remain required. These release documents and manifests are excluded from wheel/sdist.

| Artifact | SHA256 |
|---|---|
| `ionoflux-0.1.2-py3-none-any.whl` | `c34b5109db964bebe14abe5d306540d62f795712f11b4ef147db1bb17cba6c38` |
| `ionoflux-0.1.2.tar.gz` | `339dcb6a9bb2ffc421e052b4e7f1b6d06b76fd6bfec7e72ef285d2ce795d5d3d` |

## v0.1.1 published — immutable historical evidence

Published 2026-10-20 from `f6e8b92d4c656fd80580f0e8b5bf507b11dcfd55`, tag `python-v0.1.1`, with `SOURCE_DATE_EPOCH=1792482800` and `.github/release/0.1.1.json`.

| Artifact | SHA256 |
|---|---|
| `ionoflux-0.1.1-py3-none-any.whl` | `382dbc8e47d5bc2a7f4fa1b97174ff1d78b6ea2b8c9e77318df0e3d7c66209ec` |
| `ionoflux-0.1.1.tar.gz` | `c1a7ad1da545e8d1d648189bc34f8524c8f12cc703c1bec7fbf49e4635eb25d6` |

Public file allowlists, credential-like content, official LICENSE hash, Required Notice, SPDX metadata, typing marker, Twine rendering and separate clean wheel/sdist installations were checked. No live API request was made. Rebuilds must match these hashes; any included-file change requires new reviewed hashes.

## v0.1.0 published — immutable historical evidence

Published 2026-10-20 from `841af55c18537cd46bd444e6160799afa7f773a9`, tag `python-v0.1.0`. Fresh PyPI installation and cryptographic attestation verification passed. [Original release](https://github.com/hongjunna/ionoflux-python/releases/tag/python-v0.1.0).

| Artifact | SHA256 |
|---|---|
| `ionoflux-0.1.0-py3-none-any.whl` | `44a8e9a3fdad60499a7d0e70e7d53f5a6f204c3dbb93d6360d8433d04a856080` |
| `ionoflux-0.1.0.tar.gz` | `5652fee6c650af23d689f7f4df29492b9f5815f8db36fa507ed8c29e74f583c6` |
