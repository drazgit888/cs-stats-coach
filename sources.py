"""Extra data sources for CS Stats Coach, kept separate from FACEIT.

Leetify
-------
Follows the Leetify API Developer Guidelines
(https://leetify.com/blog/leetify-api-developer-guidelines/):
  * no caching or storing: every call fetches fresh data, nothing is saved;
  * metrics are passed on exactly as the API returns them (no renaming,
    rescaling or recalculating);
  * the page shows the official "Data Provided by Leetify" badge and a
    "View on Leetify" link.

The API key (if any) is only sent in a request header. It is never put in
the page data, in error messages or in logs.
"""
import base64
from pathlib import Path

import requests

LEETIFY_BASE = "https://api-public.cs-prod.leetify.com"
LEETIFY_KEY_HEADER = "_leetify_key"
TIMEOUT_SECONDS = 10
BADGE_DIR = Path(__file__).parent / "assets" / "leetify"

# Fixed, safe messages per situation. Raw error text is never shown,
# because it could contain request details.
MESSAGES = {
    401: "Leetify rejected the API key. Check LEETIFY_API_KEY in Secrets.",
    403: "Leetify refused access to this profile.",
    404: "No Leetify profile found for this Steam ID.",
    429: "Leetify rate limit reached. Try again later.",
    "server": "Leetify is unavailable right now. Try again later.",
    "timeout": "Leetify did not answer in time. Try again later.",
    "network": "Could not reach Leetify right now.",
    "bad_json": "Leetify sent an answer the app could not read.",
    "no_steam_id": "No Steam ID available. Add STEAM_ID in Secrets.",
}


class LeetifyError(Exception):
    """A Leetify problem, carrying only a safe message and status code."""

    def __init__(self, kind):
        self.kind = kind
        super().__init__(MESSAGES.get(kind, MESSAGES["server"]))


def _get(path, params, api_key, session=None):
    """One GET request to Leetify. No retries, no caching."""
    headers = {"Accept": "application/json"}
    if api_key:
        headers[LEETIFY_KEY_HEADER] = api_key
    http = session or requests
    try:
        resp = http.get(f"{LEETIFY_BASE}{path}", params=params, headers=headers,
                        timeout=TIMEOUT_SECONDS)
    except requests.Timeout:
        raise LeetifyError("timeout") from None
    except requests.RequestException:
        raise LeetifyError("network") from None
    if resp.status_code in MESSAGES:
        raise LeetifyError(resp.status_code)
    if resp.status_code >= 400:
        raise LeetifyError("server")
    try:
        return resp.json()
    except ValueError:
        raise LeetifyError("bad_json") from None


def _badge(name):
    """The official badge file, unmodified, as a data URI for the page."""
    path = BADGE_DIR / name
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def _field_names(obj):
    if isinstance(obj, dict):
        return sorted(obj.keys())
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        return sorted(obj[0].keys())
    return []


def _my_match_row(match, steam_id):
    """Pick this player's own numbers out of one match, values as returned."""
    mine = next((p for p in match.get("stats") or []
                 if str(p.get("steam64_id")) == str(steam_id)), {})
    scores = match.get("team_scores") or []
    return {
        "finished_at": match.get("finished_at"),
        "map_name": match.get("map_name"),
        "data_source": match.get("data_source"),
        "team_scores": [s.get("score") for s in scores if isinstance(s, dict)],
        "total_kills": mine.get("total_kills"),
        "total_deaths": mine.get("total_deaths"),
        "kd_ratio": mine.get("kd_ratio"),
        "leetify_rating": mine.get("leetify_rating"),
    }


