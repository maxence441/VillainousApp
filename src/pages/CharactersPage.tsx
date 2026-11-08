import { useMemo, useState } from "react";
import villains from "../data/characters.json";

const officialCatalogUrl = "https://www.ravensburger.fr/fr-FR/produits/jeux/jeux-de-societe";
const normalize = (text: string) => text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("fr");

export function CharactersPage() {
  const [query, setQuery] = useState("");
  const visibleVillains = useMemo(() => {
    const normalizedQuery = normalize(query.trim());
    return villains.filter(villain =>
      normalize(Object.values(villain).join(" ")).includes(normalizedQuery),
    );
  }, [query]);

  return (
    <section className="characters-page" aria-labelledby="characters-title">
      <header className="characters-heading">
        <div>
          <p className="eyebrow"><span className="eyebrow-mark">✦</span> LE ROYAUME DES MÉCHANTS</p>
          <h1 id="characters-title">Les <em>Personnages.</em></h1>
          <p className="intro">Explorez les vilains, leur univers et l’approche stratégique qui donne sa couleur à chaque deck.</p>
        </div>
        <span className="characters-count">{villains.length} FICHES</span>
      </header>
      <aside className="characters-note">
        <span aria-hidden="true">✧</span>
        <p>Ouvre une fiche pour lire un aperçu stratégique original. Les objectifs exacts, cartes et plateaux restent décrits dans les règles officielles de chaque boîte.</p>
        <a href={officialCatalogUrl} target="_blank" rel="noopener noreferrer">Catalogue officiel Ravensburger <span aria-hidden="true">↗</span></a>
      </aside>
      <div className="characters-toolbar">
        <label className="character-search">
          <span className="visually-hidden">Rechercher un personnage ou un univers</span>
          <span aria-hidden="true">⌕</span>
          <input type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder="Rechercher un personnage, un univers, un style…" autoComplete="off" />
        </label>
        <p className="characters-results" role="status" aria-live="polite"><strong>{visibleVillains.length}</strong> personnages</p>
      </div>
      <div className="character-catalog">
        {visibleVillains.map((villain, index) => (
          <details className="villain-card" key={villain.name}>
            <summary className="villain-card-summary" aria-controls={`villain-details-${index}`}>
              <span className="villain-card-top"><span className="villain-universe">{villain.universe}</span></span>
              <span className="villain-name">{villain.name}</span>
              <span className="villain-divider" aria-hidden="true"><span>✦</span></span>
              <span className="villain-style-label">APPROCHE DE JEU</span>
              <span className="villain-style">{villain.style}</span>
              <span className="villain-mechanics"><span>Axes de jeu</span><span className="villain-mechanics-value">{villain.mechanics}</span></span>
              <span className="villain-expand-label"><span className="expand-closed">Développer la fiche</span><span className="expand-open">Réduire la fiche</span><span className="expand-icon" aria-hidden="true">⌄</span></span>
            </summary>
            <div className="villain-details" id={`villain-details-${index}`}>
              <section><h3>Lecture stratégique</h3><p>{villain.description}</p></section>
              <section><h3>Conseil de pilotage</h3><p>{villain.advice}</p></section>
              <section className="official-rules-note">
                <h3>Objectif, cartes et plateau</h3>
                <p>Cette fiche présente une approche générale, sans reproduire les cartes. Pour les conditions de victoire exactes, les effets de cartes et les règles de plateau, consulte la notice de la boîte correspondante.</p>
                <a href={officialCatalogUrl} target="_blank" rel="noopener noreferrer">Référence officielle Ravensburger <span aria-hidden="true">↗</span></a>
              </section>
            </div>
          </details>
        ))}
      </div>
      {visibleVillains.length === 0 && <p className="characters-no-results">Aucun personnage ne correspond à cette recherche.</p>}
      <footer className="characters-footer">
        <p>Pour les objectifs exacts et le détail des cartes, reporte-toi à la notice officielle de la boîte concernée.</p>
        <a href={officialCatalogUrl} target="_blank" rel="noopener noreferrer">Consulter les produits Disney Villainous chez Ravensburger <span aria-hidden="true">↗</span></a>
      </footer>
    </section>
  );
}
