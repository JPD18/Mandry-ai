"use client"

import { useEffect, useState } from "react";
import { AnimatePresence } from "framer-motion";
import { Splash } from "@/components/splash/splash";
import SiteHeader from "@/components/layout/site-header";
import MainContentComponent from "@/components/sections/main-content";

export default function Home() {
  const [showSplash, setShowSplash] = useState(true);

  useEffect(() => {
    try {
      const hasVisitedBefore = localStorage.getItem("hasVisitedBefore");
      if (hasVisitedBefore) {
        setShowSplash(false);
      } else {
        localStorage.setItem("hasVisitedBefore", "true");
      }
    } catch {
      // localStorage might be unavailable (e.g., during ISR/prerender)
      setShowSplash(false);
    }
  }, []);

  return (
    <>
      <AnimatePresence>
        {showSplash && <Splash key="splash" onDone={() => setShowSplash(false)} />}
      </AnimatePresence>

      {!showSplash && (
        <>
          <SiteHeader />
          <MainContentComponent />
        </>
      )}
    </>
  );
} 