import type { DuelRecord } from "../types";

const monthNames = [
  "janvier",
  "février",
  "mars",
  "avril",
  "mai",
  "juin",
  "juillet",
  "août",
  "septembre",
  "octobre",
  "novembre",
  "décembre",
];
const weekdayNames = [
  "Lundi",
  "Mardi",
  "Mercredi",
  "Jeudi",
  "Vendredi",
  "Samedi",
  "Dimanche",
];

export interface CharacterStatistic {
  name: string;
  games: number;
  wins: number;
  draws: number;
  winRate: number;
  drawRate: number;
}

export interface Statistics {
  totalGames: number;
  draws: number;
  drawRate: number;
  decisiveGames: number;
  leader: string | null;
  winMargin: number;
  characters: CharacterStatistic[];
  mostPlayedCharacter: CharacterStatistic | null;
  bestCharacter: CharacterStatistic | null;
  mostDrawnCharacter: CharacterStatistic | null;
  totalDuration: number;
  averageDuration: number | null;
  averageDrawDuration: number | null;
  averageDecisiveDuration: number | null;
  medianDuration: number | null;
  shortestDuration: number | null;
  longestDuration: number | null;
  firstGame: string | null;
  lastGame: string | null;
  busiestDay: { date: string; games: number } | null;
  activeDays: number;
  comments: number;
  monthlyActivity: { label: string; games: number; draws: number }[];
  maxMonthlyGames: number;
  weekdays: { name: string; games: number }[];
  maxWeekdayGames: number;
  players: {
    name: string;
    wins: number;
    losses: number;
    draws: number;
    favoriteCharacter: string | null;
    favoriteCharacterGames: number;
  }[];
  topDrawCharacterPairings: { names: [string, string]; games: number }[];
}

function percentage(value: number, total: number): number {
  return total ? Math.round((value / total) * 100) : 0;
}

function median(values: number[]): number | null {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2
    ? sorted[middle]
    : (sorted[middle - 1] + sorted[middle]) / 2;
}