def load_leetify(steam_id, api_key=None, steam_id_from="", session=None):
    """Fetch fresh Leetify data for one Steam ID.

    Always returns a dict and never raises, so FACEIT keeps working whatever
    happens here. The dict never contains the API key.
    """
    out = {
        "enabled": True,
        "status": "error",
        "message": "",
        "steam_id": str(steam_id or ""),
        "steam_id_from": steam_id_from,
        "profile_url": f"https://leetify.com/app/profile/{steam_id}" if steam_id else "https://leetify.com/",
        "badge_small": _badge("Leetify Badge White Small.png"),
        "badge_large": _badge("Leetify Badge White Large.png"),
        "check": {"key_set": bool(api_key), "key_valid": None, "profile_found": False,
                  "premier_found": False, "competitive_ranks": 0, "matches": 0,
                  "profile_fields": [], "rank_fields": [], "match_fields": [], "my_stat_fields": [], "data_sources": []},
        "profile": None,
        "matches": [],
        "matches_message": "",
    }
    if not steam_id:
        out["message"] = MESSAGES["no_steam_id"]
        return out

    check = out["check"]
    if api_key:
        try:
            _get("/api-key/validate", None, api_key, session)
            check["key_valid"] = True
        except LeetifyError as err:
            check["key_valid"] = False if err.kind == 401 else None

    try:
        profile = _get("/v3/profile", {"steam64_id": steam_id}, api_key, session)
    except LeetifyError as err:
        out["message"] = str(err)
        return out
    if not isinstance(profile, dict):
        out["message"] = MESSAGES["bad_json"]
        return out

    ranks = profile.get("ranks") or {}
    competitive = ranks.get("competitive") or []
    check.update(profile_found=True,
                 premier_found=ranks.get("premier") is not None,
                 competitive_ranks=len(competitive) if isinstance(competitive, list) else 0,
                 profile_fields=_field_names(profile),
                 rank_fields=_field_names(ranks))
    out["profile"] = {
        "name": profile.get("name"),
        "privacy_mode": profile.get("privacy_mode"),
        "total_matches": profile.get("total_matches"),
        "winrate": profile.get("winrate"),
        "first_match_date": profile.get("first_match_date"),
        "ranks": {k: v for k, v in ranks.items() if k != "competitive"},
        "competitive": competitive if isinstance(competitive, list) else [],
        "rating": profile.get("rating") or {},
        "recent_matches": (profile.get("recent_matches") or [])[:10],
    }
    out["status"] = "ok"
    out["message"] = "Connected"

    try:
        matches = _get("/v3/profile/matches", {"steam64_id": steam_id}, api_key, session)
        if isinstance(matches, dict):  # some APIs wrap lists
            matches = matches.get("matches") or matches.get("data") or []
        if isinstance(matches, list):
            check["matches"] = len(matches)
            check["match_fields"] = _field_names(matches)
            mine = next((p for m in matches if isinstance(m, dict) for p in (m.get("stats") or [])
                         if isinstance(p, dict) and str(p.get("steam64_id")) == str(steam_id)), None)
            check["my_stat_fields"] = sorted(mine.keys()) if mine else []
            check["data_sources"] = sorted({str(m.get("data_source")) for m in matches if isinstance(m, dict)})
            out["matches"] = [_my_match_row(m, steam_id) for m in matches[:15] if isinstance(m, dict)]
    except LeetifyError as err:
        out["matches_message"] = str(err)
    return out


# ---------------------------------------------------------------------------
# Steam
# ---------------------------------------------------------------------------
# Steam Web API (https://developer.valvesoftware.com/wiki/Steam_Web_API).
# The key has to go in the URL (Steam's rule), so it is only ever used inside
# _steam_get, and no URL, raw error text or key ever goes into the result.
# Playtime is only returned when the player's "Game details" are Public.

STEAM_BASE = "https://api.steampowered.com"
CS2_APP_ID = 730

STEAM_MESSAGES = {
    "no_key": "No Steam key. Add STEAM_API_KEY in Secrets.",
    "no_steam_id": "No Steam ID available. Add STEAM_ID in Secrets.",
    401: "Steam rejected the API key. Check STEAM_API_KEY in Secrets.",
    403: "Steam rejected the API key. Check STEAM_API_KEY in Secrets.",
    429: "Steam rate limit reached. Try again later.",
    "server": "Steam is unavailable right now. Try again later.",
    "timeout": "Steam did not answer in time. Try again later.",
    "network": "Could not reach Steam right now.",
    "bad_json": "Steam sent an answer the app could not read.",
    "not_found": "Steam has no profile for this Steam ID.",
}


