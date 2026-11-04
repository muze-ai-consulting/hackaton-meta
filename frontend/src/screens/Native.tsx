import { useEffect, useRef, useState } from "react";
import { BellOff, Check as CheckIcon, Lock, Search, ShieldCheck } from "lucide-react";
import { Button } from "@/components/shell";
import { stepLine } from "@/screens/Check";
import { radar, shield, type ActOut, type AgentAction, type CheckOut, type InvestigateOut, type Mode } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Scenario {
  label: string;
  sender: string;
  text: string;
}

// Made-up messages. The phone numbers are from the UK's reserved range for fiction.
const SCENARIOS: Scenario[] = [
  {
    label: "Parcel fee",
    sender: "+44 7700 900123",
    text: "Royal Mail: Your parcel could not be delivered due to an unpaid shipping fee of £1.45. Pay now to rebook your delivery: royalmail-redelivery-uk.com",
  },
  {
    label: "Bank alert",
    sender: "+44 7700 900456",
    text: "HSBC: Your account is locked after suspicious activity. Verify your card details within 2 hours at hsbc-secure-login.top to restore access.",
  },
  {
    label: "Job offer",
    sender: "+44 7700 900789",
    text: "Hello! I'm Sarah from TalentHub. Flexible remote role rating products, £300-£800 per day. To start, just make a small deposit to activate your account at talenthub-tasks.top. Reply YES.",
  },
  { label: "GP appointment", sender: "+44 7700 900321", text: "Hi, it's Dr Patel's surgery. Your flu jab is booked for Thu 6 Nov at 10:20. Reply CANCEL if you can't make it." },
];

const LINK = /((?:https?:\/\/)?(?:[a-z0-9-]+\.)+[a-z]{2,}(?:\/\S*)?)/gi;
const BAND = {
  scam: { title: "Likely a scam", line: "border-[#d64545]", tone: "bg-[#fdecec] text-[#9b1c1c]" },
  careful: { title: "Be careful", line: "border-[#e0a030]", tone: "bg-[#fbf1dc] text-[#7a4b00]" },
  genuine: { title: "No clear signs of a scam", line: "border-line", tone: "bg-bg text-heading" },
} as const;

