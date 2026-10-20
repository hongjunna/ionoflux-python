# Independent SDK development plan

Service parent: [iono-flux#44](https://github.com/hongjunna/iono-flux/issues/44). Implementation lives exclusively in [ionoflux-python](https://github.com/hongjunna/ionoflux-python), replacing the earlier sdk/python monorepo proposal. Phase 4 improvement linked to S1/S2, excluded from the fixed core denominator; overall roadmap remains 47.9% with Phase 2 focus.

1. [#1 v0.1 contract, client and development checks](https://github.com/hongjunna/ionoflux-python/issues/1): investigate source/OpenAPI/public routes, implement supported synchronous endpoints, offline regression/security tests, documentation, packaging and CI. Completed and integrated by squash-merging PR #4 as b446319; main CI passed 9/9. Issues #1/#5/#6 are closed after integration. Mark only checks actually completed; CI success is separate from production acceptance.
2. [#2 subsequent endpoints](https://github.com/hongjunna/ionoflux-python/issues/2): TEC/MUF, propagation, stations and WSPR/PSK with contract, provider policy and model/observation distinction. Async, pandas extras and bounded historical splitting are also later work, not v0.1 claims.
3. [#3 initial release](https://github.com/hongjunna/ionoflux-python/issues/3): completed on 2026-10-20. PyPI v0.1.0, clean installation, artifact checksums and attestations were verified. [Release evidence](https://github.com/hongjunna/ionoflux-python/releases/tag/python-v0.1.0) is historical and immutable. Future endpoint work remains in #2; the optional smoke workflow in PR #8 is separate and unmerged.

The official distribution/import name is **ionoflux**: `pip install ionoflux`. Python 3.11+ is required. PolyForm Noncommercial 1.0.0 and NOTICE apply; proposed API terms remain unapproved. v0.1.1 is a documentation/metadata patch prepared for separate merge and publication approval. Protected GitHub environments and Trusted Publishing remain mandatory; TestPyPI can be skipped for this patch.

## Development setup and validation

```sh
git clone https://github.com/hongjunna/ionoflux-python.git
cd ionoflux-python
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
ruff check .
ruff format --check .
mypy
python -m build
python -m twine check dist/*
python scripts/check_readme.py
python scripts/check_artifacts.py
python scripts/check_install.py
python examples/offline.py
```

On Windows PowerShell use `py -m venv .venv` and `.\.venv\Scripts\Activate.ps1`. Release reproduction uses the pinned toolchain and epoch in the reviewed release manifest; see release-preparation.md.

Do not deploy the service, alter DB/API-key policy, touch service #43, auto-merge PRs, upload to TestPyPI/PyPI or run ML/backfill. Publishing preparation uses SDK-specific tags, protected environments, separate index Trusted Publishers/OIDC, artifact hashes, validation and explicit release authorization; see release-preparation.md. Builds and distribution files alone are not release acceptance. Stop live validation on 401/403/429; never invent a key or spoof Origin.
