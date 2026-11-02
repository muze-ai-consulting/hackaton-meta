import { ChevronLeft, Play } from "lucide-react";
import { Card, CardTitle } from "@/components/ui/card";
import { Input, Select } from "@/components/ui/input";
import { Button, PageTitle, Steps } from "@/components/shell";
import type { Target } from "@/lib/api";
import { cn } from "@/lib/utils";

export const PRESETS: { title: string; detail: string; target: Target }[] = [
  { title: "Women 25–44", detail: "United Kingdom · Instagram and Facebook", target: { age_min: 25, age_max: 44, gender: "Women", countries: ["GB"] } },
  { title: "Men 25–44", detail: "United Kingdom · Instagram and Facebook", target: { age_min: 25, age_max: 44, gender: "Men", countries: ["GB"] } },
  { title: "Everyone 18–34", detail: "Germany and Austria", target: { age_min: 18, age_max: 34, gender: "All", countries: ["DE", "AT"] } },
  { title: "Everyone 35–54", detail: "Germany and Austria", target: { age_min: 35, age_max: 54, gender: "All", countries: ["DE", "AT"] } },
  { title: "Everyone 25–54", detail: "France, Spain and Italy", target: { age_min: 25, age_max: 54, gender: "All", countries: ["FR", "ES", "IT"] } },
  { title: "Everyone 18–65+", detail: "European Union", target: { age_min: 18, age_max: 65, gender: "All", countries: ["DE", "FR", "ES", "IT", "NL", "PL"] } },
];

const GENDER = { All: "Everyone", Women: "Women", Men: "Men" } as const;

export function describeTarget(t: Target) {
  const ages = t.age_max >= 65 ? `${t.age_min}+` : `${t.age_min}–${t.age_max}`;
  return `${GENDER[t.gender]} ${ages} · ${t.countries.join(", ")}`;
}

interface Props {
  target: Target;
  setTarget: (t: Target) => void;
  personas: number;
  versions: number;
  busy: boolean;
  onBack: () => void;
  onRun: () => void;
  onStep: (i: number) => void;
}

export default function Audience({ target, setTarget, personas, versions, busy, onBack, onRun, onStep }: Props) {
  const same = (t: Target) => JSON.stringify(t) === JSON.stringify(target);
  return (
    <>
      <Steps current={1} onGo={onStep} />
      <PageTitle title="Who will see this ad?" lead={`Pick the audience as you would in Meta Ads Manager. We build ${personas} synthetic people with that profile.`} />

      <Card className="flex flex-col gap-4.5 p-6">
        <CardTitle className="text-lg">Common audiences</CardTitle>
        <div className="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-3">
          {PRESETS.map((p) => (
            <button
              key={p.title + p.detail}
              type="button"
              aria-pressed={same(p.target)}
              onClick={() => setTarget(p.target)}
              className={cn(
                "flex min-h-[92px] cursor-pointer flex-col gap-1 rounded-xl p-4 text-left",
                same(p.target) ? "border-2 border-ink bg-soft" : "border border-line bg-white hover:bg-bg",
              )}
            >
              <span className="text-base font-bold">{p.title}</span>
              <span className="text-sm text-muted">{p.detail}</span>
            </button>
          ))}
        </div>
        <details className="border-t border-line pt-3.5">
          <summary className="min-h-8 cursor-pointer text-[15px] font-semibold">Adjust age, gender and countries</summary>
          <div className="mt-3 grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-3">
            <label className="flex flex-col gap-1.5 text-sm font-semibold">
              Age from
              <Input type="number" min={18} max={65} value={target.age_min} onChange={(e) => setTarget({ ...target, age_min: Number(e.target.value) || 18 })} />
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-semibold">
              To (65 = 65+)
              <Input type="number" min={18} max={65} value={target.age_max} onChange={(e) => setTarget({ ...target, age_max: Number(e.target.value) || 65 })} />
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-semibold">
              Gender
              <Select value={target.gender} onChange={(e) => setTarget({ ...target, gender: e.target.value as Target["gender"] })}>
                <option value="All">Everyone</option>
                <option value="Women">Women</option>
                <option value="Men">Men</option>
              </Select>
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-semibold">
              Countries (codes)
              <Input
                value={target.countries.join(", ")}
                onChange={(e) => setTarget({ ...target, countries: e.target.value.split(/[,\s]+/).map((c) => c.toUpperCase()).filter(Boolean).slice(0, 10) })}
                placeholder="GB, DE, FR"
              />
            </label>
          </div>
        </details>
      </Card>

      <Card className="flex flex-wrap items-center gap-5 px-6 py-5">
        <div className="flex min-w-[240px] flex-1 flex-col gap-0.5">
          <span className="text-base font-bold">{describeTarget(target)}</span>
          <span className="text-sm text-muted">
            {personas} people will see your {versions} versions in their feed, in different orders. Takes under a minute.
          </span>
        </div>
        <Button variant="secondary" onClick={onBack}>
          <ChevronLeft aria-hidden="true" /> Back
        </Button>
        <Button onClick={onRun} disabled={busy}>
          <Play aria-hidden="true" /> {busy ? "Rehearsing…" : "Rehearse my ads"}
        </Button>
      </Card>
    </>
  );
}
