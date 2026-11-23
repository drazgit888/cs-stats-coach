"""Guards for the v7 changes: best/worst game, map details, teammates and tactics.
Every number must come from the matches themselves; nothing is invented."""
import json

import pandas as pd
import pytest

from helpers import build_test_payload, fake_faceit_matches, load_app


@pytest.fixture(scope="module")
def app():
    return load_app()


@pytest.fixture(scope="module")
def rich():
    return build_test_payload(with_steam=True, rich=True)


@pytest.fixture(scope="module")
def plain():
    return build_test_payload()


def test_payload_with_new_fields_is_valid_json(rich):
    json.dumps(rich, allow_nan=False)


def test_best_and_worst_use_kd_then_adr(app):
    m = app["tidy_matches"](fake_faceit_matches())
    bw = app["best_and_worst"](m)
    assert bw["best"]["kd"] == round(m["kd"].max(), 2)
    assert bw["worst"]["kd"] == round(m["kd"].min(), 2)
    assert bw["rule"] == "K/D, then ADR"


def test_best_and_worst_tie_break_on_adr(app):
    rows = fake_faceit_matches(n=3)
    for r, adr in zip(rows, ("70.0", "95.0", "50.0")):
        r.update({"Kills": "10", "Deaths": "10", "K/D Ratio": "1.00", "ADR": adr})
    bw = app["best_and_worst"](app["tidy_matches"](rows))
    assert bw["best"]["adr"] == 95.0 and bw["worst"]["adr"] == 50.0


def test_map_details_match_the_raw_games(app):
    m = app["tidy_matches"](fake_faceit_matches())
    details = app["map_details"](m)
    assert set(details) == set(m["map"].astype(str))
    for name, d in details.items():
        g = m[m["map"] == name]
        assert d["games"] == len(g) and d["wins"] == int(g["won"].sum()) and d["losses"] == len(g) - d["wins"]
        assert len(d["recent"]) == min(5, len(g)) and all(r["map"] == name for r in d["recent"])
        assert d["tip"]


def test_map_tip_needs_enough_games(app):
    rows = fake_faceit_matches(n=12)
    rows[0]["Map"] = "de_vertigo"  # only one game on this map
    d = app["map_details"](app["tidy_matches"](rows))
    assert "no advice yet" in d[[k for k in d if "ertigo" in k][0]]["tip"]


def test_partners_need_two_games_and_have_level_and_link(plain):
    assert plain["partners"]
    for mate in plain["partners"]:
        assert mate["games"] >= 2 and 0 <= mate["wins"] <= mate["games"]
        assert mate["url"] == f"https://www.faceit.com/en/players/{mate['name']}"
        assert mate["level"] in (2, 3, 4, 5)


def test_partners_without_level_column(app):
    mates = pd.DataFrame({"match_id": ["a", "b"], "teammate": ["x", "x"], "won": [True, False], "kd": [1.0, 0.5]})
    assert app["partners"](mates)[0]["level"] is None


def test_tactics_empty_when_faceit_sends_no_style_fields(plain):
    assert plain["tactics"] == []  # plain test matches have no entry/clutch/flash fields


def test_tactics_are_counted_from_the_fields(app, rich):
    rows = fake_faceit_matches(rich=True)
    entry = next(t for t in rich["tactics"] if t["key"] == "entry")
    won = sum(int(r["Entry Wins"]) for r in rows)
    taken = sum(int(r["Entry Count"]) for r in rows)
    assert entry["value"] == round(won / taken, 2)
    assert f"({won} of {taken})" in entry["how"]
    assert all(t["how"] for t in rich["tactics"])
    assert {t["key"] for t in rich["tactics"]} <= {"entry", "clutch", "flash", "util", "multi", "awp"}
    assert "awp" not in {t["key"] for t in rich["tactics"]}  # no sniper field in the test data, so no card


def test_premier_summary_only_counts_premier_games(rich):
    from helpers import FAKE_LEETIFY_MATCHES
    ps = rich["leetify"]["premier_stats"]
    prem = [m for m in FAKE_LEETIFY_MATCHES if m["data_source"] == "matchmaking" and "rounds_won" in m["stats"][0]]
    assert ps["games"] == len(prem)
    assert ps["wins"] == sum(m["stats"][0]["rounds_won"] > m["stats"][0]["rounds_lost"] for m in prem)
    k = sum(m["stats"][0]["total_kills"] for m in prem)
    d = sum(m["stats"][0]["total_deaths"] for m in prem)
    assert ps["kd"] == round(k / d, 2)
    assert sum(v["games"] for v in ps["maps"].values()) == ps["games"]


def test_leetify_ratings_in_rows_unchanged(rich):
    from helpers import FAKE_LEETIFY_MATCHES
    for row, src in zip(rich["leetify"]["matches"], FAKE_LEETIFY_MATCHES):
        assert row["leetify_rating"] == src["stats"][0]["leetify_rating"]


def test_steam_two_week_hours_never_reach_the_page(rich):
    assert "2weeks" not in json.dumps(rich["steam"])


def test_tod_has_kd(rich):
    assert all("kd" in t for t in rich["tod"])
