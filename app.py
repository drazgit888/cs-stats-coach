"""CS Stats Coach: a Streamlit dashboard for my own CS2 matches.

Data comes from the FACEIT Data API (https://docs.faceit.com/docs/data-api/).
The API key is read from Streamlit secrets (FACEIT_API_KEY) and is never
stored in this repository.
"""
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import base64
import html
import json
import re

import requests
import streamlit as st


API = "https://open.faceit.com/data/v4"
GAME = "cs2"
LOCAL_TZ = "Europe/Amsterdam"  # I play in the Netherlands
MIN_GAMES = 3  # don't draw conclusions from fewer games than this

st.set_page_config(
    page_title="CS Stats Coach", page_icon="🎯", layout="wide", initial_sidebar_state="collapsed"
)


# ---------- Getting the data ----------

def faceit_get(path, api_key, params=None):
    """Ask the FACEIT API for something and return the answer as a dict."""
    resp = requests.get(
        f"{API}{path}",
        headers={"Authorization": f"Bearer {api_key}"},
        params=params,
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=3600, show_spinner="Looking up your FACEIT profile...")
def load_player(nickname, api_key):
    return faceit_get("/players", api_key, {"nickname": nickname, "game": GAME})


@st.cache_data(ttl=3600, show_spinner="Downloading your matches...")
def load_matches(player_id, api_key, how_many=100):
    """Per-match stats for the most recent matches (FACEIT gives max 100 per call)."""
    data = faceit_get(
        f"/players/{player_id}/games/{GAME}/stats", api_key, {"limit": how_many}
    )
    return [item.get("stats", {}) for item in data.get("items", [])]


@st.cache_data(ttl=24 * 3600, show_spinner=False)
def load_match_details(match_id, api_key):
    """Who played in one match (both teams). Old matches never change, so cache for a day."""
    try:
        return faceit_get(f"/matches/{match_id}", api_key)
    except requests.RequestException:
        return {}


def find_teammates(matches, player_id, api_key):
    """One row per (match, teammate): who was on my team in each match."""
    rows = []
    ids = [m for m in matches["match_id"].dropna().unique()]
    bar = st.progress(0.0, text="Finding out who you played with...")
    for i, match_id in enumerate(ids):
        details = load_match_details(match_id, api_key)
        for team in (details.get("teams") or {}).values():
            roster = team.get("roster") or team.get("players") or []
            if any(p.get("player_id") == player_id for p in roster):
                for p in roster:
                    if p.get("player_id") != player_id:
                        rows.append({"match_id": match_id, "teammate": p.get("nickname", "?")})
        bar.progress((i + 1) / len(ids), text="Finding out who you played with...")
    bar.empty()
    mates = pd.DataFrame(rows, columns=["match_id", "teammate"])
    return mates.merge(matches[["match_id", "won", "kd"]], on="match_id")


def to_number(series):
    return pd.to_numeric(series, errors="coerce")


def time_of_day(hour):
    if 6 <= hour < 12:
        return "Morning (6-12)"
    if 12 <= hour < 18:
        return "Afternoon (12-18)"
    if 18 <= hour < 23:
        return "Evening (18-23)"
    return "Late night (23-6)"