class SteamError(Exception):
    def __init__(self, kind):
        self.kind = kind
        super().__init__(STEAM_MESSAGES.get(kind, STEAM_MESSAGES["server"]))


def _steam_get(path, params, api_key, session=None):
    """One GET to the Steam Web API. No retries."""
    http = session or requests
    try:
        resp = http.get(f"{STEAM_BASE}{path}", params={"key": api_key, **params},
                        headers={"Accept": "application/json"}, timeout=TIMEOUT_SECONDS)
    except requests.Timeout:
        raise SteamError("timeout") from None
    except requests.RequestException:
        raise SteamError("network") from None
    if resp.status_code in STEAM_MESSAGES:
        raise SteamError(resp.status_code)
    if resp.status_code >= 400:
        raise SteamError("server")
    try:
        data = resp.json()
    except ValueError:
        raise SteamError("bad_json") from None
    if not isinstance(data, dict):
        raise SteamError("bad_json")
    return data.get("response") or {}


def _hours(minutes):
    """Steam gives minutes; shown as hours with one decimal (labelled as converted)."""
    return round(minutes / 60, 1) if isinstance(minutes, (int, float)) else None


def load_steam(steam_id, api_key=None, steam_id_from="", session=None):
    """Fetch Steam profile + CS2 playtime. Never raises, never returns the key."""
    out = {
        "enabled": True, "status": "error", "message": "",
        "steam_id": str(steam_id or ""), "steam_id_from": steam_id_from,
        "profile": None,
        "cs2": {"found": False, "hours_total": None, "hours_2weeks": None,
                "minutes_total": None, "minutes_2weeks": None},
        "games_visible": None,
        "games_message": "",
    }
    if not api_key:
        out["message"] = STEAM_MESSAGES["no_key"]
        return out
    if not steam_id:
        out["message"] = STEAM_MESSAGES["no_steam_id"]
        return out

    try:
        summary = _steam_get("/ISteamUser/GetPlayerSummaries/v2/", {"steamids": steam_id}, api_key, session)
    except SteamError as err:
        out["message"] = str(err)
        return out
    players = summary.get("players") or []
    if not players or not isinstance(players[0], dict):
        out["message"] = STEAM_MESSAGES["not_found"]
        return out
    pl = players[0]
    out["profile"] = {
        "name": pl.get("personaname"),
        "avatar": pl.get("avatarfull") or pl.get("avatarmedium") or "",
        "url": pl.get("profileurl") or f"https://steamcommunity.com/profiles/{steam_id}",
        "public": pl.get("communityvisibilitystate") == 3,
        "country": pl.get("loccountrycode"),
        "created": pl.get("timecreated"),
    }
    out["status"] = "ok"
    out["message"] = "Connected"

    try:
        owned = _steam_get("/IPlayerService/GetOwnedGames/v1/",
                           {"steamid": steam_id, "include_appinfo": 1, "include_played_free_games": 1,
                            "appids_filter[0]": CS2_APP_ID}, api_key, session)
    except SteamError as err:
        out["games_message"] = str(err)
        return out
    games = owned.get("games")
    if games is None:  # Steam sends an empty answer when game details are private
        out["games_visible"] = False
        out["games_message"] = "Steam did not share playtime. Set Game details to Public in Steam privacy settings."
        return out
    out["games_visible"] = True
    cs2 = next((g for g in games if isinstance(g, dict) and g.get("appid") == CS2_APP_ID), None)
    if cs2 is None:
        out["games_message"] = "CS2 was not found in this Steam library."
        return out
    total, recent = cs2.get("playtime_forever"), cs2.get("playtime_2weeks", 0)
    out["cs2"] = {"found": True, "minutes_total": total, "minutes_2weeks": recent,
                  "hours_total": _hours(total), "hours_2weeks": _hours(recent)}
    return out
