export type DuelWinner = "player1" | "player2" | "draw";

export interface DuelRecord {
  id: number;
  played_on: string;
  duration_minutes: number;
  claire_character: string;
  maxence_character: string;
  winner: DuelWinner;
  claire_comment: string;
  maxence_comment: string;
  created_at: string;
}

export interface DuelFormValues {
  played_on: string;
  duration_minutes: string;
  claire_character: string;
  maxence_character: string;
  winner: DuelWinner | "";
  claire_comment: string;
  maxence_comment: string;
}

export const PLAYERS = ["Claire", "Maxence"] as const;
export const GAMES_PER_PAGE = 3;

export function newDuelFormValues(): DuelFormValues {
  const today = new Date();
  const playedOn = [
    today.getFullYear(),
    String(today.getMonth() + 1).padStart(2, "0"),
    String(today.getDate()).padStart(2, "0"),
  ].join("-");
  return {
    played_on: playedOn,
    duration_minutes: "",
    claire_character: "",
    maxence_character: "",
    winner: "",
    claire_comment: "",
    maxence_comment: "",
  };
}

export function toDuelFormValues(game: DuelRecord): DuelFormValues {
  return {
    played_on: game.played_on,
    duration_minutes: String(game.duration_minutes),
    claire_character: game.claire_character,
    maxence_character: game.maxence_character,
    winner: game.winner,
    claire_comment: game.claire_comment,
    maxence_comment: game.maxence_comment,
  };
}
