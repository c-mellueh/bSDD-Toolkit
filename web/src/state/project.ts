/* eslint-disable @typescript-eslint/no-explicit-any */
import { create } from "zustand";
import { applyPatch } from "../jsonpatch";
import { buildIndexes, type Indexes } from "../model";
import type { Doc, PatchOp, ProjectMeta, User } from "../types";
import { clientId, useSettings } from "./settings";

export type Status = "idle" | "connecting" | "online" | "reconnecting" | "error";

interface History {
  undo: string | null;
  redo: string | null;
}

interface ProjectState {
  projectId: string | null;
  status: Status;
  error: string | null;
  doc: Doc | null;
  idx: Indexes;
  version: number;
  meta: ProjectMeta | null;
  users: User[];
  me: User | null;
  history: History;
  lastRemote: { author: string; label: string; at: number } | null;
  // UI selection
  activeClass: string | null;
  activePset: string | null;
  activeClassProperty: string | null;
  selectedClasses: string[];
  setActiveClass: (code: string | null) => void;
  setActivePset: (name: string | null) => void;
  setActiveClassProperty: (code: string | null) => void;
  setSelectedClasses: (codes: string[]) => void;
}

export const useProject = create<ProjectState>((set, get) => ({
  projectId: null,
  status: "idle",
  error: null,
  doc: null,
  idx: buildIndexes(null),
  version: 0,
  meta: null,
  users: [],
  me: null,
  history: { undo: null, redo: null },
  lastRemote: null,
  activeClass: null,
  activePset: null,
  activeClassProperty: null,
  selectedClasses: [],
  setActiveClass: (code) => {
    if (get().activeClass === code) return;
    set({ activeClass: code, activePset: null, activeClassProperty: null });
    connection?.presence({ class: code ?? undefined });
  },
  setActivePset: (name) => set({ activePset: name, activeClassProperty: null }),
  setActiveClassProperty: (code) => set({ activeClassProperty: code }),
  setSelectedClasses: (codes) => set({ selectedClasses: codes }),
}));

type Pending = { resolve: (v: any) => void; reject: (e: Error) => void };

class Connection {
  ws: WebSocket | null = null;
  pending = new Map<number, Pending>();
  rid = 0;
  closed = false;
  retry = 0;
  pingTimer: number | undefined;

  constructor(public projectId: string) {
    this.open();
  }

  url() {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const name = encodeURIComponent(useSettings.getState().userName);
    return `${proto}://${location.host}/api/projects/${this.projectId}/ws?client=${clientId()}&name=${name}`;
  }

  open() {
    const state = useProject.getState();
    useProject.setState({ status: state.doc ? "reconnecting" : "connecting" });
    const ws = new WebSocket(this.url());
    this.ws = ws;
    ws.onmessage = (ev) => this.onMessage(JSON.parse(ev.data));
    ws.onclose = () => {
      window.clearInterval(this.pingTimer);
      for (const p of this.pending.values()) p.reject(new Error("Connection lost"));
      this.pending.clear();
      if (this.closed) return;
      if (useProject.getState().status === "error") return;
      useProject.setState({ status: "reconnecting" });
      const delay = Math.min(10000, 500 * 2 ** this.retry++);
      window.setTimeout(() => !this.closed && this.open(), delay);
    };
    ws.onopen = () => {
      this.retry = 0;
      this.pingTimer = window.setInterval(() => this.send({ type: "ping" }), 25000);
    };
  }

  close() {
    this.closed = true;
    this.ws?.close();
  }

  send(msg: any) {
    if (this.ws?.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(msg));
  }

  request(msg: any): Promise<any> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState !== WebSocket.OPEN) {
        reject(new Error("Not connected"));
        return;
      }
      const rid = ++this.rid;
      this.pending.set(rid, { resolve, reject });
      this.send({ ...msg, rid });
    });
  }

  presence(selection: Record<string, any>) {
    this.send({ type: "presence", selection });
  }

  onMessage(msg: any) {
    const state = useProject.getState();
    switch (msg.type) {
      case "hello":
        useProject.setState({
          status: "online",
          error: null,
          doc: msg.doc,
          idx: buildIndexes(msg.doc),
          version: msg.version,
          meta: msg.meta,
          me: msg.you,
          users: msg.users,
          history: msg.history,
        });
        break;
      case "doc":
        useProject.setState({ doc: msg.doc, idx: buildIndexes(msg.doc), version: msg.version });
        break;
      case "patch": {
        if (!state.doc || msg.version !== state.version + 1) {
          this.send({ type: "sync" });
          return;
        }
        try {
          const doc = applyPatch(state.doc, msg.patch as PatchOp[]);
          const update: Partial<ProjectState> = { doc, idx: buildIndexes(doc), version: msg.version };
          if (msg.author !== clientId()) update.lastRemote = { author: msg.author, label: msg.label, at: Date.now() };
          useProject.setState(update);
        } catch {
          this.send({ type: "sync" });
        }
        break;
      }
      case "users":
        useProject.setState({ users: msg.users });
        break;
      case "ack": {
        if (msg.history) useProject.setState({ history: msg.history });
        const p = this.pending.get(msg.rid);
        if (!p) return;
        this.pending.delete(msg.rid);
        if (msg.ok) p.resolve(msg.result);
        else p.reject(new Error(msg.error || "Operation failed"));
        break;
      }
      case "error":
        useProject.setState({ status: msg.fatal ? "error" : state.status, error: msg.error });
        if (msg.fatal) this.close();
        break;
    }
  }
}

let connection: Connection | null = null;

export function connect(projectId: string) {
  if (connection?.projectId === projectId) return;
  connection?.close();
  useProject.setState({
    projectId,
    doc: null,
    idx: buildIndexes(null),
    version: 0,
    status: "connecting",
    error: null,
    activeClass: null,
    activePset: null,
    activeClassProperty: null,
    selectedClasses: [],
    users: [],
    history: { undo: null, redo: null },
  });
  connection = new Connection(projectId);
}

export function disconnect() {
  connection?.close();
  connection = null;
  useProject.setState({ projectId: null, status: "idle", doc: null, idx: buildIndexes(null) });
}

export function op<T = any>(name: string, args: Record<string, any> = {}): Promise<T> {
  if (!connection) return Promise.reject(new Error("Not connected"));
  return connection.request({ type: "op", op: name, args });
}

export function undo() {
  return connection?.request({ type: "undo" }) ?? Promise.reject(new Error("Not connected"));
}

export function redo() {
  return connection?.request({ type: "redo" }) ?? Promise.reject(new Error("Not connected"));
}

export function renameMe(name: string) {
  connection?.send({ type: "presence", name });
}
