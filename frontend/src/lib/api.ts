// Contratos de ensayo/api.py.
export type Mode = "mock" | "real";

export interface Config {
  real_allowed: boolean;
  real_model: string;
}

async function call<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`api/${path}`, body === undefined ? undefined : {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).catch(() => {
    throw new Error("We couldn't reach the server. Check your connection and try again.");
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(typeof data.detail === "string" ? data.detail : "The server rejected the request.");
  return data as T;
}

export const api = {
  config: () => call<Config>("config"),
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
  quote: string | null;
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

// What the response agent prepared. Everything here is simulated: nothing is sent, blocked or published.
export interface AgentAction {
  tool: "alert_contact" | "draft_report" | "block_sender" | "share_pattern";
  title: string;
  why: string;
  to: string;
  body: string;
  subject?: string;
  heads_up?: string;
  report_number?: number | null;
  family?: string | null;
  auto?: boolean;
}

export interface ActOut {
  mode: Mode;
  usd: number;
  actions: AgentAction[];
  simulated: true;
  skipped?: boolean;
}

export interface NetworkCampaign {
  id: string;
  name: string;
  family: string;
  what: string;
  spot: string[];
  do: string;
  flagged_on: string;
  flag_index: number;
  warned: number;
  reports: { date: string; hook: string; channel: string; url: string | null }[];
}

export interface Network {
  source: string;
  rule: { min_reports: number; window_days: number };
  reports: number;
  branded_reports: number;
  flagged: number;
  warned: number;
  median_days_ahead: number;
  campaigns: NetworkCampaign[];
}

export const radar = {
  investigate: (req: { text: string; images: string[]; mode: Mode }) => call<InvestigateOut>("investigate", req),
  act: (req: { text: string; images: string[]; verdict: Pick<CheckOut, "band" | "probability" | "reason" | "action">; family: unknown; clues: Clue[]; mode: Mode }) =>
    call<ActOut>("act", req),
  network: () => call<Network>("network"),
  campaigns: () => call<Campaigns>("campaigns"),
};
