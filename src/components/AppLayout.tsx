import { NavLink, Outlet } from "react-router-dom";
import { supabase } from "../lib/supabase";
import { useAuth } from "../lib/auth";

export function AppLayout() {
  const { session } = useAuth();

  async function signOut() {
    if (!supabase) return;
    const { error } = await supabase.auth.signOut();
    if (error) console.error("La déconnexion Supabase a échoué.", error);
  }

  return (
    <div className="page-shell">
      <header className="topbar">
        <NavLink className="brand" to="/" aria-label="VillainousApp, accueil">
          <span className="brand-mark" aria-hidden="true">V</span>
          <span>VILLAINOUSAPP</span>
        </NavLink>
        <nav className="navigation" aria-label="Navigation principale">
          <NavLink className={({ isActive }) => `nav-button${isActive ? " nav-button-active" : ""}`} to="/scores">
            <span className="nav-icon" aria-hidden="true">♛</span>
            Scores
          </NavLink>
          <NavLink className={({ isActive }) => `nav-button${isActive ? " nav-button-active" : ""}`} to="/stats">
            <span className="nav-icon" aria-hidden="true">▤</span>
            Stats
          </NavLink>
          <NavLink className={({ isActive }) => `nav-button nav-button-primary${isActive ? " nav-button-active" : ""}`} to="/personnages">
            <span className="nav-icon" aria-hidden="true">✦</span>
            Personnages
          </NavLink>
          {session && (
            <button className="nav-button sign-out" type="button" onClick={signOut}>
              Déconnexion
            </button>
          )}
        </nav>
      </header>
      <main><Outlet /></main>
    </div>
  );
}
