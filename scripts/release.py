"""Release checks; network calls occur only in the explicitly selected tag gate."""

import hashlib
import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".github/release/0.1.0.json"
REPOSITORY = "hongjunna/ionoflux-python"


def validate_tag(index: str, event: str, repository: str, ref: str, version: str) -> None:
    if index not in {"pypi", "testpypi"}:
        raise ValueError("Unknown package index")
    prefix = "python-v" if index == "pypi" else "python-test-v"
    if event != "push" or repository != REPOSITORY or ref != f"refs/tags/{prefix}{version}":
        raise ValueError("Only the exact SDK version tag in the official repository may publish")


def verify_artifacts(dist: Path, manifest: dict[str, object]) -> None:
    expected = manifest["sha256"]
    if not isinstance(expected, dict) or set(expected) != {
        "ionoflux-0.1.0-py3-none-any.whl",
        "ionoflux-0.1.0.tar.gz",
    }:
        raise ValueError("Unexpected artifact manifest")
    actual = {p.name for p in dist.iterdir() if p.is_file()}
    if actual - {"SHA256SUMS"} != set(expected):
        raise ValueError("Unexpected distribution files")
    for name, digest in expected.items():
        if hashlib.sha256((dist / name).read_bytes()).hexdigest() != digest:
            raise ValueError("Artifact differs from reviewed release candidate")
    (dist / "SHA256SUMS").write_text("".join(f"{expected[n]}  {n}\n" for n in sorted(expected)))


def gate(index: str, version: str) -> None:
    validate_tag(
        index,
        os.environ["GITHUB_EVENT_NAME"],
        os.environ["GITHUB_REPOSITORY"],
        os.environ["GITHUB_REF"],
        version,
    )
    subprocess.run(["git", "fetch", "origin", "main"], cwd=ROOT, check=True)
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"], cwd=ROOT, check=True
    )
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    request = Request(
        f"https://api.github.com/repos/{REPOSITORY}/actions/workflows/ci.yml/runs"
        f"?event=push&head_sha={sha}&status=success&per_page=10",
        headers={
            "Authorization": "Bearer " + os.environ["GH_TOKEN"],
            "Accept": "application/vnd.github+json",
        },
    )
    with urlopen(request, timeout=20) as response:
        runs = json.load(response)["workflow_runs"]
    if not any(
        r["head_sha"] == sha and r["head_branch"] == "main" and r["conclusion"] == "success"
        for r in runs
    ):
        raise ValueError("Exact release commit has no successful main CI")
    host = "pypi.org" if index == "pypi" else "test.pypi.org"
    try:
        with urlopen(f"https://{host}/pypi/ionoflux/{version}/json", timeout=20):
            pass
    except HTTPError as error:
        if error.code != 404:
            raise RuntimeError("Cannot establish index version availability") from None
    else:
        raise ValueError("Version already exists; never overwrite or skip an existing release")
    print("Exact tag, main ancestry, successful CI and version availability verified")


def main() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    manifest = json.loads(MANIFEST.read_text())
    if project["name"] != "ionoflux" or project["version"] != manifest["version"]:
        raise ValueError("Distribution name/version mismatch")
    if sys.argv[1:] == ["verify"]:
        verify_artifacts(ROOT / "dist", manifest)
    elif len(sys.argv) == 3 and sys.argv[1] == "gate":
        gate(sys.argv[2], project["version"])
    else:
        raise ValueError("Use verify or gate pypi/testpypi")


if __name__ == "__main__":
    main()
