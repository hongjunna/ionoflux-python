# Release gates and Trusted Publisher preparation

The owner adopted PolyForm Noncommercial License 1.0.0 on 2026-10-20. LICENSE is the unmodified official text; NOTICE carries the IonoFlux name/URL and metadata declares PolyForm-Noncommercial-1.0.0 plus both files. The code-license choice is resolved; do not label it MIT/Apache or OSI open source. SDK licensing, API terms and third-party data rights are separate. API terms remain a draft. Code-license approval is not merge or upload authorization.

Target v0.1.0 distribution/import: ionoflux; alternative distribution ionoflux-sdk. Search absence/JSON404 has not reserved the name or proven registration availability. Confirm ownership before configuring or publishing; do not request a name by uploading a placeholder.

## Before TestPyPI

- Obtain the owner's final merge approval, then keep a reviewed source commit, SDK tag policy and artifact SHA256 records. Do not auto-merge or tag for publishing in this task.
- Verify the adopted SDK license and package metadata/README/LICENSE/NOTICE consistency and both license-file declarations. Build/test/inspect both artifacts again after any license or metadata change.
- Confirm PyPI/TestPyPI owner accounts,2FA, contact and recovery access. TestPyPI is a separate service/configuration; do not assume production ownership carries over.
- Choose a future publishing workflow path/name (proposal release.yml), GitHub owner hongjunna, repository ionoflux-python and GitHub environment names (proposal testpypi and pypi). Environment names must match publisher configuration exactly.
- In each index, configure an existing-project Trusted Publisher or a pending publisher for a not-yet-created project. Use the exact owner/repository/workflow filename/environment; configuring a pending publisher does not create or reserve the project name. Follow current index docs and recheck values before use.
- Add a future workflow only after its approval controls are reviewed: protected environment/manual reviewer, SDK-specific version tag, minimal contents:read/id-token:write, fixed trusted action SHA, validation before upload, build once and promote reviewed artifacts. No publish on pull_request/pull_request_target and no token credentials in CI or repository.
- Reuse the completed9request Server smoke evidence; after incompatible changes prepare a new separately bounded acceptance plan. Do not reuse the temporary key after the owner revokes it. Avoid intentional401/403/429 load/quota tests.
- Obtain explicit authorization for TestPyPI upload. Current request prohibits upload; no publishing workflow or publisher account settings were changed.

## Before production PyPI

After separately authorized TestPyPI posting, install in a clean environment and verify metadata/import/version/documented examples, source hashes and index ownership. Dependencies should come from the trusted dependency index separately to avoid mixing similarly named packages. Obtain separate production posting authorization and repeat ownership/environment/review checks; passing CI or merging PR#4 does not authorize an upload. Document install acceptance and a yank/new-version recovery procedure; never overwrite a published version.

Before API terms take effect, complete the legal/provider-rights checklist in api-terms-preflight.ko.md; this is separate from SDK licensing and package release.

Current repo workflows only test/build/install and have contents:read; they cannot publish. The9successful production read-only smoke calls are acceptance evidence, not an upload approval or a claim of all provider/API permutations.

Official setup references: [Adding a publisher](https://docs.pypi.org/trusted-publishers/adding-a-publisher/), [Pending publisher/new project](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/). Names above are proposed setup values, not completed account configuration.
