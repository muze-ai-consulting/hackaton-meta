import { useEffect, useRef, useState } from "react";
import { AlertTriangle, Ban, Bell, Check as CheckIcon, Copy, FileText, Globe, ImagePlus, Link2, Mic, RotateCcw, Search, Send, Share2, ShieldAlert, ShieldQuestion, ShieldCheck, Square, Upload, Users, Waypoints, X } from "lucide-react";
import { Card, CardTitle } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import PhoneDemo from "@/components/PhoneDemo";
import { Button, ErrorNote, PageTitle } from "@/components/shell";
import { radar, shield, type Band, type CheckOut, type Evidence, type Clue, type ActOut, type AgentAction, type InvestigateOut, type Mode, type ToolStep } from "@/lib/api";
import { cn, fileToDataUrl, pct } from "@/lib/utils";

const MAX_IMAGES = 3;
const MAX_AUDIO_BYTES = 10 * 1024 * 1024;

interface Example {
  label: string;
  kind: string;
  text?: string;
  note?: string;
  audio?: string;
  image?: string;
}

// Made-up examples for the demo (not taken from the validation set).
const EXAMPLES: Example[] = [
  {
    label: "Parcel fee text",
    kind: "SMS",
    text: "Royal Mail: Your parcel could not be delivered due to an unpaid shipping fee of £1.45. Pay now to rebook your delivery: royalmail-redelivery-uk.com",
  },
  {
    label: "Already paid",
    kind: "SMS",
    text: "HSBC-Alert: Your account is locked. Verify your card details now at hsbc-secure-login.top to restore access.",
    note: "I already paid the fee and typed my card number",
  },
  {
    label: "Marketplace buyer",
    kind: "Screenshot",
    image: "static/examples/marketplace-chat.png",
    note: "A buyer on Marketplace sent me this about my table",
  },
  { label: "Call from 'the bank'", kind: "Voice note", audio: "static/examples/bank-call.wav", note: "Someone called me saying they were from my bank" },
  {
    label: "Remote job offer",
    kind: "WhatsApp",
    text: "Hello! I'm Sarah from TalentHub recruiting. We have a flexible remote role rating products online, £300-£800 per day. No experience needed. To get started you only need to complete 3 tasks and make a small deposit to activate your account. Reply YES to continue.",
  },
  {
    label: "GP appointment",
    kind: "SMS",
    text: "Hi, it's Dr Patel's surgery. Your flu jab is booked for Thu 6 Nov at 10:20. Reply CANCEL if you can't make it.",
  },
];

const BAND: Record<Band, { title: string; tone: string; bar: string; icon: typeof ShieldAlert }> = {
  scam: { title: "Likely a scam", tone: "bg-[#fdecec] text-[#9b1c1c]", bar: "bg-[#d64545]", icon: ShieldAlert },
  careful: { title: "Be careful", tone: "bg-[#fbf1dc] text-[#7a4b00]", bar: "bg-[#e0a030]", icon: AlertTriangle },
  genuine: { title: "No clear signs of a scam", tone: "bg-bg text-heading", bar: "bg-muted", icon: ShieldQuestion },
};

function blobToDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(new Error("Could not read that audio."));
    reader.readAsDataURL(blob);
  });
}

/** When the shield says "Likely a scam", how often it was one, on the preregistered attempt 2. */
export function precision(evidence: Evidence | null) {
  const b = evidence?.round2.bands.scam;
  return b ? { share: b.scam / (b.scam + b.legit), n: b.scam + b.legit } : null;
}

