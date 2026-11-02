import { useState } from "react";
import { Check, Eye, Shuffle, Sparkles, X } from "lucide-react";
import { Card, CardTitle } from "@/components/ui/card";
import { Button, ErrorNote, PageTitle } from "@/components/shell";
import { describeTarget } from "@/screens/Audience";
import { api, type Backtest, type Example, type Mode, type SimulateOut } from "@/lib/api";
import { LETTERS, cn, num, pct } from "@/lib/utils";

interface Props {
  examples: Example[];
  index: number;
  setIndex: (i: number) => void;
  backtest: Backtest | null;
  mode: Mode;
  onOwn: () => void;
}

export default function RealAd({ examples, index, setIndex, backtest, mode, onOwn }: Props) {
  const ex = examples[index];
  const [pred, setPred] = useState<SimulateOut | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  if (!ex) {
    return (
      <Card className="p-6">
        <CardTitle>Todavía no hay anuncios reales cargados</CardTitle>
        <p className="mb-0 text-muted">Aparecen aquí cuando terminamos de armar los lanzamientos desde la Biblioteca de anuncios.</p>
      </Card>
    );
  }

  // El demo numera las versiones v1, v2…; el lote real usa ad_id.
  const idOf = (i: number) => `v${i + 1}`;
  const reachOf = (i: number) => ex.reach[ex.variants[i].ad_id] ?? 0;
  const realOrder = ex.variants.map((_, i) => i).sort((a, b) => reachOf(b) - reachOf(a));
  const realTop = realOrder[0];
  const predRank = pred ? Object.fromEntries(pred.population.ranking.map((id, r) => [id, r])) : {};
  const predTop = pred ? Number(pred.population.ranking[0].slice(1)) - 1 : -1;
  const singleTop = pred ? Number(pred.single_call.ranking[0].slice(1)) - 1 : -1;
  const hit = predTop === realTop;
  const ratio = reachOf(realOrder[1]) > 0 ? reachOf(realTop) / reachOf(realOrder[1]) : null;

  async function predict() {
    setError("");
    setBusy(true);
    try {
      setPred(
        await api.simulate({
          brand: ex.brand,
          variants: ex.variants.map((v) => ({ title: v.title, body: v.body, image_url: v.image_url })),
          target: ex.target,
          personas: 200,
          mode,
        }),
      );
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
          Anuncio real · {ex.brand}
          {ex.week ? ` · ${ex.week.replace(/^(\d{4})W(\d+)$/, "semana $2 de $1")}` : ""} · {describeTarget(ex.target)}
        </span>
        <PageTitle
          title={`${ex.variants.length} versiones que ${ex.brand} publicó la misma semana`}
          lead="Mismo anunciante, misma semana, misma audiencia. Ensayo no conoce el resultado: lo predice con 200 personas sintéticas y después lo comparamos con el alcance que Meta publica en su Biblioteca de anuncios."
        />
      </div>

      <div className="grid grid-cols-[repeat(auto-fit,minmax(240px,1fr))] gap-4">
        {ex.variants.map((v, i) => {
          const rank = predRank[idOf(i)];
          const winsPred = pred && rank === 0;
          return (
            <Card key={v.ad_id} className={cn("flex flex-col overflow-hidden", winsPred && "outline-2 outline-ink")}>
              <div className="relative aspect-square bg-bg">
                {v.image_url ? (
                  <img src={v.image_url} alt={`Versión ${LETTERS[i]} de ${ex.brand}`} className="size-full object-cover" referrerPolicy="no-referrer" />
                ) : (
                  <div className="grid size-full place-items-center text-sm text-muted">Sin imagen</div>
                )}
                <span className="absolute left-3 top-3 rounded-lg bg-white px-2.5 py-1 text-sm font-extrabold">{LETTERS[i]}</span>
                {revealed && i === realTop && <span className="absolute right-3 top-3 rounded-lg bg-ok px-2.5 py-1 text-sm font-bold text-white">Ganó de verdad</span>}
              </div>
              <div className="flex flex-1 flex-col gap-3 p-4">
                <span className="line-clamp-4 text-[15px] leading-[1.45]">{v.title ? <strong>{v.title}. </strong> : null}{v.body}</span>
                <div className="mt-auto flex flex-col gap-2 border-t border-line pt-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted">Ensayo predice</span>
                    <span className="font-bold">{pred ? (rank === 0 ? "1.º · gana" : `${rank + 1}.º lugar`) : "—"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted">Alcance real en la UE</span>
                    <span className="font-bold">{revealed ? num(reachOf(i)) : "oculto"}</span>
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
              <div className="text-2xl font-extrabold tracking-[-0.4px]">¿Cuál llegó a más gente?</div>
              <div className="text-[15px] text-muted">Primero predice Ensayo. Después miramos el resultado real.</div>
            </div>
            <Button onClick={predict} disabled={busy}>
              <Sparkles aria-hidden="true" /> {busy ? "Ensayando…" : "Predecir con Ensayo"}
            </Button>
          </>
        )}
        {pred && !revealed && (
          <>
            <div className="min-w-[260px] flex-1">
              <div className="text-2xl font-extrabold tracking-[-0.4px]">Ensayo apuesta por la {LETTERS[predTop]}</div>
              <div className="text-[15px] text-muted">
                Se detuvo el {pct(pred.population.stats[idOf(predTop)].stop_rate)} de la audiencia. Una sola pregunta a la IA eligió la {LETTERS[singleTop]}.
              </div>
            </div>
            <Button onClick={() => setRevealed(true)}>
              <Eye aria-hidden="true" /> Revelar el resultado real
            </Button>
          </>
        )}
        {pred && revealed && (
          <>
            <div className={cn("grid size-14 shrink-0 place-items-center rounded-full", hit ? "bg-ok-soft" : "bg-[#fdecec]")}>
              {hit ? <Check className="size-7 text-ok" aria-hidden="true" /> : <X className="size-7 text-[#9b1c1c]" aria-hidden="true" />}
            </div>
            <div className="min-w-[260px] flex-1">
              <div className="text-2xl font-extrabold tracking-[-0.4px]">{hit ? "Ensayo acertó la ganadora" : "Esta vez Ensayo no acertó"}</div>
              <div className="text-[15px] text-muted">
                La versión {LETTERS[realTop]} llegó a {num(reachOf(realTop))} personas
                {ratio && ratio >= 1.05 ? `, ${ratio.toFixed(1).replace(".", ",")} veces más que la siguiente` : ""}. Una sola pregunta a la IA había elegido la{" "}
                {LETTERS[singleTop]}
                {singleTop === realTop ? " (también acertó)" : ""}.
              </div>
            </div>
          </>
        )}
        {examples.length > 1 && (
          <Button variant="secondary" onClick={next}>
            <Shuffle aria-hidden="true" /> Otro anuncio real
          </Button>
        )}
      </Card>

      {pred?.mode === "mock" && (
        <p className="m-0 rounded-xl bg-[#fff6e0] px-4 py-3 text-sm text-[#7a5a00]">
          Modo prueba: la predicción sale de un simulador sin señal. El alcance real sí es el que publica Meta.
        </p>
      )}

      {backtest && (
        <Card id="metodo" className="flex flex-col gap-4 px-7 py-6">
          <CardTitle>{backtest.mock ? "Cómo lo medimos" : "No es un caso aislado"}</CardTitle>
          <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-4">
            {([
              ["Ensayo", backtest.summary.population, "bg-soft"],
              ["Una pregunta a la IA", backtest.summary.single_call, "bg-bg"],
              ["Al azar", backtest.summary.random, "bg-bg"],
            ] as const).map(([name, m, bg]) => (
              <div key={name} className={cn("rounded-xl p-4.5", bg)}>
                <div className="text-sm font-semibold">{name}</div>
                <div className="text-[32px] font-extrabold">{pct(m.top1.mean)}</div>
                <div className="text-[13px] text-muted">ganadoras acertadas</div>
              </div>
            ))}
          </div>
          <p className="m-0 text-sm leading-normal text-muted">
            {backtest.batches} lanzamientos{backtest.mock ? " de prueba (circuito sin señal, se reemplaza por la corrida real)" : ""} de marcas en la UE y el Reino Unido,
            todos posteriores al 2 de septiembre de 2026, cuando salió Muse Spark 1.3. Las predicciones del set sellado se publican con su huella SHA-256 antes de ver los
            resultados.
          </p>
          <div>
            <Button variant="secondary" onClick={onOwn}>
              Prueba con tus anuncios
            </Button>
          </div>
        </Card>
      )}
    </>
  );
}
