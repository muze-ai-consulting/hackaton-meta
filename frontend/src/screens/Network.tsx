import { useEffect, useMemo, useState } from "react";
import { BellRing, ExternalLink, Pause, Play, RotateCcw } from "lucide-react";
import { Card, CardTitle } from "@/components/ui/card";
import { Button, PageTitle } from "@/components/shell";
import { radar, type Network as NetworkData, type NetworkCampaign } from "@/lib/api";
import { cn, num } from "@/lib/utils";

const TICK_MS = 1100;
const DAY = (d: string) => new Date(`${d}T12:00:00Z`).toLocaleString("en-GB", { day: "numeric", month: "short", timeZone: "UTC" });

function headsUp(c: NetworkCampaign): string {
  return `Heads up: fake ${c.name.replace(/^Fake | messages$/g, "")} messages are going around. ${c.what}${c.spot[0] ? ` How to spot it: ${c.spot[0]}.` : ""}`;
}

function Replay({ campaign }: { campaign: NetworkCampaign }) {
  const total = campaign.reports.length;
  const [shown, setShown] = useState(1);
  const [playing, setPlaying] = useState(true);

  useEffect(() => {
    setShown(1);
    setPlaying(!window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, [campaign]);

  useEffect(() => {
    if (!playing) return;
    if (shown >= total) {
      setPlaying(false);
      return;
    }
    const t = setTimeout(() => setShown((s) => s + 1), TICK_MS);
    return () => clearTimeout(t);
  }, [playing, shown, total]);

  const flagged = shown > campaign.flag_index;
  const warned = Math.max(0, shown - campaign.flag_index - 1);
  const rows = campaign.reports.slice(0, shown);

  return (
    <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
      <Card className="flex flex-col gap-4 p-5 sm:p-7">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle className="text-lg">{campaign.name}</CardTitle>
            <span className="text-sm text-muted">{campaign.family}</span>
          </div>
          <div className="flex gap-2">
            {shown < total && (
              <Button size="sm" variant="outline" onClick={() => setPlaying((p) => !p)}>
                {playing ? <Pause /> : <Play />} {playing ? "Pause" : "Play"}
              </Button>
            )}
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                setShown(1);
                setPlaying(true);
              }}
            >
              <RotateCcw /> Replay
            </Button>
          </div>
        </div>
        <div className="flex gap-1" role="img" aria-label={`Report ${shown} of ${total}`}>
          {campaign.reports.map((_, i) => (
            <div
              key={i}
              className={cn(
                "h-2 flex-1 rounded-full transition-colors duration-300",
                i >= shown ? "bg-bg" : i < campaign.flag_index ? "bg-[#e0a030]" : i === campaign.flag_index ? "bg-[#d64545]" : "bg-ok",
              )}
            />
          ))}
        </div>
        <ol className="m-0 flex list-none flex-col gap-2 p-0">
          {rows.map((r, i) => {
            const isFlag = i === campaign.flag_index;
            const later = i > campaign.flag_index;
            return (
              <li key={i} className="flex flex-col gap-2">
                <div className={cn("flex items-start gap-3 rounded-xl px-3 py-2.5 text-sm", later ? "bg-ok-soft" : "bg-bg")}>
                  <span className="w-14 shrink-0 font-semibold text-heading">{DAY(r.date)}</span>
                  <span className="min-w-0 flex-1 leading-normal">
                    "{r.hook}"
                    {later && <span className="mt-0.5 block text-xs font-semibold text-ok">Would have been warned first</span>}
                  </span>
                  {r.url && (
                    <a href={r.url} target="_blank" rel="noreferrer" aria-label="Open the Reddit thread" className="shrink-0 text-muted hover:text-heading">
                      <ExternalLink className="size-4" />
                    </a>
                  )}
                </div>
                {isFlag && (
                  <div className="flex items-center gap-2 rounded-xl bg-[#fdecec] px-3 py-2.5 text-sm font-semibold text-[#9b1c1c]">
                    <BellRing className="size-4 shrink-0" aria-hidden="true" /> Campaign flagged on {DAY(r.date)}: {campaign.flag_index + 1} reports in under two weeks
                  </div>
                )}
              </li>
            );
          })}
        </ol>
      </Card>

      <div className="flex flex-col gap-4 lg:sticky lg:top-6">
        <Card className="flex flex-col gap-1 p-5">
          <span className="text-3xl font-bold text-heading">
            {warned} of {campaign.warned}
          </span>
          <span className="text-sm text-muted">later reports in this replay came after the flag</span>
        </Card>
        <Card className={cn("flex flex-col gap-3 p-5 transition-opacity duration-500", flagged ? "opacity-100" : "opacity-40")}>
          <span className="text-xs font-semibold text-muted">The alert people would get (simulated, never sent)</span>
          <div className="rounded-2xl rounded-bl-md bg-[#e7ece6] p-3 text-sm leading-snug text-[#16181d]">
            <div className="mb-1 font-bold">⚠️ Second Look</div>
            {flagged ? headsUp(campaign) : "Waiting for enough reports…"}
          </div>
        </Card>
      </div>
    </div>
  );
}

