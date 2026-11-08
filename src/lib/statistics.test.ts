import { describe, expect, it } from "vitest";
import { buildStatistics } from "./statistics";
import type { DuelRecord } from "../types";

const game = (
  id: number,
  playedOn: string,
  duration: number,
  winner: DuelRecord["winner"],
  claireCharacter = "Maléfique",
  maxenceCharacter = "Jafar",
): DuelRecord => ({
  id,
  played_on: playedOn,
  duration_minutes: duration,
  claire_character: claireCharacter,
  maxence_character: maxenceCharacter,
  winner,
  claire_comment: "",
  maxence_comment: "",
  created_at: `${playedOn}T12:00:00Z`,
});

describe("buildStatistics", () => {
  it("summarizes draws, durations, characters, and players", () => {
    const stats = buildStatistics([
      game(3, "2026-11-03", 60, "player1"),
      game(2, "2026-11-02", 90, "draw", "Jafar", "Maléfique"),
      game(1, "2026-10-31", 30, "player2", "Ursula", "Maléfique"),
    ]);

    expect(stats.totalGames).toBe(3);
    expect(stats.draws).toBe(1);
    expect(stats.drawRate).toBe(33);
    expect(stats.averageDuration).toBe(60);
    expect(stats.averageDrawDuration).toBe(90);
    expect(stats.averageDecisiveDuration).toBe(45);
    expect(stats.leader).toBeNull();
    expect(stats.winMargin).toBe(0);
    expect(stats.players.map(player => player.wins)).toEqual([1, 1]);
    expect(stats.topDrawCharacterPairings[0]).toEqual({
      names: ["Jafar", "Maléfique"],
      games: 1,
    });
  });

  it("returns valid empty statistics without duels", () => {
    const stats = buildStatistics([]);

    expect(stats.totalGames).toBe(0);
    expect(stats.drawRate).toBe(0);
    expect(stats.characters).toEqual([]);
    expect(stats.averageDuration).toBeNull();
    expect(stats.busiestDay).toBeNull();
  });

  it("keeps the most recent 12 active months in chronological order", () => {
    const games = Array.from({ length: 14 }, (_, index) => {
      const date = new Date(Date.UTC(2025, index, 1));
      return game(index + 1, date.toISOString().slice(0, 10), 45, "player1");
    }).reverse();

    const stats = buildStatistics(games);

    expect(stats.monthlyActivity).toHaveLength(12);
    expect(stats.monthlyActivity[0].label).toBe("Mars 2025");
    expect(stats.monthlyActivity[11].label).toBe("Février 2026");
  });
});
