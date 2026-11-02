import { useRef, useState } from "react";
import { ChevronRight, ImagePlus, Plus, ShieldCheck, Sparkles, X } from "lucide-react";
import { Card, CardTitle } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { Button, ErrorNote, PageTitle, Steps, TrustLine } from "@/components/shell";
import { api, type Backtest, type Example, type Mode, type Variant } from "@/lib/api";
import { LETTERS, fileToDataUrl } from "@/lib/utils";

const TINTS = ["#dbe7f6", "#e6dff5", "#e7f3ea", "#f6efdc"];

interface Props {
  brand: string;
  setBrand: (b: string) => void;
  variants: Variant[];
  setVariants: (v: Variant[]) => void;
  mode: Mode;
  examples: Example[];
  backtest: Backtest | null;
  onNext: () => void;
  onExample: (i: number) => void;
}

export default function Versions({ brand, setBrand, variants, setVariants, mode, examples, backtest, onNext, onExample }: Props) {
  const [brief, setBrief] = useState("");
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const files = useRef<(HTMLInputElement | null)[]>([]);

  const update = (i: number, patch: Partial<Variant>) => setVariants(variants.map((v, j) => (j === i ? { ...v, ...patch } : v)));
  const ready = variants.filter((v) => v.title.trim() || v.body.trim() || v.image_url).length >= 2;

  async function pick(i: number, file: File | undefined) {
    if (!file) return;
    try {
      update(i, { image_url: await fileToDataUrl(file) });
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function generate() {
    setError("");
    setGenerating(true);
    try {
      const photo = variants.find((v) => v.image_url)?.image_url ?? null;
      const out = await api.variants({ brand, brief, photo_url: photo, n: Math.max(3, variants.length), mode });
      setVariants(out.variants.map((v) => ({ title: v.title, body: v.body, image_url: v.image_url })));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setGenerating(false);
    }
  }

  return (
    <>
      <PageTitle
        big
        title="¿Cuál de tus anuncios va a funcionar?"
        lead="Sube tus versiones y una audiencia sintética de Instagram y Facebook te dice cuál la hace detenerse, antes de que pagues por ella."
      />
      <Steps current={0} onGo={() => undefined} />

      <div className="flex flex-wrap items-start gap-6">
        <Card className="flex min-w-0 flex-[999_1_600px] flex-col gap-5 p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <CardTitle>Tus versiones del anuncio</CardTitle>
            <span className="text-sm text-muted">De 2 a 4</span>
          </div>
          <label className="flex max-w-sm flex-col gap-1.5 text-sm font-semibold">
            Marca
            <Input value={brand} onChange={(e) => setBrand(e.target.value)} placeholder="Ej.: Snocks" />
          </label>

          <div className="grid grid-cols-[repeat(auto-fill,minmax(200px,1fr))] gap-4">
            {variants.map((v, i) => (
              <div key={i} className="flex flex-col gap-2.5">
                <div className="relative aspect-square overflow-hidden rounded-xl" style={{ background: v.image_url ? "#fff" : TINTS[i % 4] }}>
                  {v.image_url ? (
                    <img src={v.image_url} alt={`Imagen de la versión ${LETTERS[i]}`} className="size-full object-cover" />
                  ) : (
                    <button
                      type="button"
                      onClick={() => files.current[i]?.click()}
                      className="flex size-full cursor-pointer flex-col items-center justify-center gap-1.5 text-sm font-semibold text-muted"
                    >
                      <ImagePlus className="size-6" aria-hidden="true" /> Subir foto
                    </button>
                  )}
                  <span className="absolute left-2.5 top-2.5 grid size-7 place-items-center rounded-lg bg-white text-sm font-bold shadow-[0_1px_2px_rgba(0,0,0,.12)]">
                    {LETTERS[i]}
                  </span>
                  {(v.image_url || variants.length > 2) && (
                    <button
                      type="button"
                      aria-label={v.image_url ? `Quitar la foto de la versión ${LETTERS[i]}` : `Quitar la versión ${LETTERS[i]}`}
                      onClick={() => (v.image_url ? update(i, { image_url: null }) : setVariants(variants.filter((_, j) => j !== i)))}
                      className="absolute right-2.5 top-2.5 grid size-7 cursor-pointer place-items-center rounded-lg bg-white/90 text-ink"
                    >
                      <X className="size-4" aria-hidden="true" />
                    </button>
                  )}
                  <input
                    ref={(el) => { files.current[i] = el; }}
                    type="file"
                    accept="image/*"
                    hidden
                    onChange={(e) => pick(i, e.target.files?.[0])}
                  />
                </div>
                <Input aria-label={`Título de la versión ${LETTERS[i]}`} value={v.title} onChange={(e) => update(i, { title: e.target.value })} placeholder="Título" />
                <Textarea
                  aria-label={`Texto de la versión ${LETTERS[i]}`}
                  value={v.body}
                  onChange={(e) => update(i, { body: e.target.value })}
                  placeholder="Texto del anuncio"
                  rows={2}
                />
              </div>
            ))}
            {variants.length < 4 && (
              <button
                type="button"
                onClick={() => setVariants([...variants, { title: "", body: "", image_url: null }])}
                className="flex aspect-square cursor-pointer flex-col items-center justify-center gap-1.5 rounded-xl border-2 border-dashed border-[#c4c8d0] bg-[#f5f6f8] text-sm font-semibold text-muted"
              >
                <Plus className="size-6" aria-hidden="true" /> Agregar versión
              </button>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-3.5 rounded-xl bg-soft px-4 py-3.5">
            <Sparkles className="size-[22px] shrink-0" aria-hidden="true" />
            <div className="min-w-[200px] flex-1">
              <div className="text-[15px] font-bold">¿Tienes una sola foto o solo la idea?</div>
              <div className="text-sm text-muted">Muse Image crea las versiones con ángulos distintos.</div>
              <Input
                className="mt-2 bg-white"
                value={brief}
                onChange={(e) => setBrief(e.target.value)}
                placeholder="Describe el producto: calcetines de algodón orgánico, pack de 3"
                aria-label="Producto o idea"
              />
            </div>
            <Button variant="secondary" onClick={generate} disabled={generating || (!brief.trim() && !variants.some((v) => v.image_url))}>
              {generating ? "Generando…" : "Generar versiones"}
            </Button>
          </div>

          {error && <ErrorNote message={error} />}
          <div className="flex justify-end">
            <Button onClick={onNext} disabled={!ready}>
              Siguiente: tu audiencia <ChevronRight aria-hidden="true" />
            </Button>
          </div>
        </Card>

        <aside className="flex min-w-0 flex-[1_1_320px] flex-col gap-4">
          <Card className="flex flex-col gap-3.5 p-6">
            <CardTitle className="text-lg">Pruébalo con un anuncio real</CardTitle>
            <p className="m-0 text-sm leading-normal text-muted">
              Versiones que una marca publicó la misma semana. Mira qué predice Ensayo y después lo que pasó de verdad.
            </p>
            {examples.length === 0 && <p className="m-0 text-sm text-muted">Los ejemplos aparecen cuando terminamos de cargar los lanzamientos.</p>}
            {examples.slice(0, 4).map((ex, i) => (
              <button
                key={ex.batch_id}
                type="button"
                onClick={() => onExample(i)}
                className="flex min-h-11 cursor-pointer items-center gap-3 rounded-xl bg-bg p-2.5 text-left"
              >
                <span className="grid size-10 shrink-0 place-items-center rounded-full bg-white font-extrabold">{ex.brand.slice(0, 1) || "?"}</span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-[15px] font-bold">{ex.brand}</span>
                  <span className="block text-[13px] text-muted">
                    {ex.variants.length} versiones · {ex.target.countries.join(", ")}
                  </span>
                </span>
                <ChevronRight className="size-[18px] text-muted" aria-hidden="true" />
              </button>
            ))}
          </Card>
          {backtest && (
            <Card className="flex items-start gap-3.5 px-6 py-5">
              <ShieldCheck className="mt-0.5 size-[22px] shrink-0 text-ok" aria-hidden="true" />
              <TrustLine backtest={backtest} onMore={examples.length ? () => onExample(0) : undefined} />
            </Card>
          )}
        </aside>
      </div>
    </>
  );
}
