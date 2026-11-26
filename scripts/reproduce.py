"""Regenerate science artifacts in isolated directories and record their digests."""

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--science", type=Path, default=Path("artifacts/science"))
    parser.add_argument("--proof", type=Path, default=Path("artifacts/proof"))
    parser.add_argument("--out", type=Path, default=Path("artifacts/reproducibility"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    report_path = args.out / "reproducibility.json"
    report_path.unlink(missing_ok=True)
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], check=True)
    names = ["results.json", "grid-growth.svg", "versions.json"]
    with tempfile.TemporaryDirectory() as directory:
        first = Path(directory) / "first"
        second = Path(directory) / "second"
        for target in (first, second):
            subprocess.run([sys.executable, "-m", "experiments.run", "--out", str(target)], check=True)
        for name in names:
            if sha(first / name) != sha(second / name) or sha(first / name) != sha(args.science / name):
                raise ValueError(f"Regenerated artifact differs: {name}")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    proof_path = args.proof / "verification.json"
    proof = json.loads(proof_path.read_text(encoding="utf-8")) if proof_path.is_file() else None
    proof_matches = bool(proof and proof["status"] == "passed" and
                         proof["source_commit"] == commit and proof["clean_source_tree"])
    science_report = {
        "status": "passed",
        "source_commit": commit,
        "scientific_tests": "passed",
        "lean_audit_for_source_commit": "passed" if proof_matches else "unavailable",
        "versions": json.loads((args.science / "versions.json").read_text(encoding="utf-8")),
        "config": json.loads((args.science / "results.json").read_text(encoding="utf-8"))["config"],
        "sha256": {name: sha(args.science / name) for name in names},
    }
    if proof_matches:
        science_report["lean"] = proof["lean"]
        packages = json.loads(Path("lake-manifest.json").read_text(encoding="utf-8"))["packages"]
        science_report["lean_dependencies"] = {package["name"]: package["rev"] for package in packages}
        science_report["sha256"]["verification.json"] = sha(proof_path)
        for name in ["lean-audit.log", "dependencies.dot"]:
            science_report["sha256"][name] = sha(args.proof / name)
    report_path.write_text(json.dumps(science_report, indent=2) + "\n", encoding="utf-8")
    print("Scientific artifacts reproduced twice and matched the reference artifacts.")


if __name__ == "__main__":
    main()
