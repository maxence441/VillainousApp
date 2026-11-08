import { Navigate, Route, Routes } from "react-router-dom";
import type { ReactNode } from "react";
import { AppLayout } from "./components/AppLayout";
import { LoginPage } from "./components/LoginPage";
import { CharactersPage } from "./pages/CharactersPage";
import { HomePage } from "./pages/HomePage";
import { ScoresPage } from "./pages/ScoresPage";
import { StatsPage } from "./pages/StatsPage";
import { useAuth } from "./lib/auth";

function Protected({ children }: { children: ReactNode }) {
  const { session, loading } = useAuth();
  if (loading) return <p className="loading-message" role="status">Ouverture des archives…</p>;
  return session ? <>{children}</> : <LoginPage />;
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<HomePage />} />
        <Route path="personnages" element={<CharactersPage />} />
        <Route path="connexion" element={<LoginPage />} />
        <Route path="scores" element={<Protected><ScoresPage /></Protected>} />
        <Route path="stats" element={<Protected><StatsPage /></Protected>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
