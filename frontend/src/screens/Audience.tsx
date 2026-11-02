import { ChevronLeft, Play } from "lucide-react";
import { Card, CardTitle } from "@/components/ui/card";
import { Input, Select } from "@/components/ui/input";
import { Button, PageTitle, Steps } from "@/components/shell";
import type { Target } from "@/lib/api";
import { cn } from "@/lib/utils";

export const PRESETS: { title: string; detail: string; target: Target }[] = [
  { title: "Mujeres 25–44", detail: "Reino Unido · Instagram y Facebook", target: { age_min: 25, age_max: 44, gender: "Women", countries: ["GB"] } },
  { title: "Hombres 25–44", detail: "Reino Unido · Instagram y Facebook", target: { age_min: 25, age_max: 44, gender: "Men", countries: ["GB"] } },
  { title: "Todos 18–34", detail: "Alemania y Austria", target: { age_min: 18, age_max: 34, gender: "All", countries: ["DE", "AT"] } },
  { title: "Todos 35–54", detail: "Alemania y Austria", target: { age_min: 35, age_max: 54, gender: "All", countries: ["DE", "AT"] } },
  { title: "Todos 25–54", detail: "Francia, España e Italia", target: { age_min: 25, age_max: 54, gender: "All", countries: ["FR", "ES", "IT"] } },
  { title: "Todos 18–65+", detail: "Unión Europea", target: { age_min: 18, age_max: 65, gender: "All", countries: ["DE", "FR", "ES", "IT", "NL", "PL"] } },
];

const GENDER = { All: "Todos", Women: "Mujeres", Men: "Hombres" } as const;

export function describeTarget(t: Target) {
  const ages = t.age_max >= 65 ? `${t.age_min} años o más` : `de ${t.age_min} a ${t.age_max} años`;
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
      <PageTitle title="¿A quién le vas a mostrar el anuncio?" lead={`Elige la audiencia como lo harías en Meta. Armamos ${personas} personas con ese perfil.`} />

      <Card className="flex flex-col gap-4.5 p-6">
        <CardTitle className="text-lg">Audiencias frecuentes</CardTitle>
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
          <summary className="min-h-8 cursor-pointer text-[15px] font-semibold">Ajustar edad, género y países</summary>
          <div className="mt-3 grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-3">
            <label className="flex flex-col gap-1.5 text-sm font-semibold">
              Edad desde
              <Input type="number" min={18} max={65} value={target.age_min} onChange={(e) => setTarget({ ...target, age_min: Number(e.target.value) || 18 })} />
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-semibold">
              Hasta (65 = 65 o más)
              <Input type="number" min={18} max={65} value={target.age_max} onChange={(e) => setTarget({ ...target, age_max: Number(e.target.value) || 65 })} />
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-semibold">
              Género
              <Select value={target.gender} onChange={(e) => setTarget({ ...target, gender: e.target.value as Target["gender"] })}>
                <option value="All">Todos</option>
                <option value="Women">Mujeres</option>
                <option value="Men">Hombres</option>
              </Select>
            </label>
            <label className="flex flex-col gap-1.5 text-sm font-semibold">
              Países (códigos)
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
            {personas} personas verán tus {versions} versiones en su feed, en distinto orden. Tarda menos de un minuto.
          </span>
        </div>
        <Button variant="secondary" onClick={onBack}>
          <ChevronLeft aria-hidden="true" /> Atrás
        </Button>
        <Button onClick={onRun} disabled={busy}>
          <Play aria-hidden="true" /> {busy ? "Ensayando…" : "Ensayar mis anuncios"}
        </Button>
      </Card>
    </>
  );
}
