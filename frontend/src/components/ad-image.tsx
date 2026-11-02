import { useState } from "react";
import { ExternalLink } from "lucide-react";

/** Ad Library images are signed fbcdn URLs that expire; when one fails, link to the ad in the Ad Library instead. */
export function AdImage({ src, adId, alt }: { src: string | null; adId: string; alt: string }) {
  const [failed, setFailed] = useState(false);
  if (src && !failed) {
    return <img src={src} alt={alt} className="size-full object-cover" referrerPolicy="no-referrer" onError={() => setFailed(true)} />;
  }
  return (
    <a
      href={`https://www.facebook.com/ads/library/?id=${adId}`}
      target="_blank"
      rel="noreferrer"
      className="flex size-full flex-col items-center justify-center gap-1.5 p-4 text-center text-sm font-semibold text-muted hover:text-ink"
    >
      <ExternalLink className="size-5" aria-hidden="true" />
      View this ad in the Meta Ad Library
    </a>
  );
}
