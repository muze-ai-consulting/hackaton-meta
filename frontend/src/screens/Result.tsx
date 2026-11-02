import { useEffect, useRef, useState } from "react";
import { MessageCircle, RotateCcw, Send } from "lucide-react";
import { Card, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button, ErrorNote, Steps } from "@/components/shell";
import { api, type Mode, type Reaction, type SimulateOut, type Variant } from "@/lib/api";
import { LETTERS, cn, pct } from "@/lib/utils";

const SUGGESTED = ["¿Por qué te detuviste en ese anuncio?", "¿Qué te haría hacer clic?", "¿Le crees a la oferta?"];

interface Props {
  brand: string;
  variants: Variant[];
  data: SimulateOut;
  mode: Mode;
  onRestart: () => void;
  onStep: (i: number) => void;
}

export default function Result({ brand, variants, data, mode, onRestart, onStep }: Props) {
  const pop = data.population;
  const letter = (id: string) => LETTERS[Number(id.slice(1)) - 1];
  const byId = (id: string) => variants[Number(id.slice(1)) - 1];
  const winner = pop.ranking[0];
  const w = pop.stats[winner];
  const others = pop.ranking.slice(1).map((id) => `${Math.round(pop.stats[id].stop_rate * 10)} en la ${letter(id)}`);
  const maxStop = Math.max(0.01, ...pop.ranking.map((id) => pop.stats[id].stop_rate));
  const singleTop = data.single_call.ranking[0];
  const reasons = [...new Set(w.click_reasons)].slice(0, 3);
  const [person, setPerson] = useState(0);

  return (
    <>
      <Steps current={2} onGo={onStep} />
      {data.mode === "mock" && (
        <p className="m-0 rounded-xl bg-[#fff6e0] px-4 py-3 text-sm text-[#7a5a00]">
          Modo prueba: las reacciones salen de un simulador sin señal. Sirve para ver el recorrido, no para decidir.
        </p>
      )}

      <div className="flex flex-wrap items-start gap-6">
        <div className="flex min-w-0 flex-[999_1_620px] flex-col gap-6">
          <Card className="flex flex-wrap overflow-hidden">
            <div className="relative aspect-square w-full bg-[#e6dff5] sm:w-[300px]">
              {byId(winner).image_url && <img src={byId(winner).image_url!} alt={`Versión ganadora ${letter(winner)}`} className="size-full object-cover" />}
              <span className="absolute left-3 top-3 rounded-lg bg-ok px-2.5 py-1 text-sm font-bold text-white">Gana</span>
            </div>
            <div className="flex min-w-[260px] flex-1 flex-col justify-center gap-3 p-7">
              <span className="text-[15px] font-semibold text-muted">Tu audiencia eligió</span>
              <h1 className="m-0 text-[44px] font-bold leading-[1.05] tracking-[-1.2px]">La versión {letter(winner)}</h1>
              <p className="m-0 text-[17px] leading-normal text-muted">
                {Math.round(w.stop_rate * 10)} de cada 10 personas se detuvieron a mirarla{others.length ? `, contra ${others.join(" y ")}` : ""}.
              </p>
              <p className="m-0 text-sm text-muted">
                {data.personas} personas · {pop.calls + 1} llamadas a {data.model}
                {data.mode === "real" ? ` · US$ ${data.usd.toFixed(3)}` : ""}
              </p>
              <div className="mt-1 flex flex-wrap gap-3">
                <Button asChild>
                  <a href="#chat">
                    <MessageCircle aria-hidden="true" /> Pregúntale a tu audiencia
                  </a>
                </Button>
                <Button variant="secondary" onClick={onRestart}>
                  <RotateCcw aria-hidden="true" /> Ensayar otras versiones
                </Button>
              </div>
            </div>
          </Card>

          {reasons.length > 0 && (
            <Card className="flex flex-col gap-4 p-6">
              <CardTitle>Por qué gana la {letter(winner)}</CardTitle>
              {reasons.map((r, i) => (
                <div key={r} className="flex items-start gap-3.5">
                  <span className="grid size-8 shrink-0 place-items-center rounded-full bg-soft text-sm font-bold">{i + 1}</span>
                  <p className="m-0 pt-1 text-[15px] leading-normal">{r}</p>
                </div>
              ))}
            </Card>
          )}

          <Card className="flex flex-col gap-4 p-6">
            <CardTitle>{variants.length === 2 ? "Las dos versiones" : `Las ${variants.length} versiones`}</CardTitle>
            {pop.ranking.map((id, i) => {
              const s = pop.stats[id];
              const v = byId(id);
              return (
                <div key={id} className="flex items-center gap-3.5">
                  <div className={cn("grid size-12 shrink-0 place-items-center overflow-hidden rounded-[10px] font-extrabold", i === 0 ? "bg-ink text-white" : "bg-bg")}>
                    {v.image_url ? <img src={v.image_url} alt="" className="size-full object-cover" /> : letter(id)}
                  </div>
                  <div className="flex min-w-0 flex-1 flex-col gap-1.5">
                    <span className="truncate text-sm">
                      <strong>{letter(id)}</strong> · {v.title || v.body || "(sin texto)"}
                    </span>
                    <div className="h-2.5 overflow-hidden rounded-full bg-bg" role="img" aria-label={`Se detienen: ${pct(s.stop_rate)}. Hacen clic: ${pct(s.click_rate)}`}>
                      <div className={cn("h-full rounded-full", i === 0 ? "brand-gradient" : "bg-[#b9bec8]")} style={{ width: `${(s.stop_rate / maxStop) * 100}%` }} />
                    </div>
                  </div>
                  <div className="w-24 shrink-0 text-right text-sm">
                    <div className="font-bold">{pct(s.stop_rate)}</div>
                    <div className="text-xs text-muted">{pct(s.click_rate)} clic</div>
                  </div>
                </div>
              );
            })}
            <p className="m-0 text-sm text-muted">
              Barra: personas que se detuvieron.{" "}
              {singleTop === winner
                ? `Una sola pregunta a la IA también habría elegido la ${letter(winner)}.`
                : `Una sola pregunta a la IA habría elegido la ${letter(singleTop)}.`}
            </p>
          </Card>
        </div>

        <Chat brand={brand} variants={variants} people={pop.sample_reactions} person={person} setPerson={setPerson} mode={mode} letter={letter} />
      </div>
    </>
  );
}

