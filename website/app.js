import { boost, causalType, interval, reaches, requires } from "./models.js";

const $ = id => document.getElementById(id);
const repo = "https://github.com/TastyHeadphones/Deriving-Minkowski-Spacetime-from-a-Spaceless-and-Timeless-Quantum-System";
const fixed = n => Number(n.toFixed(3));
const plain = (tag, value, parent) => {
  const element = document.createElement(tag);
  element.textContent = value;
  parent.append(element);
  return element;
};
const link = (label, url, parent) => {
  const element = plain("a", label, parent);
  element.href = url;
  return element;
};
const newContext = (canvas, color = "#f6f9f4") => {
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = color;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  return ctx;
};
const line = (ctx, x, y, a, b, color, width = 2) => {
  ctx.strokeStyle = color; ctx.lineWidth = width;
  ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(a, b); ctx.stroke();
};
const label = (ctx, text, x, y, color = "#174938", size = 20) => {
  ctx.fillStyle = color; ctx.font = size + "px system-ui"; ctx.fillText(text, x, y);
};
const dot = (ctx, x, y, r, color) => {
  ctx.fillStyle = color; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
};

function cone(canvas, event = null, beta = 0, dark = false) {
  const ctx = newContext(canvas, dark ? "#183a30" : "#f6f9f4");
  const w = canvas.width, h = canvas.height, cx = w / 2, cy = h / 2, limit = Math.min(cx, cy) - 30;
  const grid = dark ? "#315046" : "#dce8dd";
  for (let px = cx % 20; px < w; px += 20) line(ctx, px, 0, px, h, grid, 1);
  for (let py = cy % 20; py < h; py += 20) line(ctx, 0, py, w, py, grid, 1);
  const rays = dark ? "#d9f194" : "#21724b";
  const axes = dark ? "#a9c2b3" : "#516a5d";
  ctx.fillStyle = dark ? "#52713c88" : "#baddbb77";
  for (const sign of [-1, 1]) {
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx - limit, cy + sign * limit);
    ctx.lineTo(cx + limit, cy + sign * limit); ctx.closePath(); ctx.fill();
  }
  line(ctx, cx, 16, cx, h - 16, axes);
  line(ctx, 16, cy, w - 16, cy, axes);
  for (const sign of [-1, 1]) line(ctx, cx - limit, cy + sign * limit, cx + limit, cy - sign * limit, rays, 2);
  label(ctx, "ct", cx + 12, 28, axes);
  label(ctx, "x", w - 26, cy - 9, axes);
  if (beta) {
    line(ctx, cx - beta * limit, cy + limit, cx + beta * limit, cy - limit, "#976412", 3);
    line(ctx, cx - limit, cy + beta * limit, cx + limit, cy - beta * limit, "#976412", 3);
    label(ctx, "ct′", cx + beta * limit + 10, cy - limit - 8, "#754800");
  }
  if (event) {
    const [t, x] = event;
    dot(ctx, cx + x * limit / 3, cy - t * limit / 3, 7, "#ac4131");
  }
}

function selectOptions(element, items) {
  for (const item of items) {
    const option = plain("option", item.title, element);
    option.value = item.id;
  }
}

