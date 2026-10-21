"""Install each artifact in a fresh venv and run only offline API examples.

Requires package-index access for dependencies/build tools, never calls IonoFlux.
"""

import os
import subprocess
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    artifacts = sorted((ROOT / "dist").glob("*.whl")) + sorted((ROOT / "dist").glob("*.tar.gz"))
    assert len(artifacts) == 2, "Build wheel and sdist first"
    for artifact in artifacts:
        with tempfile.TemporaryDirectory(prefix="ionoflux-install-") as directory:
            tmp = Path(directory)
            venv.create(tmp / "venv", with_pip=True)
            python = tmp / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            subprocess.run(
                [str(python), "-m", "pip", "install", str(artifact)], check=True, cwd=tmp
            )
            subprocess.run([str(python), "-m", "pip", "check"], check=True, cwd=tmp)
            code = "\n".join(
                [
                    "import importlib.metadata as m, importlib.resources as r",
                    "import ionoflux",
                    "assert m.version('ionoflux') == ionoflux.__version__ == '0.1.2'",
                    "assert r.files('ionoflux').joinpath('py.typed').is_file()",
                    "print('Installed artifact:', ionoflux.__file__)",
                    (ROOT / "examples/offline.py").read_text(encoding="utf-8"),
                ]
            )
            env = {
                k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "IONOFLUX_API_KEY")
            }
            subprocess.run([str(python), "-c", code], check=True, cwd=tmp, env=env)
            print(f"Clean install PASS: {artifact.name}")


if __name__ == "__main__":
    main()
