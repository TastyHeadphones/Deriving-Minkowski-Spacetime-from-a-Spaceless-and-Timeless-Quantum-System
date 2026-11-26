"""Generate a deterministic sweep with no external Python dependencies."""

import argparse
import json
import platform
from fractions import Fraction
from pathlib import Path
from random import Random
from xml.sax.saxutils import escape

from experiments import models

SEED = 24_149
GRAPHS = {
    "path": [(0, 1), (1, 2)],
    "triangle": [(0, 1), (1, 2), (0, 2)],
    "disconnected": [(0, 1)],
}
DIMENSIONS = [1, 2, 3, 4]
RADII = [1, 2, 4, 8, 16, 32, 64]
MESHES = [4, 8, 16, 32, 64]


def run():
    rng = Random(SEED)
    graph_data = {}
    for name, edges in GRAPHS.items():
        registers = models.endpoint_registers(3, edges)
        information = [[models.enumerate_information_bits(registers, a, b)
                        for b in range(3)] for a in range(3)]
        graph_data[name] = {
            "edges": edges,
            "mutual_information_bits": information,
            "distance_from_0": models.distances(3, edges, 0),
            "signal_rounds": models.signal_rounds(3, edges, 0, 3),
        }

    sampled_pairs = [[tuple(Fraction(rng.randrange(-65, 66), 67) for _ in range(2))
                      for _ in range(2)] for _ in range(64)]
    return {
        "config": {"seed": SEED, "dimensions": DIMENSIONS, "radii": RADII, "meshes": MESHES},
        "graphs": graph_data,
        "ball_volumes": {d: [models.lattice_ball(d, r) for r in RADII] for d in DIMENSIONS},
        "random_walk_return": {d: [str(models.product_lazy_return(d, r)) for r in RADII] for d in DIMENSIONS},
        "continuum_grid": [{"mesh": m, "max_sampled_error": str(max(
            models.rounded_metric_error(a, b, m) for a, b in sampled_pairs)),
            "proven_error_bound": str(Fraction(4, m))} for m in MESHES],
        "clock": models.clock_probabilities(8),
        "bell_remote_marginals": [[str(x) for x in row] for row in models.bell_remote_marginals()],
        "boost_witnesses": [{"beta": b, "transformed": [round(x, 12) for x in models.boost(2, 1, b)]}
                            for b in [-0.8, -0.4, 0, 0.4, 0.8]],
    }


def growth_svg(results):
    palette = ["#28608a", "#06816e", "#a25300", "#9c3b76"]
    width, height = 600, 340
    from math import log2
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">',
             '<title id="title">Grid ball-volume growth by dimension</title>',
             '<rect width="600" height="340" fill="#fff"/>',
             '<path d="M55 34V287H555" fill="none" stroke="#26364b" stroke-width="2"/>',
             '<text x="55" y="23" font-family="sans-serif" fill="#26364b">log₂ vertices in ball</text>',
             '<text x="395" y="320" font-family="sans-serif" fill="#26364b">log₂ graph radius</text>']
    for dimension, color in zip(DIMENSIONS, palette, strict=True):
        points = " ".join(f"{55 + 70 * log2(r):.2f},{287 - 8 * log2(n):.2f}"
                          for r, n in zip(RADII, results["ball_volumes"][dimension], strict=True))
        label = escape(f"d = {dimension}")
        lines.extend([f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>',
                      f'<text x="500" y="{45 + 20 * dimension}" font-family="sans-serif" fill="{color}">{label}</text>'])
    return "\n".join([*lines, "</svg>", ""])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("artifacts/science"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    results = run()
    (args.out / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    (args.out / "grid-growth.svg").write_text(growth_svg(results), encoding="utf-8")
    versions = {"python": platform.python_version(), "dependencies": []}
    (args.out / "versions.json").write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