export default function Check({
  mode,
  evidence,
  onEvidence,
  onCampaigns,
  onNetwork,
}: {
  mode: Mode;
  evidence: Evidence | null;
  onEvidence: () => void;
  onCampaigns: () => void;
  onNetwork: () => void;
}) {
  const [text, setText] = useState("");
  const [note, setNote] = useState("");
  const [images, setImages] = useState<string[]>([]);
  const [audio, setAudio] = useState<string | null>(null);
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<CheckOut | null>(null);
  const [probe, setProbe] = useState<InvestigateOut | null>(null);
  const [probing, setProbing] = useState(false);
  const [plan, setPlan] = useState<ActOut | null>(null);
  const [planning, setPlanning] = useState(false);
  const [checked, setChecked] = useState(""); // the text as it was when the person pressed "Check it"
  const recorder = useRef<MediaRecorder | null>(null);
  const imageInput = useRef<HTMLInputElement | null>(null);
  const audioInput = useRef<HTMLInputElement | null>(null);
  const resultRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (result) resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [result]);

  // Once the verdict and the investigation are in, the response agent prepares what it could do. Nothing runs by itself.
  const agentContext = useRef("");
  const planned = useRef<CheckOut | null>(null);
  useEffect(() => {
    if (!result || busy || probing || planned.current === result || result.band === "genuine") return;
    planned.current = result;
    setPlanning(true);
    radar
      .act({
        text: agentContext.current || result.transcript || "",
        images,
        verdict: { band: result.band, probability: result.probability, reason: result.reason, action: result.action },
        family: probe?.family ?? null,
        clues: probe?.investigation?.clues ?? [],
        mode,
      })
      .then(setPlan)
      .catch(() => setPlan(null))
      .finally(() => setPlanning(false));
  }, [result, busy, probing, probe, images, mode]);

  const ready = Boolean(text.trim() || note.trim() || images.length || audio);
  const p = precision(evidence);

  async function addImages(files: File[]) {
    try {
      const room = MAX_IMAGES - images.length;
      const added = await Promise.all(files.filter((f) => f.type.startsWith("image/")).slice(0, room).map((f) => fileToDataUrl(f, 1024)));
      setImages((prev) => [...prev, ...added].slice(0, MAX_IMAGES));
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function addAudio(blob: Blob) {
    if (blob.size > MAX_AUDIO_BYTES) {
      setError("That voice note is too long. Keep it under 10 MB.");
      return;
    }
    setAudio(await blobToDataUrl(blob));
  }

  async function toggleRecording() {
    if (recording) {
      recorder.current?.stop();
      return;
    }
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream);
      const chunks: Blob[] = [];
      rec.ondataavailable = (e) => chunks.push(e.data);
      rec.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        setRecording(false);
        void addAudio(new Blob(chunks, { type: rec.mimeType }));
      };
      recorder.current = rec;
      rec.start();
      setRecording(true);
    } catch {
      setError("We couldn't use your microphone. You can upload a voice note instead.");
    }
  }

  async function loadExample(ex: Example) {
    setResult(null);
    setProbe(null);
    setPlan(null);
    setError("");
    setText(ex.text ?? "");
    setNote(ex.note ?? "");
    setImages(ex.image ? [await fileToDataUrl(new File([await (await fetch(ex.image)).blob()], "example.png", { type: "image/png" }), 1024)] : []);
    setAudio(ex.audio ? await blobToDataUrl(await (await fetch(ex.audio)).blob()) : null);
  }

  function reset() {
    setText("");
    setNote("");
    setImages([]);
    setAudio(null);
    setResult(null);
    setProbe(null);
    setPlan(null);
    setError("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // The investigation runs apart from the verdict, which comes only from the tested prompt. Without a voice note both
  // start together; with one, the investigation waits for the transcript.
  async function investigate(content: string) {
    if (!content.trim() && !images.length) return;
    setProbing(true);
    try {
      setProbe(await radar.investigate({ text: content, images, mode }));
    } catch {
      setProbe(null);
    } finally {
      setProbing(false);
    }
  }

  async function run() {
    setError("");
    setBusy(true);
    setProbe(null);
    setPlan(null);
    setChecked(text);
    const context = [note, text].filter((s) => s.trim()).join("\n\n");
    agentContext.current = context;
    const early = audio ? null : investigate(context);
    try {
      const out = await shield.check({ text, note, images, audio, mode });
      setResult(out);
      if (audio) agentContext.current = [context, out.transcript].filter((s) => s.trim()).join("\n\n");
      if (audio) void investigate([context, out.transcript].filter((s) => s.trim()).join("\n\n"));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
    await early;
  }

  return (
    <>
      <div className="grid items-start gap-10 lg:grid-cols-[minmax(0,1fr)_300px]">
        <div className="flex flex-col gap-7">
          <div className="flex max-w-[680px] flex-col gap-3">
            <h1 className="m-0 text-[38px] font-bold leading-[1.06] tracking-[-1px] md:text-[52px] md:tracking-[-1.4px]">
              Got a message that feels off? Check it before you act.
            </h1>
            <p className="m-0 text-lg leading-normal text-muted">
              Paste the text, add a screenshot or a voice note of the call. In seconds you'll know if it looks like a scam, why, and the one thing to do
              now.
            </p>
          </div>
          <Card className="flex flex-col gap-5 p-5 sm:p-7">
            <div className="flex flex-col gap-2">
              <span className="text-sm text-muted">No message at hand? Try one (made up, based on common scams):</span>
              <div className="flex flex-wrap gap-2">
                {EXAMPLES.map((ex) => (
                  <button
                    key={ex.label}
                    type="button"
                    onClick={() => void loadExample(ex)}
                    className="flex cursor-pointer items-baseline gap-1.5 rounded-lg border border-line bg-white px-3 py-1.5 text-sm hover:border-ink"
                  >
                    <span className="font-semibold text-heading">{ex.label}</span>
                    <span className="text-xs text-muted">{ex.kind}</span>
                  </button>
                ))}
              </div>
            </div>
          <label className="flex flex-col gap-2">
            <span className="text-sm font-semibold text-heading">The message</span>
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              onPaste={(e) => {
                const files = Array.from(e.clipboardData.files);
                if (files.length) {
                  e.preventDefault();
                  void addImages(files);
                }
              }}
              placeholder="Paste the text, email or chat here. You can also paste a screenshot."
              className="min-h-36 text-base"
              maxLength={6000}
            />
          </label>

          <label className="flex flex-col gap-2">
            <span className="text-sm font-semibold text-heading">
              What happened? <span className="font-normal text-muted">(optional)</span>
            </span>
            <Input value={note} onChange={(e) => setNote(e.target.value)} placeholder="e.g. A buyer on Marketplace sent me this link" maxLength={500} />
          </label>

          <div className="flex flex-wrap gap-3">
            <Button variant="outline" size="sm" disabled={images.length >= MAX_IMAGES} onClick={() => imageInput.current?.click()}>
              <ImagePlus /> Add screenshot
            </Button>
            <Button variant={recording ? "default" : "outline"} size="sm" onClick={toggleRecording} aria-pressed={recording}>
              {recording ? <Square /> : <Mic />} {recording ? "Stop recording" : "Record voice note"}
            </Button>
            <Button variant="outline" size="sm" onClick={() => audioInput.current?.click()}>
              <Upload /> Upload audio
            </Button>
            <input ref={imageInput} type="file" accept="image/*" multiple hidden onChange={(e) => void addImages(Array.from(e.target.files ?? []))} />
            <input
              ref={audioInput}
              type="file"
              accept="audio/*,.opus,.ogg,.m4a"
              hidden
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) void addAudio(f);
                e.target.value = "";
              }}
            />
          </div>

          {(images.length > 0 || audio) && (
            <div className="flex flex-wrap items-center gap-3">
              {images.map((src, i) => (
                <div key={i} className="relative">
                  <img src={src} alt={`Screenshot ${i + 1}`} className="size-20 rounded-lg object-cover" />
                  <button
                    type="button"
                    aria-label={`Remove screenshot ${i + 1}`}
                    onClick={() => setImages(images.filter((_, j) => j !== i))}
                    className="absolute -right-2 -top-2 grid size-6 cursor-pointer place-items-center rounded-full bg-ink text-white"
                  >
                    <X className="size-3.5" />
                  </button>
                </div>
              ))}
              {audio && (
                <div className="flex items-center gap-2 rounded-xl bg-bg p-2">
                  <audio controls src={audio} className="h-9 max-w-[240px]" />
                  <Button variant="ghost" size="icon" aria-label="Remove voice note" onClick={() => setAudio(null)}>
                    <X />
                  </Button>
                </div>
              )}
            </div>
          )}

          <div className="flex flex-wrap items-center gap-4">
            <Button disabled={!ready || busy || recording} onClick={run}>
              <Send /> {busy ? "Checking…" : "Check it"}
            </Button>
            {mode === "mock" && <span className="text-sm text-muted">Demo mode: answers are placeholders, not real verdicts.</span>}
          </div>
          {error && <ErrorNote message={error} />}
          </Card>
        </div>

        <div className="hidden lg:sticky lg:top-6 lg:block">
          <PhoneDemo />
        </div>
      </div>

      {busy && <div className="skeleton h-48" aria-label="Checking" />}

      {result && !busy && (
        <div ref={resultRef} className="scroll-mt-6">
          <Result result={result} precision={p} onEvidence={onEvidence} onReset={reset} />
          <div className="mt-6">
            <Investigation probe={probe} probing={probing} message={checked} onCampaigns={onCampaigns} />
          </div>
          <div className="mt-6">
            <AgentActions plan={plan} planning={planning} onNetwork={onNetwork} />
          </div>
        </div>
      )}

      {p && !result && (
        <p className="m-0 text-sm leading-normal">
          Tested on {evidence!.round2.scored.n} real "is this a scam?" questions posted after the model was released: when it says{" "}
          <strong>Likely a scam</strong>, it was one <strong>{pct(p.share)}</strong> of the time.{" "}
          <button type="button" onClick={onEvidence} className="cursor-pointer font-semibold underline">
            How we measured it
          </button>
        </p>
      )}
    </>
  );
}

