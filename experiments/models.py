"""Executable models used by the paper and the reproducibility workflow."""

from collections import Counter, deque
from fractions import Fraction
from itertools import product
from math import comb, cos, pi, sin


def endpoint_registers(size, edges):
    """Give the two orientations of each edge independent fair bits."""
    tokens = {(a, b) for a, b in edges} | {(b, a) for a, b in edges}
    return [sorted(token for token in tokens if v in token) for v in range(size)]


def information_bits(registers, first, second):
    """Exact Shannon mutual information for repeated independent fair bits."""
    return len(set(registers[first]) & set(registers[second]))


def enumerate_information_bits(registers, first, second):
    """Independent check by enumerating the diagonal law and counting supports."""
    tokens = sorted(set().union(*registers))
    if len(tokens) > 16:
        raise ValueError("Enumeration is intended for small graphs")
    assignments = (dict(zip(tokens, bits, strict=True)) for bits in product((0, 1), repeat=len(tokens)))
    joint = Counter((tuple(a[t] for t in registers[first]), tuple(a[t] for t in registers[second]))
                    for a in assignments)
    assert len(set(joint.values())) == 1, "Expected a uniform diagonal marginal"
    support_a = len({a for a, _ in joint})
    support_b = len({b for _, b in joint})
    ratio = Fraction(support_a * support_b, len(joint))
    assert ratio.denominator == 1 and ratio.numerator.bit_count() == 1
    return ratio.numerator.bit_length() - 1


def distances(size, edges, source):
    """Unweighted shortest-walk distances. None denotes a different component."""
    neighbors = [[] for _ in range(size)]
    for first, second in edges:
        neighbors[first].append(second)
        neighbors[second].append(first)
    result = [None] * size
    result[source] = 0
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for other in neighbors[vertex]:
            if result[other] is None:
                result[other] = result[vertex] + 1
                queue.append(other)
    return result


def signal_rounds(size, edges, source, rounds):
    """An optional intervention protocol with one graph hop per update."""
    reached = {source}
    snapshots = [sorted(reached)]
    for _ in range(rounds):
        next_reached = reached.copy()
        for first, second in edges:
            if first in reached:
                next_reached.add(second)
            if second in reached:
                next_reached.add(first)
        reached = next_reached
        snapshots.append(sorted(reached))
    return snapshots


def lattice_ball(dimension, radius):
    """Integer L1 ball cardinality by nonzero coordinate count and sign."""
    return sum(2**k * comb(dimension, k) * comb(radius, k)
               for k in range(min(dimension, radius) + 1))


def product_lazy_return(dimension, steps):
    return Fraction(comb(2 * steps, steps), 4**steps) ** dimension


def clock_probabilities(ticks):
    """Clock labels with a real rotation by pi/ticks and periodic system rays."""
    return [[round(cos(pi * j / ticks)**2, 12), round(sin(pi * j / ticks)**2, 12)]
            for j in range(ticks)]


def boost(t, x, beta):
    gamma = (1 - beta**2)**-0.5
    return gamma * (t - beta * x), gamma * (x - beta * t)


def rounded_metric_error(first, second, mesh):
    """Distance error for floor samples in grid units, computed exactly."""
    world_distance = sum(abs(a - b) for a, b in zip(first, second, strict=True))
    grid_first = [(x * mesh).__floor__() for x in first]
    grid_second = [(x * mesh).__floor__() for x in second]
    grid_distance = Fraction(sum(abs(a - b) for a, b in zip(grid_first, grid_second, strict=True)), mesh)
    return abs(grid_distance - world_distance)


def bell_remote_marginals():
    """Reduced diagonals after the identity and bit flip on the first register."""
    identity = [(0, 0), (1, 1)]
    bit_flip = [(1 - a, b) for a, b in identity]
    return [[Fraction(sum(b == value for _, b in basis), 2) for value in (0, 1)]
            for basis in (identity, bit_flip)]