function shortName(p: Reaction) {
  return p.persona.split(/[.;]/)[0].slice(0, 60);
}

function Chat({
  brand, variants, people, person, setPerson, mode, letter,
}: {
  brand: string;
  variants: Variant[];
  people: Reaction[];
  person: number;
  setPerson: (i: number) => void;
  mode: Mode;
  letter: (id: string) => string;
}) {
  const [threads, setThreads] = useState<Record<number, { role: "user" | "persona"; text: string }[]>>({});
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const log = useRef<HTMLDivElement>(null);
  const p = people[person];
  const history = threads[person] ?? [];

  useEffect(() => {
    log.current?.scrollTo({ top: log.current.scrollHeight });
  }, [history.length, busy]);

  if (!p) return null;
  const did = p.stopped.length ? `Se detuvo en la ${p.stopped.map(letter).join(" y la ")}` : "Pasó de largo";

  async function ask(q: string) {
    if (!q.trim() || busy) return;
    setError("");
    setBusy(true);
    setQuestion("");
    const next = [...history, { role: "user" as const, text: q }];
    setThreads((t) => ({ ...t, [person]: next }));
    try {
      const out = await api.chat({
        brand, persona: p.persona, variants, stopped: p.stopped, clicked: p.clicked, reason: p.reason, history, question: q, mode,
      });
      setThreads((t) => ({ ...t, [person]: [...next, { role: "persona", text: out.answer }] }));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card id="chat" aria-label="Conversación con tu audiencia" className="flex min-w-0 flex-[1_1_340px] flex-col gap-4 p-6 lg:sticky lg:top-6">
      <CardTitle className="text-lg">Pregúntale a tu audiencia</CardTitle>
      <div className="flex flex-wrap gap-2">
        {people.slice(0, 6).map((x, i) => (
          <button
            key={i}
            type="button"
            onClick={() => setPerson(i)}
            aria-pressed={i === person}
            className={cn("flex min-h-10 max-w-full cursor-pointer items-center gap-2 rounded-full py-1 pl-1 pr-3 text-[13px] font-semibold", i === person ? "bg-ink text-white" : "bg-bg")}
          >
            <span className={cn("grid size-8 shrink-0 place-items-center rounded-full font-bold", i === person ? "bg-white/20" : "bg-white")}>{shortName(x).slice(0, 1)}</span>
            <span className="truncate">{x.segment.replace("instagram", "Instagram").replace("facebook", "Facebook")}</span>
          </button>
        ))}
      </div>
      <div className="rounded-xl bg-bg px-4 py-3">
        <div className="text-[15px] font-bold">{shortName(p)}</div>
        <div className="text-[13px] text-muted">
          {did}
          {p.clicked.length ? ` · hizo clic en la ${p.clicked.map(letter).join(" y la ")}` : ""}
        </div>
        {p.reason && <div className="mt-1.5 text-sm italic">«{p.reason}»</div>}
      </div>
      <div ref={log} className="flex max-h-[360px] min-h-24 flex-col gap-2.5 overflow-y-auto" aria-live="polite">
        {history.length === 0 && <p className="m-0 text-sm text-muted">Pregúntale lo que le preguntarías en un focus group.</p>}
        {history.map((t, i) => (
          <div
            key={i}
            className={cn("max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-normal", t.role === "user" ? "self-end bg-ink text-white" : "self-start bg-soft")}
          >
            {t.text}
          </div>
        ))}
        {busy && <div className="skeleton h-10 w-2/3" />}
      </div>
      {error && <ErrorNote message={error} />}
      <div className="flex flex-wrap gap-2">
        {SUGGESTED.map((q) => (
          <button key={q} type="button" onClick={() => ask(q)} disabled={busy} className="min-h-9 cursor-pointer rounded-full border border-line bg-white px-3 text-[13px] font-medium hover:bg-bg">
            {q}
          </button>
        ))}
      </div>
      <form className="flex gap-2" onSubmit={(e) => { e.preventDefault(); ask(question); }}>
        <Input aria-label="Tu pregunta" value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Escribe una pregunta…" maxLength={500} />
        <Button type="submit" size="icon" aria-label="Enviar" disabled={busy || !question.trim()} className="shrink-0">
          <Send aria-hidden="true" />
        </Button>
      </form>
    </Card>
  );
}
