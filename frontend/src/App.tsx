import { useEffect, useState } from "react";
import { Header } from "@/components/shell";
import { ErrorNote } from "@/components/shell";
import Versions from "@/screens/Versions";
import Audience, { PRESETS } from "@/screens/Audience";
import Result from "@/screens/Result";
import RealAd from "@/screens/RealAd";
import { api, type Backtest, type Example, type Mode, type SimulateOut, type Target, type Variant } from "@/lib/api";

type Screen = "versions" | "audience" | "result" | "real";

const PERSONAS = 200;
const EMPTY: Variant = { title: "", body: "", image_url: null };

export default function App() {
  const [screen, setScreen] = useState<Screen>("versions");
  const [mode, setMode] = useState<Mode>("mock");
  const [brand, setBrand] = useState("");
  const [variants, setVariants] = useState<Variant[]>([{ ...EMPTY }, { ...EMPTY }, { ...EMPTY }]);
  const [target, setTarget] = useState<Target>(PRESETS[0].target);
  const [result, setResult] = useState<SimulateOut | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [examples, setExamples] = useState<Example[]>([]);
  const [exampleIndex, setExampleIndex] = useState(0);
  const [backtest, setBacktest] = useState<Backtest | null>(null);

  useEffect(() => {
    api.config().then((c) => setMode(c.real_allowed ? "real" : "mock")).catch(() => undefined);
    api.examples().then(setExamples).catch(() => undefined);
    api.backtest().then(setBacktest).catch(() => undefined);
  }, []);

  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [screen]);

  const filled = variants.filter((v) => v.title.trim() || v.body.trim() || v.image_url);
  const go = (i: number) => setScreen((["versions", "audience", "result"] as const)[i]);

  async function run() {
    setError("");
    setBusy(true);
    try {
      setResult(await api.simulate({ brand, variants: filled, target, personas: PERSONAS, mode }));
      setVariants(filled);
      setScreen("result");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-x-clip">
      <div className="orb" aria-hidden="true" />
      <Header onHome={() => setScreen("versions")} onExamples={() => setScreen("real")} />
      <main className="relative mx-auto flex max-w-[1180px] flex-col gap-7 px-4 pb-14 pt-10 sm:px-6">
        {screen === "versions" && (
          <Versions
            brand={brand}
            setBrand={setBrand}
            variants={variants}
            setVariants={setVariants}
            mode={mode}
            examples={examples}
            backtest={backtest}
            onNext={() => setScreen("audience")}
            onExample={(i) => {
              setExampleIndex(i);
              setScreen("real");
            }}
          />
        )}
        {screen === "audience" && (
          <>
            <Audience
              target={target}
              setTarget={setTarget}
              personas={PERSONAS}
              versions={filled.length}
              busy={busy}
              onBack={() => setScreen("versions")}
              onRun={run}
              onStep={go}
            />
            {error && <ErrorNote message={error} />}
          </>
        )}
        {screen === "result" && result && (
          <Result brand={brand} variants={variants} data={result} mode={mode} onRestart={() => setScreen("versions")} onStep={go} />
        )}
        {screen === "real" && (
          <RealAd
            key={exampleIndex}
            examples={examples}
            index={exampleIndex}
            setIndex={setExampleIndex}
            backtest={backtest}
            mode={mode}
            onOwn={() => setScreen("versions")}
          />
        )}
      </main>
    </div>
  );
}
