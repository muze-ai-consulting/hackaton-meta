import { useState } from "react";
import { Check, Eye, Shuffle, Sparkles, X } from "lucide-react";
import { AdImage } from "@/components/ad-image";
import { Card, CardTitle } from "@/components/ui/card";
import { Button, ErrorNote, PageTitle } from "@/components/shell";
import { describeTarget } from "@/screens/Audience";
import { api, type Backtest, type Example, type Mode } from "@/lib/api";
import { LETTERS, cn, num, pct } from "@/lib/utils";

interface Props {
  examples: Example[];
  index: number;
  setIndex: (i: number) => void;
  backtest: Backtest | null;
  mode: Mode;
  onOwn: () => void;
}

/** A prediction in the shape this screen needs, keyed by ad_id. */
interface Prediction {
  ranking: string[];
  stopRate: Record<string, number>;
  single: string[];
  live: boolean; // true: just simulated here; false: precomputed by the dev backtest
  mock: boolean;
  note: string;
}

const weekLabel = (w: string) => w.replace(/^(\d{4})W(\d+)$/, "week $2 of $1");

export default function RealAd({ examples, index, setIndex, backtest, mode, onOwn }: Props) {
  const ex = examples[index];
  const [pred, setPred] = useState<Prediction | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  if (!ex) {
    return (
      <Card className="p-6">
        <CardTitle>No real ads loaded yet</CardTitle>
        <p className="mb-0 text-muted">They show up here once the launches from the Meta Ad Library are built.</p>
      </Card>
    );
  }

  const ids = ex.variants.map((v) => v.ad_id);
  const reachOf = (id: string) => ex.reach[id] ?? 0;
  const realOrder = [...ids].sort((a, b) => reachOf(b) - reachOf(a));
  const realTop = realOrder[0];
  const letterOf = (id: string) => LETTERS[ids.indexOf(id)];
  const predTop = pred?.ranking[0];
  const singleTop = pred?.single[0];
  const hit = predTop === realTop;
  const ratio = reachOf(realOrder[1]) > 0 ? reachOf(realTop) / reachOf(realOrder[1]) : null;

  async function predict() {
    setError("");
    const pre = ex.prediction;
    if (pre) {
      // Precomputed before anyone looked at this screen: same answer for every visitor, no cost.
      setPred({
        ranking: pre.ranking,
        stopRate: Object.fromEntries(Object.entries(pre.stats).map(([id, s]) => [id, s.stop_rate])),
        single: pre.single_call ?? [],
        live: false,
        mock: false,
        note: `Predicted with ${pre.model ?? "Muse Spark 1.3"} and ${pre.personas ?? ""} synthetic people${pre.ran_at ? ` on ${pre.ran_at.slice(0, 10)}` : ""}. The model only saw the ads, never the reach.`,
      });
      return;
    }
    setBusy(true);
    try {
      const out = await api.simulate({
        brand: ex.brand,
        variants: ex.variants.map((v) => ({ title: v.title, body: v.body, image_url: v.image_url })),
        target: ex.target,
        personas: 200,
        mode,
      });
      const toId = (v: string) => ids[Number(v.slice(1)) - 1]; // the demo API numbers variants v1, v2…
      setPred({
        ranking: out.population.ranking.map(toId),
        stopRate: Object.fromEntries(Object.entries(out.population.stats).map(([v, s]) => [toId(v), s.stop_rate])),
        single: out.single_call.ranking.map(toId),
        live: true,
        mock: out.mode === "mock",
        note: `Simulated just now with ${out.model} and ${out.personas} synthetic people.`,
      });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  function next() {
    setIndex((index + 1) % examples.length);
    setPred(null);
    setRevealed(false);
    setError("");
  }

  return (
    <>
      <div className="flex flex-col gap-2">
        <span className="text-[15px] font-semibold text-muted">
          Real ad · {ex.brand}
          {ex.week ? ` · ${weekLabel(ex.week)}` : ""} · {describeTarget(ex.target)}
        </span>
        <PageTitle
          title={`${ex.variants.length} versions ${ex.brand} ran the same week`}
          lead="Same advertiser, same week, same targeting. Ensayo doesn't know the outcome: it predicts it with synthetic people, then we compare against the reach Meta publishes in its Ad Library."
        />
      </div>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(240px,1fr))] gap-4">
        {ex.variants.map((v, i) => {
          const rank = pred ? pred.ranking.indexOf(v.ad_id) : -1;
          return (
            <Card key={v.ad_id} className={cn("flex flex-col overflow-hidden", pred && rank === 0 && "outline-2 outline-ink")}>
              <div className="relative aspect-square bg-bg">
                <AdImage src={v.image_url} adId={v.ad_id} alt={`Version ${LETTERS[i]} by ${ex.brand}`} />
                <span className="absolute left-3 top-3 rounded-lg bg-white px-2.5 py-1 text-sm font-extrabold">{LETTERS[i]}</span>
                {revealed && v.ad_id === realTop && (
                  <span className="absolute right-3 top-3 rounded-lg bg-ok px-2.5 py-1 text-sm font-bold text-white">Real winner</span>
                )}
              </div>
              <div className="flex flex-1 flex-col gap-3 p-4">
                <span className="line-clamp-4 text-[15px] leading-[1.45]">
                  {v.title ? <strong>{v.title}. </strong> : null}
                  {v.body}
                </span>
                <div className="mt-auto flex flex-col gap-2 border-t border-line pt-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted">Ensayo predicts</span>
                    <span className="font-bold">{pred ? (rank === 0 ? "1st · winner" : ["", "2nd", "3rd", "4th", "5th", "6th"][rank]) : "—"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted">Real EU reach</span>
                    <span className="font-bold">{revealed ? num(reachOf(v.ad_id)) : "hidden"}</span>
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {error && <ErrorNote message={error} />}

      <Card className="flex flex-wrap items-center gap-5 px-7 py-6">
        {!pred && (
          <>
            <div className="min-w-[260px] flex-1">
              <div className="text-2xl font-extrabold tracking-[-0.4px]">Which one reached the most people?</div>
              <div className="text-[15px] text-muted">Ensayo predicts first. Then we look at what really happened.</div>
            </div>
            <Button onClick={predict} disabled={busy}>
              <Sparkles aria-hidden="true" /> {busy ? "Rehearsing…" : "Predict with Ensayo"}
            </Button>
          </>
        )}
        {pred && predTop && !revealed && (
          <>
            <div className="min-w-[260px] flex-1">
              <div className="text-2xl font-extrabold tracking-[-0.4px]">Ensayo bets on {letterOf(predTop)}</div>
              <div className="text-[15px] text-muted">
                {pct(pred.stopRate[predTop] ?? 0)} of the audience stopped scrolling for it.
                {singleTop ? ` A single AI prompt picked ${letterOf(singleTop)}.` : ""}
              </div>
            </div>
            <Button onClick={() => setRevealed(true)}>
              <Eye aria-hidden="true" /> Reveal the real result
            </Button>
          </>
        )}
        {pred && revealed && (
          <>
            <div className={cn("grid size-14 shrink-0 place-items-center rounded-full", hit ? "bg-ok-soft" : "bg-[#fdecec]")}>
              {hit ? <Check className="size-7 text-ok" aria-hidden="true" /> : <X className="size-7 text-[#9b1c1c]" aria-hidden="true" />}
            </div>
            <div className="min-w-[260px] flex-1">
              <div className="text-2xl font-extrabold tracking-[-0.4px]">{hit ? "Ensayo called the winner" : "Ensayo missed this one"}</div>
              <div className="text-[15px] text-muted">
                Version {letterOf(realTop)} reached {num(reachOf(realTop))} people
                {ratio && ratio >= 1.05 ? `, ${ratio.toFixed(1)}× the runner-up` : ""}.
                {singleTop ? ` A single AI prompt had picked ${letterOf(singleTop)}${singleTop === realTop ? " (also right)" : ""}.` : ""}
              </div>
            </div>
          </>
        )}
        {examples.length > 1 && (
          <Button variant="secondary" onClick={next}>
            <Shuffle aria-hidden="true" /> Another real ad
          </Button>
        )}
      </Card>

      {pred && (
        <p className={cn("m-0 rounded-xl px-4 py-3 text-sm", pred.mock ? "bg-[#fff6e0] text-[#7a5a00]" : "bg-white/70 text-muted")}>
          {pred.mock ? "Test mode: this prediction comes from a placeholder simulator with no signal. The real reach is what Meta publishes." : pred.note}
        </p>
      )}

      {backtest && !backtest.mock && (
        <Card id="method" className="flex flex-col gap-4 px-7 py-6">
          <CardTitle>Not a one-off</CardTitle>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-4">
            {([
              ["Ensayo", backtest.summary.population, "bg-soft"],
              ["A single AI prompt", backtest.summary.single_call, "bg-bg"],
              ["Chance", backtest.summary.random, "bg-bg"],
            ] as const).map(([name, m, bg]) => (
              <div key={name} className={cn("rounded-xl p-4.5", bg)}>
                <div className="text-sm font-semibold">{name}</div>
                <div className="text-[32px] font-extrabold">{pct(m.top1.mean)}</div>
                <div className="text-[13px] text-muted">winners called</div>
              </div>
            ))}
          </div>
          <p className="m-0 text-sm leading-normal text-muted">
            {backtest.batches} launches by brands in the EU and the UK, all after September 2, 2026, when Muse Spark 1.3 came out. Predictions for the sealed
            set are published with their SHA-256 fingerprint before we look at the results.
          </p>
          <div>
            <Button variant="secondary" onClick={onOwn}>
              Try it with your own ads
            </Button>
          </div>
        </Card>
      )}
    </>
  );
}