function Sim({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-start gap-1.5 self-center rounded-lg bg-white/85 px-2.5 py-1.5 text-[11.5px] leading-snug text-[#3f4650] shadow-[0_1px_0_rgba(0,0,0,0.05)]">
      {children}
    </div>
  );
}

function Tag() {
  return <span className="font-semibold text-[#7a4b00]"> Simulated.</span>;
}

export default function Native({ mode, onCheck, onEvidence, onNetwork }: { mode: Mode; onCheck: () => void; onEvidence: () => void; onNetwork: () => void }) {
  const [message, setMessage] = useState<Scenario | null>(null);
  const [own, setOwn] = useState("");
  const [verdict, setVerdict] = useState<CheckOut | null>(null);
  const [seconds, setSeconds] = useState(0);
  const [probe, setProbe] = useState<InvestigateOut | null>(null);
  const [plan, setPlan] = useState<ActOut | null>(null);
  const [error, setError] = useState("");
  const [working, setWorking] = useState(false);
  const [sheet, setSheet] = useState(false);
  const [openedAnyway, setOpenedAnyway] = useState(false);
  const [done, setDone] = useState<AgentAction[]>([]);
  const run = useRef(0);
  const chat = useRef<HTMLDivElement | null>(null);
  const phone = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    chat.current?.scrollTo({ top: chat.current.scrollHeight, behavior: "smooth" });
  }, [message, verdict, probe, plan, openedAnyway, done, working]);

  // The agent runs by itself when the message arrives: nobody forwards or pastes anything.
  async function receive(s: Scenario) {
    const id = ++run.current;
    if (window.matchMedia("(max-width: 1023px)").matches) phone.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    setMessage(s);
    setVerdict(null);
    setProbe(null);
    setPlan(null);
    setError("");
    setSheet(false);
    setOpenedAnyway(false);
    setDone([]);
    setWorking(true);
    const started = performance.now();
    const investigation = radar.investigate({ text: s.text, images: [], mode }).catch(() => null);
    void investigation.then((p) => id === run.current && setProbe(p));
    try {
      const v = await shield.check({ text: s.text, note: "", images: [], audio: null, mode });
      if (id !== run.current) return;
      setVerdict(v);
      setSeconds((performance.now() - started) / 1000);
      if (v.band === "genuine") return;
      // The agent acts on the verdict without waiting for the slower link checks.
      const a = await radar.act({
        text: s.text,
        images: [],
        verdict: { band: v.band, probability: v.probability, reason: v.reason, action: v.action },
        family: null,
        clues: [],
        mode,
      });
      if (id === run.current) setPlan(a);
      await investigation;
    } catch (err) {
      if (id === run.current) setError((err as Error).message);
    } finally {
      if (id === run.current) setWorking(false);
    }
  }

  const risky = verdict && verdict.band !== "genuine";
  const locked = !verdict || risky; // the link stays locked while the agent checks it
  const alert = plan?.actions.find((a) => a.tool === "alert_contact");
  const alertBody = alert?.body ?? `This looks like a scam and they just tried to open its link: ${verdict?.reason ?? ""} Please check on them.`;
  const buttons = plan?.actions.filter((a) => a.tool !== "alert_contact" && !done.includes(a)) ?? [];
  const parts = message?.text.split(LINK) ?? [];

  return (
    <div className="grid items-start gap-10 lg:grid-cols-[minmax(0,1fr)_340px]">
      <div className="flex flex-col gap-6">
        <div className="flex max-w-[680px] flex-col gap-3">
          <h1 className="m-0 text-[38px] font-bold leading-[1.06] tracking-[-1px] md:text-[52px] md:tracking-[-1.4px]">
            A scam lands in your WhatsApp. An agent stops it right there.
          </h1>
          <p className="m-0 text-lg leading-normal text-muted">
            Nothing to paste or forward. Second Look flags the message as it arrives, checks its links, locks them, and steps in if you're about to fall for it.
          </p>
        </div>

        <div className="flex flex-col gap-2">
          <span className="text-sm font-semibold text-heading">Send a message to this phone</span>
          <div className="flex flex-wrap gap-2">
            {SCENARIOS.map((s) => (
              <button
                key={s.label}
                type="button"
                onClick={() => void receive(s)}
                className={cn(
                  "cursor-pointer rounded-lg border px-3 py-1.5 text-sm font-semibold",
                  message?.text === s.text ? "border-ink bg-ink text-white" : "border-line bg-white text-heading hover:border-ink",
                )}
              >
                {s.label}
              </button>
            ))}
          </div>
          <form
            className="flex flex-wrap gap-2"
            onSubmit={(e) => {
              e.preventDefault();
              if (own.trim()) void receive({ label: "Yours", sender: "Unknown number", text: own.trim() });
            }}
          >
            <input
              value={own}
              onChange={(e) => setOwn(e.target.value)}
              maxLength={1000}
              placeholder="Or write your own, as if a stranger sent it"
              aria-label="Your own message"
              className="min-w-0 flex-1 rounded-lg border border-line bg-white px-3 py-2 text-sm"
            />
            <Button type="submit" size="sm" disabled={!own.trim()}>
              Send
            </Button>
          </form>
        </div>

        <div className="grid gap-3 rounded-xl bg-white/70 p-4 text-sm leading-normal sm:grid-cols-2">
          <div>
            <div className="font-semibold text-heading">Real in this demo</div>
            <p className="m-0 mt-1">The verdict, the link and domain checks, the scam family, and what the agent chooses and writes. All of it runs on Muse Spark 1.3 as you watch.</p>
          </div>
          <div>
            <div className="font-semibold text-heading">Simulated</div>
            <p className="m-0 mt-1">The phone and every action: nothing is locked, muted, blocked or sent. Second Look isn't part of WhatsApp. This shows how it could work if it were.</p>
          </div>
          <p className="m-0 text-muted sm:col-span-2">
            Inside WhatsApp, chats are end-to-end encrypted, so a native version would have to be opt-in and keep that promise. We haven't solved that here. What exists today is the bot on the
            WhatsApp Cloud API, where you forward a message and get the same agent.
          </p>
        </div>

        <p className="m-0 flex flex-wrap gap-x-4 gap-y-1 text-sm font-semibold">
          <button type="button" onClick={onEvidence} className="cursor-pointer underline">
            Tested on 945 real cases
          </button>
          <button type="button" onClick={onNetwork} className="cursor-pointer underline">
            How early warning would work
          </button>
          <button type="button" onClick={onCheck} className="cursor-pointer underline">
            Check a message yourself
          </button>
        </p>
      </div>

      <div ref={phone} className="mx-auto w-[316px] scroll-mt-4 lg:sticky lg:top-6">
        <div className="rounded-[40px] bg-[#16181d] p-2.5 shadow-[0_30px_60px_-20px_rgba(20,24,40,0.45)]">
          <div className="relative flex h-[640px] flex-col overflow-hidden rounded-[32px] bg-[#e7ece6]">
            <div className="flex items-center gap-2 bg-[#1f6f5c] px-3.5 pb-2.5 pt-5 text-white">
              <div className="grid size-8 place-items-center rounded-full bg-white/15 text-sm font-semibold">?</div>
              <div className="min-w-0 flex-1 leading-tight">
                <div className="truncate text-[14px] font-semibold">{message?.sender ?? "New message"}</div>
                <div className="text-[11px] text-white/75">{risky ? "Muted by Second Look (simulated)" : "Not in your contacts"}</div>
              </div>
              <ShieldCheck className={cn("size-5", working && "animate-pulse")} aria-label="Second Look is on" />
            </div>

            <div ref={chat} className="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto p-2.5" aria-live="polite">
              {!message && (
                <div className="m-auto max-w-[220px] text-center text-[13px] leading-snug text-[#5b6470]">
                  <ShieldCheck className="mx-auto mb-2 size-7" aria-hidden="true" />
                  Second Look is on. Choose a message on the left and watch what happens when it arrives.
                </div>
              )}

              {message && (
                <div className={cn("max-w-[90%] shrink-0 self-start overflow-hidden rounded-2xl rounded-bl-md border-2 bg-white", verdict ? BAND[verdict.band].line : "border-transparent")}>
                  <p className="m-0 px-3 py-2 text-[13px] leading-snug text-[#16181d]">
                    {parts.map((p, i) =>
                      i % 2 === 0 ? (
                        p
                      ) : locked ? (
                        <button key={i} type="button" onClick={() => setSheet(true)} className="inline cursor-pointer break-all text-left text-[#7b8590] line-through">
                          <Lock className="mr-0.5 inline size-3 align-[-1px]" aria-hidden="true" />
                          {p}
                        </button>
                      ) : (
                        <span key={i} className="break-all text-[#1a6fb5] underline">
                          {p}
                        </span>
                      ),
                    )}
                  </p>
                  {!verdict && !error && (
                    <div className="flex items-center gap-1.5 bg-bg px-3 py-1.5 text-[11.5px] font-semibold text-muted">
                      <Search className="size-3 animate-pulse" aria-hidden="true" /> Second Look is checking…
                    </div>
                  )}
                  {verdict && (
                    <div className={cn("px-3 py-2 text-[12px] leading-snug", BAND[verdict.band].tone)}>
                      <div className="font-bold">
                        {BAND[verdict.band].title} · {Math.round(verdict.probability * 100)}% · {seconds.toFixed(1)} s
                      </div>
                      <div className="mt-0.5 text-[#16181d]">{verdict.reason}</div>
                      <div className="mt-1 font-semibold text-[#16181d]">{verdict.action}</div>
                    </div>
                  )}
                </div>
              )}

              {error && <Sim>{error}</Sim>}

              {risky && (
                <Sim>
                  <BellOff className="mt-0.5 size-3 shrink-0" aria-hidden="true" />
                  <span>
                    The agent locked the link and muted this sender.
                    <Tag />
                  </span>
                </Sim>
              )}

              {risky &&
                probe?.investigation?.steps.map((s, i) => (
                  <Sim key={i}>
                    <Search className="mt-0.5 size-3 shrink-0" aria-hidden="true" />
                    <span className="break-words">{stepLine(s).text}</span>
                  </Sim>
                ))}

              {risky && probe?.family && (
                <Sim>
                  <span>
                    👥 <strong>{probe.family.name}:</strong> {probe.family.reports} people reported this kind of scam on Reddit since September.
                  </span>
                </Sim>
              )}

              {openedAnyway && (
                <div className="self-center rounded-xl bg-[#fdecec] px-3 py-2 text-[12px] leading-snug text-[#16181d]">
                  <div className="font-bold text-[#9b1c1c]">You tried to open it, so the agent told Ana</div>
                  <p className="m-0 mt-1">"{alertBody}"</p>
                  <p className="m-0 mt-1 font-semibold text-[#7a4b00]">Simulated. Ana is made up and nothing was sent.</p>
                </div>
              )}

              {done.map((a) => (
                <div key={a.tool} className="self-center rounded-xl bg-ok-soft px-3 py-2 text-[12px] leading-snug text-[#16181d]">
                  <div className="flex items-center gap-1 font-bold text-ok">
                    <CheckIcon className="size-3.5" aria-hidden="true" /> {a.title}
                  </div>
                  {a.tool === "draft_report" ? (
                    <p className="m-0 mt-1 whitespace-pre-wrap">
                      <strong>{a.subject}</strong>
                      {"\n"}
                      {a.body}
                    </p>
                  ) : (
                    <p className="m-0 mt-1">{a.heads_up ?? a.body}</p>
                  )}
                  <p className="m-0 mt-1 font-semibold text-[#7a4b00]">
                    {a.tool === "draft_report" ? "Written by the agent. Not sent: you'd send it yourself." : "Simulated. Nothing was changed or sent."}
                  </p>
                </div>
              ))}

              {risky && working && (
                <Sim>
                  <ShieldCheck className="mt-0.5 size-3 shrink-0 animate-pulse" aria-hidden="true" /> The agent is working…
                </Sim>
              )}
            </div>

            {buttons.length > 0 ? (
              <div className="flex shrink-0 flex-wrap gap-1.5 bg-[#f4f6f4] p-2">
                {buttons.map((a) => (
                  <button
                    key={a.tool}
                    type="button"
                    onClick={() => setDone((d) => [...d, a])}
                    className="min-w-[45%] flex-1 cursor-pointer truncate rounded-full bg-[#1f6f5c] px-3 py-1.5 text-[12px] font-semibold text-white"
                  >
                    {a.tool === "share_pattern" ? "Warn others" : a.tool === "block_sender" ? "Block sender" : "Write my report"}
                  </button>
                ))}
              </div>
            ) : (
              <div className="flex shrink-0 items-center gap-2 bg-[#f4f6f4] px-2.5 py-2">
                <div className="h-7 flex-1 rounded-full bg-white px-3 text-[11.5px] leading-7 text-[#9aa3ad]">Message</div>
              </div>
            )}

            {sheet && (
              <div className="absolute inset-0 flex items-end bg-black/45" role="dialog" aria-label="Link locked">
                <div className="flex w-full flex-col gap-2 rounded-t-3xl bg-white p-4">
                  <div className="text-[16px] font-bold text-[#9b1c1c]">{verdict ? "Wait. This link looks dangerous." : "Still checking this link."}</div>
                  <p className="m-0 text-[13px] leading-snug text-[#16181d]">{verdict ? verdict.reason : "Second Look keeps links locked until the check is done."}</p>
                  <button type="button" onClick={() => setSheet(false)} className="cursor-pointer rounded-full bg-[#1f6f5c] px-3 py-2 text-[13px] font-semibold text-white">
                    Go back
                  </button>
                  {verdict && !openedAnyway && (
                    <button
                      type="button"
                      onClick={() => {
                        setOpenedAnyway(true);
                        setSheet(false);
                      }}
                      className="cursor-pointer rounded-full px-3 py-2 text-[13px] font-semibold text-muted"
                    >
                      Open anyway
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
        <p className="m-0 mt-3 text-center text-sm text-muted">Concept prototype. Not a WhatsApp feature.</p>
      </div>
    </div>
  );
}
