"""CS Stats Coach: a Streamlit dashboard for my own CS2 matches.

Data comes from the FACEIT Data API (https://docs.faceit.com/docs/data-api/).
The API key is read from Streamlit secrets (FACEIT_API_KEY) and is never
stored in this repository.
"""
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API = "https://open.faceit.com/data/v4"
GAME = "cs2"
LOCAL_TZ = "Europe/Amsterdam"  # I play in the Netherlands
MIN_GAMES = 3  # don't draw conclusions from fewer games than this

st.set_page_config(page_title="CS Stats Coach", page_icon="🎯", layout="wide")


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
    fig.update_yaxes(tickformat=".0%", range=[0, 1])
    fig.add_hline(y=0.5, line_dash="dot", annotation_text="50%")
    return fig


def secret(name, default=None):
    """Read a value from Streamlit secrets without crashing if there are none."""
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


# ---------- The page ----------

st.title("🎯 CS Stats Coach")
st.caption("A coach made from my own Counter-Strike 2 numbers.")

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
st.subheader(
    f"Hi {player.get('nickname', nickname)} 👋 here are your last {len(matches)} FACEIT matches"
)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("FACEIT level", cs2.get("skill_level", "?"))
c2.metric("Elo", cs2.get("faceit_elo", "?"))
c3.metric("Win rate", f"{matches['won'].mean():.0%}")
c4.metric("Average K/D", f"{matches['kd'].mean():.2f}")
c5.metric("Average headshot %", f"{matches['hs_pct'].mean():.0f}%")

tab_overview, tab_time = st.tabs(["📈 Overview", "🕒 When I play"])

# ===== Overview =====
with tab_overview:
    st.markdown("### 📈 Is my aim getting better?")
    matches["kd_trend"] = matches["kd"].rolling(10, min_periods=1).mean()
    fig = px.line(
        matches,
        x="match_nr",
        y=["kd", "kd_trend"],
        labels={"match_nr": "Match (oldest → newest)", "value": "K/D", "variable": ""},
        color_discrete_sequence=["#9ecae1", "#e6550d"],
    )
    fig.for_each_trace(
        lambda t: t.update(
            name={"kd": "K/D per match", "kd_trend": "Average of last 10"}[t.name]
        )
    )
    fig.update_traces(line_width=3, selector={"name": "Average of last 10"})
    fig.add_hline(y=1, line_dash="dot", annotation_text="K/D = 1")
    st.plotly_chart(fig, width="stretch")

    st.markdown("### 🗺️ Which maps am I best on?")
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

st.caption(
    f"Data from the FACEIT Data API · loaded {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC"
)
