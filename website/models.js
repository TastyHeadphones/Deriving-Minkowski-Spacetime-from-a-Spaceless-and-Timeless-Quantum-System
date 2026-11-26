export function boost(t, x, beta) {
  if (Math.abs(beta) >= 1) throw new RangeError("The selected boost requires |β| < 1.");
  const gamma = 1 / Math.sqrt(1 - beta * beta);
  return [gamma * (t - beta * x), gamma * (x - beta * t)];
}

export function reaches(distance, elapsed) {
  return distance !== null && Number.isFinite(distance) && distance <= elapsed;
}

export function requires(items, start, goal) {
  const pending = [...(items.get(start)?.requirements ?? [])];
  const seen = new Set();
  while (pending.length) {
    const id = pending.pop();
    if (id === goal) return true;
    if (!seen.has(id)) {
      seen.add(id);
      pending.push(...(items.get(id)?.requirements ?? []));
    }
  }
  return false;
}

export function interval(t, x) {
  return t * t - x * x;
}

export function causalType(t, x) {
  const q = interval(t, x);
  if (Math.abs(q) < 1e-10) return "null";
  return q > 0 ? "timelike" : "spacelike";
}
