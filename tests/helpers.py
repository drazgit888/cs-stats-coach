"""Test helpers: load app.py's functions without running the Streamlit page,
and build clearly fake sample data. Nothing here touches the network."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKER = "# ---------- The page ----------"


def load_app():
    """Run app.py up to the page section and return its functions."""
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    ns = {"__file__": str(ROOT / "app.py"), "__name__": "app_under_test"}
    exec(compile(source.split(MARKER)[0], "app.py", "exec"), ns)
    return ns


def fake_faceit_matches(n=40, seed=7, rich=False):
    """Fake FACEIT /games/cs2/stats rows (TEST DATA, not real matches)."""
    rnd = random.Random(seed)
    maps = ["de_mirage", "de_inferno", "de_ancient", "de_nuke", "de_anubis"]
    rows, t = [], 1_760_000_000
    for i in range(n):
        k, d = rnd.randint(8, 28), rnd.randint(10, 22)
        t += rnd.randint(3_000, 90_000)
        rows.append({"Match Id": f"test-{i}", "Map": rnd.choice(maps), "Result": str(rnd.randint(0, 1)),
                     "Kills": str(k), "Deaths": str(d), "Assists": str(rnd.randint(1, 8)),
                     "K/D Ratio": f"{k / d:.2f}", "Headshots %": str(rnd.randint(25, 60)),
                     "ADR": f"{rnd.uniform(55, 110):.1f}", "Match Finished At": str(t * 1000),
                     "Score": f"{13 if rnd.random() > .5 else rnd.randint(5, 12)} / {rnd.randint(5, 13)}"})
        if rich:  # optional CS2 fields, only in the "rich" test set
            ec = rnd.randint(1, 8)
            rows[-1].update({"Entry Count": str(ec), "Entry Wins": str(rnd.randint(0, ec)), "1v1Count": str(rnd.randint(0, 2)),
                             "1v1Wins": "0", "Triple Kills": str(rnd.randint(0, 2)), "Quadro Kills": "0", "Penta Kills": "0",
                             "Utility Damage": str(rnd.randint(0, 60)), "Flash Count": str(rnd.randint(2, 10)),
                             "Flash Successes": str(rnd.randint(0, 2))})
    return rows


FAKE_PLAYER = {"player_id": "test-player", "nickname": "busiks1", "avatar": "", "country": "nl",
               "faceit_url": "https://www.faceit.com/{lang}/players/busiks1",
               "games": {"cs2": {"skill_level": 3, "faceit_elo": 888, "game_player_id": "76561198000000001"}}}

FAKE_LEETIFY_PROFILE = {
    "name": "busiks1", "privacy_mode": "public", "total_matches": 140, "winrate": 0.52,
    "first_match_date": "2024-01-02T10:00:00Z", "steam64_id": "76561198000000001",
    "ranks": {"leetify": 1.23, "premier": 11234, "faceit": 3, "faceit_elo": 888, "wingman": None, "renown": None,
              "competitive": [{"map_name": "de_mirage", "rank": 9}, {"map_name": "de_inferno", "rank": 7}]},
    "rating": {"aim": 61.2, "positioning": 48, "utility": 40.5, "clutch": 0.11, "opening": -0.02},
    "recent_matches": [],
}
FAKE_LEETIFY_MATCHES = [{"finished_at": "2026-11-19T20:00:00Z", "map_name": "de_mirage", "data_source": "matchmaking",
                         "team_scores": [{"score": 13}, {"score": 9}],
                         "stats": [{"steam64_id": "76561198000000001", "total_kills": 21, "total_deaths": 15,
                                    "kd_ratio": 1.4, "leetify_rating": 0.05, "reaction_time": 0.612,
                                    "preaim": 9.87, "flashbang_hit_foe": 7, "trade_kills_success_percentage": 0.333,
                                    "utility_on_death_avg": 145.5, "some_new_field": 1}]}]


class FakeResponse:
    def __init__(self, status, body):
        self.status_code, self._body = status, body

    def json(self):
        return json.loads(json.dumps(self._body))


class FakeLeetifySession:
    """Answers like Leetify would, and remembers every request it got."""

    def __init__(self, status=200):
        self.status, self.calls = status, []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append({"url": url, "params": params, "headers": headers})
        if self.status != 200:
            return FakeResponse(self.status, {})
        if url.endswith("/v3/profile"):
            return FakeResponse(200, FAKE_LEETIFY_PROFILE)
        if url.endswith("/v3/profile/matches"):
            return FakeResponse(200, FAKE_LEETIFY_MATCHES)
        return FakeResponse(200, {})


FAKE_STEAM_SUMMARY = {"response": {"players": [{
    "steamid": "76561198000000001", "personaname": "busiks1", "profileurl": "https://steamcommunity.com/id/test/",
    "avatarfull": "", "communityvisibilitystate": 3, "loccountrycode": "NL", "timecreated": 1500000000}]}}
FAKE_STEAM_GAMES = {"response": {"game_count": 1, "games": [
    {"appid": 730, "name": "Counter-Strike 2", "playtime_forever": 12645, "playtime_2weeks": 754}]}}


class FakeSteamSession:
    """Answers like the Steam Web API would. games=None means game details are private."""

    def __init__(self, status=200, games=FAKE_STEAM_GAMES, players=FAKE_STEAM_SUMMARY, raise_exc=None):
        self.status, self.games, self.players, self.raise_exc, self.calls = status, games, players, raise_exc, []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append({"url": url, "params": params, "headers": headers})
        if self.raise_exc:
            raise self.raise_exc
        if self.status != 200:
            return FakeResponse(self.status, {})
        if "GetPlayerSummaries" in url:
            return FakeResponse(200, self.players)
        if "GetOwnedGames" in url:
            return FakeResponse(200, self.games if self.games is not None else {"response": {}})
        return FakeResponse(200, {})


def build_test_payload(with_leetify=True, with_steam=False, steam_session=None, rich=False):
    import pandas as pd
    from sources import load_leetify

    app = load_app()
    matches = app["tidy_matches"](fake_faceit_matches(rich=rich))
    rnd = random.Random(3)
    levels = {"mate_a": 4, "mate_b": 3, "mate_c": 5, "rando": 2}
    rows = []
    for m in matches["match_id"]:
        name = rnd.choice(list(levels))
        rows.append({"match_id": m, "teammate": name, "mate_id": f"id-{name}", "mate_level": levels[name]})
    mates = pd.DataFrame(rows).merge(matches[["match_id", "won", "kd"]], on="match_id")
    payload = app["build_payload"](FAKE_PLAYER, FAKE_PLAYER["games"]["cs2"], matches, mates)
    if with_leetify:
        payload["leetify"] = load_leetify("76561198000000001", api_key="SECRET-TEST-KEY",
                                          steam_id_from="Secrets", session=FakeLeetifySession())
    if with_steam:
        from sources import load_steam
        payload["steam"] = load_steam("76561198000000001", api_key="STEAM-SECRET-KEY", steam_id_from="Secrets",
                                      session=steam_session or FakeSteamSession())
    return payload


def render(payload):
    html = (ROOT / "dashboard.html").read_text(encoding="utf-8")
    return html.replace("__DATA__", json.dumps(payload).replace("</", "<\\/"))
