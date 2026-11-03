import { useEffect, useRef, useState } from "react";
import { AlertTriangle, ImagePlus, Mic, RotateCcw, Send, Share2, ShieldAlert, ShieldCheck, Square, Upload, X } from "lucide-react";
import { Card, CardTitle } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { Button, ErrorNote, PageTitle } from "@/components/shell";
import { shield, type Band, type CheckOut, type Evidence, type Mode } from "@/lib/api";
import { cn, fileToDataUrl, pct } from "@/lib/utils";

const MAX_IMAGES = 3;
const MAX_AUDIO_BYTES = 10 * 1024 * 1024;

interface Example {
  label: string;
  kind: string;
  text?: string;
  note?: string;
  audio?: string;
}

// Made-up examples for the demo (not taken from the validation set).
const EXAMPLES: Example[] = [
  {
    label: "Parcel fee text",
    kind: "SMS",
    text: "Royal Mail: Your parcel could not be delivered due to an unpaid shipping fee of £1.45. Pay now to rebook your delivery: royalmail-redelivery-uk.com",
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
  genuine: { title: "No clear signs of a scam", tone: "bg-ok-soft text-ok", bar: "bg-ok", icon: ShieldCheck },
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

export default function Check({ mode, evidence, onEvidence }: { mode: Mode; evidence: Evidence | null; onEvidence: () => void }) {
  const [text, setText] = useState("");
  const [note, setNote] = useState("");
  const [images, setImages] = useState<string[]>([]);
  const [audio, setAudio] = useState<string | null>(null);
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<CheckOut | null>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const imageInput = useRef<HTMLInputElement | null>(null);
  const audioInput = useRef<HTMLInputElement | null>(null);
  const resultRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (result) resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [result]);

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
    setError("");
    setText(ex.text ?? "");
    setNote(ex.note ?? "");
    setImages([]);
    setAudio(ex.audio ? await blobToDataUrl(await (await fetch(ex.audio)).blob()) : null);
  }

  function reset() {
    setText("");
    setNote("");
    setImages([]);
    setAudio(null);
    setResult(null);
    setError("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function run() {
    setError("");
    setBusy(true);
    try {
      setResult(await shield.check({ text, note, images, audio, mode }));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageTitle
        big
        title="Got a message that feels off? Check it before you act."
        lead="Paste the text, add a screenshot or a voice note of the call. In a few seconds you'll know if it looks like a scam, why, and the one thing to do now."
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <Card className="flex flex-col gap-5 p-5 sm:p-7">
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

        <Card className="flex flex-col gap-3 p-5 sm:p-6">
          <CardTitle className="text-lg">Try an example</CardTitle>
          <p className="m-0 text-sm text-muted">Made up for this demo, based on common scams.</p>
          {EXAMPLES.map((ex) => (
            <button
              key={ex.label}
              type="button"
              onClick={() => void loadExample(ex)}
              className="flex cursor-pointer items-center justify-between gap-3 rounded-xl bg-bg px-4 py-3 text-left hover:bg-line"
            >
              <span className="font-semibold text-heading">{ex.label}</span>
              <span className="shrink-0 text-xs text-muted">{ex.kind}</span>
            </button>
          ))}
        </Card>
      </div>

      {busy && <div className="skeleton h-48" aria-label="Checking" />}

      {result && !busy && (
        <div ref={resultRef} className="scroll-mt-6">
          <Result result={result} precision={p} onEvidence={onEvidence} onReset={reset} />
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
