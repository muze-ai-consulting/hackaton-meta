import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

// How Second Look works on WhatsApp: the person forwards the message and gets the answer in the chat.
// Texts are the real answers Second Look gave for this example (verdict, then the agent's checks).
const STEPS = 5; // forwarded message, typing, verdict, typing, clues
const DELAYS = [0, 1400, 2600, 1300, 7000]; // time on each step; it starts with the forwarded message already there

function Bubble({ show, out = false, children }: { show: boolean; out?: boolean; children: React.ReactNode }) {
  return (
    <div
      className={cn(
        "max-w-[86%] rounded-2xl px-3 py-2 text-[12px] leading-snug shadow-[0_1px_0_rgba(0,0,0,0.06)] transition-all duration-500",
        out ? "self-end rounded-br-md bg-[#d7f5d0] text-[#0f2a12]" : "self-start rounded-bl-md bg-white text-[#16181d]",
        show ? "translate-y-0 opacity-100" : "pointer-events-none h-0 translate-y-2 overflow-hidden p-0 opacity-0",
      )}
    >
      {children}
    </div>
  );
}

function Typing({ show }: { show: boolean }) {
  if (!show) return null;
  return (
    <div className="flex gap-1 self-start rounded-2xl rounded-bl-md bg-white px-3 py-2.5" aria-hidden="true">
      {[0, 1, 2].map((i) => (
        <span key={i} className="size-1.5 animate-bounce rounded-full bg-[#9aa3ad]" style={{ animationDelay: `${i * 150}ms` }} />
      ))}
    </div>
  );
}

export default function PhoneDemo() {
  const [step, setStep] = useState(1);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setStep(STEPS - 1);
      return;
    }
    const t = setTimeout(() => setStep((s) => (s >= STEPS - 1 ? 1 : s + 1)), DELAYS[Math.min(step, DELAYS.length - 1)]);
    return () => clearTimeout(t);
  }, [step]);

  return (
    <figure className="m-0 flex flex-col items-center gap-3">
      <div
        className="w-[284px] rounded-[38px] bg-[#16181d] p-2.5 shadow-[0_30px_60px_-20px_rgba(20,24,40,0.45)]"
        role="img"
        aria-label="A phone where someone forwards a parcel-fee text to Second Look on WhatsApp and gets back 'Likely a scam', why, what to do, and what the agent checked."
      >
        <div className="flex h-[600px] flex-col overflow-hidden rounded-[30px] bg-[#e7ece6]">
          <div className="flex items-center gap-2 bg-[#1f6f5c] px-3.5 pb-2.5 pt-5 text-white">
            <div className="grid size-8 place-items-center rounded-full bg-white/15">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6z" />
                <path d="M9 12l2 2 4-4" />
              </svg>
            </div>
            <div className="leading-tight">
              <div className="text-[14px] font-semibold">Second Look</div>
              <div className="text-[11px] text-white/75">{step === 1 || step === 3 ? "typing…" : "on WhatsApp"}</div>
            </div>
          </div>
          <div className="flex min-h-0 flex-1 flex-col gap-1.5 overflow-hidden p-2.5">
            <div className="mb-1 self-center rounded-md bg-white/80 px-2 py-0.5 text-[10.5px] text-[#5b6470]">Today</div>
            <Bubble show={step >= 1} out>
              <div className="mb-0.5 text-[10.5px] italic text-[#4b6b4f]">↪ Forwarded</div>
              Royal Mail: Your parcel could not be delivered due to an unpaid shipping fee of £1.45. Pay now: royalmail-redelivery-uk.com
            </Bubble>
            <Typing show={step === 1} />
            <Bubble show={step >= 2}>
              <div className="font-bold text-[#b42318]">🔴 Likely a scam · 99%</div>
              <div className="mt-1">
                <b>Why:</b> Royal Mail never uses royalmail-redelivery-uk.com; a £1.45 fee is classic delivery smishing.
              </div>
              <div className="mt-1">
                <b>Do now:</b> Don't click or pay. Delete it and report it to 7726.
              </div>
            </Bubble>
            <Typing show={step === 3} />
            <Bubble show={step >= 4}>
              <div className="font-bold">🔎 What I checked</div>
              <div className="mt-0.5">🔗 Followed the link: the site doesn't exist</div>
              <div>🌐 No registration record for the domain</div>
              <div>⚠️ The domain imitates Royal Mail</div>
              <div className="mt-1.5 font-bold">👥 Seen before: Delivery Fee Texts</div>
              <div>39 people reported this on Reddit since September, rising.</div>
            </Bubble>
          </div>
          <div className="flex shrink-0 items-center gap-2 bg-[#f4f6f4] px-2.5 py-2">
            <div className="h-7 flex-1 rounded-full bg-white px-3 text-[11.5px] leading-7 text-[#9aa3ad]">Message</div>
          </div>
        </div>
      </div>
      <figcaption className="max-w-[280px] text-center text-sm text-muted">
        On WhatsApp: forward the message, get the answer in the chat.
      </figcaption>
    </figure>
  );
}
