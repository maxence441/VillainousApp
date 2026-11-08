import { useState, type FormEvent } from "react";
import { supabaseConfigError, supabase } from "../lib/supabase";
import { useAuth } from "../lib/auth";

export function LoginPage() {
  const { error: sessionError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function signIn(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!supabase) return;
    setBusy(true);
    setError(null);
    const { error: signInError } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password,
    });
    setBusy(false);
    if (signInError) setError(signInError.message);
  }

  return (
    <section className="scores-page auth-page" aria-labelledby="login-title">
      <header className="scores-heading">
        <div>
          <p className="eyebrow"><span className="eyebrow-mark">♛</span> ACCÈS AUX ARCHIVES</p>
          <h1 id="login-title">Connexion.</h1>
          <p className="intro">Connecte-toi pour consulter et gérer les duels du royaume.</p>
        </div>
      </header>

      <form className="score-form login-form" onSubmit={signIn}>
        <div className="form-heading">
          <div>
            <span className="form-kicker">ESPACE PRIVÉ</span>
            <h2>Se connecter</h2>
          </div>
        </div>
        {supabaseConfigError && <p className="form-errors" role="alert">{supabaseConfigError}</p>}
        {(error || sessionError) && (
          <p className="form-errors" role="alert">{error ?? sessionError}</p>
        )}
        {!supabaseConfigError && (
          <>
            <label className="date-field login-field">
              <span>Adresse e-mail</span>
              <input
                type="email"
                autoComplete="username"
                value={email}
                onChange={event => setEmail(event.target.value)}
                required
              />
            </label>
            <label className="date-field login-field">
              <span>Mot de passe</span>
              <input
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={event => setPassword(event.target.value)}
                required
              />
            </label>
            <div className="form-actions">
              <span className="duel-hint">Comptes créés par l’administrateur Supabase.</span>
              <button className="save-game" type="submit" disabled={busy}>
                {busy ? "Connexion…" : "Se connecter"}
              </button>
            </div>
          </>
        )}
      </form>
    </section>
  );
}