TIME_ORDER = ["Morning (6-12)", "Afternoon (12-18)", "Evening (18-23)", "Late night (23-6)"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def tidy_matches(raw):
    """Turn the raw API answer into a clean table with one row per match."""
    df = pd.DataFrame(raw)
    if df.empty:
        return df

    clean = pd.DataFrame()
    clean["match_id"] = df.get("Match Id", pd.Series([None] * len(df)))
    clean["map"] = df.get("Map", pd.Series(["unknown"] * len(df))).fillna("unknown")
    clean["map"] = clean["map"].str.replace("de_", "", regex=False).str.title()
    clean["won"] = to_number(df.get("Result")) == 1
    for col, name in [
        ("Kills", "kills"),
        ("Deaths", "deaths"),
        ("Assists", "assists"),
        ("K/D Ratio", "kd"),
        ("Headshots %", "hs_pct"),
        ("ADR", "adr"),
    ]:
        clean[name] = to_number(df[col]) if col in df else float("nan")

    # When the match was played (FACEIT gives milliseconds or seconds)
    when = None
    for col in ["Match Finished At", "Updated At", "Created At"]:
        if col in df:
            when = df[col]
            break
    if when is not None:
        nums = to_number(when)
        if nums.notna().any():
            unit = "ms" if nums.max() > 1e11 else "s"
            clean["played_at"] = pd.to_datetime(nums, unit=unit, utc=True)
        else:
            clean["played_at"] = pd.to_datetime(when, utc=True, errors="coerce")
    else:
        clean["played_at"] = pd.NaT

    clean = clean.sort_values("played_at").reset_index(drop=True)
    clean["match_nr"] = range(1, len(clean) + 1)

    # Local time, so "late night" means late night in the Netherlands
    local = clean["played_at"].dt.tz_convert(LOCAL_TZ)
    clean["hour"] = local.dt.hour
    clean["time_of_day"] = clean["hour"].map(time_of_day, na_action="ignore")
    clean["weekday"] = local.dt.day_name()
    return clean


def summary_by(df, column, order=None):
    """Games, win rate and average K/D for each value in a column."""
    out = (
        df.groupby(column)
        .agg(games=("won", "size"), win_rate=("won", "mean"), avg_kd=("kd", "mean"))
        .reset_index()
    )
    if order:
        out[column] = pd.Categorical(out[column], categories=order, ordered=True)
        out = out.sort_values(column)
    return out


def pct(x):
    return f"{x:.0%}"


def coach_tips(matches, mates):
    """Simple rules that turn my numbers into advice. Returns (emoji, tip) pairs."""
    tips = []

    # 1. Maps
    maps = summary_by(matches, "map")
    maps = maps[maps["games"] >= MIN_GAMES].sort_values("win_rate", ascending=False)
    if len(maps) >= 2:
        best, worst = maps.iloc[0], maps.iloc[-1]
        tips.append(("🗺️", f"Your best map is **{best['map']}**: you win **{pct(best['win_rate'])}** there "
                           f"({best['games']} games). Pick it when you can."))
        if worst["win_rate"] < 0.45:
            tips.append(("🚫", f"**{worst['map']}** is your hardest map: only **{pct(worst['win_rate'])}** wins "
                               f"({worst['games']} games). Ban it, or watch a short guide for it."))

    # 2. Time of day
    times = summary_by(matches, "time_of_day", TIME_ORDER)
    times = times[times["games"] >= MIN_GAMES]
    if len(times) >= 2:
        best_t = times.sort_values("win_rate").iloc[-1]
        worst_t = times.sort_values("win_rate").iloc[0]
        if best_t["win_rate"] - worst_t["win_rate"] >= 0.10:
            tips.append(("🕒", f"You win **{pct(best_t['win_rate'])}** in the **{best_t['time_of_day'].split(' (')[0].lower()}** "
                               f"but only **{pct(worst_t['win_rate'])}** in the **{worst_t['time_of_day'].split(' (')[0].lower()}**. "
                               f"Try to play your FACEIT games at your best time."))
        else:
            tips.append(("🕒", "The time you play doesn't change your results much. Play whenever suits you!"))

    # 3. Form: last 10 games vs before
    if len(matches) >= 20:
        recent, before = matches["kd"].tail(10).mean(), matches["kd"].iloc[:-10].mean()
        if recent > before + 0.05:
            tips.append(("📈", f"You're in form! K/D in your last 10 games is **{recent:.2f}**, "
                               f"up from **{before:.2f}** before. Keep doing what you're doing."))
        elif recent < before - 0.05:
            tips.append(("📉", f"Your last 10 games went a bit worse (K/D **{recent:.2f}** vs **{before:.2f}** before). "
                               f"A short break or an aim warm-up could help."))

    # 4. Tilt: what happens in the next game (within 2 hours) after a loss?
    m = matches.dropna(subset=["played_at"]).sort_values("played_at").copy()
    m["prev_won"] = m["won"].shift()
    m["gap"] = m["played_at"].diff()
    same_session = m[m["gap"] <= pd.Timedelta(hours=2)]
    after_loss = same_session[same_session["prev_won"] == False]  # noqa: E712
    after_win = same_session[same_session["prev_won"] == True]  # noqa: E712
    if len(after_loss) >= MIN_GAMES and len(after_win) >= MIN_GAMES:
        wl, ww = after_loss["won"].mean(), after_win["won"].mean()
        if wl < ww - 0.10:
            tips.append(("😤", f"Watch out for tilt: right after a loss you win only **{pct(wl)}** of the next games, "
                               f"after a win **{pct(ww)}**. After a loss, take a 10-minute break."))
        else:
            tips.append(("🧊", f"You handle losses well: after a loss you still win **{pct(wl)}** of the next games."))

    # 5. Teammates
    if not mates.empty:
        per = mates.groupby("teammate").agg(games=("won", "size"), win_rate=("won", "mean")).reset_index()
        per = per[per["games"] >= MIN_GAMES].sort_values(["win_rate", "games"], ascending=False)
        if not per.empty and per.iloc[0]["win_rate"] > matches["won"].mean():
            b = per.iloc[0]
            tips.append(("🤝", f"Your lucky teammate is **{b['teammate']}**: you win **{pct(b['win_rate'])}** together "
                               f"({b['games']} games). Invite them more often!"))

    # 6. Aim: weakest map for headshots
    aim = matches.groupby("map").agg(games=("hs_pct", "size"), hs=("hs_pct", "mean")).reset_index()
    aim = aim[aim["games"] >= MIN_GAMES].sort_values("hs")
    if len(aim) >= 2 and aim.iloc[0]["hs"] < matches["hs_pct"].mean() - 3:
        w = aim.iloc[0]
        tips.append(("🎯", f"Your headshot % is lowest on **{w['map']}** (**{w['hs']:.0f}%** vs your usual "
                           f"**{matches['hs_pct'].mean():.0f}%**). Practise pre-aiming the common angles on that map."))

    return tips


def coach_insights(matches, mates):
    """Concrete coaching points from my own FACEIT matches.

    Every point uses only numbers FACEIT returns per match (result, kills,
    deaths, K/D, HS%, ADR, map, time, teammates), needs MIN_GAMES+ games in
    each group it compares, and says how many games it is based on.
    Returns dicts: icon, title, html (with **bold**), action, games.
    """
    out = []
    m = matches.dropna(subset=["played_at"]).sort_values("played_at").reset_index(drop=True)
    if len(m) < MIN_GAMES:
        return out
    avg = {"kd": m["kd"].mean(), "adr": m["adr"].mean(), "hs": m["hs_pct"].mean(), "deaths": m["deaths"].mean(),
           "kills": m["kills"].mean(), "wr": m["won"].mean()}

    def add(icon, title, text, action, games):
        out.append({"icon": icon, "title": title, "html": text, "action": action, "games": int(games)})

    # 1. Hardest map, with what goes wrong there
    per_map = m.groupby("map").agg(games=("won", "size"), wr=("won", "mean"), adr=("adr", "mean"),
                                   deaths=("deaths", "mean"), kd=("kd", "mean")).reset_index()
    per_map = per_map[per_map["games"] >= MIN_GAMES].sort_values(["wr", "games"])
    if len(per_map) >= 2:
        w = per_map.iloc[0]
        if w["wr"] < avg["wr"] - 0.05:
            parts = []
            if w["adr"] < avg["adr"] - 5:
                parts.append(f"your ADR there is **{w['adr']:.0f}** (usually **{avg['adr']:.0f}**)")
            if w["deaths"] > avg["deaths"] + 1:
                parts.append(f"you die **{w['deaths']:.1f}** times per game (usually **{avg['deaths']:.1f}**)")
            why = (", and " + " and ".join(parts)) if parts else ""
            add("map", f"{w['map']} is costing you games",
                f"You win **{w['wr']:.0%}** on **{w['map']}** ({int(w['games'])} games) against **{avg['wr']:.0%}** overall{why}.",
                f"Ban {w['map']} for now, or watch 2 of your own {w['map']} demos and note where you die first.", w["games"])
        b = per_map.iloc[-1]
        if b["wr"] > avg["wr"] + 0.05:
            add("star", f"{b['map']} is your map",
                f"You win **{b['wr']:.0%}** on **{b['map']}** ({int(b['games'])} games) with K/D **{b['kd']:.2f}**.",
                f"Vote {b['map']} in the map veto whenever you can.", b["games"])

    # 2. Why I lose: dying more or killing less?
    wins, losses = m[m["won"]], m[~m["won"]]
    if len(wins) >= MIN_GAMES and len(losses) >= MIN_GAMES:
        dd = losses["deaths"].mean() - wins["deaths"].mean()
        dk = wins["kills"].mean() - losses["kills"].mean()
        if dd >= dk and dd >= 1:
            add("shield", "Your losses come from dying more",
                f"In losses you die **{losses['deaths'].mean():.1f}** times per game, in wins **{wins['deaths'].mean():.1f}**. "
                f"Your kills change less (**{losses['kills'].mean():.1f}** vs **{wins['kills'].mean():.1f}**).",
                "Play for trades: stay close to a teammate and don't take the first duel alone.", len(m))
        elif dk > dd and dk >= 1:
            add("cross", "Your losses come from fewer kills",
                f"In losses you get **{losses['kills'].mean():.1f}** kills per game, in wins **{wins['kills'].mean():.1f}**. "
                f"Your deaths change less (**{losses['deaths'].mean():.1f}** vs **{wins['deaths'].mean():.1f}**).",
                "Warm up your aim for 10 minutes before the first game.", len(m))

    # 3. Late night (Dutch time) vs earlier
    late = m[(m["hour"] >= 23) | (m["hour"] < 6)]
    early = m[(m["hour"] >= 6) & (m["hour"] < 23)]
    if len(late) >= MIN_GAMES and len(early) >= MIN_GAMES:
        if early["kd"].mean() - late["kd"].mean() >= 0.1 or early["won"].mean() - late["won"].mean() >= 0.10:
            add("clock", "You play worse after 23:00",
                f"After 23:00: K/D **{late['kd'].mean():.2f}**, win rate **{late['won'].mean():.0%}** ({len(late)} games). "
                f"Before 23:00: K/D **{early['kd'].mean():.2f}**, win rate **{early['won'].mean():.0%}** ({len(early)} games).",
                "Start your last FACEIT game before 23:00.", len(m))

    # 4. Sessions: games within 2 hours of each other count as one session
    gap = m["played_at"].diff()
    session = (gap.isna() | (gap > pd.Timedelta(hours=2))).cumsum()
    m = m.assign(session=session, game_in_session=m.groupby(session).cumcount() + 1)
    first, later = m[m["game_in_session"] <= 3], m[m["game_in_session"] >= 4]
    if len(later) >= MIN_GAMES and first["won"].mean() - later["won"].mean() >= 0.10:
        add("brain", "Long sessions hurt you",
            f"Games 1 to 3 of a session: **{first['won'].mean():.0%}** wins ({len(first)} games). "
            f"Game 4 and later: **{later['won'].mean():.0%}** ({len(later)} games).",
            "Stop after 3 games in a row, or take a 15-minute break first.", len(first) + len(later))

    # 5. Tilt: the game after two losses in a row (same session)
    prev2 = (~m["won"].shift(1).fillna(True).astype(bool)) & (~m["won"].shift(2).fillna(True).astype(bool))
    same = m["session"] == m["session"].shift(2)
    after = m[prev2 & same]
    if len(after) >= MIN_GAMES and after["won"].mean() < avg["wr"] - 0.10:
        add("brain", "Two losses in a row = tilt",
            f"After two losses in a row you won **{int(after['won'].sum())} of {len(after)}** next games "
            f"(**{after['won'].mean():.0%}**, overall **{avg['wr']:.0%}**).",
            "After the second loss in a row, take a break before queueing again.", len(after))

    # 6. Form: last 10 vs before, the metric that changed most
    if len(m) >= 20:
        last, before = m.tail(10), m.iloc[:-10]
        changes = [("K/D", last["kd"].mean(), before["kd"].mean(), 0.15, "{:.2f}"),
                   ("HS%", last["hs_pct"].mean(), before["hs_pct"].mean(), 4, "{:.0f}%"),
                   ("ADR", last["adr"].mean(), before["adr"].mean(), 6, "{:.0f}")]
        changes = [c for c in changes if abs(c[1] - c[2]) >= c[3]]
        if changes:
            name, now, was, lim, fmt = max(changes, key=lambda c: abs(c[1] - c[2]) / c[3])
            up = now > was
            add("chart", f"Your {name} is {'going up' if up else 'dropping'}",
                f"Last 10 games: **{fmt.format(now)}**. The {len(before)} games before: **{fmt.format(was)}**.",
                "Keep your current routine, it is working." if up else
                ("10 minutes of aim training before you play." if name in ("HS%", "K/D") else
                 "Play more with your team: use utility before peeking to deal more damage."), len(m))

    # 7. Best teammate
    if mates is not None and not mates.empty:
        per = mates.groupby("teammate").agg(games=("won", "size"), wr=("won", "mean")).reset_index()
        per = per[per["games"] >= MIN_GAMES].sort_values(["wr", "games"], ascending=False)
        if not per.empty and per.iloc[0]["wr"] > avg["wr"] + 0.05:
            t = per.iloc[0]
            add("users", f"Queue with {t['teammate']}",
                f"With **{t['teammate']}** you won **{int(round(t['wr'] * t['games']))} of {int(t['games'])}** games "
                f"(**{t['wr']:.0%}**, overall **{avg['wr']:.0%}**).",
                f"Invite {t['teammate']} when you want to climb.", t["games"])
    return out


def secret(name, default=None):
    """Read a value from Streamlit secrets without crashing if there are none."""
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


# ---------- Building the data for the dashboard ----------

# FACEIT Elo needed for each level (level: (min, max))
LEVELS = {1: (100, 500), 2: (501, 750), 3: (751, 900), 4: (901, 1050), 5: (1051, 1200),
          6: (1201, 1350), 7: (1351, 1530), 8: (1531, 1750), 9: (1751, 2000), 10: (2001, None)}
HERE = Path(__file__).parent


def clean_num(x, digits=3):
    """JSON can't hold NaN, so turn missing numbers into None."""
    try:
        return None if pd.isna(x) else round(float(x), digits)
    except (TypeError, ValueError):
        return None


def records(df, cols):
    out = []
    for _, row in df.iterrows():
        out.append({k: (clean_num(row[c]) if isinstance(row[c], (int, float)) and not isinstance(row[c], bool)
                        else (bool(row[c]) if isinstance(row[c], bool) else str(row[c])))
                    for k, c in cols.items()})
    return out


def tip_html(text):
    safe = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)


