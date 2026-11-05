/// <reference lib="webworker" />
/* eslint-disable @typescript-eslint/no-explicit-any */
// Runs the Rust/WebAssembly force simulation off the main thread and streams positions back.

interface Exports {
  memory: WebAssembly.Memory;
  init(n: number, m: number): void;
  set_params(rep: number, len: number, k: number, gravity: number, damping: number, theta: number, maxSpeed: number, collision: number): void;
  step(dt: number, alpha: number): number;
  pos_ptr(): number;
  fixed_ptr(): number;
  mass_ptr(): number;
  radius_ptr(): number;
  edges_ptr(): number;
  rest_ptr(): number;
  strength_ptr(): number;
}

let ex: Exports | null = null;
let n = 0;
let running = false;
let alpha = 1;
let alphaTarget = 0;
let alphaDecay = 0.0228; // ~300 steps from 1 to 0.001 like d3-force
const ALPHA_MIN = 0.002;
const stepsPerFrame = 4;
let timer: number | undefined;
let params = { repulsion: 1200, springLength: 90, springK: 0.04, gravity: 0.02, damping: 0.6, theta: 0.8, maxSpeed: 60, collision: 1 };

const post = (msg: any, transfer?: Transferable[]) => (self as unknown as Worker).postMessage(msg, transfer ?? []);

function view<T extends Float32Array | Uint32Array | Uint8Array>(Ctor: new (b: ArrayBuffer, o: number, l: number) => T, ptr: number, len: number): T {
  return new Ctor(ex!.memory.buffer as ArrayBuffer, ptr, len);
}

function applyParams() {
  if (!ex) return;
  ex.set_params(params.repulsion, params.springLength, params.springK, params.gravity, params.damping, params.theta, params.maxSpeed, params.collision);
}

function sendPositions() {
  if (!ex) return;
  const copy = view(Float32Array, ex.pos_ptr(), n * 2).slice();
  post({ type: "positions", positions: copy, alpha, running }, [copy.buffer]);
}

function loop() {
  timer = undefined;
  if (!running || !ex) return;
  const start = performance.now();
  // as many steps as fit into ~12 ms (but at least one)
  // a few steps per frame: fast, but the layout still visibly settles
  let count = 0;
  do {
    ex.step(1, alpha);
    alpha += (alphaTarget - alpha) * alphaDecay;
    count++;
  } while (count < stepsPerFrame && performance.now() - start < 12 && alpha > ALPHA_MIN);
  if (alpha <= ALPHA_MIN && alphaTarget <= ALPHA_MIN) running = false;
  sendPositions();
  if (running) timer = self.setTimeout(loop, 4) as unknown as number;
}

function startLoop() {
  running = true;
  if (timer === undefined) timer = self.setTimeout(loop, 0) as unknown as number;
}

self.onmessage = async (ev: MessageEvent) => {
  const msg = ev.data;
  switch (msg.type) {
    case "init": {
      const bytes = await (await fetch(msg.wasmUrl)).arrayBuffer();
      const { instance } = await WebAssembly.instantiate(bytes, {});
      ex = instance.exports as unknown as Exports;
      applyParams();
      post({ type: "ready" });
      break;
    }
    case "graph": {
      if (!ex) return;
      n = msg.n;
      const m = msg.m;
      ex.init(n, m);
      applyParams();
      view(Float32Array, ex.pos_ptr(), n * 2).set(msg.positions);
      view(Uint8Array, ex.fixed_ptr(), n).set(msg.fixed);
      view(Float32Array, ex.mass_ptr(), n).set(msg.mass);
      view(Float32Array, ex.radius_ptr(), n).set(msg.radius);
      view(Uint32Array, ex.edges_ptr(), m * 2).set(msg.edges);
      view(Float32Array, ex.rest_ptr(), m).set(msg.rest);
      view(Float32Array, ex.strength_ptr(), m).set(msg.strength);
      if (msg.alpha !== undefined) {
        alpha = Math.max(alpha, msg.alpha);
        startLoop();
      } else sendPositions();
      break;
    }
    case "params":
      params = { ...params, ...msg.params };
      if (msg.alphaDecay) alphaDecay = msg.alphaDecay;
      applyParams();
      if (msg.reheat) {
        alpha = Math.max(alpha, 0.3);
        startLoop();
      }
      break;
    case "start":
      alpha = Math.max(alpha, msg.alpha ?? 1);
      startLoop();
      break;
    case "stop":
      running = false;
      sendPositions();
      break;
    case "drag": {
      // move nodes (pinned while dragging) and keep the simulation warm
      if (!ex) return;
      const pos = view(Float32Array, ex.pos_ptr(), n * 2);
      const fixed = view(Uint8Array, ex.fixed_ptr(), n);
      for (const [i, x, y] of msg.items as [number, number, number][]) {
        if (i >= n) continue;
        pos[2 * i] = x;
        pos[2 * i + 1] = y;
        fixed[i] = 1;
      }
      if (msg.simulate) {
        alphaTarget = 0.3;
        alpha = Math.max(alpha, 0.3);
        startLoop();
      } else sendPositions();
      break;
    }
    case "dragEnd":
      alphaTarget = 0;
      break;
    case "fixed": {
      if (!ex) return;
      const fixed = view(Uint8Array, ex.fixed_ptr(), n);
      for (const i of msg.indices as number[]) if (i < n) fixed[i] = msg.value ? 1 : 0;
      break;
    }
    case "positions": {
      if (!ex) return;
      view(Float32Array, ex.pos_ptr(), n * 2).set(msg.positions);
      running = false;
      sendPositions();
      break;
    }
  }
};
export {};