function setupExplorers(data) {
  const proofs = data.proofs;
  const axiomItems = data.axioms;
  const nodes = [...axiomItems, ...proofs, ...data.conjectures].map(item => ({
    ...item, requirements: [...(item.assumptions ?? []), ...(item.dependencies ?? [])]
  }));
  const map = new Map(nodes.map(node => [node.id, node]));
  const proofSelect = $("proof-select"), nodeSelect = $("node-select"), axiomSelect = $("axiom-select");
  selectOptions(proofSelect, proofs);
  selectOptions(nodeSelect, nodes.map(node => ({...node, title: node.id + " · " + node.title})));
  selectOptions(axiomSelect, axiomItems);
  proofSelect.value = nodeSelect.value = "MAIN-NEGATIVE";
  const names = ids => ids.map(id => map.get(id).title).join(", ") || "None";

  function showProof() {
    const entry = map.get(proofSelect.value);
    const region = $("proof-record");
    region.replaceChildren();
    plain("h3", entry.title, region);
    plain("p", entry.statement, region);
    plain("pre", entry.lean_statement, region);
    plain("p", entry.scientific_interpretation, region);
    plain("p", "Assumptions · " + names(entry.assumptions), region);
    plain("p", "Dependencies · " + names(entry.dependencies), region);
    const verified = entry.verification_status === "verified";
    plain("p", verified ? "Verified and audited · " + entry.latest_verification_commit.slice(0, 12)
      : "Awaiting an audit report for this source.", region);
    if (verified) plain("p", "Kernel axioms · " + (entry.kernel_axioms.join(", ") || "None"), region);
    link("View Lean source ↗", repo + "/blob/" + data.source_commit + "/" + entry.source, region);
  }

  function showDependencies() {
    const node = map.get(nodeSelect.value);
    const parents = node.requirements.map(id => map.get(id));
    const children = nodes.filter(item => item.requirements.includes(node.id));
    const canvas = $("dependency-graph"), ctx = newContext(canvas);
    const left = 35, center = 390, right = 745, box = 220;
    function draw(labelText, x, y, active = false) {
      ctx.fillStyle = active ? "#17553e" : "#dfece1";
      ctx.fillRect(x, y - 21, box, 42);
      label(ctx, labelText, x + 10, y + 6, active ? "white" : "#174938", 16);
    }
    const plotEdges = (items, x, incoming) => items.forEach((item, i) => {
      const y = 52 + i * (canvas.height - 92) / Math.max(1, items.length - 1);
      const start = incoming ? [x + box, y] : [center + box, 200];
      const end = incoming ? [center, 200] : [x, y];
      line(ctx, ...start, ...end, "#688a73");
      line(ctx, end[0] - 9, end[1] - 5, ...end, "#688a73");
      line(ctx, end[0] - 9, end[1] + 5, ...end, "#688a73");
      draw(item.id, x, y);
    });
    label(ctx, "Recorded dependencies", left, 22, "#174938", 17);
    label(ctx, "Direct dependents", right, 22, "#174938", 17);
    plotEdges(parents, left, true);
    plotEdges(children, right, false);
    draw(node.id, center, 200, true);
    $("node-description").textContent = node.title + " · " + (node.motivation ?? node.statement);
    $("dependency-summary").textContent = "Dependencies · " + names(node.requirements) +
      ". Direct dependents · " + (children.map(item => item.title).join(", ") || "None") + ".";
  }

  function showAxiom() {
    const item = map.get(axiomSelect.value);
    const region = $("axiom-record");
    region.replaceChildren();
    plain("h3", item.title, region);
    plain("p", item.kind + " · " + item.motivation, region);
    const dependent = proofs.filter(proof => requires(map, proof.id, item.id));
    plain("p", "Recorded dependent proofs · " + (dependent.map(proof => proof.title).join(", ") || "None"), region);
    link("View source ↗", repo + "/blob/" + data.source_commit + "/" + item.source, region);
  }

  for (const [element, handler] of [[proofSelect, showProof], [nodeSelect, showDependencies], [axiomSelect, showAxiom]]) {
    element.addEventListener("change", handler);
    handler();
  }
}

function plot(canvas, values, captions, {max, bars = false, yTitle = "", xTitle = ""}) {
  const ctx = newContext(canvas), lo = 82, hi = canvas.width - 65, bottom = canvas.height - 62, top = 62;
  line(ctx, lo, top, lo, bottom, "#536f5f");
  line(ctx, lo, bottom, hi, bottom, "#536f5f");
  label(ctx, yTitle, lo, 32);
  label(ctx, xTitle, hi - 86, bottom + 48, "#455d4e", 16);
  const coordinates = values.map((y, i) => [lo + 18 + i * (hi - lo - 36) / Math.max(values.length - 1, 1),
    bottom - y / max * (bottom - top)]);
  if (bars) {
    for (const [x, y] of coordinates) {
      ctx.fillStyle = "#2a7855"; ctx.fillRect(x - 10, y, 20, bottom - y);
    }
  } else {
    for (let i = 1; i < coordinates.length; i++) line(ctx, ...coordinates[i - 1], ...coordinates[i], "#26784f", 3);
    for (const [x, y] of coordinates) dot(ctx, x, y, 5, "#26784f");
  }
  coordinates.forEach(([x], i) => label(ctx, String(captions[i]), x - 7, bottom + 25, "#455d4e", 16));
}