function Result({
  result,
  precision: p,
  onEvidence,
  onReset,
}: {
  result: CheckOut;
  precision: { share: number; n: number } | null;
  onEvidence: () => void;
  onReset: () => void;
}) {
  const b = BAND[result.band];
  const Icon = b.icon;
  const warning = `${b.title}: ${result.reason} What to do: ${result.action} (checked with Second Look)`;

  async function share() {
    if (navigator.share) {
      try {
        await navigator.share({ text: warning });
        return;
      } catch {
        return; // the person closed the share sheet
      }
    }
    window.open(`https://wa.me/?text=${encodeURIComponent(warning)}`, "_blank", "noopener");
  }

  return (
    <Card className="flex flex-col gap-5 overflow-hidden p-0" aria-live="polite">
      <div className={cn("flex items-center gap-3 px-5 py-4 sm:px-7", b.tone)}>
        <Icon className="size-7 shrink-0" aria-hidden="true" />
        <h2 className="m-0 text-2xl font-bold text-inherit">{b.title}</h2>
        <span className="ml-auto text-sm font-semibold">{pct(result.probability)} scam likelihood</span>
      </div>
      <div className="flex flex-col gap-5 px-5 pb-6 sm:px-7">
        <div className="h-2 rounded-full bg-bg" role="presentation">
          <div className={cn("h-2 rounded-full", b.bar)} style={{ width: `${Math.max(3, result.probability * 100)}%` }} />
        </div>
        <div className="grid gap-5 md:grid-cols-2">
          <div>
            <div className="text-sm font-semibold text-muted">Why</div>
            <p className="m-0 mt-1 text-lg leading-snug text-heading">{result.reason}</p>
          </div>
          <div>
            <div className="text-sm font-semibold text-muted">What to do now</div>
            <p className="m-0 mt-1 text-lg font-semibold leading-snug text-heading">{result.action}</p>
          </div>
        </div>
        {result.transcript && (
          <details className="rounded-xl bg-bg px-4 py-3 text-sm">
            <summary className="cursor-pointer font-semibold">What we heard in the voice note</summary>
            <p className="m-0 mt-2 leading-normal">{result.transcript}</p>
          </details>
        )}
        {result.band === "genuine" && (
          <p className="m-0 text-sm text-muted">
            This doesn't mean it's safe. If it asks for money, codes or passwords, contact the company through its official app or number.
          </p>
        )}
        <div className="flex flex-wrap items-center gap-3">
          {result.band !== "genuine" && (
            <Button onClick={share}>
              <Share2 /> Warn someone
            </Button>
          )}
          <Button variant="outline" onClick={onReset}>
            <RotateCcw /> Check something else
          </Button>
        </div>
        <p className="m-0 text-xs leading-normal text-muted">
          Muse Spark 1.3{result.transcript ? " and Muse Voice Transcribe" : ""} · {result.mode === "mock" ? "demo mode" : `US$ ${result.usd.toFixed(4)}`}
          {p && (
            <>
              {" "}
              · In real tests, {pct(p.share)} of "Likely a scam" answers were scams.{" "}
              <button type="button" onClick={onEvidence} className="cursor-pointer underline">
                How we measured it
              </button>
            </>
          )}
        </p>
      </div>
    </Card>
  );
}

