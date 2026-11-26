"""Build and audit registered Lean declarations from the pinned source tree."""

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(r"\b(?:sorry|admit|sorryAx|axiom|axioms|constant|unsafe|native_decide|run_tac)\b")
DECLARATION = re.compile(r"(?m)^\s*(?:(?:private|protected)\s+)?(?:theorem|lemma)\s+(\w+)")


def run(*args, capture=False):
    return subprocess.run(args, cwd=ROOT, check=True, text=True,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.STDOUT if capture else None).stdout


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def validate_registry(theorems, axioms, conjectures):
    records = theorems + axioms + conjectures
    graph = {item["id"]: item.get("dependencies", []) + item.get("assumptions", [])
             for item in records}
    if len(graph) != len(records):
        raise ValueError("Duplicate registry identifier")
    visited = set()

    def visit(node, parents):
        if node not in graph:
            raise ValueError(f"Missing dependency {node}")
        if node in parents:
            raise ValueError(f"Registry dependency cycle through {node}")
        if node not in visited:
            for edge in graph[node]:
                visit(edge, parents | {node})
            visited.add(node)

    for node in graph:
        visit(node, set())
    declared = set()
    for path in [ROOT / "EmergentSpacetime.lean", *sorted((ROOT / "EmergentSpacetime").glob("*.lean"))]:
        # Apply a deliberately conservative source rule to executable and comment text.
        text = path.read_text(encoding="utf-8")
        violation = FORBIDDEN.search(text)
        if violation:
            raise ValueError(f"{path.relative_to(ROOT)} contains forbidden token {violation[0]}")
        declared.update((path.relative_to(ROOT).as_posix(), name) for name in DECLARATION.findall(text))
    registered = {(item["source"], item["lean_name"].split(".")[-1]) for item in theorems}
    if declared != registered:
        raise ValueError(f"Registry and source disagree: {declared ^ registered}")


LEAN_HEADER = '''import EmergentSpacetime
import Lean.Util.FoldConsts

open Lean Elab Command in
elab "#project_deps" id:ident : command => do
  let info ← getConstInfo id.getId
  let deps := info.getUsedConstantsAsSet.toList
  logInfo m!"PROJECT_DEPS {id.getId}: {String.intercalate "," (deps.map Name.toString)}"

'''


def audit(theorems, allowed, output):
    command_file = output / "Audit.lean"
    commands = []
    names = {entry["lean_name"]: entry["id"] for entry in theorems}
    for item in theorems:
        name = item["lean_name"]
        commands.extend((f"#check {name}", f"#print axioms {name}", f"#project_deps {name}"))
    command_file.write_text(LEAN_HEADER + "\n".join(commands) + "\n", encoding="utf-8")
    result = subprocess.run(["lake", "env", "lean", str(command_file)], cwd=ROOT,
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output / "lean-audit.log").write_text(result.stdout, encoding="utf-8")
    print(result.stdout, end="", flush=True)
    result.check_returncode()

    commit = run("git", "rev-parse", "HEAD", capture=True).strip()
    clean_sources = not run("git", "status", "--porcelain", "--untracked-files=all", capture=True).strip()
    for item in theorems:
        name = item["lean_name"]
        axiom_prefix = rf"(?m)^'{re.escape(name)}' "
        axiom_match = re.search(axiom_prefix + r"(?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)", result.stdout)
        if not axiom_match:
            raise ValueError(f"No axiom audit for {name}")
        axioms = sorted(a.strip() for a in (axiom_match[1] or "").split(",") if a.strip())
        unexpected = set(axioms) - allowed
        if unexpected:
            raise ValueError(f"{name} depends on unexpected axioms {unexpected}")
        if axioms != sorted(item["expected_kernel_axioms"]):
            raise ValueError(f"Kernel axiom footprint changed for {name}: {axioms}")
        signature = re.search(rf"(?ms)^({re.escape(name)}(?=[. ({{]).*?)\n'{re.escape(name)}' ", result.stdout)
        if not signature:
            raise ValueError(f"No Lean statement for {name}")
        deps = re.search(rf"PROJECT_DEPS {re.escape(name)}: ([^\n]*)", result.stdout)
        if not deps:
            raise ValueError(f"No compiler dependency footprint for {name}")
        project_constants = sorted(dependency for dependency in deps[1].split(",")
                                   if dependency.startswith("EmergentSpacetime."))
        formal_deps = {names[dep] for dep in project_constants if dep in names}
        declared_formal_deps = set(item["dependencies"]) & set(names.values())
        if formal_deps != declared_formal_deps:
            raise ValueError(f"Declared theorem dependencies differ for {name}: {formal_deps ^ declared_formal_deps}")
        item.update(verification_status="verified", lean_statement=signature[1],
                    kernel_axioms=axioms, compiler_project_dependencies=project_constants,
                    latest_verification_commit=commit if clean_sources else None)
    return {"status": "passed", "source_commit": commit, "clean_source_tree": clean_sources,
            "lean": run("lake", "env", "lean", "--version", capture=True).strip(),
            "physical_axioms_in_lean": 0, "theorems": theorems}


def write_graph(theorems, axioms, conjectures, output):
    lines = ["digraph project {"]
    for item in theorems + axioms + conjectures:
        ident = item["id"]
        lines.append(f'  "{ident}" [label={json.dumps(item["title"] + " (" + ident + ")")}];')
        for requirement in item.get("dependencies", []) + item.get("assumptions", []):
            lines.append(f'  "{requirement}" -> "{ident}";')
    (output / "dependencies.dot").write_text("\n".join([*lines, "}", ""]), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts/proof")
    options = parser.parse_args()
    output = options.out.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = output / "verification.json"
    report.unlink(missing_ok=True)
    registry = read_json("registry/axioms.json")
    theorems = read_json("registry/theorems.json")["theorems"]
    conjectures = read_json("registry/conjectures.json")["conjectures"]
    validate_registry(theorems, registry["entries"], conjectures)
    run("lake", "build")
    verified = audit(theorems, set(registry["kernel_allowed"]), output)
    write_graph(theorems, registry["entries"], conjectures, output)
    report.write_text(json.dumps(verified, indent=2) + "\n", encoding="utf-8")
    print(f"Verified and audited {len(theorems)} Lean theorems.")


if __name__ == "__main__":
    main()
