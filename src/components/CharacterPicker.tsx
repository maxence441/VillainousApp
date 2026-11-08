import { useMemo, useState } from "react";
import { CHARACTERS } from "../data/characters";

interface CharacterPickerProps {
  label: string;
  value: string;
  unavailableValue: string;
  onChange: (value: string) => void;
}

const normalize = (text: string) => text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("fr");

export function CharacterPicker({ label, value, unavailableValue, onChange }: CharacterPickerProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const options = useMemo(() => CHARACTERS.filter(name => normalize(name).includes(normalize(query.trim()))), [query]);

  return (
    <div className="character-picker">
      <button
        className="character-picker-toggle"
        type="button"
        role="combobox"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={`Personnage de ${label}`}
        onClick={() => {
          setOpen(current => !current);
          setQuery("");
        }}
      >
        <span className="character-picker-value">{value || "Choisir un personnage"}</span>
        <span className="character-picker-arrow" aria-hidden="true">⌄</span>
      </button>
      {open && (
        <div className="character-picker-menu">
          <input
            className="character-filter"
            type="search"
            placeholder="Filtrer les personnages…"
            aria-label={`Filtrer les personnages de ${label}`}
            autoFocus
            value={query}
            onChange={event => setQuery(event.target.value)}
            onKeyDown={event => {
              if (event.key === "Escape") setOpen(false);
            }}
          />
          <div className="character-picker-options" role="listbox" aria-label={`Personnages de ${label}`}>
            {options.map(character => (
              <button
                className="character-picker-option"
                type="button"
                role="option"
                aria-selected={value === character}
                disabled={Boolean(unavailableValue && unavailableValue === character)}
                key={character}
                onClick={() => {
                  onChange(character);
                  setOpen(false);
                  setQuery("");
                }}
              >
                {character}
              </button>
            ))}
          </div>
          {options.length === 0 && <p className="character-picker-empty">Aucun personnage trouvé.</p>}
        </div>
      )}
    </div>
  );
}