const ACTION_ICON = { alert_contact: Bell, draft_report: FileText, block_sender: Ban, share_pattern: Waypoints } as const;

function doneLine(a: AgentAction): string {
  if (a.tool === "alert_contact") return `Simulated: alert delivered to ${a.to}. Nothing was really sent.`;
  if (a.tool === "block_sender") return "Simulated: sender blocked. Nothing was changed.";
  if (a.tool === "share_pattern")
    return `Simulated: added to the network${a.report_number ? ` as report #${a.report_number} of ${a.family}` : ""}. Nobody was contacted.`;
  return "Marked as done. We never send it for you: copy it and send it yourself.";
}

function ActionCard({ action, done, onDo }: { action: AgentAction; done: boolean; onDo: () => void }) {
  const Icon = ACTION_ICON[action.tool];
  const [copied, setCopied] = useState(false);
  const report = action.tool === "draft_report";
  async function copy() {
    await navigator.clipboard.writeText(`${action.subject}\n\n${action.body}`);
    setCopied(true);
  }
  return (
    <li className={cn("flex flex-col gap-3 rounded-xl border p-4", done ? "border-ok bg-ok-soft" : "border-line bg-white")}>
      <div className="flex items-start gap-3">
        <Icon className="mt-0.5 size-5 shrink-0" aria-hidden="true" />
        <div className="min-w-0">
          <div className="font-semibold text-heading">{action.title}</div>
          <p className="m-0 text-sm text-muted">{action.why}</p>
        </div>
      </div>
      {report && action.subject && <div className="text-sm font-semibold">Subject: {action.subject}</div>}
      <p className="m-0 whitespace-pre-wrap rounded-lg bg-bg px-3 py-2 text-sm leading-normal">{action.body}</p>
      {done && action.heads_up && (
        <div className="rounded-lg bg-white px-3 py-2 text-sm leading-normal">
          <div className="text-xs font-semibold text-muted">In production, people who haven't seen it yet would get</div>
          {action.heads_up}
        </div>
      )}
      {done ? (
        <div className="flex flex-col gap-2">
          <p className="m-0 flex gap-1.5 text-sm font-semibold text-ok" role="status">
            <CheckIcon className="mt-0.5 size-4 shrink-0" aria-hidden="true" /> {action.auto ? "You already acted, so the agent didn't wait. " : ""}
            {doneLine(action)}
          </p>
          {report && (
            <Button size="sm" variant="outline" className="self-start" onClick={copy}>
              <Copy /> {copied ? "Copied" : "Copy report"}
            </Button>
          )}
        </div>
      ) : (
        <div className="flex flex-wrap gap-2">
          {report && (
            <Button size="sm" variant="outline" onClick={copy}>
              <Copy /> {copied ? "Copied" : "Copy report"}
            </Button>
          )}
          <Button size="sm" onClick={onDo}>
            {report ? "Mark as done" : "Approve (simulated)"}
          </Button>
        </div>
      )}
    </li>
  );
}

