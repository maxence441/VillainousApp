from datetime import date
from typing import Any, Optional

import psycopg
from psycopg.rows import dict_row

PLAYER_NAMES = ("Claire", "Maxence")

SCHEMA = """
CREATE TABLE IF NOT EXISTS games (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    played_on DATE NOT NULL,
    duration_minutes INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT games_duration_minutes_check
        CHECK (duration_minutes IS NULL OR duration_minutes BETWEEN 1 AND 1440)
);

CREATE TABLE IF NOT EXISTS game_players (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    game_id BIGINT NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    seat SMALLINT NOT NULL CHECK (seat BETWEEN 1 AND 2),
    player_name TEXT NOT NULL CHECK (char_length(btrim(player_name)) BETWEEN 1 AND 80),
    character_name TEXT NOT NULL CHECK (char_length(btrim(character_name)) > 0),
    result TEXT NOT NULL,
    comment TEXT NOT NULL DEFAULT '',
    UNIQUE (game_id, seat),
    CONSTRAINT game_players_result_check CHECK (result IN ('win', 'loss', 'draw')),
    CONSTRAINT game_players_comment_check CHECK (char_length(comment) <= 1000)
);
"""

MIGRATION = """
ALTER TABLE games ADD COLUMN IF NOT EXISTS duration_minutes INTEGER;
ALTER TABLE game_players ADD COLUMN IF NOT EXISTS result TEXT;
ALTER TABLE game_players ADD COLUMN IF NOT EXISTS comment TEXT NOT NULL DEFAULT '';
"""


def _connect(database_url: str) -> psycopg.Connection[dict[str, Any]]:
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured. Start the app with Docker Compose "
            "or configure a PostgreSQL connection."
        )
    return psycopg.connect(database_url, row_factory=dict_row)


def initialize_database(database_url: str) -> None:
    with _connect(database_url) as connection:
        connection.execute(SCHEMA)
        connection.execute(MIGRATION)
        legacy_score = connection.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'game_players'
                  AND column_name = 'score'
            ) AS exists
            """
        ).fetchone()
        if legacy_score is None:
            raise RuntimeError("Could not inspect the existing score schema.")
        if legacy_score["exists"]:
            connection.execute(
                """
                UPDATE game_players AS player
                SET result = CASE
                    WHEN player.score = (
                        SELECT MAX(opponent.score)
                        FROM game_players AS opponent
                        WHERE opponent.game_id = player.game_id
                    ) THEN CASE
                        WHEN (
                            SELECT COUNT(*)
                            FROM game_players AS tied
                            WHERE tied.game_id = player.game_id
                              AND tied.score = player.score
                        ) > 1 THEN 'draw'
                        ELSE 'win'
                    END
                    ELSE 'loss'
                END
                WHERE player.result IS NULL
                """
            )
            unresolved = connection.execute(
                "SELECT EXISTS (SELECT 1 FROM game_players WHERE result IS NULL) AS exists"
            ).fetchone()
            if unresolved is None or unresolved["exists"]:
                raise RuntimeError(
                    "Legacy scores could not all be converted to duel results."
                )
            connection.execute(
                "ALTER TABLE game_players ALTER COLUMN result SET NOT NULL"
            )
            connection.execute("ALTER TABLE game_players DROP COLUMN score")
        else:
            unresolved = connection.execute(
                "SELECT EXISTS (SELECT 1 FROM game_players WHERE result IS NULL) AS exists"
            ).fetchone()
            if unresolved is None or unresolved["exists"]:
                raise RuntimeError("Some saved players have no duel result.")
            connection.execute(
                "ALTER TABLE game_players ALTER COLUMN result SET NOT NULL"
            )

        connection.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'games_duration_minutes_check'
                      AND conrelid = 'games'::regclass
                ) THEN
                    ALTER TABLE games
                        ADD CONSTRAINT games_duration_minutes_check
                        CHECK (duration_minutes IS NULL OR duration_minutes BETWEEN 1 AND 1440);
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'game_players_result_check'
                      AND conrelid = 'game_players'::regclass
                ) THEN
                    ALTER TABLE game_players
                        ADD CONSTRAINT game_players_result_check
                        CHECK (result IN ('win', 'loss', 'draw'));
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'game_players_comment_check'
                      AND conrelid = 'game_players'::regclass
                ) THEN
                    ALTER TABLE game_players
                        ADD CONSTRAINT game_players_comment_check
                        CHECK (char_length(comment) <= 1000);
                END IF;
            END;
            $$
            """
        )


