import { ExternalLink, TrendingDown, TrendingUp } from "lucide-react";
import { Card, CardTitle } from "@/components/ui/card";
import { Button, PageTitle } from "@/components/shell";
import type { Campaigns as CampaignsData, Family } from "@/lib/api";
import { cn, num, pct } from "@/lib/utils";

const CHANNEL: Record<string, string> = {
  sms: "Text message",
  whatsapp: "WhatsApp",
  instagram: "Instagram",
  facebook: "Facebook",
  messenger: "Messenger",
  marketplace: "Marketplace",
  email: "Email",
  phone_call: "Phone call",
  website: "Website or ad",
  dating_app: "Dating app",
  telegram: "Telegram",
  other_app: "Other app",
  in_person: "In person",
  unknown: "Not said",
};
const AI: Record<string, string> = {
  deepfake_video: "deepfake videos",
  voice_clone: "cloned voices",
  ai_image: "AI images",
  ai_chatbot: "AI chatbots",
  ai_other: "other AI",
};
const MONTH = (m: string) => new Date(`${m}-01T12:00:00Z`).toLocaleString("en-GB", { month: "short", timeZone: "UTC" });
const DAY = (d: string) => new Date(`${d}T12:00:00Z`).toLocaleString("en-GB", { day: "numeric", month: "short", timeZone: "UTC" });

function Trend({ family }: { family: Family }) {
  if (family.trend === "steady") return <span className="rounded-full bg-bg px-2.5 py-1 text-xs font-semibold text-muted">Steady</span>;
  const up = family.trend === "rising";
  const Icon = up ? TrendingUp : TrendingDown;
  return (
    <span className={cn("flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold", up ? "bg-[#fdecec] text-[#9b1c1c]" : "bg-ok-soft text-ok")}>
      <Icon className="size-3.5" aria-hidden="true" /> {up ? "Rising" : "Falling"} {Math.abs(Math.round(family.trend_change * 100))}%
    </span>
  );
}

function FamilyCard({ family, max }: { family: Family; max: number }) {
  const channels = Object.entries(family.channels).filter(([c]) => c !== "unknown").slice(0, 3);
  return (
    <Card className="flex flex-col gap-3 p-5 sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <CardTitle className="text-lg">{family.name}</CardTitle>
        <Trend family={family} />
      </div>
      <div className="flex items-center gap-3 text-sm">
        <div className="h-2 flex-1 rounded-full bg-bg" role="presentation">
          <div className="h-2 rounded-full bg-ink" style={{ width: `${Math.max(3, (family.reports / max) * 100)}%` }} />
        </div>
        <span className="shrink-0 font-semibold text-heading">{num(family.reports)} reports</span>
      </div>
      <p className="m-0 text-[15px] leading-normal">{family.what}</p>
      {family.spot.length > 0 && (
        <ul className="m-0 flex flex-col gap-1 pl-5 text-sm">
          {family.spot.map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ul>
      )}
      {family.top_brands.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="font-semibold text-muted">Posing as</span>
          {family.top_brands.map((b) => (
            <span key={b.brand} className="rounded-full bg-bg px-2.5 py-1 font-semibold text-heading">
              {b.brand} · {b.reports}
            </span>
          ))}
        </div>
      )}
      {channels.length > 0 && (
        <p className="m-0 text-xs text-muted">Arrived by {channels.map(([c, n]) => `${CHANNEL[c] ?? c} (${n})`).join(", ")}</p>
      )}
      {family.examples.length > 0 && (
        <details className="rounded-xl bg-bg px-4 py-3 text-sm">
          <summary className="cursor-pointer font-semibold">How it looked to people</summary>
          <ul className="m-0 mt-2 flex list-none flex-col gap-2 p-0">
            {family.examples.map((e, i) => (
              <li key={i} className="flex items-start justify-between gap-3 leading-normal">
                <span>
                  "{e.hook}" <span className="text-muted">· {CHANNEL[e.channel] ?? e.channel}</span>
                </span>
                {e.url && (
                  <a href={e.url} target="_blank" rel="noreferrer" aria-label="Open the Reddit thread" className="shrink-0 text-muted hover:text-heading">
                    <ExternalLink className="size-4" />
                  </a>
                )}
              </li>
            ))}
          </ul>
        </details>
      )}
      <p className="m-0 mt-auto text-sm font-semibold text-heading">{family.do}</p>
    </Card>
  );
}

