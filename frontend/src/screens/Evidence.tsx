import { Card, CardTitle } from "@/components/ui/card";
import { Button, PageTitle } from "@/components/shell";
import type { Band, Evidence as EvidenceData, Round } from "@/lib/api";
import { cn, num, pct } from "@/lib/utils";

const REPO = "https://github.com/muze-ai-consulting/hackaton-meta";
const BAND_LABEL: Record<Band, string> = { scam: "Likely a scam (50%+)", careful: "Be careful (20-49%)", genuine: "No clear signs (under 20%)" };
const RULE_LABEL: Record<string, string> = {
  enough_legit: "At least 30 genuine cases",
  "ba_at_least_0.80": "Balanced accuracy of 0.80 or more",
  "beats_keywords_by_0.10": "Beats a keyword filter by 0.10, with the 95% interval above zero",
  "false_alarm_at_most_0.30": "False alarms on genuine cases of 30% or less",
};

function Metrics({ round }: { round: Round }) {
  const s = round.scored;
  const rows = [
    { name: "Second Look (Muse Spark 1.3)", m: s.shield, strong: true },
    { name: "Keyword filter", m: s.keywords },
    { name: "Always says scam", m: s.always_scam },
  ];
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[520px] border-collapse text-left text-sm">
        <thead>
          <tr className="text-muted">
            <th className="py-2 pr-3 font-semibold">Method</th>
            <th className="py-2 pr-3 font-semibold">Balanced accuracy</th>
            <th className="py-2 pr-3 font-semibold">Scams caught</th>
            <th className="py-2 font-semibold">False alarms</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.name} className={cn("border-t border-line", r.strong && "font-semibold text-heading")}>
              <td className="py-2.5 pr-3">{r.name}</td>
              <td className="py-2.5 pr-3">{r.m.balanced_accuracy.toFixed(3)}</td>
              <td className="py-2.5 pr-3">{pct(r.m.recall_scam)}</td>
              <td className="py-2.5">{pct(r.m.false_alarm_legit)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Rule({ round }: { round: Round }) {
  const rule = round.scored.rule;
  const passed = rule.validated;
  return (
    <ul className="m-0 flex list-none flex-col gap-1.5 p-0 text-sm">
      {Object.entries(RULE_LABEL).map(([key, label]) => (
        <li key={key} className="flex gap-2">
          <span className={rule[key] ? "text-ok" : "text-[#9b1c1c]"}>{rule[key] ? "✓" : "✗"}</span> {label}
        </li>
      ))}
      <li className={cn("mt-1 font-bold", passed ? "text-ok" : "text-[#9b1c1c]")}>{passed ? "Passed" : "Did not pass"}</li>
    </ul>
  );
}

export default function Evidence({ evidence, onBack }: { evidence: EvidenceData | null; onBack: () => void }) {
  if (!evidence) return <div className="skeleton h-64" aria-label="Loading" />;
  const r1 = evidence.round1;
  const r2 = evidence.round2;
  const b = r2.bands;
  return (
    <>
      <PageTitle
        title="How we measured it"
        lead="We wrote the pass rule before looking at any result, tested on real cases the model could not have seen, and published both attempts, including the one that failed."
      />

      <Card className="flex flex-col gap-4 p-5 sm:p-7">
        <CardTitle>The test</CardTitle>
        <ol className="m-0 flex flex-col gap-2 pl-5 text-[15px] leading-normal">
          <li>
            People post messages, screenshots and calls on Reddit (r/Scams, r/isthisascam and others) and ask "is this a scam?". We took posts from{" "}
            <strong>after 3 September 2026</strong>, after Muse Spark 1.3 was released, so the model could not have memorized them.
          </li>
          <li>The answer key is the community's verdict, read only from the replies. Unclear threads were left out.</li>
          <li>Second Look read only the post (title, text and up to 3 screenshots), never the replies.</li>
          <li>
            We published the predictions' SHA-256 hash in a commit <strong>before</strong> scoring them, and compared against two rivals: a keyword filter and
            always saying "scam".
          </li>
        </ol>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="flex flex-col gap-4 p-5 sm:p-7">
          <CardTitle>Attempt 2 · {num(r2.scored.n)} new cases</CardTitle>
          <Metrics round={r2} />
          <p className="m-0 text-sm text-muted">
            Lead over the keyword filter: +{(r2.scored.shield.balanced_accuracy - r2.scored.keywords.balanced_accuracy).toFixed(2)} (95% interval{" "}
            {r2.scored.gap_vs_keywords_ci95[0].toFixed(2)} to {r2.scored.gap_vs_keywords_ci95[1].toFixed(2)}).
          </p>
          <Rule round={r2} />
          <code className="break-all text-xs text-muted">SHA-256 {r2.sha256}</code>
        </Card>
        <Card className="flex flex-col gap-4 p-5 sm:p-7">
          <CardTitle>Attempt 1 · {num(r1.scored.n)} cases</CardTitle>
          <Metrics round={r1} />
          <Rule round={r1} />
          <p className="m-0 text-sm leading-normal text-muted">
            It missed the bar by 0.013. The question asked whether the post was deceptive, not whether what the person ran into was a scam. We fixed the
            question, wrote the rule again and ran it on new posts, without touching the attempt 1 data. The sample changed too: attempt 2 added r/ScamCenter and r/scamsUK and left out r/isthisascam and r/IsThisAScamIndia, the two lowest scores in attempt 1. On r/Scams, the one community in both, the score went from 0.816 to 0.803, so we can't credit the pass to the new question.
          </p>
          <code className="break-all text-xs text-muted">SHA-256 {r1.sha256}</code>
        </Card>
      </div>

      <Card className="flex flex-col gap-4 p-5 sm:p-7">
        <CardTitle>What each answer means, in attempt 2</CardTitle>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[460px] border-collapse text-left text-sm">
            <thead>
              <tr className="text-muted">
                <th className="py-2 pr-3 font-semibold">Answer</th>
                <th className="py-2 pr-3 font-semibold">Cases</th>
                <th className="py-2 font-semibold">Were scams</th>
              </tr>
            </thead>
            <tbody>
              {(Object.keys(BAND_LABEL) as Band[]).map((k) => (
                <tr key={k} className="border-t border-line">
                  <td className="py-2.5 pr-3 font-semibold text-heading">{BAND_LABEL[k]}</td>
                  <td className="py-2.5 pr-3">{num(b[k].scam + b[k].legit)}</td>
                  <td className="py-2.5">{pct(b[k].scam / (b[k].scam + b[k].legit))}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="m-0 text-sm leading-normal">
          That's why the lowest band says "no clear signs" and never "safe": people only post when something already worries them, so even there about half
          turned out to be scams.
        </p>
      </Card>

      <Card className="flex flex-col gap-3 p-5 sm:p-7">
        <CardTitle>Limits</CardTitle>
        <ul className="m-0 flex flex-col gap-2 pl-5 text-[15px] leading-normal">
          <li>Balanced accuracy of 0.801, with a 95% interval of 0.76 to 0.84: the 0.80 bar sits inside it, so we only claim "about 8 in 10".</li>
          <li>The answer key is a Reddit community, not a fraud investigator. Mostly English, mostly UK, US and India.</li>
          <li>About 1 in 4 genuine cases got a false alarm, mostly consumer disputes people already call "scams".</li>
          <li>Voice notes were not part of the test: they are transcribed by Muse Voice Transcribe and judged like text.</li>
          <li>The product adds one line to the tested prompt so it answers in the person's language.</li>
        </ul>
        <div className="flex flex-wrap gap-3 pt-1">
          <Button onClick={onBack}>Check a message</Button>
          <Button variant="outline" asChild>
            <a href={REPO} target="_blank" rel="noreferrer">
              Code and data
            </a>
          </Button>
        </div>
      </Card>
    </>
  );
}
