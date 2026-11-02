import * as React from "react";
import { cn } from "@/lib/utils";

export function Badge({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn("inline-flex items-center gap-1.5 rounded-lg bg-bg px-2.5 py-1.5 text-[13px] font-medium text-muted", className)}
      {...props}
    />
  );
}
