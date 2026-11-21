"""Steam: fresh profile + CS2 hours, key never leaves the server, errors never raise."""
import json

import pytest
import requests

from helpers import FakeSteamSession, build_test_payload, render
from sources import load_steam

SID = "76561198000000001"
KEY = "STEAM-SECRET-KEY"


def test_profile_and_cs2_hours():
    out = load_steam(SID, api_key=KEY, session=FakeSteamSession())
    assert out["status"] == "ok"
    assert out["profile"]["name"] == "busiks1" and out["profile"]["public"] is True
    assert out["cs2"]["found"] is True
    assert out["cs2"]["minutes_total"] == 12645 and out["cs2"]["hours_total"] == 210.8
    assert out["cs2"]["minutes_2weeks"] == 754 and out["cs2"]["hours_2weeks"] == 12.6


def test_key_never_in_result_or_page():
    payload = build_test_payload(with_steam=True)
    assert KEY not in json.dumps(payload["steam"])
    assert KEY not in render(payload)


def test_key_sent_only_to_steam():
    session = FakeSteamSession()
    load_steam(SID, api_key=KEY, session=session)
    assert session.calls and all(c["url"].startswith("https://api.steampowered.com/") for c in session.calls)


def test_private_game_details():
    out = load_steam(SID, api_key=KEY, session=FakeSteamSession(games=None))
    assert out["status"] == "ok" and out["games_visible"] is False
    assert out["cs2"]["hours_total"] is None and "Public" in out["games_message"]


def test_cs2_not_in_library():
    out = load_steam(SID, api_key=KEY, session=FakeSteamSession(games={"response": {"games": []}}))
    assert out["cs2"]["found"] is False and out["cs2"]["hours_total"] is None


def test_unknown_steam_id():
    out = load_steam(SID, api_key=KEY, session=FakeSteamSession(players={"response": {"players": []}}))
    assert out["status"] == "error" and out["profile"] is None


@pytest.mark.parametrize("status", [401, 403, 429, 500])
def test_http_errors_never_raise(status):
    out = load_steam(SID, api_key=KEY, session=FakeSteamSession(status=status))
    assert out["status"] == "error" and out["message"] and KEY not in out["message"]


@pytest.mark.parametrize("exc", [requests.Timeout(f"url?key={KEY}"), requests.ConnectionError(f"url?key={KEY}")])
def test_network_errors_hide_raw_text(exc):
    out = load_steam(SID, api_key=KEY, session=FakeSteamSession(raise_exc=exc))
    assert out["status"] == "error" and KEY not in json.dumps(out)


def test_no_key_or_no_id():
    assert load_steam(SID, api_key=None)["message"].startswith("No Steam key")
    assert load_steam("", api_key=KEY)["message"].startswith("No Steam ID")
