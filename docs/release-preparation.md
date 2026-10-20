# v0.1.0 release preparation

PR #4 was approved and squash-merged on 2026-10-20 as `b4463192737b7de8400283d5bb20a4c6933d0177`. [Merged main CI](https://github.com/hongjunna/ionoflux-python/actions/runs/39383090956) passed all nine jobs (111 tests). The original preparation stopped before publication; the subsequently approved publication is recorded below.

## Completed first publication (2026-10-20)

PR #7 was subsequently approved and squash-merged as `841af55c18537cd46bd444e6160799afa7f773a9`; exact main CI39385132041 passed9/9 with135 tests. Tag `python-v0.1.0` and [production run39386641635](https://github.com/hongjunna/ionoflux-python/actions/runs/39386641635) published [ionoflux0.1.0](https://pypi.org/project/ionoflux/0.1.0/) after hongjunna manually approved `pypi`. A fresh PyPI install, import/version, pip check, SPDX/LICENSE/NOTICE/py.typed and offline example passed. Both actual downloaded file hashes match the manifest and both attestations passed cryptographic verification using pypi-attestations0.0.30. The owner confirmed2FA; production and testing variables are false again. TestPyPI was skipped. The [GitHub Release](https://github.com/hongjunna/ionoflux-python/releases/tag/python-v0.1.0) includes reviewed artifacts and hashes. No additional live API call was made. This completed release is immutable.

The checklist below records the approved first-release procedure; it is not authorization to repeat a publish. Future optional smoke automation is a separate development change, excluded from the existing0.1.0 commit/tag/files. Normal development CI validates newly changed artifacts without demanding byte equality to an already published release; tag publishers retain strict release-manifest verification. A future package release requires a new version, manifest and approval.

## Exact Trusted Publisher settings

| Field | Production | Future testing |
|---|---|---|
| Index | PyPI | TestPyPI (separate account/service) |
| Project | `ionoflux` | `ionoflux` |
| GitHub owner | `hongjunna` | `hongjunna` |
| Repository | `ionoflux-python` | `ionoflux-python` |
| Workflow filename | `publish.yml` | `publish-test.yml` |
| Environment | `pypi` | `testpypi` |
| SDK tag for 0.1.0 | `python-v0.1.0` | `python-test-v0.1.0` |
| Enable variable | `PYPI_PUBLISH_ENABLED` | `TESTPYPI_PUBLISH_ENABLED` |

The owner reports that the production Pending Trusted Publisher is registered and visible. This private account state was not independently inspected. Pending registration does not reserve a project name; actual creation may still fail. Do not upload a placeholder. TestPyPI registration has not been confirmed. The production v0.1.0 release deliberately skips TestPyPI, and does not wait for a Junlab Community organization. A later ownership transfer needs a separate plan.

Both GitHub environments are configured with tag-only patterns (`python-v*` / `python-test-v*`) and required reviewer `hongjunna`. Self-approval is explicitly authorized by the owner for this personal repository; it still requires a manual approval action. GitHub currently permits administrator bypass of environment protection; do not use bypass. Repository administrators can also change workflows, variables and protections; this is not a two-person approval system. Both enable variables are `false` and must remain so until the respective publication is explicitly approved. No API token or long-lived PyPI credential is needed.

## Workflow safety and verification

- The two independently pinned workflows publish to separate index URLs and environments. Normal PR CI has only `contents: read`; release build jobs additionally have `actions: read` to check CI. Only the protected publish job receives `id-token: write`.
- `workflow_dispatch` validates/builds only. It cannot publish even if an enable variable is true. There is no release creation or tag push step, no PR publisher, no `pull_request_target` handler and no repository write permission.
- Tag publishing requires the exact manifest version/tag, official repository, tag commit already on main, and successful `ci.yml` push CI for that exact commit. Missing CI, index lookup errors, an existing version or checksum differences fail closed. Checks do not deliberately consume IonoFlux API quota.
- Build tools are pinned in `.github/release/requirements.txt`. `SOURCE_DATE_EPOCH` is fixed in `.github/release/0.1.0.json`; wheel and sdist hashes must match the reviewed candidate. Runtime code, README, tests or packaging changes require a new candidate and hash review. The manifest and workflow/internal documents are excluded from distributions.
- Build validates Twine, LICENSE/NOTICE, SPDX, metadata, file allowlists, credential-like content and clean wheel/sdist installs. Both artifacts plus SHA256SUMS use an immutable Actions artifact ID. The publisher downloads that exact ID, checks hashes, removes the checksum file and invokes the SHA-pinned official PyPA action with OIDC attestations and `skip-existing: false`.
- Per-index/tag concurrency serializes runs. PyPI immutable versions and `skip-existing: false` reject duplicate posting; a rerun after a partial upload can fail rather than silently complete. Inspect index state before deciding recovery; never overwrite. The availability check is advisory and cannot reserve a name or eliminate a race.

## Final production authorization checklist

1. Review/integrate the publishing preparation PR and wait for its exact main CI to pass; manual validation must reproduce the manifest hashes. Verify environments/variables and the registered Pending Publisher still match the table.
2. Owner confirms PyPI account email/2FA/recovery and project creation rights; the reported pending registration is already complete. No new organization approval or TestPyPI run is required.
3. Obtain explicit production posting approval covering the reviewed commit/artifact hashes, enabling `PYPI_PUBLISH_ENABLED`, and creating/pushing **only** `python-v0.1.0`. Current authorization excludes these actions. Keep the TestPyPI flag false.
4. After approval, set the production flag true, create the exact SDK tag at the reviewed main commit and push it. Verify the build artifact and manually approve the `pypi` environment job. This final manual environment action is independent of chat approval; never bypass it.
5. After posting, disable the flag, install `ionoflux==0.1.0` from PyPI in a clean environment, verify metadata/import/offline example and index hashes/attestations. Inspect public README rendering and license notices. A live API check requires a separately safe key/budget if needed; the prior nine successful requests are reused here.

A package defect after posting requires a new version; consider yanking a broken version with a reason instead of replacing files. Any GitHub Release creation requires separate authorization. Future TestPyPI testing requires its own Pending Publisher/account confirmation, version/candidate review, flag and upload authorization; it does not block this production release.

The adopted SDK code license is the unmodified PolyForm Noncommercial License 1.0.0, with IonoFlux Required Notice and SPDX metadata. SDK license approval is complete. API terms remain a draft, and [legal/provider-rights preflight](api-terms-preflight.ko.md) must precede any later API terms activation. No service/DB/key-policy/terms changes are part of publishing.

References: [PyPI publisher setup](https://docs.pypi.org/trusted-publishers/adding-a-publisher/), [pending publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/), [official OIDC publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/), [GitHub environment protection](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment).
