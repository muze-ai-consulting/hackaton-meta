import { Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Backtest } from "@/lib/api";
import { cn, pct } from "@/lib/utils";

export function Logo() {
  return (
    <div className="flex items-center gap-2.5">
      <div className="brand-gradient grid size-9 place-items-center rounded-[10px]">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6z" />
          <path d="M9 12l2 2 4-4" />
        </svg>
      </div>
      <span className="text-xl font-extrabold tracking-[-0.3px] text-heading">Second Look</span>
    </div>
  );
}

export function Header({ onHome, onCampaigns, onEvidence }: { onHome: () => void; onCampaigns: () => void; onEvidence: () => void }) {
  return (
    <header className="relative border-b border-white/40 bg-white/70 backdrop-blur-md">
      <div className="mx-auto flex min-h-16 max-w-[1180px] flex-wrap items-center justify-between gap-4 px-6">
        <button type="button" onClick={onHome} className="cursor-pointer" aria-label="Home">
          <Logo />
        </button>
        <nav aria-label="Main" className="flex flex-wrap items-center gap-5 text-[15px] font-semibold">
          <button type="button" onClick={onCampaigns} className="cursor-pointer hover:text-heading">
            What's going around
          </button>
          <button type="button" onClick={onEvidence} className="cursor-pointer hover:text-heading">
            How we measured it
          </button>
          <Badge className="hidden sm:inline-flex">Built on Muse Spark 1.3 and Muse Voice Transcribe</Badge>
        </nav>
      </div>
    </header>
  );
}

const STEPS = ["Your versions", "Your audience", "Result"];

export function Steps({ current, onGo }: { current: number; onGo: (i: number) => void }) {
  return (
    <ol aria-label="Steps" className="m-0 flex list-none flex-wrap gap-2 p-0">
      {STEPS.map((s, i) => (
        <li key={s}>
          <button
            type="button"
            disabled={i > current}
            onClick={() => onGo(i)}
            aria-current={i === current ? "step" : undefined}
            className={cn(
              "flex items-center gap-2 rounded-[10px] px-3.5 py-2 text-sm font-semibold",
              i === current ? "bg-ink text-white" : i < current ? "cursor-pointer bg-white text-ok" : "bg-white text-muted",
            )}
          >
            {i < current ? <Check className="size-4" aria-hidden="true" /> : `${i + 1} ·`} {s}
          </button>
        </li>
      ))}
    </ol>
  );
}

export function PageTitle({ title, lead, big = false }: { title: string; lead: string; big?: boolean }) {
  return (
    <div className="flex max-w-[760px] flex-col gap-2.5">
      <h1 className={cn("m-0 font-bold leading-[1.1]", big ? "text-[40px] tracking-[-1px] md:text-[60px] md:tracking-[-1.5px]" : "text-[34px] tracking-[-0.8px] md:text-[48px] md:tracking-[-1.2px]")}>
        {title}
      </h1>
      <p className={cn("m-0 text-muted", big ? "text-lg leading-[1.625] md:text-xl" : "text-[17px] leading-normal")}>{lead}</p>
    </div>
  );
}

/** The trust line: how often Ensayo picks the winner vs the rivals. Hidden until there is a real backtest. */
export function TrustLine({ backtest, onMore }: { backtest: Backtest | null; onMore?: () => void }) {
  if (!backtest || backtest.mock) return null;
  const s = backtest.summary;
  return (
    <div className="text-sm leading-normal">
      Across <strong>{backtest.batches} real launches</strong>, Ensayo picked the winning version <strong>{pct(s.population.top1.mean)}</strong> of
      the time. A single AI prompt: {pct(s.single_call.top1.mean)}. Chance: {pct(s.random.top1.mean)}.{" "}
      {onMore && (
        <button type="button" onClick={onMore} className="cursor-pointer font-semibold underline">
          How we measure it
        </button>
      )}
    </div>
  );
}

export function ErrorNote({ message }: { message: string }) {
  return (
    <p role="alert" className="m-0 rounded-xl bg-[#fdecec] px-4 py-3 text-sm text-[#9b1c1c]">
      {message}
    </p>
  );
}

export { Button };
