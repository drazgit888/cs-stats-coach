"""Guards for the v5 redesign: the page still gets every field it uses,
no secret ever reaches the page, and Leetify values pass through unchanged."""
import json
import re

import pytest

from helpers import ROOT, FAKE_LEETIFY_PROFILE, FakeLeetifySession, build_test_payload, render

# Every top-level field dashboard.html reads (D.<name>)
PAGE_FIELDS = {"player", "summary", "form", "tips", "kd", "maps", "tod", "hours", "heat", "squad",
               "friends", "points", "recent", "shots", "min_games", "loaded", "trend"}


@pytest.fixture(scope="module")
def payload():
    return build_test_payload()


def test_payload_has_every_field_the_page_reads(payload):
    used = set(re.findall(r"\bD\.([a-z_]+)", (ROOT / "dashboard.html").read_text(encoding="utf-8")))
    assert used - {"leetify"} <= set(payload), used - set(payload)
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


def test_page_uses_design_tokens_and_no_old_theme():
    html = (ROOT / "dashboard.html").read_text(encoding="utf-8")
    for token in ("--bg: #0E0D12", "--violet: #8B5CF6", "--faceit: #FF5500", "--leetify: #F84982"):
        assert token in html
    assert "Barlow" not in html and "function scene" not in html
    assert html.lower().count("#ff7a00") == 0  # old orange is gone


def test_profile_never_shows_steam_numbers():
    # Steam is not connected yet, so the page must not show playtime numbers
    html = (ROOT / "dashboard.html").read_text(encoding="utf-8")
    assert "Not connected" in html
    assert re.search(r"steam[^\n]*hours[^\n]*\d+\s*h", html, re.I) is None
