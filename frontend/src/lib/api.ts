// Contratos de ensayo/api.py.
export type Mode = "mock" | "real";

export interface Variant {
  title: string;
  body: string;
  image_url: string | null;
}

export interface Target {
  age_min: number;
  age_max: number;
  gender: "All" | "Women" | "Men";
  countries: string[];
}

export interface VariantStats {
  stop_rate: number;
  click_rate: number;
  click_reasons: string[];
  stop_rate_by_segment: Record<string, number>;
}

export interface Reaction {
  persona: string;
  segment: string;
  stopped: string[];
  clicked: string[];
  reason: string;
}

export interface SimulateOut {
  mode: Mode;
  model: string;
  personas: number;
  usd: number;
  population: { ranking: string[]; stats: Record<string, VariantStats>; sample_reactions: Reaction[]; calls: number };
  single_call: { ranking: string[] };
}

export interface Example {
  batch_id: string;
  brand: string;
  week: string | null;
  target: Target;
  variants: { ad_id: string; title: string; body: string; image_url: string | null }[];
  reach: Record<string, number | null>;
}

export interface Metric {
  mean: number;
  ci95: [number, number];
  n: number;
}

export interface Backtest {
  mock: boolean;
  batches: number;
  source: string | null;
  summary: Record<"population" | "single_call" | "random", { batches: number; pairwise: Metric; top1: Metric }>;
}

export interface Config {
  real_allowed: boolean;
  real_model: string;
}

async function call<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`api/${path}`, body === undefined ? undefined : {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "El servidor no aceptó el pedido.");
  return data as T;
}

export const api = {
  config: () => call<Config>("config"),
  examples: () => call<Example[]>("examples"),
  backtest: () => call<Backtest>("backtest"),
  simulate: (req: { brand: string; variants: Variant[]; target: Target; personas: number; mode: Mode }) => call<SimulateOut>("simulate", req),
  variants: (req: { brand: string; brief: string; photo_url: string | null; n: number; mode: Mode }) =>
    call<{ usd: number; variants: { angle: string; title: string; body: string; image_url: string }[] }>("variants", req),
  chat: (req: {
    brand: string;
    persona: string;
    variants: Variant[];
    stopped: string[];
    clicked: string[];
    reason: string;
    history: { role: "user" | "persona"; text: string }[];
    question: string;
    mode: Mode;
  }) => call<{ answer: string; usd: number }>("chat", req),
};