def screenshots():
    shots = []
    for f in sorted(HERE.joinpath("assets", "screenshots").glob("*")):
        mime = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp", ".gif": "gif"}.get(f.suffix.lower())
        if mime:
            data = base64.b64encode(f.read_bytes()).decode()
            caption = f.stem.replace("-", " ").replace("_", " ").capitalize()
            shots.append({"src": f"data:image/{mime};base64,{data}", "caption": caption})
    return shots


def build_payload(player, cs2, matches, mates):
    level = cs2.get("skill_level")
    elo = cs2.get("faceit_elo")
    lo, hi = LEVELS.get(level, (None, None))
    progress = 1.0 if hi is None or elo is None or lo is None else max(0, min(1, (elo - lo) / (hi - lo + 1)))
    to_next = None if hi is None or elo is None else hi + 1 - elo

    wins = int(matches["won"].sum())
    # current streak
    streak, last = 0, None
    for w in reversed(matches["won"].tolist()):
        if last is None or w == last:
            streak, last = streak + 1, w
        else:
            break
    streak_text = f"{'🔥 ' if last else ''}{streak} {'win' if last else 'loss'}{'es' if not last and streak > 1 else ''}{'s' if last and streak > 1 else ''} in a row"

    kd = matches[["match_nr", "kd", "map", "won"]].copy()
    kd["avg10"] = matches["kd"].rolling(10, min_periods=1).mean()

    maps = summary_by(matches, "map").merge(
        matches.groupby("map").agg(hs=("hs_pct", "mean"), adr=("adr", "mean")).reset_index(), on="map"
    ).sort_values(["win_rate", "games"], ascending=False)
    maps["tag"] = ""
    enough = maps[maps["games"] >= MIN_GAMES]
    if len(enough) >= 2:
        maps.loc[enough.index[0], "tag"] = "best"
        maps.loc[enough.index[-1], "tag"] = "worst"

    tod = summary_by(matches, "time_of_day", TIME_ORDER).dropna(subset=["games"])
    tod["label"] = tod["time_of_day"].astype(str).str.split(" ").str[0] + \
        tod["time_of_day"].astype(str).str.extract(r"( night)?")[0].fillna("")
    hours = matches.groupby("hour").agg(games=("kd", "size"), kd=("kd", "mean")).reset_index()

    heat_rows = []
    for day in DAY_ORDER:
        cells = []
        for t in TIME_ORDER:
            g = matches[(matches["weekday"] == day) & (matches["time_of_day"] == t)]
            cells.append({"games": int(len(g)), "win_rate": clean_num(g["won"].mean()) if len(g) else None})
        heat_rows.append({"day": day[:3], "cells": cells})

    squad, friends = [], {"with": None, "without": None, "with_games": 0, "without_games": 0}
    if not mates.empty:
        per = (mates.groupby("teammate")
               .agg(games=("won", "size"), win_rate=("won", "mean"), kd=("kd", "mean")).reset_index())
        per = per[per["games"] >= 2].sort_values(["win_rate", "games"], ascending=False)
        squad = records(per, {"name": "teammate", "games": "games", "win_rate": "win_rate", "kd": "kd"})
        known = set(per["teammate"])
        has_friend = mates.groupby("match_id")["teammate"].apply(lambda n: any(x in known for x in n))
        m = matches.assign(friend=matches["match_id"].map(has_friend)).dropna(subset=["friend"])
        w, wo = m[m["friend"] == True], m[m["friend"] == False]  # noqa: E712
        friends = {"with": clean_num(w["won"].mean()), "without": clean_num(wo["won"].mean()),
                   "with_games": int(len(w)), "without_games": int(len(wo))}

    # Public Steam ID as FACEIT reports it (used only for a "Steam profile" link)
    steam_id64 = str(cs2.get("game_player_id") or player.get("steam_id_64") or "").strip()
    steam_id64 = steam_id64 if steam_id64.isdigit() else ""

    recent = matches.sort_values("played_at", ascending=False).head(20).copy()
    recent["date"] = recent["played_at"].dt.tz_convert(LOCAL_TZ).dt.strftime("%d %b %H:%M")

    return {
        "player": {"nickname": player.get("nickname"), "avatar": player.get("avatar") or "",
                   "url": (player.get("faceit_url") or "").replace("{lang}", "en"),
                   "level": level, "elo": elo, "progress": progress, "to_next": to_next,
                   "country": (player.get("country") or "").upper(),
                   "steam_id64": steam_id64},
        "summary": {"matches": int(len(matches)), "wins": wins, "losses": int(len(matches) - wins),
                    "win_rate": clean_num(matches["won"].mean()), "kd": clean_num(matches["kd"].mean()),
                    "hs": clean_num(matches["hs_pct"].mean()), "adr": clean_num(matches["adr"].mean()),
                    "streak_text": streak_text, "streak": streak, "streak_win": bool(last)},
        "form": [bool(x) for x in matches["won"].tail(10)],
        "tips": [{"icon": e, "html": tip_html(t)} for e, t in coach_tips(matches, mates)],
        "insights": [dict(i, html=tip_html(i["html"]), title=html.escape(i["title"]), action=html.escape(i["action"]))
                     for i in coach_insights(matches, mates)],
        "kd": records(kd, {"n": "match_nr", "kd": "kd", "avg10": "avg10", "map": "map", "won": "won"}),
        "maps": records(maps, {"map": "map", "games": "games", "win_rate": "win_rate", "kd": "avg_kd",
                               "hs": "hs", "adr": "adr", "tag": "tag"}),
        "tod": records(tod, {"label": "label", "games": "games", "win_rate": "win_rate"}),
        "hours": records(hours, {"hour": "hour", "games": "games", "kd": "kd"}),
        "heat": {"cols": [t.split(" (")[0] for t in TIME_ORDER], "rows": heat_rows},
        "squad": squad,
        "friends": friends,
        "trend": records(matches, {"n": "match_nr", "kd": "kd", "adr": "adr", "hs": "hs_pct", "won": "won", "map": "map"}),
        "points": records(matches.dropna(subset=["hs_pct", "kd"]), {"hs": "hs_pct", "kd": "kd", "won": "won"}),
        "recent": records(recent, {"date": "date", "map": "map", "won": "won", "kills": "kills", "deaths": "deaths",
                                   "assists": "assists", "kd": "kd", "hs": "hs_pct", "adr": "adr"}),
        "shots": screenshots(),
        "min_games": MIN_GAMES,
        "loaded": f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC",
    }


