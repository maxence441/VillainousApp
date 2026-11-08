import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <>
      <section className="hero" aria-labelledby="hero-title">
        <div className="hero-copy">
          <p className="eyebrow"><span className="eyebrow-mark">✦</span> LE DESTIN DES MÉCHANTS EST ENTRE VOS MAINS</p>
          <h1 id="hero-title">À vous<br />de jouer,<br /><em>méchant.</em></h1>
          <p className="intro">Entrez dans un royaume de magie et de machinations. Cette fois, le méchant, c’est vous.</p>
          <div className="hero-note"><span className="note-rule" /><span>À VOUS D’ÉCRIRE LA LÉGENDE</span></div>
          <div className="home-actions">
            <Link className="nav-button nav-button-primary" to="/scores">Consulter les scores <span aria-hidden="true">↗</span></Link>
            <Link className="nav-button" to="/personnages">Explorer les personnages</Link>
          </div>
        </div>
        <div className="stage" role="img" aria-label="Boîte Villainous en trois dimensions, illuminée par une aura violette">
          <div className="stage-halo" aria-hidden="true" />
          <div className="stage-rings" aria-hidden="true" />
          <span className="stage-label label-top">ÉDITION MÉCHANTE <span>✦</span></span>
          <span className="stage-label label-bottom">LE DESTIN VOUS APPARTIENT</span>
          <span className="stage-coordinate coordinate-left">N° 001 — ROYAUME OBSCUR</span>
          <span className="stage-coordinate coordinate-right">MAGIE / AMBITION</span>
          <div className="box-wrap" aria-hidden="true">
            <div className="game-box">
              <div className="box-spine"><span>VILLAINOUS</span><span className="spine-mark">✦</span><span>ENTREZ DANS LA LÉGENDE</span></div>
              <div className="box-top" />
              <div className="box-front">
                <div className="cover-frame">
                  <span className="cover-edition">UN JEU DE STRATÉGIE</span>
                  <div className="cover-art">
                    <span className="art-orbit orbit-a" /><span className="art-orbit orbit-b" />
                    <span className="art-star star-a">✦</span><span className="art-star star-b">✧</span>
                    <svg className="cover-sigil" viewBox="0 0 180 210" xmlns="http://www.w3.org/2000/svg">
                      <defs><linearGradient id="sigil-fill" x1="20" y1="20" x2="160" y2="190" gradientUnits="userSpaceOnUse"><stop stopColor="#b39bd9" /><stop offset="1" stopColor="#554574" /></linearGradient></defs>
                      <path d="M90 17 111 53 153 39 139 80 165 105 137 124 148 169 105 153 90 190 73 153 31 169 43 124 15 105 41 80 27 39 69 53 90 17Z" fill="url(#sigil-fill)" stroke="#f8dca8" strokeWidth="1.5" />
                      <circle cx="90" cy="104" r="39" fill="#17101d" stroke="#f8dca8" strokeWidth="1.5" />
                      <path d="M67 112 79 92 90 106 101 92 114 112 105 130 90 136 75 130Z" fill="#d2a96c" fillOpacity=".86" />
                      <path d="M75 109 84 112M105 109 96 112" stroke="#fff0c8" strokeLinecap="round" strokeWidth="3" />
                      <path d="M73 80 59 64M107 80 121 64M90 65V45" fill="none" stroke="#f8dca8" strokeLinecap="round" strokeWidth="2" />
                      <circle cx="90" cy="104" r="52" fill="none" stroke="#c3a2eb" strokeOpacity=".58" />
                    </svg>
                    <span className="art-caption">C’EST À VOTRE TOUR</span>
                  </div>
                  <div className="cover-title"><span className="title-rule" /><span className="title-main">VILLAINOUS</span><span className="title-sub">À CHACUN SON DESTIN</span><span className="title-rule" /></div>
                  <span className="cover-footer">CHOISISSEZ VOTRE DESTIN. RÉÉCRIVEZ L’HISTOIRE.</span>
                </div>
              </div>
            </div>
          </div>
          <span className="stage-spark spark-one" aria-hidden="true">✧</span><span className="stage-spark spark-two" aria-hidden="true">✦</span>
        </div>
        <div className="hero-footer"><span>CHAQUE MÉCHANT A SON HISTOIRE</span><span className="footer-center"><i /> LE GRAND JEU COMMENCE</span><span>CHOISISSEZ VOTRE DESTIN</span></div>
      </section>
      <section className="signal" aria-label="Le royaume vous attend">
        <span className="signal-index">[ LE ROYAUME VOUS ATTEND ]</span>
        <p>Le pouvoir ne se donne pas.<br /><span>Il se conquiert, un tour après l’autre.</span></p>
        <span className="signal-mark" aria-hidden="true">✦</span>
      </section>
    </>
  );
}
