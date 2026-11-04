import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function Logo() {
  return <img src="static/brand/second-look-wordmark-light-bg.svg" alt="Second Look" className="h-[30px] w-auto" />;
}

export function Header({
  onHome,
  onCheck,
  onCampaigns,
  onNetwork,
  onEvidence,
}: {
  onHome: () => void;
  onCheck: () => void;
  onCampaigns: () => void;
  onNetwork: () => void;
  onEvidence: () => void;
}) {
  return (
    <header className="relative border-b border-white/40 bg-white/70 backdrop-blur-md">
      <div className="mx-auto flex min-h-16 max-w-[1180px] flex-wrap items-center justify-between gap-x-4 gap-y-2 px-6 py-3">
        <button type="button" onClick={onHome} className="cursor-pointer" aria-label="Home">
          <Logo />
        </button>
        <nav aria-label="Main" className="flex flex-wrap items-center gap-5 text-[15px] font-semibold">
          <button type="button" onClick={onCheck} className="cursor-pointer hover:text-heading">
            Check a message
          </button>
          <button type="button" onClick={onCampaigns} className="cursor-pointer hover:text-heading">
            What's going around
          </button>
          <button type="button" onClick={onNetwork} className="cursor-pointer hover:text-heading">
            Early warning
          </button>
          <button type="button" onClick={onEvidence} className="cursor-pointer hover:text-heading">
            How we measured it
          </button>
        </nav>
      </div>
    </header>
  );
}

const STEPS = ["Your versions", "Your audience", "Result"];

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
export function ErrorNote({ message }: { message: string }) {
  return (
    <p role="alert" className="m-0 rounded-xl bg-[#fdecec] px-4 py-3 text-sm text-[#9b1c1c]">
      {message}
    </p>
  );
}

export { Button };