def list_games(database_url: str) -> list[dict[str, Any]]:
    query = """
        SELECT
            games.id AS game_id,
            games.played_on,
            games.duration_minutes,
            game_players.character_name,
            game_players.result,
            game_players.comment,
            game_players.seat
        FROM games
        JOIN game_players ON game_players.game_id = games.id
        ORDER BY games.played_on DESC, games.id DESC, game_players.seat
    """
    with _connect(database_url) as connection:
        rows = connection.execute(query).fetchall()

    games_by_id: dict[int, dict[str, Any]] = {}
    for row in rows:
        game_id = row["game_id"]
        game = games_by_id.setdefault(
            game_id,
            {
                "id": game_id,
                "played_on": row["played_on"],
                "duration_minutes": row["duration_minutes"],
                "players": [],
            },
        )
        game["players"].append(
            {
                "name": PLAYER_NAMES[row["seat"] - 1],
                "character": row["character_name"],
                "result": row["result"],
                "comment": row["comment"],
                "seat": row["seat"],
            }
        )
    for game in games_by_id.values():
        results = [player["result"] for player in game["players"]]
        game["winner"] = (
            "draw"
            if results == ["draw", "draw"]
            else "player1"
            if results[0] == "win"
            else "player2"
        )
    return list(games_by_id.values())


def get_game(database_url: str, game_id: int) -> Optional[dict[str, Any]]:
    return next(
        (game for game in list_games(database_url) if game["id"] == game_id),
        None,
    )


def update_game(
    database_url: str,
    game_id: int,
    played_on: date,
    duration_minutes: int,
    players: list[dict[str, Any]],
) -> bool:
    if len(players) != 2:
        raise ValueError("A duel must have exactly two players.")
    results = [player["result"] for player in players]
    if results not in (["win", "loss"], ["loss", "win"], ["draw", "draw"]):
        raise ValueError("A duel must have one winner and one loser, or two draws.")
    if not 1 <= duration_minutes <= 1440:
        raise ValueError("Duel duration must be between 1 and 1440 minutes.")

    with _connect(database_url) as connection:
        game = connection.execute(
            """
            UPDATE games
            SET played_on = %s, duration_minutes = %s
            WHERE id = %s
            RETURNING id
            """,
            (played_on, duration_minutes, game_id),
        ).fetchone()
        if game is None:
            return False
        for seat, player in enumerate(players, start=1):
            updated = connection.execute(
                """
                UPDATE game_players
                SET player_name = %s, character_name = %s, result = %s, comment = %s
                WHERE game_id = %s AND seat = %s
                """,
                (
                    PLAYER_NAMES[seat - 1],
                    player["character"],
                    player["result"],
                    player["comment"],
                    game_id,
                    seat,
                ),
            )
            if updated.rowcount != 1:
                raise RuntimeError(
                    f"Expected one player at seat {seat} for duel {game_id}."
                )
    return True


def delete_game(database_url: str, game_id: int) -> bool:
    with _connect(database_url) as connection:
        deleted = connection.execute(
            "DELETE FROM games WHERE id = %s RETURNING id",
            (game_id,),
        ).fetchone()
    return deleted is not None


def save_game(
    database_url: str,
    played_on: date,
    duration_minutes: int,
    players: list[dict[str, Any]],
) -> None:
    if len(players) != 2:
        raise ValueError("A duel must have exactly two players.")
    results = [player["result"] for player in players]
    if results not in (["win", "loss"], ["loss", "win"], ["draw", "draw"]):
        raise ValueError("A duel must have one winner and one loser, or two draws.")
    if not 1 <= duration_minutes <= 1440:
        raise ValueError("Duel duration must be between 1 and 1440 minutes.")

    with _connect(database_url) as connection:
        game = connection.execute(
            """
            INSERT INTO games (played_on, duration_minutes)
            VALUES (%s, %s)
            RETURNING id
            """,
            (played_on, duration_minutes),
        ).fetchone()
        if game is None:
            raise RuntimeError("PostgreSQL did not return the new game ID.")
        game_id = game["id"]
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO game_players
                    (game_id, seat, player_name, character_name, result, comment)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                [
                    (
                        game_id,
                        seat,
                        PLAYER_NAMES[seat - 1],
                        player["character"],
                        player["result"],
                        player["comment"],
                    )
                    for seat, player in enumerate(players, start=1)
                ],
            )