export default function Network({ onCheck }: { onCheck: () => void }) {
  const [data, setData] = useState<NetworkData | null>(null);
  const [pick, setPick] = useState(0);
  useEffect(() => {
    radar.network().then(setData).catch(() => undefined);
  }, []);
  const campaign = useMemo(() => data?.campaigns[pick] ?? null, [data, pick]);
  if (!data || !campaign) return <div className="skeleton h-64" aria-label="Loading" />;
  return (
    <>
      <PageTitle
        title="Early warning"
        lead="What if each forward protected the next person? We replayed real scam reports day by day, as if they had reached Second Look. When reports about the same brand pile up, the network flags a campaign and warns people before it reaches them."
      />
      <p className="m-0 rounded-xl bg-[#fbf1dc] px-4 py-3 text-sm font-semibold leading-normal text-[#7a4b00]">
        Simulation. The reports are real public Reddit posts, but the network doesn't exist yet and nobody received an alert.
      </p>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="flex flex-col gap-1 p-5">
          <span className="text-3xl font-bold text-heading">{num(data.flagged)}</span>
          <span className="text-sm text-muted">campaigns flagged from {num(data.branded_reports)} reports that name a brand</span>
        </Card>
        <Card className="flex flex-col gap-1 p-5">
          <span className="text-3xl font-bold text-heading">{num(data.warned)}</span>
          <span className="text-sm text-muted">later reports came after the flag, so they could have been warned</span>
        </Card>
        <Card className="flex flex-col gap-1 p-5">
          <span className="text-3xl font-bold text-heading">{Math.round(data.median_days_ahead)} days</span>
          <span className="text-sm text-muted">median head start between the flag and those later reports</span>
        </Card>
      </div>

      <div className="flex flex-wrap gap-2" role="group" aria-label="Choose a campaign">
        {data.campaigns.map((c, i) => (
          <button
            key={c.id}
            type="button"
            aria-pressed={i === pick}
            onClick={() => setPick(i)}
            className={cn(
              "cursor-pointer rounded-lg border px-3 py-1.5 text-sm font-semibold",
              i === pick ? "border-ink bg-ink text-white" : "border-line bg-white text-heading hover:border-ink",
            )}
          >
            {c.name}
          </button>
        ))}
      </div>

      <Replay key={campaign.id} campaign={campaign} />

      <Card className="flex flex-col gap-3 p-5 sm:p-7">
        <CardTitle>How to read this</CardTitle>
        <ul className="m-0 flex flex-col gap-2 pl-5 text-[15px] leading-normal">
          <li>
            The rule: a campaign is flagged at {data.rule.min_reports} reports about the same brand and scam family within {data.rule.window_days} days. We chose it by looking at these same
            reports, so this is an illustration, not a test like the one in "How we measured it".
          </li>
          <li>The numbers are small because this is a few Reddit communities, not millions of forwards. A real network would see far more, and we haven't measured what it would catch.</li>
          <li>In production, a person would opt in to alerts, and only an anonymous description of the scam would be shared: no names, numbers or links.</li>
          <li>Nothing you check in Second Look is added to this page.</li>
        </ul>
        <div className="pt-1">
          <Button onClick={onCheck}>Check a message</Button>
        </div>
      </Card>
    </>
  );
}
