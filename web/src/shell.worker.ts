/// <reference lib="webworker" />
/* eslint-disable @typescript-eslint/no-explicit-any */
// Python shell running entirely in the browser (Pyodide / WebAssembly).
// Nothing typed here is executed on the server.

const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.27.5/full/";
let pyodide: any = null;
let ns: any = null;

const post = (msg: any) => (self as unknown as Worker).postMessage(msg);

const SETUP = `
import sys, types, json
# the 'bsdd' HTTP client is not available in the browser: provide a stub
_stub = types.ModuleType("bsdd")
class _Client:
    def __init__(self, *a, **k):
        raise RuntimeError("Remote bSDD requests are not available in the browser shell")
_stub.Client = _Client
sys.modules["bsdd"] = _stub
sys.path.insert(0, "/home/pyodide/pkgs")
from bsdd_json import BsddDictionary, BsddClass, BsddProperty, BsddClassProperty, BsddAllowedValue, BsddClassRelation, BsddPropertyRelation
from bsdd_json.utils import class_utils as cl_utils, property_utils as prop_utils, dictionary_utils as dict_utils
from bsdd_json.utils.cache import configure as _configure
_configure(offline=True)
`;

async function init(dictionaryJson: string, zipUrl: string) {
  post({ type: "status", text: "Loading Python (Pyodide)…" });
  const mod: any = await import(/* @vite-ignore */ `${PYODIDE_URL}pyodide.mjs`);
  pyodide = await mod.loadPyodide({ indexURL: PYODIDE_URL });
  pyodide.setStdout({ batched: (s: string) => post({ type: "out", text: s }) });
  pyodide.setStderr({ batched: (s: string) => post({ type: "err", text: s }) });
  post({ type: "status", text: "Loading pydantic…" });
  await pyodide.loadPackage(["pydantic"]);
  const buf = await (await fetch(zipUrl)).arrayBuffer();
  pyodide.unpackArchive(buf, "zip", { extractDir: "/home/pyodide/pkgs" });
  ns = pyodide.globals.get("dict")();
  await pyodide.runPythonAsync(SETUP, { globals: ns });
  load(dictionaryJson);
  post({ type: "ready" });
}

function load(dictionaryJson: string) {
  ns.set("_raw", dictionaryJson);
  pyodide.runPython("d = BsddDictionary.model_validate(json.loads(_raw)); del _raw", { globals: ns });
}

async function run(code: string) {
  try {
    const result = await pyodide.runPythonAsync(code, { globals: ns });
    if (result !== undefined && result !== null) {
      let text: string;
      if (result && typeof result === "object" && "toString" in result && result.type !== undefined) {
        ns.set("_r", result);
        text = pyodide.runPython("repr(_r)", { globals: ns });
        result.destroy?.();
      } else text = String(result);
      post({ type: "result", text });
    }
  } catch (e: any) {
    post({ type: "err", text: String(e.message ?? e) });
  }
  post({ type: "done" });
}

self.onmessage = async (ev: MessageEvent) => {
  const msg = ev.data;
  try {
    if (msg.type === "init") await init(msg.dictionary, msg.zipUrl);
    else if (msg.type === "run") await run(msg.code);
    else if (msg.type === "load") {
      load(msg.dictionary);
      post({ type: "out", text: "Dictionary reloaded from the server.\n" });
      post({ type: "done" });
    } else if (msg.type === "export") {
      const json = pyodide.runPython("json.dumps(d.model_dump(mode='json', exclude_none=True))", { globals: ns });
      post({ type: "exported", json });
    }
  } catch (e: any) {
    post({ type: "err", text: String(e.message ?? e) });
    post({ type: "done" });
  }
};
export {};