export function buildStatistics(games: DuelRecord[]): Statistics {
  const characters = new Map<string, { games: number; wins: number; draws: number }>();
  const playerStats = [
    { name: "Claire", wins: 0, losses: 0, draws: 0, characters: new Map<string, number>() },
    { name: "Maxence", wins: 0, losses: 0, draws: 0, characters: new Map<string, number>() },
  ];
  const durations: number[] = [];
  const drawDurations: number[] = [];
  const decisiveDurations: number[] = [];
  const monthCounts = new Map<string, { label: string; games: number; draws: number }>();
  const weekdayCounts = new Array(7).fill(0) as number[];
  const dayCounts = new Map<string, number>();
  const drawPairs = new Map<string, { names: [string, string]; games: number }>();
  let draws = 0;
  let comments = 0;

  for (const game of games) {
    const date = new Date(`${game.played_on}T12:00:00`);
    const monthKey = game.played_on.slice(0, 7);
    const monthEntry = monthCounts.get(monthKey) ?? {
      label: `${monthNames[date.getMonth()].replace(/^./, char => char.toUpperCase())} ${date.getFullYear()}`,
      games: 0,
      draws: 0,
    };
    monthEntry.games += 1;
    monthCounts.set(monthKey, monthEntry);
    weekdayCounts[(date.getDay() + 6) % 7] += 1;
    dayCounts.set(game.played_on, (dayCounts.get(game.played_on) ?? 0) + 1);
    durations.push(game.duration_minutes);

    const names = [game.claire_character, game.maxence_character];
    const results = game.winner === "draw"
      ? ["draw", "draw"]
      : game.winner === "player1"
        ? ["win", "loss"]
        : ["loss", "win"];
    names.forEach((name, index) => {
      const character = characters.get(name) ?? { games: 0, wins: 0, draws: 0 };
      character.games += 1;
      if (results[index] === "win") character.wins += 1;
      if (results[index] === "draw") character.draws += 1;
      characters.set(name, character);

      const player = playerStats[index];
      const resultKey = results[index] === "win"
        ? "wins"
        : results[index] === "loss"
          ? "losses"
          : "draws";
      player[resultKey] += 1;
      player.characters.set(name, (player.characters.get(name) ?? 0) + 1);
    });

    comments += Number(Boolean(game.claire_comment.trim())) + Number(Boolean(game.maxence_comment.trim()));
    if (game.winner === "draw") {
      draws += 1;
      monthEntry.draws += 1;
      drawDurations.push(game.duration_minutes);
      const sortedNames = [...names].sort((a, b) => a.localeCompare(b, "fr")) as [string, string];
      const key = sortedNames.join("\u0000");
      const pairing = drawPairs.get(key) ?? { names: sortedNames, games: 0 };
      pairing.games += 1;
      drawPairs.set(key, pairing);
    } else {
      decisiveDurations.push(game.duration_minutes);
    }
  }

  const characterRows = [...characters].map(([name, stats]) => ({
    name,
    ...stats,
    winRate: percentage(stats.wins, stats.games),
    drawRate: percentage(stats.draws, stats.games),
  })).sort((a, b) => b.games - a.games || b.winRate - a.winRate || a.name.localeCompare(b.name, "fr"));
  const qualified = characterRows.filter(character => character.games >= 3);
  const bestCharacter = [...qualified].sort((a, b) => b.winRate - a.winRate || b.wins - a.wins || b.games - a.games)[0] ?? null;
  const mostDrawnCharacter = [...qualified].sort((a, b) => b.drawRate - a.drawRate || b.draws - a.draws || b.games - a.games)[0] ?? null;
  const claireWins = playerStats[0].wins;
  const maxenceWins = playerStats[1].wins;
  const winMargin = Math.abs(claireWins - maxenceWins);
  const busiest = [...dayCounts].sort((a, b) => b[1] - a[1] || b[0].localeCompare(a[0]))[0];
  const monthlyActivity = [...monthCounts.entries()]
    .sort(([first], [second]) => first.localeCompare(second))
    .slice(-12)
    .map(([, month]) => month);

  return {
    totalGames: games.length,
    draws,
    drawRate: percentage(draws, games.length),
    decisiveGames: games.length - draws,
    leader: winMargin ? (claireWins > maxenceWins ? "Claire" : "Maxence") : null,
    winMargin,
    characters: characterRows,
    mostPlayedCharacter: characterRows[0] ?? null,
    bestCharacter,
    mostDrawnCharacter,
    totalDuration: durations.reduce((sum, duration) => sum + duration, 0),
    averageDuration: durations.length ? Math.round(durations.reduce((sum, duration) => sum + duration, 0) / durations.length) : null,
    averageDrawDuration: drawDurations.length ? Math.round(drawDurations.reduce((sum, duration) => sum + duration, 0) / drawDurations.length) : null,
    averageDecisiveDuration: decisiveDurations.length ? Math.round(decisiveDurations.reduce((sum, duration) => sum + duration, 0) / decisiveDurations.length) : null,
    medianDuration: median(durations),
    shortestDuration: durations.length ? Math.min(...durations) : null,
    longestDuration: durations.length ? Math.max(...durations) : null,
    firstGame: games.length ? [...games].sort((a, b) => a.played_on.localeCompare(b.played_on))[0].played_on : null,
    lastGame: games.length ? [...games].sort((a, b) => b.played_on.localeCompare(a.played_on))[0].played_on : null,
    busiestDay: busiest ? { date: busiest[0], games: busiest[1] } : null,
    activeDays: dayCounts.size,
    comments,
    monthlyActivity,
    maxMonthlyGames: Math.max(0, ...monthlyActivity.map(month => month.games)),
    weekdays: weekdayNames.map((name, index) => ({ name, games: weekdayCounts[index] })),
    maxWeekdayGames: Math.max(...weekdayCounts),
    players: playerStats.map(player => {
      const favorite = [...player.characters].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "fr"))[0];
      return {
        name: player.name,
        wins: player.wins,
        losses: player.losses,
        draws: player.draws,
        favoriteCharacter: favorite?.[0] ?? null,
        favoriteCharacterGames: favorite?.[1] ?? 0,
      };
    }),
    topDrawCharacterPairings: [...drawPairs.values()].sort((a, b) => b.games - a.games).slice(0, 5),
  };
}
