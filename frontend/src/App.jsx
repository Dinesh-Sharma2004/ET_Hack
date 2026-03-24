import { Suspense, lazy } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/layout/AppShell";
import { Loader } from "./components/ui/Loader";

const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const MyNewsPage = lazy(() => import("./pages/MyNewsPage"));
const BriefingPage = lazy(() => import("./pages/BriefingPage"));
const StoryPage = lazy(() => import("./pages/StoryPage"));
const VideosPage = lazy(() => import("./pages/VideosPage"));
const VideoDetailPage = lazy(() => import("./pages/VideoDetailPage"));
const VernacularPage = lazy(() => import("./pages/VernacularPage"));
const ProfilePage = lazy(() => import("./pages/ProfilePage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));

export default function App() {
  return (
    <AppShell>
      <Suspense fallback={<Loader label="Loading MyET AI" fullPage />}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/my-news" element={<MyNewsPage />} />
          <Route path="/briefing/:topic" element={<BriefingPage />} />
          <Route path="/story/:id" element={<StoryPage />} />
          <Route path="/videos" element={<VideosPage />} />
          <Route path="/video/:id" element={<VideoDetailPage />} />
          <Route path="/vernacular" element={<VernacularPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/home" element={<Navigate to="/" replace />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </AppShell>
  );
}
