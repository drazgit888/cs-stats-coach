"""CS Stats Coach: a Streamlit dashboard for my own CS2 matches.

Data comes from the FACEIT Data API (https://docs.faceit.com/docs/data-api/).
The API key is read from Streamlit secrets (FACEIT_API_KEY) and is never
stored in this repository.
"""
from datetime import datetime, timezone

from pathlib import Path

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from theme import LOSS, ORANGE, SKY, WIN, apply_theme, banner, hud_strip, tip_card

API = "https://open.faceit.com/data/v4"
GAME = "cs2"
LOCAL_TZ = "Europe/Amsterdam"  # I play in the Netherlands
MIN_GAMES = 3  # don't draw conclusions from fewer games than this

st.set_page_config(page_title="CS Stats Coach", page_icon="🎯", layout="wide")
apply_theme()


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


def win_rate_bar(table, x, title_x):
    fig = px.bar(
        table,
        x=x,
        y="win_rate",
        text=table["games"].astype(str) + " games",
        labels={x: title_x, "win_rate": "Win rate"},
    )
    fig.update_yaxes(tickformat=".0%", range=[0, 1.08])
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.add_hline(y=0.5, line_dash="dot", annotation_text="50%")
    return fig


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


def secret(name, default=None):
    """Read a value from Streamlit secrets without crashing if there are none."""
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


# ---------- The page ----------

banner()
st.caption("Your personal tactical coach, built from your own CS2 match data.")

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

# --- Big numbers at the top ---
hud_strip(
    player=player.get("nickname", nickname),
    matches=len(matches),
    level=cs2.get("skill_level", "?"),
    elo=cs2.get("faceit_elo", "?"),
)
st.subheader("📋 Scoreboard")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("FACEIT level", cs2.get("skill_level", "?"))
c2.metric("Elo", cs2.get("faceit_elo", "?"))
c3.metric("Win rate", f"{matches['won'].mean():.0%}")
c4.metric("Average K/D", f"{matches['kd'].mean():.2f}")
c5.metric("Headshot %", f"{matches['hs_pct'].mean():.0f}%")

SHOTS = sorted(
    p for p in Path(__file__).parent.joinpath("assets", "screenshots").glob("*")
    if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}
)
tab_tips, tab_overview, tab_time, tab_mates, tab_aim, tab_shots = st.tabs(
    ["🧠 Briefing", "📈 Match history", "🕒 Round timing", "👥 Squad",
     "🎯 Aim & map pool", "📸 Highlights"]
)

mates = find_teammates(matches, player_id, api_key)

# ===== Coach tips =====
with tab_tips:
    st.markdown("### 🧠 Pre-match briefing: what your coach says")
    tips = coach_tips(matches, mates)
    if not tips:
        st.info("Play a few more games so the coach has enough to go on!")
    for emoji, tip in tips:
        tip_card(emoji, tip)
    st.caption(
        f"Tips only use groups with at least {MIN_GAMES} games. With few games, "
        "a tip can be luck, so look at the other tabs to check."
    )

# ===== Overview =====
with tab_overview:
    st.markdown("### 📈 Is my aim getting better?")
    matches["kd_trend"] = matches["kd"].rolling(10, min_periods=1).mean()
    fig = px.line(
        matches,
        x="match_nr",
        y=["kd", "kd_trend"],
        labels={"match_nr": "Match (oldest → newest)", "value": "K/D", "variable": ""},
        color_discrete_sequence=[SKY, ORANGE],
    )
    fig.for_each_trace(
        lambda t: t.update(
            name={"kd": "K/D per match", "kd_trend": "Average of last 10"}[t.name]
        )
    )
    fig.update_traces(line_width=3, selector={"name": "Average of last 10"})
    fig.add_hline(y=1, line_dash="dot", annotation_text="K/D = 1")
    st.plotly_chart(fig, width="stretch")

    st.markdown("### 🗺️ Map pool: which maps am I best on?")
    per_map = summary_by(matches, "map").sort_values("win_rate", ascending=False)
    st.plotly_chart(win_rate_bar(per_map, "map", "Map"), width="stretch")

    with st.expander("See all matches as a table"):
        st.dataframe(
            matches[["played_at", "map", "won", "kills", "deaths", "assists", "kd", "hs_pct", "adr"]]
            .sort_values("played_at", ascending=False),
            width="stretch",
            hide_index=True,
        )

