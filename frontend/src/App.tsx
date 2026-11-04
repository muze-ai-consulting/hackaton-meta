import { useEffect, useState } from "react";
import { Header } from "@/components/shell";
import Check from "@/screens/Check";
import Campaigns from "@/screens/Campaigns";
import Evidence from "@/screens/Evidence";
import Native from "@/screens/Native";
import Network from "@/screens/Network";
import { api, radar, shield, type Campaigns as CampaignsData, type Evidence as EvidenceData, type Mode } from "@/lib/api";

type Screen = "native" | "check" | "evidence" | "campaigns" | "network";

export default function App() {
  const [screen, setScreen] = useState<Screen>("native");
  const [mode, setMode] = useState<Mode>("mock");
  const [evidence, setEvidence] = useState<EvidenceData | null>(null);
  const [campaigns, setCampaigns] = useState<CampaignsData | null>(null);

  useEffect(() => {
    api.config().then((c) => setMode(c.real_allowed ? "real" : "mock")).catch(() => undefined);
    shield.evidence().then(setEvidence).catch(() => undefined);
    radar.campaigns().then(setCampaigns).catch(() => undefined);
  }, []);

  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [screen]);

  return (
    <div className="relative min-h-screen overflow-x-clip">
      <div className="orb" aria-hidden="true" />
      <Header onHome={() => setScreen("native")} onCheck={() => setScreen("check")} onCampaigns={() => setScreen("campaigns")} onNetwork={() => setScreen("network")} onEvidence={() => setScreen("evidence")} />
      <main className="relative mx-auto flex max-w-[1180px] flex-col gap-7 px-4 pb-14 pt-10 sm:px-6">
        {screen === "native" && (
          <Native mode={mode} onCheck={() => setScreen("check")} onEvidence={() => setScreen("evidence")} onNetwork={() => setScreen("network")} />
        )}
        {/* Check stays mounted so going to the evidence page and back keeps what the person typed. */}
        <div className={screen === "check" ? "contents" : "hidden"}>
          <Check mode={mode} evidence={evidence} onEvidence={() => setScreen("evidence")} onCampaigns={() => setScreen("campaigns")} onNetwork={() => setScreen("network")} />
        </div>
        {screen === "campaigns" && <Campaigns data={campaigns} onCheck={() => setScreen("check")} />}
        {screen === "network" && <Network onCheck={() => setScreen("check")} />}
        {screen === "evidence" && <Evidence evidence={evidence} onBack={() => setScreen("check")} />}
      </main>
      <footer className="relative mx-auto flex max-w-[1180px] flex-wrap gap-5 px-4 pb-8 text-sm text-muted sm:px-6">
        <a href="https://labs.muze.cl/hackaton-meta/privacy.html" target="_blank" rel="noreferrer">Privacy</a>
        <a href="https://github.com/muze-ai-consulting/hackaton-meta" target="_blank" rel="noreferrer">Source code</a>
      </footer>
    </div>
  );
}