export default function Campaigns({ data, onCheck }: { data: CampaignsData | null; onCheck: () => void }) {
  if (!data) return <div className="skeleton h-64" aria-label="Loading" />;
  const families = data.families.filter((f) => f.id !== "other");
  const other = data.families.find((f) => f.id === "other");
  const max = Math.max(...families.map((f) => f.reports));
  const rising = families.filter((f) => f.trend === "rising");
  const known = Object.entries(data.channels).filter(([c]) => c !== "unknown");
  const knownTotal = known.reduce((a, [, n]) => a + n, 0);
  const aiTotal = Object.values(data.ai).reduce((a, n) => a + n, 0);
  const tm = data.trend_months;
  return (
    <>
      <PageTitle
        title="What's going around"
        lead={`${num(data.reports)} scams people asked about on Reddit between ${DAY(data.window[0])} and ${DAY(data.window[1])}, that the community confirmed, grouped by how they work. Learn the pattern once and you'll spot the next one.`}
      />

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="flex flex-col gap-1 p-5">
          <span className="text-3xl font-bold text-heading">{num(data.reports)}</span>
          <span className="text-sm text-muted">confirmed scam reports, in {families.length} families</span>
        </Card>
        <Card className="flex flex-col gap-1 p-5">
          <span className="text-3xl font-bold text-heading">{pct(data.known_channel_meta_share)}</span>
          <span className="text-sm text-muted">reached people on WhatsApp, Instagram, Facebook, Messenger or Marketplace (when the post says where)</span>
        </Card>
        <Card className="flex flex-col gap-1 p-5">
          <span className="text-3xl font-bold text-heading">{num(aiTotal)}</span>
          <span className="text-sm text-muted">
            reports say AI was used
            {aiTotal > 0 && <>: {Object.entries(data.ai).map(([k, n]) => `${AI[k] ?? k} (${n})`).join(", ")}</>}
          </span>
        </Card>
      </div>

      {rising.length > 0 && tm?.length === 2 && (
        <p className="m-0 text-[15px] leading-normal">
          <strong>Rising in {MONTH(tm[1])}</strong> compared with {MONTH(tm[0])}, as a share of all reports: {rising.map((f) => f.name).join(", ")}.
        </p>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {families.map((f) => (
          <FamilyCard key={f.id} family={f} max={max} />
        ))}
      </div>

      <Card className="flex flex-col gap-4 p-5 sm:p-7">
        <CardTitle>Where they reached people</CardTitle>
        <ul className="m-0 flex list-none flex-col gap-2 p-0 text-sm">
          {known.map(([c, n]) => (
            <li key={c} className="grid grid-cols-[120px_1fr_48px] items-center gap-3">
              <span className="font-semibold text-heading">{CHANNEL[c] ?? c}</span>
              <div className="h-2 rounded-full bg-bg" role="presentation">
                <div className="h-2 rounded-full bg-ink" style={{ width: `${Math.max(2, (n / known[0][1]) * 100)}%` }} />
              </div>
              <span className="text-right text-muted">{pct(n / knownTotal)}</span>
            </li>
          ))}
        </ul>
        <p className="m-0 text-sm text-muted">{num(data.channels.unknown ?? 0)} posts didn't say where the scam arrived and are left out of these shares.</p>
      </Card>

      <Card className="flex flex-col gap-3 p-5 sm:p-7">
        <CardTitle>How this was made</CardTitle>
        <ul className="m-0 flex flex-col gap-2 pl-5 text-[15px] leading-normal">
          <li>The cases are the public Reddit posts from our test (r/Scams, r/isthisascam and others) plus newer ones, all posted after Muse Spark 1.3 came out. Only posts the community judged to be scams are counted.</li>
          <li>Muse Spark 1.3 described each case (channel, brand used as bait, what the scammer wanted, whether AI was involved), grouped the descriptions into families, and placed every case in one.</li>
          <li>These are reports, not victims. Reddit leans towards English-speaking countries, and people mostly post when something already feels wrong.</li>
          <li>
            Examples are rewritten by the model without names, numbers or links.{other ? ` ${num(other.reports)} cases didn't fit any family.` : ""}
          </li>
          <li>Nothing you check in Second Look is added here.</li>
        </ul>
        <div className="pt-1">
          <Button onClick={onCheck}>Check a message</Button>
        </div>
      </Card>
    </>
  );
}