function AgentActions({ plan, planning, onNetwork }: { plan: ActOut | null; planning: boolean; onNetwork: () => void }) {
  const [done, setDone] = useState<number[]>([]);
  useEffect(() => setDone((plan?.actions ?? []).flatMap((a, i) => (a.auto ? [i] : []))), [plan]);
  if (planning) {
    return (
      <Card className="flex items-center gap-3 p-5 text-sm text-muted sm:p-7" aria-live="polite">
        <ShieldCheck className="size-5 animate-pulse" aria-hidden="true" /> The agent is preparing what it could do for you…
      </Card>
    );
  }
  if (!plan?.actions.length) return null;
  const all = plan.actions.map((_, i) => i);
  return (
    <Card className="flex flex-col gap-4 p-5 sm:p-7" aria-live="polite">
      <div className="flex flex-wrap items-center gap-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <ShieldCheck className="size-5" aria-hidden="true" /> What the agent prepared for you
        </CardTitle>
        <span className="rounded-full bg-[#fbf1dc] px-2.5 py-1 text-xs font-semibold text-[#7a4b00]">Demo: simulated, nothing is really sent</span>
        {done.length < all.length && (
          <Button size="sm" variant="outline" className="sm:ml-auto" onClick={() => setDone(all)}>
            Approve all
          </Button>
        )}
      </div>
      <ul className="m-0 grid list-none gap-3 p-0 lg:grid-cols-2">
        {plan.actions.map((a, i) => (
          <ActionCard key={a.tool} action={a} done={done.includes(i)} onDo={() => setDone((d) => [...d, i])} />
        ))}
      </ul>
      <p className="m-0 text-xs text-muted">
        An agent on Muse Spark 1.3 chose these with function calling, and each one waits for your approval, unless you've already paid: then the alert to your contact runs at once. Ana is a made-up contact.{" "}
        <button type="button" onClick={onNetwork} className="cursor-pointer underline">
          See how early warning would work
        </button>
      </p>
    </Card>
  );
}