function graph(canvas, model, views) {
  const ctx = newContext(canvas);
  const positions = [[155, 263], [380, 91], [605, 263]];
  for (const [a, b] of model.edges) line(ctx, ...positions[a], ...positions[b], "#598368", 4);
  if (views === "graph") {
    for (const [a, b] of model.edges) {
      const [x, y] = positions[a], [u, v] = positions[b];
      label(ctx, "2 bits", (x + u) / 2 - 22, (y + v) / 2 - 10);
    }
  }
  positions.forEach(([x, y], i) => {
    const active = typeof views !== "number" || reaches(model.distance_from_0[i], views);
    dot(ctx, x, y, 29, active ? "#17553e" : "#7c887f");
    label(ctx, String(i), x - 6, y + 8, "#fff");
    if (views === "metric") label(ctx, "d(0, " + i + ") = " + (model.distance_from_0[i] ?? "∞"), x - 55, y + 56);
  });
}

function orderPlot(canvas, round) {
  const ctx = newContext(canvas);
  const vertices = [0, 1, 2], rows = [0, 1, 2, 3];
  const x = v => 170 + 200 * v;
  const y = row => 305 - 75 * row;
  for (const tick of rows) {
    label(ctx, "round " + tick, 22, y(tick) + 6, "#455d4e", 17);
    if (tick > 0) for (const a of vertices) for (const b of vertices) {
      if (Math.abs(a - b) <= 1) line(ctx, x(a), y(tick - 1), x(b), y(tick), "#8a9f90", 2);
    }
  }
  for (const tick of rows) for (const v of vertices) {
    dot(ctx, x(v), y(tick), 17, tick <= round && reaches(v, tick) ? "#17553e" : "#a9b7ac");
    label(ctx, String(v), x(v) - 5, y(tick) + 6, "white", 16);
  }
}

