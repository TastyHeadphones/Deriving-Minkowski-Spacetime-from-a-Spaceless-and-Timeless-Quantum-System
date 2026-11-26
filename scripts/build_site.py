"""Build a self-contained static site with commit-matched scientific reports."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "research/papers/correlation-underdetermination.md"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_document(source, target, title=None):
    command = ["pandoc", "--standalone", "--mathml", "--css", "site.css",
               "--include-before-body", str(target.parent / "navigation.html"),
               "--variable", "document-css=false", str(source), "-o", str(target)]
    if title:
        command.extend(["--metadata", f"pagetitle={title}"])
    subprocess.run(command, check=True)
    html = target.read_text(encoding="utf-8")
    target.write_text(html.replace("<body>", '<body class="document">', 1), encoding="utf-8")


def use_report(path, commit, proof=False):
    if not path.is_file():
        return None
    report = read(path)
    if report.get("status") != "passed" or report.get("source_commit") != commit:
        return None
    if proof and not report.get("clean_source_tree"):
        return None
    return report


def build(output, artifacts, require_verification, pdf):
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=ROOT).strip()
    source_registry = read(ROOT / "registry/theorems.json")["theorems"]
    proof_path = artifacts / "proof/verification.json"
    repro_path = artifacts / "reproducibility/reproducibility.json"
    proof = use_report(proof_path, commit, proof=True)
    reproducibility = use_report(repro_path, commit)
    if require_verification and (not proof or not reproducibility or
                                 reproducibility["lean_audit_for_source_commit"] != "passed"):
        raise ValueError("This build requires commit-matched proof and reproducibility reports")
    if require_verification:
        reports = {"verification.json": proof_path, "results.json": artifacts / "science/results.json",
                   "grid-growth.svg": artifacts / "science/grid-growth.svg"}
        for name, path in reports.items():
            if hashlib.sha256(path.read_bytes()).hexdigest() != reproducibility["sha256"][name]:
                raise ValueError(f"Published artifact does not match the recorded checksum: {name}")
    if proof and {r["id"] for r in proof["theorems"]} != {r["id"] for r in source_registry}:
        raise ValueError("Proof report does not match the source theorem registry")

    if not proof:
        for record in source_registry:
            path = ROOT / record["source"]
            name = record["lean_name"].split(".")[-1]
            source = path.read_text(encoding="utf-8")
            match = re.search(rf"(?ms)^theorem {re.escape(name)}(?=\s).*?:= by", source)
            if not match:
                raise ValueError(f"Cannot locate signature for {name}")
            record["lean_statement"] = match[0].removesuffix(":= by").rstrip()

    examples = [line.strip("|").split("|") for line in
                (ROOT / "research/counterexamples/README.md").read_text(encoding="utf-8").splitlines()
                if re.match(r"\| C[0-9]+ ", line)]
    milestones = read(ROOT / "research/research-log/milestones.json")
    if proof:
        date = subprocess.check_output(["git", "show", "-s", "--format=%cs", commit],
                                       text=True, cwd=ROOT).strip()
        milestones.append({"date": date, "title": "Lean verification",
                           "detail": f"Built and audited {len(proof['theorems'])} declarations for {commit[:12]}."})
    data = {
        "source_commit": commit,
        "verification": {"physical_axioms_in_lean": proof["physical_axioms_in_lean"]} if proof else None,
        "proofs": proof["theorems"] if proof else source_registry,
        "axioms": read(ROOT / "registry/axioms.json")["entries"],
        "conjectures": read(ROOT / "registry/conjectures.json")["conjectures"],
        "milestones": milestones,
        "counterexamples": [[part.strip() for part in example] for example in examples],
        "science": read(artifacts / "science/results.json"),
        "reproducibility": bool(reproducibility),
        "ci_url": os.getenv("RESEARCH_CI_URL"),
        "default_branch": os.getenv("RESEARCH_DEFAULT_BRANCH", "main"),
        "pdf": pdf,
    }
    output.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output.parent) as directory:
        site = Path(directory)
        for name in ("index.html", "site.css", "app.js", "models.js"):
            shutil.copyfile(ROOT / "website" / name, site / name)
        (site / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (site / "navigation.html").write_text(
            '<nav aria-label="Research site"><a href="index.html#library">← Research library</a></nav>\n',
            encoding="utf-8")
        build_document(PAPER, site / "paper.html")
        build_document(ROOT / "research/literature/README.md", site / "literature.html", "Primary sources")
        (site / "navigation.html").unlink()
        if pdf:
            subprocess.run(["pandoc", str(PAPER), "--pdf-engine=pdflatex", "-V", "geometry:margin=1in",
                            "-o", str(site / "paper.pdf")], check=True)
        if proof:
            shutil.copyfile(proof_path, site / "proof-verification.json")
        if reproducibility:
            shutil.copyfile(repro_path, site / "reproducibility.json")
        shutil.copyfile(artifacts / "science/grid-growth.svg", site / "grid-growth.svg")
        (site / ".nojekyll").touch()
        for name in ("paper.pdf", "proof-verification.json", "reproducibility.json"):
            if not (site / name).exists():
                (output / name).unlink(missing_ok=True)
        shutil.copytree(site, output, dirs_exist_ok=True)
    print(f"Built static research site in {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "_site")
    parser.add_argument("--artifacts", type=Path, default=ROOT / "artifacts")
    parser.add_argument("--require-verification", action="store_true")
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()
    build(args.out.resolve(), args.artifacts.resolve(), args.require_verification, args.pdf)


if __name__ == "__main__":
    main()
