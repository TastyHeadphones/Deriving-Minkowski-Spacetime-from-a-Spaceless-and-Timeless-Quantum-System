import { strict as assert } from "node:assert";
import test from "node:test";
import { boost, causalType, interval, reaches, requires } from "../website/models.js";

test("boost preserves the selected interval", () => {
  for (const beta of [-0.9, -0.2, 0, 0.3, 0.9]) {
    assert.ok(Math.abs(interval(...boost(2, 1, beta)) - 3) < 1e-12);
  }
  assert.throws(() => boost(1, 0, 1), RangeError);
});

test("cone classification", () => {
  assert.equal(causalType(1, 0), "timelike");
  assert.equal(causalType(1, 1), "null");
  assert.equal(causalType(1, 2), "spacelike");
});

test("causal reach allows waiting and handles disconnected labels", () => {
  assert.equal(reaches(2, 2), true);
  assert.equal(reaches(2, 1), false);
  assert.equal(reaches(null, 99), false);
});

test("dependency filtering is transitive and terminates", () => {
  const graph = new Map([["R", {requirements: ["L"]}], ["L", {requirements: ["A", "R"]}]]);
  assert.equal(requires(graph, "R", "A"), true);
  assert.equal(requires(graph, "R", "U"), false);
});