function setupModels(science) {
  const mode = $("model-select"), slider = $("parameter"), canvas = $("model-canvas");
  const sweep = science.config;
  const graphNames = ["path", "triangle", "disconnected"];
  const notes = {
    clock: "Conditioning on labels in a stationary history requires a chosen clock and system map.",
    entanglement: "The local unitary changes the joint correlations. No outcome is sent to the remote register.",
    graph: "Endpoint registers contain repeated fair bits in a separable diagonal state. Their mutual information does not require entanglement.",
    metric: "Distance counts the fewest edges on a walk. Labels in different components have infinite distance.",
    signal: "The selected circuit permits one hop per round. The static correlation graph does not execute the protocol.",
    order: "Reachability between event pairs orders the selected layered protocol. The round index is supplied.",
    dimension: "Volume-growth dimension is the asymptotic log–log slope. The selected grid family fixes the target dimension.",
    boost: "This Lorentz comparison supplies the invariant slope and interval in advance.",
    cone: "The null lines are a feature of the chosen Lorentzian form.",
    continuum: "Floor sampling on an expanding grid gives a pair-distance error bounded by 4/m in two dimensions."
  };
  const config = {
    clock: [0, science.clock.length - 1, 1, 0, "Clock label"],
    entanglement: [0, 1, 1, 0, "Local intervention"],
    graph: [0, 2, 1, 0, "Prepared graph"],
    metric: [0, 2, 1, 0, "Prepared graph"],
    signal: [0, 3, 1, 0, "Update round"],
    order: [0, 3, 1, 0, "Latest highlighted round"],
    dimension: [1, 4, 1, 2, "Grid dimension"],
    boost: [-0.8, 0.8, 0.05, 0.35, "β = v/c"],
    cone: [0, 3, 0.25, 1, "Event x at ct = 1"],
    continuum: [0, sweep.meshes.length - 1, 1, 0, "Mesh refinement"]
  };

  function render() {
    const key = mode.value, n = Number(slider.value);
    let summary, display = String(n);
    if (key === "clock") {
      const data = science.clock[n];
      plot(canvas, data, ["|0⟩", "|1⟩"], {max: 1, bars: true, yTitle: "Conditional probability"});
      summary = "At clock label " + n + ", P(0) = " + fixed(data[0]) + " and P(1) = " + fixed(data[1]) + ".";
    } else if (key === "entanglement") {
      const ctx = newContext(canvas);
      display = n ? "Bit flip on A" : "Identity on A";
      label(ctx, n ? "|Ψ⁺⟩ = (|01⟩ + |10⟩)/√2" : "|Φ⁺⟩ = (|00⟩ + |11⟩)/√2", 55, 145, "#17553e", 31);
      label(ctx, "Remote B · ρ = I/2", 55, 225, "#426650", 25);
      summary = "Remote outcomes remain " + science.bell_remote_marginals[n].join(" and ") + ".";
    } else if (key === "graph" || key === "metric") {
      const shape = science.graphs[graphNames[n]];
      display = graphNames[n];
      graph(canvas, shape, key);
      summary = key === "metric" ? "Distances from 0 · " + shape.distance_from_0.map(d => d ?? "∞").join(", ") + "."
        : "Exactly " + shape.edges.length + " of the three pairs share tokens.";
    } else if (key === "signal" || key === "order") {
      const shape = science.graphs.path;
      if (key === "signal") graph(canvas, shape, n);
      else orderPlot(canvas, n);
      summary = "Starting at label 0, affected labels at round " + n + " · " + shape.signal_rounds[n].join(", ") + ".";
    } else if (key === "dimension") {
      const counts = science.ball_volumes[n], logs = counts.map(Math.log2);
      plot(canvas, logs, sweep.radii, {max: Math.max(...logs) + 1, yTitle:"log₂ ball volume", xTitle:"Radius"});
      const slope = logs.at(-1) - logs.at(-2);
      summary = "The last measured log–log slope is " + fixed(slope) + ", with limiting dimension " + n + ".";
    } else if (key === "boost" || key === "cone") {
      const event = key === "boost" ? [2, 1] : [1, n];
      cone(canvas, event, key === "boost" ? n : 0);
      if (key === "boost") {
        const [t, x] = boost(...event, n);
        summary = "The event becomes (ct′, x′) = (" + fixed(t) + ", " + fixed(x) + "). The interval is " +
          fixed(interval(t, x)) + ".";
      } else {
        summary = "This event is " + causalType(...event) + " relative to the origin.";
      }
    } else {
      const row = science.continuum_grid[n];
      display = "m = " + row.mesh;
      const frac = text => text.split("/").map(Number).reduce((a, b) => a / b);
      const values = science.continuum_grid.slice(0, n + 1).map(entry => frac(entry.max_sampled_error));
      plot(canvas, values, sweep.meshes.slice(0, n + 1), {max: 1, yTitle: "Max sampled distance error", xTitle: "Mesh"});
      summary = "Measured error " + row.max_sampled_error + " across the sampled pairs. Analytic bound " + row.proven_error_bound + ".";
    }
    $("parameter-value").value = display;
    $("model-summary").textContent = summary;
    $("model-note").textContent = notes[key];
  }

  function changeModel() {
    const [min, max, step, value, text] = config[mode.value];
    Object.assign(slider, {min, max, step, value});
    $("parameter-label").textContent = text;
    render();
  }
  mode.addEventListener("change", changeModel);
  slider.addEventListener("input", render);
  changeModel();
}

