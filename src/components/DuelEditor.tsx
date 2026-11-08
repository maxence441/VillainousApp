import type { FormEvent } from "react";
import type { DuelFormValues } from "../types";
import { CharacterPicker } from "./CharacterPicker";

interface DuelEditorProps {
  values: DuelFormValues;
  onChange: (values: DuelFormValues) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onCancel?: () => void;
  busy: boolean;
}

export function DuelEditor({ values, onChange, onSubmit, onCancel, busy }: DuelEditorProps) {
  function update<K extends keyof DuelFormValues>(key: K, value: DuelFormValues[K]) {
    onChange({ ...values, [key]: value });
  }

  return (
    <form className={onCancel ? "duel-edit-form" : "score-form"} onSubmit={onSubmit}>
      {!onCancel && (
        <div className="form-heading">
          <div><span className="form-kicker">NOUVELLE ENTRÉE</span><h2>Enregistrer un duel</h2></div>
          <div className="game-meta">
            <label className="date-field"><span>Date du duel</span><input type="date" name="played_on" value={values.played_on} onChange={event => update("played_on", event.target.value)} required /></label>
            <label className="date-field duration-field"><span>Durée</span><span className="duration-input"><input type="number" name="duration_minutes" min="1" max="1440" step="1" inputMode="numeric" placeholder="60" value={values.duration_minutes} onChange={event => update("duration_minutes", event.target.value)} required /><span>min</span></span></label>
          </div>
        </div>
      )}
      {onCancel && (
        <div className="game-meta edit-game-meta">
          <label className="date-field"><span>Date du duel</span><input type="date" name="played_on" value={values.played_on} onChange={event => update("played_on", event.target.value)} required /></label>
          <label className="date-field duration-field"><span>Durée</span><span className="duration-input"><input type="number" name="duration_minutes" min="1" max="1440" step="1" inputMode="numeric" placeholder="60" value={values.duration_minutes} onChange={event => update("duration_minutes", event.target.value)} required /><span>min</span></span></label>
        </div>
      )}
      <div className="duel-players">
        {(["Claire", "Maxence"] as const).map((player, index) => {
          const field = index === 0 ? "claire_character" : "maxence_character";
          const commentField = index === 0 ? "claire_comment" : "maxence_comment";
          const otherCharacter = index === 0 ? values.maxence_character : values.claire_character;
          return (
            <fieldset className="duel-player" key={player}>
              <legend><span className="player-index">{String(index + 1).padStart(2, "0")}</span> {player}</legend>
              <div className="player-field character-field">
                <span>Personnage</span>
                <CharacterPicker label={player} value={values[field]} unavailableValue={otherCharacter} onChange={character => update(field, character)} />
              </div>
              <label className="player-field player-comment">
                <span>Commentaire <small>(facultatif)</small></span>
                <textarea name={commentField} maxLength={1000} rows={2} placeholder={`Un mot sur la partie de ${player}…`} value={values[commentField]} onChange={event => update(commentField, event.target.value)} />
              </label>
            </fieldset>
          );
        })}
      </div>
      <label className="player-field winner-field">
        <span>Résultat du duel</span>
        <select name="winner" value={values.winner} onChange={event => update("winner", event.target.value as DuelFormValues["winner"])} required>
          <option value="">Qui remporte le duel ?</option>
          <option value="player1">Claire gagne</option>
          <option value="player2">Maxence gagne</option>
          <option value="draw">Égalité</option>
        </select>
      </label>
      {onCancel ? (
        <div className="edit-actions">
          <button className="cancel-edit" type="button" onClick={onCancel}>Annuler</button>
          <button className="save-game" type="submit" disabled={busy}><span aria-hidden="true">✦</span> Enregistrer les modifications</button>
        </div>
      ) : (
        <div className="form-actions">
          <span className="duel-hint"><span aria-hidden="true">✦</span> Un duel, deux destins.</span>
          <button className="save-game" type="submit" disabled={busy}><span aria-hidden="true">✦</span> {busy ? "Enregistrement…" : "Enregistrer le duel"}</button>
        </div>
      )}
    </form>
  );
}