# ---------- The page ----------

# Hide Streamlit's own header and spacing so the dashboard fills the page
st.markdown(
    """<style>
    header[data-testid="stHeader"] {display: none;}
    .block-container {padding: 0.5rem 0.5rem 0 0.5rem; max-width: 100%;}
    iframe {display: block;}
    </style>""",
    unsafe_allow_html=True,
)

api_key = secret("FACEIT_API_KEY")
if not api_key:
    st.warning(
        "No FACEIT key found. Add **FACEIT_API_KEY** in the app's Secrets "
        "settings (see the README) and reload the page."
    )
    st.stop()

nickname = st.sidebar.text_input("FACEIT nickname", value=secret("FACEIT_NICKNAME", "busiks1"))

try:
    player = load_player(nickname, api_key)
except requests.HTTPError as err:
    code = err.response.status_code if err.response is not None else "?"
    if code == 404:
        st.error(f"FACEIT doesn't know a CS2 player called **{nickname}**.")
    elif code in (401, 403):
        st.error("FACEIT said the key is wrong. Check FACEIT_API_KEY in Secrets.")
    else:
        st.error(f"FACEIT gave an error ({code}). Try again in a minute.")
    st.stop()

cs2 = player.get("games", {}).get(GAME, {})
player_id = player["player_id"]
matches = tidy_matches(load_matches(player_id, api_key))

