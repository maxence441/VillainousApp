from collections import Counter, defaultdict
from statistics import median
from typing import Any

from flask import Blueprint, current_app, render_template

from python_app.database import PLAYER_NAMES, list_games

stats = Blueprint("stats", __name__, url_prefix="/stats")

MONTH_NAMES = (
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
)
WEEKDAY_NAMES = (
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
)


def _build_statistics(games: list[dict[str, Any]]) -> dict[str, Any]:
    character_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"name": "", "games": 0, "wins": 0, "losses": 0, "draws": 0}
    )
    player_stats = {
        name: {
            "name": name,
            "games": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "characters": Counter(),
            "character_wins": Counter(),
        }
        for name in PLAYER_NAMES
    }
    draw_character_pairings: Counter[tuple[str, str]] = Counter()
    month_counts: Counter[tuple[int, int]] = Counter()
    monthly_draw_counts: Counter[tuple[int, int]] = Counter()
    weekday_counts: Counter[int] = Counter()
    day_counts: Counter[Any] = Counter()
    durations: list[int] = []
    draw_durations: list[int] = []
    decisive_durations: list[int] = []
    draws = 0
    comments = 0

    for game in games:
        players = game["players"]
        played_on = game["played_on"]
        month_counts[(played_on.year, played_on.month)] += 1
        weekday_counts[played_on.weekday()] += 1
        day_counts[played_on] += 1

        if game["duration_minutes"] is not None:
            durations.append(game["duration_minutes"])

        characters = []
        for index, player in enumerate(players[:2]):
            name = PLAYER_NAMES[index]
            characters.append(player["character"])
            comments += bool(player.get("comment", "").strip())

            aggregate = player_stats[name]
            aggregate["games"] += 1
            aggregate[player["result"] + "s" if player["result"] != "loss" else "losses"] += 1
            aggregate["characters"][player["character"]] += 1
            if player["result"] == "win":
                aggregate["character_wins"][player["character"]] += 1

            character = character_stats[player["character"]]
            character["name"] = player["character"]
            character["games"] += 1
            character[player["result"] + "s" if player["result"] != "loss" else "losses"] += 1

        if len(players) == 2:
            if all(player["result"] == "draw" for player in players):
                draws += 1
                month_key = (played_on.year, played_on.month)
                monthly_draw_counts[month_key] += 1
                draw_character_pairings[tuple(sorted(characters))] += 1
                if game["duration_minutes"] is not None:
                    draw_durations.append(game["duration_minutes"])
            elif game["duration_minutes"] is not None:
                decisive_durations.append(game["duration_minutes"])

    for character in character_stats.values():
        character["win_rate"] = round(
            character["wins"] / character["games"] * 100
        )
        character["draw_rate"] = round(
            character["draws"] / character["games"] * 100
        )
    for player in player_stats.values():
        player["win_rate"] = (
            round(player["wins"] / player["games"] * 100)
            if player["games"]
            else 0
        )
        player["favorite_character"] = max(
            player["characters"].items(),
            key=lambda item: (item[1], item[0].casefold()),
            default=(None, 0),
        )[0]
        player["favorite_character_games"] = max(
            player["characters"].values(), default=0
        )
        player["favorite_character_wins"] = player["character_wins"].get(
            player["favorite_character"], 0
        )
        player["characters"] = dict(player["characters"])

    characters = sorted(
        character_stats.values(),
        key=lambda item: (-item["games"], -item["win_rate"], item["name"].casefold()),
    )
    best_character = max(
        (character for character in characters if character["games"] >= 3),
        key=lambda item: (item["win_rate"], item["wins"], item["games"]),
        default=None,
    )
    best_character = max(
        (character for character in characters if character["games"] >= 3),
        key=lambda item: (item["win_rate"], item["wins"], item["games"]),
        default=None,
    )
    most_drawn_character = max(
        (character for character in characters if character["games"] >= 3),
        key=lambda item: (item["draw_rate"], item["draws"], item["games"]),
        default=None,
    )
    players = list(player_stats.values())
    leader = max(players, key=lambda item: item["wins"])
    player_wins = [player["wins"] for player in players]
    win_margin = abs(player_wins[0] - player_wins[1])
    longest_streaks = {name: 0 for name in PLAYER_NAMES}
    running_streaks = {name: 0 for name in PLAYER_NAMES}
    ordered_games = sorted(games, key=lambda game: (game["played_on"], game["id"]))
    for game in ordered_games:
        for index, player in enumerate(game["players"][:2]):
            name = PLAYER_NAMES[index]
            if player["result"] == "win":
                running_streaks[name] += 1
                longest_streaks[name] = max(
                    longest_streaks[name], running_streaks[name]
                )
            else:
                running_streaks[name] = 0
    for player in players:
        player["longest_win_streak"] = longest_streaks[player["name"]]
        player["current_win_streak"] = running_streaks[player["name"]]
    monthly_activity = [
        {
            "label": f"{MONTH_NAMES[month - 1].capitalize()} {year}",
            "games": count,
            "draws": monthly_draw_counts[(year, month)],
        }
        for (year, month), count in sorted(month_counts.items())[-12:]
    ]
    max_monthly_games = max(
        (month["games"] for month in monthly_activity), default=0
    )
    weekdays = [
        {"name": name, "games": weekday_counts[index]}
        for index, name in enumerate(WEEKDAY_NAMES)
    ]
    max_weekday_games = max((day["games"] for day in weekdays), default=0)

    return {
        "total_games": len(games),
        "draws": draws,
        "draw_rate": round(draws / len(games) * 100) if games else 0,
        "decisive_games": len(games) - draws,
        "leader": leader["name"] if win_margin else None,
        "win_margin": win_margin,
        "characters": characters,
        "most_played_character": characters[0] if characters else None,
        "best_character": best_character,
        "most_drawn_character": most_drawn_character,
        "players": players,
        "comments": comments,
        "active_days": len(day_counts),
        "top_draw_character_pairings": [
            {"names": pairing, "games": count}
            for pairing, count in draw_character_pairings.most_common(5)
        ],
        "durations": durations,
        "average_duration": round(sum(durations) / len(durations)) if durations else None,
        "draw_durations": draw_durations,
        "average_draw_duration": (
            round(sum(draw_durations) / len(draw_durations))
            if draw_durations
            else None
        ),
        "average_decisive_duration": (
            round(sum(decisive_durations) / len(decisive_durations))
            if decisive_durations
            else None
        ),
        "median_duration": median(durations) if durations else None,
        "total_duration": sum(durations),
        "shortest_duration": min(durations) if durations else None,
        "longest_duration": max(durations) if durations else None,
        "first_game": min((game["played_on"] for game in games), default=None),
        "last_game": max((game["played_on"] for game in games), default=None),
        "busiest_day": max(day_counts.items(), key=lambda item: item[1], default=None),
        "monthly_activity": monthly_activity,
        "max_monthly_games": max_monthly_games,
        "weekdays": weekdays,
        "max_weekday_games": max_weekday_games,
    }


@stats.get("")
def index() -> str:
    games = list_games(current_app.config["DATABASE_URL"])
    return render_template("stats.html", stats=_build_statistics(games))
