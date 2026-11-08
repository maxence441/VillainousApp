import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { buildStatistics } from "../lib/statistics";
import { supabase } from "../lib/supabase";
import type { DuelRecord } from "../types";

function formatDate(value: string | null) {
  return value ? new Date(`${value}T12:00:00`).toLocaleDateString("fr-FR") : "—";
}

function formatDuration(value: number | null) {
  return value === null ? "—" : `${Math.round(value)} min`;
}

export function StatsPage() {
  const [games, setGames] = useState<DuelRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function load() {
      if (!supabase) {
        setError("Supabase n’est pas configuré.");
        setLoading(false);
        return;
      }
      const { data, error: loadError } = await supabase
        .from("duels")
        .select("*")
        .order("played_on", { ascending: false });
      if (!active) return;
      if (loadError) setError(loadError.message);
      else setGames((data ?? []) as DuelRecord[]);
      setLoading(false);
    }
    void load();
    return () => { active = false; };
  }, []);

  const stats = buildStatistics(games);

  return (
    <section className="stats-page" aria-labelledby="stats-title">
      <header className="stats-heading">
        <div>
          <p className="eyebrow"><span className="eyebrow-mark">▤</span> LES CHRONIQUES DU ROYAUME</p>
          <h1 id="stats-title">Les <em>Statistiques.</em></h1>
          <p className="intro">Chaque duel laisse une trace. Voici ce que racontent vos parties enregistrées.</p>
        </div>
        <Link className="stats-link" to="/scores">Voir les scores <span aria-hidden="true">↗</span></Link>
      </header>

      {loading && <p className="loading-message" role="status">Lecture des chroniques…</p>}
      {error && <p className="form-errors" role="alert">{error}</p>}
      {!loading && !error && stats.totalGames > 0 && (
        <>
          <div className="stats-overview">
            <article className="stat-card stat-card-primary"><span className="stat-label">DUELS ARCHIVÉS</span><strong>{stats.totalGames}</strong><span className="stat-note">depuis le {formatDate(stats.firstGame)}</span></article>
            <article className="stat-card"><span className="stat-label">ÉGALITÉS</span><strong>{stats.draws}</strong><span className="stat-note">{stats.drawRate} % des duels</span></article>
            <article className="stat-card"><span className="stat-label">ÉCART AU SCORE</span><strong>{stats.leader ?? "À égalité"}</strong><span className="stat-note">{stats.winMargin ? `${stats.winMargin} victoire(s) d’avance` : "autant de victoires chacun"}</span></article>
            <article className="stat-card"><span className="stat-label">DURÉE MOYENNE</span><strong>{formatDuration(stats.averageDuration)}</strong><span className="stat-note">par duel enregistré</span></article>
          </div>
          <div className="stats-grid">
            <section className="stats-panel duration-panel" aria-labelledby="duration-title">
              <div className="panel-heading"><div><span className="panel-kicker">LE TEMPS PASSÉ À JOUER</span><h2 id="duration-title">Durée des parties</h2></div></div>
              {stats.totalDuration > 0 ? (
                <>
                  <div className="duration-total"><strong>{stats.totalDuration >= 60 ? `${Math.floor(stats.totalDuration / 60)} h ${stats.totalDuration % 60}` : stats.totalDuration}</strong><span>minutes de jeu cumulées</span></div>
                  <div className="duration-metrics">
                    <div><span>Parties nulles</span><strong>{formatDuration(stats.averageDrawDuration)}</strong></div>
                    <div><span>Parties décidées</span><strong>{formatDuration(stats.averageDecisiveDuration)}</strong></div>
                    <div><span>Médiane</span><strong>{formatDuration(stats.medianDuration)}</strong></div>
                    <div><span>Plus courte / plus longue</span><strong>{stats.shortestDuration} / {stats.longestDuration} min</strong></div>
                  </div>
                </>
              ) : <p className="stats-empty">Aucune durée n’a été renseignée.</p>}
            </section>
            <section className="stats-panel calendar-panel" aria-labelledby="calendar-title">
              <div className="panel-heading"><div><span className="panel-kicker">LE RYTHME DES PARTIES</span><h2 id="calendar-title">Quand jouez-vous ?</h2></div></div>
              {stats.busiestDay && <p className="busiest-day"><span>Journée la plus active</span><strong>{formatDate(stats.busiestDay.date)} <small>· {stats.busiestDay.games} duels</small></strong></p>}
              <div className="weekday-chart">
                {stats.weekdays.map(day => <div className="weekday-row" key={day.name}><span>{day.name}</span><span className="bar-track"><span className="bar-fill" style={{ "--bar-width": `${stats.maxWeekdayGames ? day.games / stats.maxWeekdayGames * 100 : 0}%` } as React.CSSProperties} /></span><strong>{day.games}</strong></div>)}
              </div>
              <p className="chart-caption">Nombre de duels par jour de la semaine</p>
            </section>
            <section className="stats-panel activity-panel" aria-labelledby="activity-title">
              <div className="panel-heading"><div><span className="panel-kicker">AU FIL DES MOIS</span><h2 id="activity-title">Activité des archives</h2></div></div>
              <div className="activity-chart">
                {stats.monthlyActivity.map(month => <div className="activity-column" title={`${month.label} : ${month.games} duels, ${month.draws} égalité(s)`} key={month.label}><strong>{month.games}</strong><span className="activity-track"><span className="activity-fill" style={{ "--bar-height": `${month.games / stats.maxMonthlyGames * 100}%` } as React.CSSProperties}><span className="activity-draw-fill" style={{ "--draw-share": `${month.draws / month.games * 100}%` } as React.CSSProperties} /></span></span><span className="activity-label">{month.label}</span></div>)}
              </div>
              <p className="chart-caption"><span className="legend-swatch legend-all" /> Tous les duels <span className="legend-swatch legend-draw" /> Égalités · Les 12 derniers mois avec au moins une partie</p>
              <p className="date-range">Première partie : <strong>{formatDate(stats.firstGame)}</strong><span>·</span> Dernière partie : <strong>{formatDate(stats.lastGame)}</strong><span>·</span><strong>{stats.activeDays} jours joués</strong><span>·</span><strong>{stats.comments} commentaires</strong></p>
            </section>
            <section className="stats-panel character-panel" aria-labelledby="character-title">
              <div className="panel-heading"><div><span className="panel-kicker">QUI DOMINE LE ROYAUME ?</span><h2 id="character-title">Personnages</h2></div></div>
              {stats.mostPlayedCharacter && (
                <>
                  <div className="character-highlights">
                    <p><span>Le plus choisi</span><strong>{stats.mostPlayedCharacter.name}</strong><small>{stats.mostPlayedCharacter.games} parties</small></p>
                    {stats.bestCharacter && <p><span>Meilleur taux de victoire <small>(3 parties minimum)</small></span><strong>{stats.bestCharacter.name}</strong><small>{stats.bestCharacter.winRate} % de ses parties</small></p>}
                    {stats.mostDrawnCharacter && <p><span>Le plus souvent à égalité <small>(3 parties minimum)</small></span><strong>{stats.mostDrawnCharacter.name}</strong><small>{stats.mostDrawnCharacter.drawRate} % · {stats.mostDrawnCharacter.draws} égalité(s)</small></p>}
                  </div>
                  <div className="table-scroll"><table className="stats-table"><thead><tr><th>Personnage</th><th>Parties</th><th>Égalités</th><th>Taux d’égalité</th><th>Taux de victoire</th></tr></thead><tbody>
                    {stats.characters.map(character => <tr key={character.name}><th scope="row">{character.name}</th><td>{character.games}</td><td>{character.draws}</td><td><span className="rate-cell"><span className="mini-track draw-mini-track"><span style={{ "--bar-width": `${character.drawRate}%` } as React.CSSProperties} /></span><strong>{character.drawRate} %</strong></span></td><td><span className="rate-cell"><span className="mini-track"><span style={{ "--bar-width": `${character.winRate}%` } as React.CSSProperties} /></span><strong>{character.winRate} %</strong></span></td></tr>)}
                  </tbody></table></div>
                </>
              )}
            </section>
            <section className="stats-panel players-panel" aria-labelledby="players-title">
              <div className="panel-heading"><div><span className="panel-kicker">CLAIRE CONTRE MAXENCE</span><h2 id="players-title">Face-à-face</h2></div></div>
              <p className="chart-caption">Les égalités sont affichées séparément du bilan de chaque joueur.</p>
              <div className="table-scroll"><table className="stats-table"><thead><tr><th>Joueur</th><th>Victoires</th><th>Défaites</th><th>Égalités</th><th>Personnage favori</th></tr></thead><tbody>
                {stats.players.map(player => <tr key={player.name}><th scope="row">{player.name}</th><td>{player.wins}</td><td>{player.losses}</td><td className="draw-result-cell">{player.draws}</td><td>{player.favoriteCharacter ? <>{player.favoriteCharacter} <small>({player.favoriteCharacterGames} parties)</small></> : "—"}</td></tr>)}
              </tbody></table></div>
            </section>
            <section className="stats-panel pairings-panel" aria-labelledby="pairings-title">
              <div className="panel-heading"><div><span className="panel-kicker">LES DUELS QUI NE SE DÉPARTAGENT PAS</span><h2 id="pairings-title">Égalités par duo de personnages</h2></div></div>
              {stats.topDrawCharacterPairings.length > 0
                ? <ol className="pairing-list">{stats.topDrawCharacterPairings.map(pairing => <li key={pairing.names.join("-")}><span>{pairing.names[0]} <i>contre</i> {pairing.names[1]}</span><strong>{pairing.games} égalité(s)</strong></li>)}</ol>
                : <p className="stats-empty">Aucun affrontement enregistré.</p>}
            </section>
          </div>
        </>
      )}
      {!loading && !error && stats.totalGames === 0 && (
        <section className="stats-empty-state"><span aria-hidden="true">✧</span><h2>Les chroniques sont encore vierges.</h2><p>Enregistrez votre premier duel pour voir apparaître les statistiques du royaume.</p><Link className="stats-link" to="/scores">Enregistrer un duel <span aria-hidden="true">↗</span></Link></section>
      )}
    </section>
  );
}