if matches.empty:
    st.info("No CS2 matches found on FACEIT for this player yet.")
    st.stop()

mates = find_teammates(matches, player_id, api_key)

# The key never leaves the server: only the finished numbers go into the page.
payload = build_payload(player, cs2, matches, mates)

# ---------- Leetify (separate source, off unless LEETIFY_ENABLED = "true") ----------
# Runs after FACEIT and can never stop the FACEIT page: errors become a message.
# No caching on purpose (Leetify guidelines: don't store their data).
if str(secret("LEETIFY_ENABLED", "false")).strip().lower() == "true":
    from sources import load_leetify

    steam_id = str(secret("STEAM_ID", "") or "").strip()
    steam_id_from = "Secrets" if steam_id else ""
    if not steam_id:
        steam_id = str(cs2.get("game_player_id") or player.get("steam_id_64") or "").strip()
        steam_id_from = "FACEIT profile" if steam_id else ""
    try:
        payload["leetify"] = load_leetify(
            steam_id, api_key=secret("LEETIFY_API_KEY") or None, steam_id_from=steam_id_from
        )
    except Exception:  # last safety net; never show raw error text
        payload["leetify"] = {"enabled": True, "status": "error",
                              "message": "Leetify part failed to load.", "check": {}}
# ---------- Steam (separate source, on when STEAM_API_KEY is in Secrets) ----------
# Runs after FACEIT and can never stop the FACEIT page. The key stays on the server.
steam_key = secret("STEAM_API_KEY") or None
if steam_key:
    from sources import load_steam

    sid = str(secret("STEAM_ID", "") or "").strip()
    sid_from = "Secrets" if sid else ""
    if not sid:
        sid = str(cs2.get("game_player_id") or player.get("steam_id_64") or "").strip()
        sid_from = "FACEIT profile" if sid else ""
    try:
        payload["steam"] = load_steam(sid, api_key=steam_key, steam_id_from=sid_from)
    except Exception:  # last safety net; never show raw error text
        payload["steam"] = {"enabled": True, "status": "error", "message": "Steam part failed to load."}
data_json = json.dumps(payload).replace("</", "<\\/")
page = HERE.joinpath("dashboard.html").read_text(encoding="utf-8").replace("__DATA__", data_json)
st.iframe(page, height="content")