const SIGNAL = {
  risky: "bg-[#fdecec] text-[#9b1c1c]",
  reassuring: "bg-ok-soft text-ok",
  neutral: "bg-bg text-muted",
} as const;

const TREND_LABEL = { rising: "Rising", falling: "Falling", steady: "Steady" } as const;

/** One line per tool the agent used, in plain words. */
export function stepLine(s: ToolStep): { icon: typeof Link2; text: string } {
  const r = s.result as Record<string, unknown>;
  if (s.tool === "inspect_link") {
    const hops = (r.hops as { domain: string }[] | undefined) ?? [];
    const path = hops.map((h) => h.domain).join(" → ");
    if (r.error) return { icon: Link2, text: `Followed ${s.input.url}: ${String(r.error)}` };
    return { icon: Link2, text: `Followed the link without opening it: ${path || s.input.url}` };
  }
  if (s.tool === "domain_registration") {
    if (r.error) return { icon: Globe, text: `Looked up who registered ${String(r.domain ?? s.input.domain)}: ${String(r.error)}` };
    if (r.registered === false) return { icon: Globe, text: `${String(r.domain)} has no public registration record` };
    const age = typeof r.age_days === "number" ? r.age_days : null;
    const when = age === null ? "" : age < 60 ? `, ${age} days ago` : `, ${Math.round(age / 365)} years ago`;
    return { icon: Globe, text: `${String(r.domain)} was registered on ${String(r.registered_on)}${when}${r.registrar ? ` (${String(r.registrar)})` : ""}` };
  }
  return { icon: Search, text: s.tool };
}

const MARK = {
  risky: "bg-[#fdecec] text-[#9b1c1c] decoration-[#d64545]",
  reassuring: "bg-ok-soft text-ok decoration-ok",
  neutral: "bg-bg decoration-muted",
} as const;

