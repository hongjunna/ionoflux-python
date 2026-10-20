"""Fail if builds contain unexpected files or credential-like content; print SHA256."""

import hashlib
import re
import tarfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
FORBIDDEN = {".env", ".git", ".venv", "__pycache__", ".aws", ".codex", "agent-handoff.md"}
SECRET = re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ifx_[A-Za-z0-9_-]{20,}")


def inspect_file(name: str, body: bytes, wheel: bool) -> None:
    parts = PurePosixPath(name).parts
    assert not PurePosixPath(name).is_absolute() and ".." not in parts, "Unsafe archive path"
    assert not (set(parts) & FORBIDDEN), f"Forbidden path: {name}"
    assert not SECRET.search(body), f"Credential-like bytes in {name}"
    if wheel:
        assert parts[0] == "ionoflux" or parts[0].endswith(".dist-info"), name
        if parts[0] == "ionoflux":
            assert name.endswith((".py", "/py.typed")), name
    else:
        relative = parts[1:]
        assert relative and relative[0] in {
            "src",
            "tests",
            "examples",
            "scripts",
            "docs",
            "README.md",
            "README.ko.md",
            "CHANGELOG.md",
            "LICENSE",
            "pyproject.toml",
            "PKG-INFO",
            ".gitignore",
        }, name
        if relative[0] == "docs":
            assert len(relative) == 2 and relative[1] in {"api-contract.md", "openapi-v0.1.json"}, (
                "Internal development document in distribution"
            )


def main() -> None:
    wheels, sdists = list(DIST.glob("*.whl")), list(DIST.glob("*.tar.gz"))
    assert len(wheels) == len(sdists) == 1, "Expect exactly one wheel and one sdist"
    for artifact in wheels + sdists:
        files = {}
        if artifact.suffix == ".whl":
            with zipfile.ZipFile(artifact) as archive:
                files = {n: archive.read(n) for n in archive.namelist() if not n.endswith("/")}
        else:
            with tarfile.open(artifact) as archive:
                for member in archive.getmembers():
                    assert member.isfile() or member.isdir(), "Links are not allowed in sdist"
                    if member.isfile():
                        stream = archive.extractfile(member)
                        assert stream is not None
                        files[member.name] = stream.read()
        for name, body in files.items():
            if name.endswith(("/METADATA", "/PKG-INFO")):
                assert body.startswith(b"Metadata-Version: 2.4\n"), "Unsupported metadata version"
            inspect_file(name, body, artifact.suffix == ".whl")
        assert any(n.endswith("ionoflux/py.typed") for n in files), "py.typed missing"
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        print(f"{artifact.name}: {len(files)} files, sha256={digest}")


if __name__ == "__main__":
    main()