# ===== When I play =====
with tab_time:
    st.markdown("### 🌙 Do I play worse late at night?")
    st.caption("Times are Dutch time. Bars show how often I win; the label shows how many games.")
    by_time = summary_by(matches, "time_of_day", TIME_ORDER)
    st.plotly_chart(win_rate_bar(by_time, "time_of_day", "Time of day"), width="stretch")

    st.markdown("### 📅 Which day of the week is my best?")
    by_day = summary_by(matches, "weekday", DAY_ORDER)
    st.plotly_chart(win_rate_bar(by_day, "weekday", "Day"), width="stretch")

    st.markdown("### 🔥 Hour by hour: my K/D")
    by_hour = matches.groupby("hour").agg(games=("kd", "size"), avg_kd=("kd", "mean")).reset_index()
    fig_h = px.bar(by_hour, x="hour", y="avg_kd", text="games",
                   labels={"hour": "Hour of the day", "avg_kd": "Average K/D"})
    fig_h.add_hline(y=1, line_dash="dot")
    fig_h.update_xaxes(dtick=1)
    st.plotly_chart(fig_h, width="stretch")
    st.caption("The number on each bar is how many games I played in that hour.")

# ===== Teammates =====
with tab_mates:
    st.markdown("### 👥 Squad: which teammates help me win?")
    if mates.empty:
        st.info("Couldn't find teammate information for these matches.")
    else:
        per_mate = (
            mates.groupby("teammate")
            .agg(games=("won", "size"), win_rate=("won", "mean"), my_kd=("kd", "mean"))
            .reset_index()
        )
        regulars = per_mate[per_mate["games"] >= 2].sort_values(
            ["win_rate", "games"], ascending=False
        )
        if regulars.empty:
            st.info("You never played with the same person twice in these matches.")
        else:
            st.caption(
                "People I played with at least 2 times. Bars show how often we won "
                "together; the label shows how many games."
            )
            fig_m = win_rate_bar(regulars, "teammate", "Teammate")
            st.plotly_chart(fig_m, width="stretch")
            st.dataframe(
                regulars.rename(columns={
                    "teammate": "Teammate", "games": "Games together",
                    "win_rate": "Win rate", "my_kd": "My K/D with them",
                }).style.format({"Win rate": "{:.0%}", "My K/D with them": "{:.2f}"}),
                width="stretch", hide_index=True,
            )

        st.markdown("### 🤝 With friends or with strangers?")
        friends = set(regulars["teammate"])
        with_friend = mates.groupby("match_id")["teammate"].apply(
            lambda names: any(n in friends for n in names)
        )
        squad = matches[["match_id", "won", "kd"]].copy()
        squad["who"] = squad["match_id"].map(with_friend).map(
            {True: "With a friend", False: "Only strangers"}
        )
        squad = squad.dropna(subset=["who"])
        st.plotly_chart(
            win_rate_bar(summary_by(squad, "who"), "who", ""), width="stretch"
        )
        st.caption("A \"friend\" here means someone who was on my team in 2 or more of these matches.")

# ===== Aim per map =====
with tab_aim:
    st.markdown("### 🎯 Loadout check: how good is my aim on each map?")
    aim = (
        matches.groupby("map")
        .agg(games=("kd", "size"), hs_pct=("hs_pct", "mean"), kd=("kd", "mean"),
             adr=("adr", "mean"), win_rate=("won", "mean"))
        .reset_index()
        .sort_values("hs_pct", ascending=False)
    )
    metric_names = {
        "Headshot %": "hs_pct",
        "K/D": "kd",
        "Damage per round (ADR)": "adr",
    }
    if aim["adr"].isna().all():
        metric_names.pop("Damage per round (ADR)")
    choice = st.radio("Show", list(metric_names), horizontal=True)
    col = metric_names[choice]
    fig_a = px.bar(
        aim.sort_values(col, ascending=False), x="map", y=col,
        text=aim.sort_values(col, ascending=False)["games"].astype(str) + " games",
        labels={"map": "Map", col: choice},
    )
    fig_a.add_hline(y=matches[col].mean(), line_dash="dot", annotation_text="my average")
    st.plotly_chart(fig_a, width="stretch")
    st.caption("The dotted line is my average over all maps. Bars above it = better than usual.")

    st.markdown("### 🤔 Does good aim mean I win?")
    pts = matches.dropna(subset=["hs_pct", "kd"]).copy()
    pts["result"] = pts["won"].map({True: "Won", False: "Lost"})
    fig_s = px.scatter(
        pts, x="hs_pct", y="kd", color="result", hover_data=["map", "played_at"],
        color_discrete_map={"Won": WIN, "Lost": LOSS},
        labels={"hs_pct": "Headshot %", "kd": "K/D", "result": ""},
    )
    st.plotly_chart(fig_s, width="stretch")
    st.caption(
        "Every dot is one match. If green dots sit higher up, a good K/D helps me win. "
        "If green dots sit more to the right, headshots help me win."
    )

# ===== Highlights (my own screenshots) =====
with tab_shots:
    st.markdown("### 📸 Highlight reel")
    if not SHOTS:
        st.info("No screenshots yet. Add your own CS2 screenshots to the assets/screenshots folder.")
    cols = st.columns(2)
    for i, shot in enumerate(SHOTS):
        caption = shot.stem.replace("-", " ").replace("_", " ").capitalize()
        cols[i % 2].image(str(shot), caption=caption, width="stretch")

st.caption(
    f"Data from the FACEIT Data API · loaded {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC"
)
