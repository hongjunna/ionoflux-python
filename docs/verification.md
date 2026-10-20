# Development verification — 2026-10-20 KST

Local environment: macOS, CPython 3.14. Mock tests block socket connections. Subsequent final review completed a separately authorized nine-request Server-key acceptance (release-review.md); no package-index upload or service changes. Public GET investigation is documented separately in api-contract.md.

| Check | Result |
|---|---|
| pytest | 111 passed after release and licensing regressions |
| Ruff lint and format | Passed |
| mypy strict | No issues in five SDK modules |
| examples/offline.py | Passed with mock transport |
| isolated python -m build | wheel and sdist produced; wheel built from sdist |
| twine check | Both distributions passed |
| artifact content scan | Allowed paths, py.typed and no credential-like content; exact counts/hashes printed per build |
| fresh wheel installation | Passed outside source tree in new venv; version/import/py.typed/offline example |
| fresh sdist installation | Passed independently in new venv; version/import/py.typed/offline example |
| GitHub multi-version/platform CI | Runtime head83cc217: [nine jobs passed](https://github.com/hongjunna/ionoflux-python/actions/runs/39379999139), including minimumHTTPX0.27.0; see PR checks for later documentation-head validation |
| safe authenticated production acceptance | Nine sequential GET requests, all200 and field/type checks passed; no retries; session closed |
| TestPyPI / PyPI | Not uploaded; explicitly excluded |

Initial Windows CI exposed an implicit cp1252 file read of the UTF-8 OpenAPI fixture (77 passed/1 failed). Explicit UTF-8 reads fix the fixture and install-script example loading. Full original failure log remains linked in the PR checks.

The first contract test incorrectly looked up concrete dataset paths in an OpenAPI document that uses path templates; corrected the fixture lookup. Initial result 71 passed/1 failed; final tests all pass. No server changes resulted.

A real packaging incompatibility was detected: Hatchling1.32.4 emitted core metadata2.5 while Twine6.2.0's package validator accepts up to2.4. Initial check output:

```text
Checking dist/ionoflux-0.1.0-py3-none-any.whl: ERROR InvalidDistribution:
Invalid distribution metadata: '2.5' is not a valid metadata version
```

Both build targets now explicitly request core-metadata-version2.4; artifact inspection asserts the version so a regression fails CI. This follows the documented [Hatch sdist](https://hatch.pypa.io/latest/plugins/builder/sdist/) and [wheel](https://hatch.pypa.io/latest/plugins/builder/wheel/) settings. Build and Twine checks then passed. The later owner-approved license adoption is independent of that compatibility fix.

Artifacts are intentionally ignored by Git. `python scripts/check_artifacts.py` prints SHA256 for each freshly built file; final source changes require fresh build hashes. Distribution content scanning is a bounded filename/credential-pattern check and allowlist, not a claim of universal secret detection. LICENSE now contains owner-approved, unmodified PolyForm Noncommercial1.0.0. NOTICE and SPDX/License-File fields are checked in both artifacts. TestPyPI/PyPI upload still needs separate approval; see issue3.
