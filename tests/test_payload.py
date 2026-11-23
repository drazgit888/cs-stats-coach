"""Guards for the v5 redesign: the page still gets every field it uses,
no secret ever reaches the page, and Leetify values pass through unchanged."""
import json
import re

import pytest

from helpers import ROOT, FAKE_LEETIFY_PROFILE, FakeLeetifySession, build_test_payload, render

# Every top-level field dashboard.html reads (D.<name>)
PAGE_FIELDS = {"player", "summary", "kd", "insights", "maps", "hours", "heat",
               "friends", "points", "recent", "shots", "min_games", "loaded",
               "best_worst", "map_details", "partners", "tactics"}


@pytest.fixture(scope="module")
def payload():
    return build_test_payload()


def test_payload_has_every_field_the_page_reads(payload):
    used = set(re.findall(r"\bD\.([a-z_]+)", (ROOT / "dashboard.html").read_text(encoding="utf-8")))
    assert used - {"leetify", "steam", "faceit_check"} <= set(payload), used - set(payload)
    assert PAGE_FIELDS <= set(payload)


def test_existing_fields_unchanged(payload):
    assert payload["player"]["level"] == 3 and payload["player"]["elo"] == 888
    assert payload["player"]["to_next"] == 13
    for key in ("matches", "wins", "losses", "win_rate", "kd", "hs", "adr", "streak_text"):
        assert key in payload["summary"]
    assert payload["summary"]["matches"] == len(payload["trend"]) == len(payload["kd"])


def test_new_profile_fields(payload):
    assert payload["player"]["country"] == "NL"
    assert payload["player"]["steam_id64"] == "76561198000000001"
    t = payload["trend"][0]
    assert set(t) == {"n", "kd", "adr", "hs", "won", "map"}


def test_won_is_a_real_boolean(payload):
    # JS treats the string "False" as true, so results must be real booleans
    for row in payload["trend"] + payload["kd"] + payload["recent"]:
        assert isinstance(row["won"], bool)


def test_trend_matches_raw_numbers(payload):
    by_n = {r["n"]: r for r in payload["kd"]}
    for t in payload["trend"]:
        assert t["kd"] == by_n[t["n"]]["kd"]


def test_payload_is_valid_json_without_nan(payload):
    text = json.dumps(payload, allow_nan=False)
    assert "NaN" not in text


def test_no_api_key_in_page(payload):
    page = render(payload)
    assert "SECRET-TEST-KEY" not in page
    assert "_leetify_key" not in page
    assert "__DATA__" not in page


def test_leetify_values_pass_through_unchanged(payload):
    lt = payload["leetify"]
    assert lt["status"] == "ok"
    assert lt["profile"]["rating"] == FAKE_LEETIFY_PROFILE["rating"]
    ranks = {k: v for k, v in FAKE_LEETIFY_PROFILE["ranks"].items() if k != "competitive"}
    assert lt["profile"]["ranks"] == ranks
    assert lt["profile"]["winrate"] == 0.52  # not turned into 52


def test_leetify_game_fields_pass_through_unchanged(payload):
    game = payload["leetify"]["matches"][0]["game"]
    assert game == {"leetify_rating": 0.05, "reaction_time": 0.612, "preaim": 9.87, "flashbang_hit_foe": 7,
                    "trade_kills_success_percentage": 0.333, "utility_on_death_avg": 145.5}
    html = (ROOT / "dashboard.html").read_text(encoding="utf-8")
    assert "raw(m.game[k])" in html  # shown only through raw()


def test_leetify_badge_files_unmodified_and_used():
    lt = build_test_payload()["leetify"]
    import base64
    raw = (ROOT / "assets" / "leetify" / "Leetify Badge White Small.png").read_bytes()
    assert lt["badge_small"] == "data:image/png;base64," + base64.b64encode(raw).decode()


def test_leetify_key_only_in_header():
    from sources import load_leetify
    session = FakeLeetifySession()
    out = load_leetify("76561198000000001", api_key="SECRET-TEST-KEY", session=session)
    assert "SECRET-TEST-KEY" not in json.dumps(out)
    for call in session.calls:
        assert "SECRET-TEST-KEY" not in call["url"] and "SECRET-TEST-KEY" not in json.dumps(call["params"])


