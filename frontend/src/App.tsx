import { useEffect, useState } from "react";
import { Header } from "@/components/shell";
import Check from "@/screens/Check";
import Campaigns from "@/screens/Campaigns";
import Evidence from "@/screens/Evidence";
import { api, radar, shield, type Campaigns as CampaignsData, type Evidence as EvidenceData, type Mode } from "@/lib/api";

type Screen = "check" | "evidence" | "campaigns";

export default function App() {
  const [screen, setScreen] = useState<Screen>("check");
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
      <Header onHome={() => setScreen("check")} onCampaigns={() => setScreen("campaigns")} onEvidence={() => setScreen("evidence")} />
      <main className="relative mx-auto flex max-w-[1180px] flex-col gap-7 px-4 pb-14 pt-10 sm:px-6">
        {/* Check stays mounted so going to the evidence page and back keeps what the person typed. */}
        <div className={screen === "check" ? "contents" : "hidden"}>
          <Check mode={mode} evidence={evidence} onEvidence={() => setScreen("evidence")} onCampaigns={() => setScreen("campaigns")} />
        </div>
        {screen === "campaigns" && <Campaigns data={campaigns} onCheck={() => setScreen("check")} />}
        {screen === "evidence" && <Evidence evidence={evidence} onBack={() => setScreen("check")} />}
      </main>
    </div>
  );
}