async function showLatestWorkflow(branch, region) {
  const slug = new URL(repo).pathname.slice(1);
  const endpoint = new URL("https://api.github.com/repos/" + slug +
    "/actions/workflows/deploy-pages.yml/runs");
  endpoint.search = new URLSearchParams({branch, per_page: 1});
  try {
    const response = await fetch(endpoint, {signal: AbortSignal.timeout(4000)});
    if (!response.ok) throw new Error("GitHub Actions returned " + response.status);
    const latest = (await response.json()).workflow_runs?.[0];
    if (!latest) {
      region.textContent = "No default-branch workflow run reported.";
      return;
    }
    region.textContent = "Latest run on " + branch + " · " + (latest.conclusion ?? latest.status).replaceAll("_", " ") + " · ";
    link("View run ↗", repo + "/actions/runs/" + latest.id, region);
  } catch {
    region.textContent = "Live workflow status is temporarily unavailable. ";
    link("View Actions history ↗", repo + "/actions", region);
  }
}

function setupRecords(data) {
  $("pdf-link").hidden = !data.pdf;
  const dashboard = $("dashboard");
  dashboard.replaceChildren();
  const stats = plain("div", "", dashboard);
  stats.className = "stats";
  const labels = [
    ["Lean theorems verified", data.verification ? data.proofs.length : "Unavailable"],
    ["Open conjectures", data.conjectures.length],
    ["Counterexamples", data.counterexamples.length],
    ["Physical axioms in Lean", data.verification?.physical_axioms_in_lean ?? "Unavailable"]
  ];
  for (const [text, total] of labels) {
    const stat = plain("p", "", stats); stat.className = "stat";
    plain("strong", total, stat); stat.append(text);
  }
  if (data.verification) {
    plain("p", "Lean build and axiom audit passed at " + data.source_commit.slice(0, 12) + ".", dashboard);
    link("Download verification registry", "proof-verification.json", dashboard);
  } else plain("p", "No clean, commit-matched Lean verification report was included in this build.", dashboard);
  if (data.reproducibility) {
    plain("p", "Scientific tests passed and the published results reproduced with identical SHA-256 checksums.", dashboard);
    link("Download reproducibility report", "reproducibility.json", dashboard);
  }
  const workflow = plain("p", "", dashboard);
  if (data.ci_url) link("CI run for this site snapshot ↗", data.ci_url, workflow);
  else link("GitHub Actions workflow history ↗", repo + "/actions", workflow);
  if (location.hostname.endsWith(".github.io")) {
    const latest = plain("p", "Checking latest default-branch workflow…", dashboard);
    void showLatestWorkflow(data.default_branch, latest);
  }
  const tableWrap = plain("div", "", $("counterexamples"));
  tableWrap.className = "table-scroll";
  plain("h3", "Counterexample database", tableWrap);
  const table = plain("table", "", tableWrap);
  const head = table.createTHead().insertRow();
  for (const item of ["Model", "Inference it rules out"]) plain("th", item, head).scope = "col";
  const body = table.createTBody();
  for (const example of data.counterexamples) {
    const row = body.insertRow();
    plain("td", example[0] + " · " + example[1], row);
    plain("td", example[2], row);
  }
  for (const milestone of data.milestones) {
    const row = plain("li", "", $("milestones"));
    plain("strong", milestone.title + " · " + milestone.date, row);
    plain("div", milestone.detail, row);
  }
  for (const conjecture of data.conjectures) {
    const card = plain("article", "", $("conjectures"));
    plain("h3", conjecture.title, card); plain("p", conjecture.statement, card);
  }
}

cone($("hero-cone"), null, 0, true);
try {
  const response = await fetch("./data.json");
  if (!response.ok) throw new Error("Research data returned " + response.status);
  const data = await response.json();
  setupExplorers(data);
  setupModels(data.science);
  setupRecords(data);
} catch (error) {
  $("dashboard").textContent = "Research data could not be loaded.";
  console.error(error);
}
