"""Distribution licensing gates: prevent dropping a required notice or changing the standard."""

import hashlib
from pathlib import Path

import pytest

from scripts.check_artifacts import OFFICIAL_LICENSE_SHA256, REQUIRED_NOTICE, inspect_licensing

ROOT = Path(__file__).parents[1]


def bundle(wheel):
    prefix = "ionoflux-0.1.0.dist-info/" if wheel else "ionoflux-0.1.0/"
    licenses = prefix + "licenses/" if wheel else prefix
    name = prefix + ("METADATA" if wheel else "PKG-INFO")
    return (
        name,
        licenses,
        {
            name: (
                b"Metadata-Version: 2.4\nLicense-Expression: PolyForm-Noncommercial-1.0.0\n"
                b"License-File: LICENSE\nLicense-File: NOTICE\n\n"
            ),
            licenses + "LICENSE": (ROOT / "LICENSE").read_bytes(),
            licenses + "NOTICE": (ROOT / "NOTICE").read_bytes(),
        },
    )


@pytest.mark.parametrize("wheel", [True, False])
def test_license_and_notice_in_both_distribution_formats(wheel):
    _, _, files = bundle(wheel)
    inspect_licensing(files, wheel)
    assert hashlib.sha256((ROOT / "LICENSE").read_bytes()).hexdigest() == OFFICIAL_LICENSE_SHA256
    assert (ROOT / "NOTICE").read_bytes() == REQUIRED_NOTICE


@pytest.mark.parametrize("wheel", [True, False])
@pytest.mark.parametrize(
    "defect",
    [
        "missing_license",
        "missing_notice",
        "changed_license",
        "changed_notice",
        "missing_declaration",
        "wrong_spdx",
    ],
)
def test_distribution_gate_rejects_license_or_notice_regressions(wheel, defect):
    name, prefix, files = bundle(wheel)
    if defect == "missing_license":
        del files[prefix + "LICENSE"]
    elif defect == "missing_notice":
        del files[prefix + "NOTICE"]
    elif defect == "changed_license":
        files[prefix + "LICENSE"] += b"Additional restriction\n"
    elif defect == "changed_notice":
        files[prefix + "NOTICE"] = b"IonoFlux\n"
    elif defect == "missing_declaration":
        files[name] = files[name].replace(b"License-File: NOTICE\n", b"")
    elif defect == "wrong_spdx":
        files[name] = files[name].replace(b"PolyForm-Noncommercial-1.0.0", b"MIT")
    with pytest.raises(AssertionError):
        inspect_licensing(files, wheel)
