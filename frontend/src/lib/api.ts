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
  prediction: {
    model: string | null;
    personas: number | null;
    ran_at: string | null;
    ranking: string[];
    stats: Record<string, { stop_rate: number; click_rate: number }>;
    single_call: string[] | null;
  } | null;
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
  if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "The server rejected the request.");
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

// Escudo antiestafas (POST /api/check, GET /api/evidence).
export type Band = "scam" | "careful" | "genuine";

export interface CheckIn {
  text: string;
  note: string;
  images: string[];
  audio: string | null;
  mode: Mode;
}

export interface CheckOut {
  mode: Mode;
  model: string;
  usd: number;
  probability: number;
  band: Band;
  verdict: "scam" | "legit";
  reason: string;
  action: string;
  transcript: string;
  images: number;
}

export interface ShieldMetrics {
  balanced_accuracy: number;
  recall_scam: number;
  false_alarm_legit: number;
  auc: number;
}

export interface Round {
  sha256: string;
  bands: Record<Band, { scam: number; legit: number }>;
  scored: {
    n: number;
    scam: number;
    legit: number;
    shield: ShieldMetrics;
    keywords: ShieldMetrics;
    always_scam: ShieldMetrics;
    gap_vs_keywords_ci95: [number, number];
    rule: Record<string, boolean>;
  };
}

export type Evidence = Record<"round1" | "round2", Round>;

export const shield = {
  check: (req: CheckIn) => call<CheckOut>("check", req),
  evidence: () => call<Evidence>("evidence"),
};

// Pistas aparte del veredicto (POST /api/investigate) y qué está circulando (GET /api/campaigns).
export type Trend = "rising" | "falling" | "steady";

export interface Family {
  id: string;
  name: string;
  what: string;
  spot: string[];
  do: string;
  reports: number;
  share: number;
  monthly: Record<string, number>;
  trend: Trend;
  trend_change: number;
  channels: Record<string, number>;
  payments: Record<string, number>;
  top_brands: { brand: string; reports: number }[];
  meta_share: number;
  ai_share: number;
  examples: { hook: string; channel: string; url: string | null }[];
}

export interface Clue {
  label: string;
  detail: string;
  signal: "risky" | "reassuring" | "neutral";
}

export interface ToolStep {
  tool: "inspect_link" | "domain_registration" | string;
  input: Record<string, string>;
  result: Record<string, unknown>;
}

export interface InvestigateOut {
  mode: Mode;
  usd: number;
  family: (Pick<Family, "id" | "name" | "what" | "spot" | "do" | "reports" | "trend" | "top_brands"> & { fit: "strong" | "partial" }) | null;
  investigation: { clues: Clue[]; summary: string; steps: ToolStep[]; skipped?: boolean } | null;
}

export interface Campaigns {
  source: string;
  window: [string, string];
  reports: number;
  months: Record<string, number>;
  trend_months: string[];
  channels: Record<string, number>;
  meta_share: number;
  known_channel_meta_share: number;
  ai: Record<string, number>;
  ai_share: number;
  families: Family[];
}

export const radar = {
  investigate: (req: { text: string; images: string[]; mode: Mode }) => call<InvestigateOut>("investigate", req),
  campaigns: () => call<Campaigns>("campaigns"),
};
