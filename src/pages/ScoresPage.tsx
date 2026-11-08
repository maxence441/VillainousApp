import { useCallback, useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import type { DuelFormValues, DuelRecord } from "../types";
import { GAMES_PER_PAGE, newDuelFormValues, toDuelFormValues } from "../types";
import { supabase } from "../lib/supabase";
import { DuelEditor } from "../components/DuelEditor";

function formatDate(value: string) {
  return new Date(`${value}T12:00:00`).toLocaleDateString("fr-FR");
}

export function ScoresPage() {
  const [games, setGames] = useState<DuelRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [form, setForm] = useState<DuelFormValues>(newDuelFormValues);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<DuelFormValues | null>(null);
  const [page, setPage] = useState(1);
  const historyRef = useRef<HTMLElement>(null);
  const didMount = useRef(false);

  const loadGames = useCallback(async () => {
    if (!supabase) {
      setLoading(false);
      setError("Supabase n’est pas configuré.");
      return;
    }
    setLoading(true);
    setError(null);
    const { data, error: loadError } = await supabase
      .from("duels")
      .select("*")
      .order("played_on", { ascending: false })
      .order("id", { ascending: false });
    if (loadError) setError(loadError.message);
    else setGames((data ?? []) as DuelRecord[]);
    setLoading(false);
  }, []);

  useEffect(() => { void loadGames(); }, [loadGames]);

  const pageCount = Math.max(1, Math.ceil(games.length / GAMES_PER_PAGE));
  const visibleGames = useMemo(
    () => games.slice((page - 1) * GAMES_PER_PAGE, page * GAMES_PER_PAGE),
    [games, page],
  );

  useEffect(() => {
    if (!didMount.current) {
      didMount.current = true;
      return;
    }
    historyRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [page]);

  const saveDuel = async (event: FormEvent<HTMLFormElement>, values: DuelFormValues, gameId?: number) => {
    event.preventDefault();
    if (!supabase) return;
    setError(null);
    setNotice(null);
    if (values.claire_character === values.maxence_character) {
      setError("Claire et Maxence doivent choisir des personnages différents.");
      return;
    }
    const duration = Number(values.duration_minutes);
    if (!Number.isInteger(duration) || duration < 1 || duration > 1440) {
      setError("La durée doit être comprise entre 1 et 1 440 minutes.");
      return;
    }
    if (!values.winner) {
      setError("Choisis le résultat du duel.");
      return;
    }
    setBusy(true);
    const record = {
      played_on: values.played_on,
      duration_minutes: duration,
      claire_character: values.claire_character,
      maxence_character: values.maxence_character,
      winner: values.winner,
      claire_comment: values.claire_comment.trim(),
      maxence_comment: values.maxence_comment.trim(),
    };
    const result = gameId
      ? await supabase.from("duels").update(record).eq("id", gameId)
      : await supabase.from("duels").insert(record);
    setBusy(false);
    if (result.error) {
      setError(result.error.message);
      return;
    }
    setNotice(gameId ? "Le duel a été modifié." : "Le duel a été enregistré.");
    setEditingId(null);
    setEditForm(null);
    setForm(newDuelFormValues());
    await loadGames();
  };

  async function deleteGame(game: DuelRecord) {
    if (!supabase || !window.confirm("Supprimer définitivement ce duel ?")) return;
    setError(null);
    setNotice(null);
    const { error: deleteError } = await supabase.from("duels").delete().eq("id", game.id);
    if (deleteError) {
      setError(deleteError.message);
      return;
    }
    setNotice("Le duel a été supprimé.");
    const nextCount = Math.max(1, Math.ceil((games.length - 1) / GAMES_PER_PAGE));
    setPage(current => Math.min(current, nextCount));
    await loadGames();
  }

  function startEditing(game: DuelRecord) {
    setEditingId(game.id);
    setEditForm(toDuelFormValues(game));
    requestAnimationFrame(() => document.getElementById(`game-card-${game.id}`)?.scrollIntoView({ behavior: "smooth", block: "start" }));
  }

  return (
    <section className="scores-page" aria-labelledby="scores-title">
      <div className="scores-heading">
        <div>
          <p className="eyebrow"><span className="eyebrow-mark">♛</span> ARCHIVES DU ROYAUME</p>
          <h1 id="scores-title">Les <em>Scores.</em></h1>
          <p className="intro">Consignez les duels de vos méchants et retrouvez leurs résultats dans les archives.</p>
        </div>
        <span className="scores-count">{games.length} DUEL{games.length === 1 ? "" : "S"} ARCHIVÉ{games.length === 1 ? "" : "S"}</span>
      </div>

      {notice && <p className="flash flash-success" role="status">{notice}</p>}
      {error && <div className="form-errors" role="alert"><p>Une erreur est survenue :</p><p>{error}</p></div>}

      <DuelEditor values={form} onChange={setForm} onSubmit={event => void saveDuel(event, form)} busy={busy} />

      <section className="game-history" aria-labelledby="history-title" aria-live="polite" ref={historyRef}>
        <div className="history-heading">
          <div><span className="form-kicker">LES CHRONIQUES DU ROYAUME</span><h2 id="history-title">Duels enregistrés</h2></div>
          {games.length > 0 && <span className="history-total">{games.length} résultat{games.length === 1 ? "" : "s"}</span>}
        </div>
        {loading ? <p className="loading-message" role="status">Chargement des archives…</p> : visibleGames.length ? (
          <div className="game-list">
            {visibleGames.map(game => (
              <article className="game-card" id={`game-card-${game.id}`} key={game.id}>
                <header className="game-card-header">
                  <div className="game-time"><span className="game-date"><span aria-hidden="true">◷</span> {formatDate(game.played_on)}</span><span className="time-separator" aria-hidden="true">•</span><span className="game-duration">{game.duration_minutes} min</span></div>
                  <div className="game-card-actions">
                    <span className="game-number">DUEL N° {String(game.id).padStart(3, "0")}</span>
                    {editingId === game.id
                      ? <button className="record-action edit-action" type="button" aria-label={`Annuler la modification du duel ${game.id}`} data-tooltip="Annuler la modification" onClick={() => { setEditingId(null); setEditForm(null); }}>↩</button>
                      : <button className="record-action edit-action" type="button" aria-label={`Modifier le duel ${game.id}`} data-tooltip="Modifier ce duel" onClick={() => startEditing(game)}>✎</button>}
                    <button className="record-action delete-action" type="button" aria-label={`Supprimer le duel ${game.id}`} data-tooltip="Supprimer ce duel" onClick={() => void deleteGame(game)}>×</button>
                  </div>
                </header>
                {editingId === game.id && editForm ? (
                  <DuelEditor values={editForm} onChange={setEditForm} onSubmit={event => void saveDuel(event, editForm, game.id)} onCancel={() => { setEditingId(null); setEditForm(null); }} busy={busy} />
                ) : (
                  <div className="score-table-wrap">
                    <table className="score-table">
                      <thead><tr><th scope="col">Résultat</th><th scope="col">Joueur</th><th scope="col">Personnage</th><th scope="col">Commentaire</th></tr></thead>
                      <tbody>
                        {(["Claire", "Maxence"] as const).map((player, index) => {
                          const winner = index === 0 ? game.winner === "player1" : game.winner === "player2";
                          const draw = game.winner === "draw";
                          const character = index === 0 ? game.claire_character : game.maxence_character;
                          const comment = index === 0 ? game.claire_comment : game.maxence_comment;
                          return (
                            <tr className={draw ? "draw-row" : winner ? "winner-row" : "loss-row"} key={player}>
                              <td className="result-cell"><span className={`result-badge result-${draw ? "draw" : winner ? "win" : "loss"}`}>{draw ? "Égalité" : winner ? <><span aria-hidden="true">♛</span> Victoire</> : "Défaite"}</span></td>
                              <td className="player-name-cell">{player}</td><td className="character-cell">{character}</td><td className="comment-cell">{comment || <span className="no-comment">—</span>}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </article>
            ))}
          </div>
        ) : !error && (
          <div className="empty-history"><span aria-hidden="true">✧</span><p>Aucun duel dans les archives.<br /><span>La première légende reste à écrire.</span></p></div>
        )}
        {pageCount > 1 && (
          <nav className="pagination" aria-label="Pagination des duels">
            {page > 1 && <button className="pagination-link pagination-direction" type="button" onClick={() => setPage(current => current - 1)}>‹ Précédent</button>}
            {Array.from({ length: pageCount }, (_, index) => index + 1).map(pageNumber => pageNumber === page
              ? <span className="pagination-link pagination-current" aria-current="page" key={pageNumber}>{pageNumber}</span>
              : <button className="pagination-link" type="button" onClick={() => setPage(pageNumber)} key={pageNumber}>{pageNumber}</button>)}
            {page < pageCount && <button className="pagination-link pagination-direction" type="button" onClick={() => setPage(current => current + 1)}>Suivant ›</button>}
          </nav>
        )}
      </section>
    </section>
  );
}