@pytest.mark.parametrize("status", [401, 404, 429, 500])
def test_leetify_errors_never_raise(status):
    from sources import load_leetify
    out = load_leetify("76561198000000001", api_key="k", session=FakeLeetifySession(status))
    assert out["status"] == "error" and out["profile"] is None and out["message"]


def test_no_caching_of_leetify():
    src = (ROOT / "sources.py").read_text(encoding="utf-8")
    assert "cache" not in src.replace("no caching", "").replace("No caching", "").replace("caching or storing", "")


def test_page_uses_avatar_palette_and_orange_only_for_faceit():
    html = (ROOT / "dashboard.html").read_text(encoding="utf-8")
    for token in ("--bg: #0E0B11", "--pink: #FF4FA3", "--faceit: #FF5500", "--premier: #4FD1E8"):
        assert token in html
    assert "#ff7a00" not in html.lower() and "255,122,0" not in html  # old orange is gone
    assert "--orange" not in html


def test_leetify_ratings_shown_as_returned_with_badge():
    # Leetify ratings are shown on the site, but only through raw() (no rounding, rescaling or maths)
    html = (ROOT / "dashboard.html").read_text(encoding="utf-8")
    assert "raw(LR[k])" in html and "raw(m.leetify_rating)" in html
    assert "Data Provided by Leetify" in html  # badge stays wherever Leetify data is shown
    for bad in ("LR[k] *", "LR[k] /", "LR[k].toFixed", "leetify_rating *", "leetify_rating.toFixed"):
        assert bad not in html


def test_every_page_has_a_glossary_and_tooltips():
    html = (ROOT / "dashboard.html").read_text(encoding="utf-8")
    assert "${glossary(id)}" in html and 'class="tt"' in html
    for term in ("K/D", "ADR", "HS%", "Elo"):
        assert f'["{term}",' in html


def test_insights_are_concrete(payload):
    assert payload["insights"], "test data should produce at least one insight"
    for i in payload["insights"]:
        assert set(i) >= {"icon", "title", "html", "action", "games"}
        assert i["games"] >= 3 and any(ch.isdigit() for ch in i["html"])


def test_profile_without_steam_says_not_connected(payload):
    assert "steam" not in payload  # no STEAM_API_KEY -> no Steam data at all
    html = (ROOT / "dashboard.html").read_text(encoding="utf-8")
    assert "Not connected" in html


def _matches(rows):
    import pandas as pd
    from helpers import load_app
    app = load_app()
    raw = [{"Match Id": f"m{i}", "Map": mp, "Result": "1" if won else "0", "Kills": str(k), "Deaths": str(d),
            "Assists": "3", "K/D Ratio": f"{k / d:.2f}", "Headshots %": "40", "ADR": str(adr),
            "Match Finished At": str(ts * 1000)} for i, (mp, won, k, d, adr, ts) in enumerate(rows)]
    return app, app["tidy_matches"](raw), pd.DataFrame(columns=["match_id", "teammate", "won", "kd"])


def test_insight_losses_from_dying_more():
    rows = []
    t = 1_760_000_000
    for i in range(12):
        won = i % 2 == 0
        rows.append(("de_mirage", won, 18 if won else 17, 12 if won else 20, 80, t + i * 86_400))
    app, m, mates = _matches(rows)
    titles = [i["title"] for i in app["coach_insights"](m, mates)]
    assert "Your losses come from dying more" in titles


def test_insight_hardest_map_needs_three_games():
    t = 1_760_000_000
    rows = [("de_inferno", False, 10, 20, 50, t), ("de_inferno", False, 10, 20, 50, t + 86_400)] + \
           [("de_mirage", True, 20, 10, 90, t + (i + 2) * 86_400) for i in range(6)]
    app, m, mates = _matches(rows)
    assert not any("Inferno" in i["title"] for i in app["coach_insights"](m, mates))  # only 2 Inferno games


def test_data_check_lists_names_only():
    from sources import load_leetify
    from helpers import FakeLeetifySession
    out = load_leetify("76561198000000001", api_key="k", session=FakeLeetifySession())
    c = out["check"]
    assert c["my_stat_fields"] == sorted(["kd_ratio", "leetify_rating", "steam64_id", "total_deaths", "total_kills", "reaction_time",
                                          "preaim", "flashbang_hit_foe", "trade_kills_success_percentage", "utility_on_death_avg", "some_new_field"])
    assert c["data_sources"] == ["matchmaking"]
    assert all(isinstance(x, str) for x in c["my_stat_fields"])
