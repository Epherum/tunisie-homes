"use client";

import SmoothScrollWrapper from "@/utils/SmoothScrollWrapper";
import { ViewTransitions } from "next-view-transitions";

export function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <ViewTransitions>
      <SmoothScrollWrapper>{children}</SmoothScrollWrapper>
    </ViewTransitions>
  );
}