/** The message with each quoted clue marked in place and numbered like its clue. */
function MarkedMessage({ text, clues }: { text: string; clues: Clue[] }) {
  const lower = text.toLowerCase();
  const spans: { start: number; end: number; n: number; signal: Clue["signal"] }[] = [];
  clues.forEach((c, i) => {
    if (!c.quote) return;
    const start = lower.indexOf(c.quote.toLowerCase());
    const end = start + c.quote.length;
    if (start < 0 || spans.some((s) => start < s.end && end > s.start)) return;
    spans.push({ start, end, n: i + 1, signal: c.signal });
  });
  if (!spans.length) return null;
  spans.sort((a, b) => a.start - b.start);
  const parts: React.ReactNode[] = [];
  let at = 0;
  for (const s of spans) {
    parts.push(text.slice(at, s.start));
    parts.push(
      <mark key={s.n} className={cn("rounded px-0.5 underline decoration-2 underline-offset-4", MARK[s.signal])}>
        {text.slice(s.start, s.end)}
        <sup className="ml-0.5 text-[10px] font-bold no-underline">{s.n}</sup>
      </mark>,
    );
    at = s.end;
  }
  parts.push(text.slice(at));
  return <p className="m-0 whitespace-pre-wrap rounded-xl border border-line bg-white px-4 py-3 text-[15px] leading-relaxed">{parts}</p>;
}

function Investigation({
  probe,
  probing,
  message,
  onCampaigns,
}: {
  probe: InvestigateOut | null;
  probing: boolean;
  message: string;
  onCampaigns: () => void;
}) {
  if (probing) {
    return (
      <Card className="flex items-center gap-3 p-5 text-sm text-muted sm:p-7" aria-live="polite">
        <Search className="size-5 animate-pulse" aria-hidden="true" /> Checking the links and looking for this pattern in past reports…
      </Card>
    );
  }
  const inv = probe?.investigation;
  const fam = probe?.family;
  const checked = inv && !inv.skipped && (inv.steps.length > 0 || inv.clues.length > 0);
  if (!checked && !fam) return null;
  return (
    <div className="grid gap-6 lg:grid-cols-2" aria-live="polite">
      {checked && (
        <Card className="flex flex-col gap-4 p-5 sm:p-7">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Search className="size-5" aria-hidden="true" /> {inv.steps.length ? "What we checked" : "What we found"}
          </CardTitle>
          {inv.steps.length > 0 && (
            <ul className="m-0 flex list-none flex-col gap-2 p-0 text-sm">
              {inv.steps.map((s, i) => {
                const { icon: I, text } = stepLine(s);
                return (
                  <li key={i} className="flex gap-2 break-all">
                    <I className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden="true" /> {text}
                  </li>
                );
              })}
            </ul>
          )}
          <MarkedMessage text={message} clues={inv.clues} />
          {inv.clues.length > 0 && (
            <ul className="m-0 flex list-none flex-col gap-2 p-0">
              {inv.clues.map((c, i) => (
                <li key={i} className={cn("flex gap-2 rounded-xl px-4 py-3 text-sm", SIGNAL[c.signal])}>
                  <span className="font-bold">{i + 1}</span>
                  <span>
                    <strong>{c.label}.</strong> {c.detail}
                  </span>
                </li>
              ))}
            </ul>
          )}
          <p className="m-0 text-xs text-muted">An agent on Muse Spark 1.3 chose which checks to run. These clues don't change the score above.</p>
        </Card>
      )}
      {fam && (
        <Card className="flex flex-col gap-4 p-5 sm:p-7">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Users className="size-5" aria-hidden="true" /> {fam.fit === "strong" ? "Seen before" : "Looks similar to"}: {fam.name}
          </CardTitle>
          <p className="m-0 text-[15px] leading-normal">{fam.what}</p>
          <p className="m-0 text-sm">
            <strong>{fam.reports} people</strong> reported this kind of scam on Reddit since September
            {fam.trend !== "steady" && (
              <>
                {" "}
                · <strong>{TREND_LABEL[fam.trend].toLowerCase()}</strong> last month
              </>
            )}
            {fam.top_brands.length > 0 && <> · often posing as {fam.top_brands.slice(0, 3).map((b) => b.brand).join(", ")}</>}
          </p>
          {fam.spot.length > 0 && (
            <ul className="m-0 flex flex-col gap-1 pl-5 text-sm">
              {fam.spot.map((s) => (
                <li key={s}>{s}</li>
              ))}
            </ul>
          )}
          <button type="button" onClick={onCampaigns} className="cursor-pointer self-start text-sm font-semibold underline">
            See what's going around
          </button>
        </Card>
      )}
    </div>
  );
}
