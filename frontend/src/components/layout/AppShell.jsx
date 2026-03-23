import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useLocation } from "react-router-dom";

import { Footer } from "./Footer";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";

export function AppShell({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(15,118,110,0.22),_transparent_30%),linear-gradient(180deg,_#091521_0%,_#071018_55%,_#0f1f29_100%)] text-white">
      <Navbar onMenuToggle={() => setCollapsed((current) => !current)} />
      <div className="mx-auto flex max-w-[1600px] gap-6 px-4 pb-8 pt-24 md:px-6">
        <Sidebar collapsed={collapsed} />
        <AnimatePresence mode="wait">
          <motion.main
            key={location.pathname}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.24 }}
            className="min-w-0 flex-1"
          >
            <div className="space-y-6">{children}</div>
            <Footer />
          </motion.main>
        </AnimatePresence>
      </div>
    </div>
  );
}
