"""Release gates are tested offline; these tests never invoke an upload."""

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release", ROOT / "scripts/release.py")
assert spec and spec.loader
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


@pytest.mark.parametrize("index,prefix", [("pypi", "python-v"), ("testpypi", "python-test-v")])
def test_exact_release_tag(index, prefix):
    release.validate_tag(index, "push", release.REPOSITORY, f"refs/tags/{prefix}0.1.0", "0.1.0")


@pytest.mark.parametrize(
    "event,repo,ref",
    [
        ("workflow_dispatch", release.REPOSITORY, "refs/tags/python-v0.1.0"),
        ("pull_request", release.REPOSITORY, "refs/tags/python-v0.1.0"),
        ("push", "other/ionoflux-python", "refs/tags/python-v0.1.0"),
        ("push", release.REPOSITORY, "refs/heads/main"),
        ("push", release.REPOSITORY, "refs/tags/v0.1.0"),
        ("push", release.REPOSITORY, "refs/tags/python-test-v0.1.0"),
        ("push", release.REPOSITORY, "refs/tags/python-v0.2.0"),
    ],
)
def test_reject_unapproved_trigger(event, repo, ref):
    with pytest.raises(ValueError):
        release.validate_tag("pypi", event, repo, ref, "0.1.0")


def test_unknown_index():
    with pytest.raises(ValueError):
        release.validate_tag(
            "other", "push", release.REPOSITORY, "refs/tags/python-v0.1.0", "0.1.0"
        )


def candidate(tmp_path):
    files = {"ionoflux-0.1.0-py3-none-any.whl": b"wheel", "ionoflux-0.1.0.tar.gz": b"sdist"}
    for name, body in files.items():
        (tmp_path / name).write_bytes(body)
    return {"sha256": {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}}


def test_checksums(tmp_path):
    manifest = candidate(tmp_path)
    release.verify_artifacts(tmp_path, manifest)
    assert (tmp_path / "SHA256SUMS").read_text().count("\n") == 2
    release.verify_artifacts(tmp_path, manifest)


def test_tampered_artifact(tmp_path):
    manifest = candidate(tmp_path)
    (tmp_path / "ionoflux-0.1.0.tar.gz").write_bytes(b"changed")
    with pytest.raises(ValueError, match="differs"):
        release.verify_artifacts(tmp_path, manifest)


def test_extra_file_rejected(tmp_path):
    manifest = candidate(tmp_path)
    (tmp_path / "credentials.txt").write_text("not a distribution")
    with pytest.raises(ValueError, match="Unexpected distribution"):
        release.verify_artifacts(tmp_path, manifest)


def test_manifest_path_escape(tmp_path):
    with pytest.raises(ValueError, match="Unexpected artifact"):
        release.verify_artifacts(tmp_path, {"sha256": {"../outside": "a"}})


@pytest.mark.parametrize(
    "index,file,flag",
    [
        ("pypi", "publish.yml", "PYPI_PUBLISH_ENABLED"),
        ("testpypi", "publish-test.yml", "TESTPYPI_PUBLISH_ENABLED"),
    ],
)
def test_publisher_security_boundaries(index, file, flag):
    # Workflow files are intentionally excluded from distributions.
    path = ROOT / ".github/workflows" / file
    if not path.exists():
        pytest.skip("Repository-only workflow check")
    body = path.read_text()
    assert "pull_request" not in body
    assert body.count("id-token: write") == 1
    assert f"name: {index}" in body
    assert f"vars.{flag} == 'true'" in body
    assert "github.event_name == 'push'" in body
    assert "skip-existing: false" in body
    assert "attestations: true" in body
    assert "artifact-ids: ${{ needs.build.outputs.artifact-id }}" in body
    assert "sha256sum --strict --check SHA256SUMS" in body
    assert "persist-credentials: false" in body
    if index == "pypi":
        assert "https://upload.pypi.org/legacy/" in body
        assert "test.pypi.org" not in body
    else:
        assert "https://test.pypi.org/legacy/" in body


def test_release_version_matches_project():
    path = ROOT / ".github/release/0.1.0.json"
    if not path.exists():
        pytest.skip("Repository-only release manifest")
    assert json.loads(path.read_text())["version"] == "0.1.0"


@pytest.mark.parametrize("status", [401, 403, 429, 500])
def test_index_error_fails_closed(monkeypatch, status):
    from io import BytesIO
    from urllib.error import HTTPError

    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_REPOSITORY", release.REPOSITORY)
    monkeypatch.setenv("GITHUB_REF", "refs/tags/python-v0.1.0")
    monkeypatch.setenv("GH_TOKEN", "mock-ci-token")
    monkeypatch.setattr(release.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(release.subprocess, "check_output", lambda *a, **k: "abc\n")

    def open_response(url, **kwargs):
        if isinstance(url, release.Request):
            return BytesIO(
                json.dumps(
                    {
                        "workflow_runs": [
                            {"head_sha": "abc", "head_branch": "main", "conclusion": "success"}
                        ]
                    }
                ).encode()
            )
        raise HTTPError(url, status, "mock index error", {}, None)

    monkeypatch.setattr(release, "urlopen", open_response)
    with pytest.raises(RuntimeError, match="availability"):
        release.gate("pypi", "0.1.0")


@pytest.mark.parametrize("available", [True, False])
def test_version_must_be_absent(monkeypatch, available):
    from io import BytesIO
    from urllib.error import HTTPError

    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_REPOSITORY", release.REPOSITORY)
    monkeypatch.setenv("GITHUB_REF", "refs/tags/python-v0.1.0")
    monkeypatch.setenv("GH_TOKEN", "mock-ci-token")
    monkeypatch.setattr(release.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(release.subprocess, "check_output", lambda *a, **k: "abc\n")

    def open_response(url, **kwargs):
        if isinstance(url, release.Request):
            return BytesIO(
                json.dumps(
                    {
                        "workflow_runs": [
                            {"head_sha": "abc", "head_branch": "main", "conclusion": "success"}
                        ]
                    }
                ).encode()
            )
        if available:
            raise HTTPError(url, 404, "not found", {}, None)
        return BytesIO(b"{}")

    monkeypatch.setattr(release, "urlopen", open_response)
    if available:
        release.gate("pypi", "0.1.0")
    else:
        with pytest.raises(ValueError, match="already exists"):
            release.gate("pypi", "0.1.0")


def test_missing_main_ci_stops_before_index(monkeypatch):
    from io import BytesIO

    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_REPOSITORY", release.REPOSITORY)
    monkeypatch.setenv("GITHUB_REF", "refs/tags/python-v0.1.0")
    monkeypatch.setenv("GH_TOKEN", "mock-ci-token")
    monkeypatch.setattr(release.subprocess, "run", lambda *a, **k: None)
    monkeypatch.setattr(release.subprocess, "check_output", lambda *a, **k: "abc\n")
    calls = []

    def open_response(url, **kwargs):
        calls.append(url)
        return BytesIO(b'{"workflow_runs": []}')

    monkeypatch.setattr(release, "urlopen", open_response)
    with pytest.raises(ValueError, match="successful main CI"):
        release.gate("pypi", "0.1.0")
    assert len(calls) == 1
