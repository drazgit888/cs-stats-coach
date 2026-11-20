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


def tidy_matches(raw):
    """Turn the raw API answer into a clean table with one row per match."""
    df = pd.DataFrame(raw)
    if df.empty:
        return df

    clean = pd.DataFrame()
    clean["map"] = df.get("Map", pd.Series(dtype=str)).fillna("unknown")
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
    return clean


# ---------- The page ----------

st.title("🎯 CS Stats Coach")
st.caption("A coach made from my own Counter-Strike 2 numbers.")

def secret(name, default=None):
    """Read a value from Streamlit secrets without crashing if there are none."""
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


api_key = secret("FACEIT_API_KEY")
if not api_key:
    st.warning(
        "No FACEIT key found. Add **FACEIT_API_KEY** in the app's Secrets "
        "settings (see the README) and reload the page."
    )
    st.stop()

nickname = st.sidebar.text_input(
    "FACEIT nickname", value=secret("FACEIT_NICKNAME", "busiks1")
)

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
raw = load_matches(player["player_id"], api_key)
matches = tidy_matches(raw)

if matches.empty:
    st.info("No CS2 matches found on FACEIT for this player yet.")
    st.stop()

# --- Big numbers at the top ---
st.subheader(f"Hi {player.get('nickname', nickname)} 👋 here are your last {len(matches)} FACEIT matches")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("FACEIT level", cs2.get("skill_level", "?"))
c2.metric("Elo", cs2.get("faceit_elo", "?"))
c3.metric("Win rate", f"{matches['won'].mean():.0%}")
c4.metric("Average K/D", f"{matches['kd'].mean():.2f}")
c5.metric("Average headshot %", f"{matches['hs_pct'].mean():.0f}%")

# --- K/D over time ---
st.markdown("### 📈 Is my aim getting better?")
matches["kd_trend"] = matches["kd"].rolling(10, min_periods=1).mean()
fig = px.line(
    matches,
    x="match_nr",
    y=["kd", "kd_trend"],
    labels={"match_nr": "Match (oldest → newest)", "value": "K/D", "variable": ""},
)
fig.for_each_trace(
    lambda t: t.update(
        name={"kd": "K/D per match", "kd_trend": "Average of last 10"}[t.name]
    )
)
fig.add_hline(y=1, line_dash="dot", annotation_text="K/D = 1")
st.plotly_chart(fig, use_container_width=True)

# --- Maps ---
st.markdown("### 🗺️ Which maps am I best on?")
per_map = (
    matches.groupby("map")
    .agg(matches=("won", "size"), win_rate=("won", "mean"), avg_kd=("kd", "mean"))
    .reset_index()
    .sort_values("win_rate", ascending=False)
)
fig_map = px.bar(
    per_map,
    x="map",
    y="win_rate",
    text=per_map["matches"].astype(str) + " games",
    labels={"map": "Map", "win_rate": "Win rate"},
)
fig_map.update_yaxes(tickformat=".0%", range=[0, 1])
st.plotly_chart(fig_map, use_container_width=True)

best = per_map[per_map["matches"] >= 3].head(1)
if not best.empty:
    b = best.iloc[0]
    st.success(
        f"💡 Coach says: you win **{b['win_rate']:.0%}** of your games on "
        f"**{b['map']}** ({int(b['matches'])} games). Pick it when you can!"
    )

# --- Raw table ---
with st.expander("See all matches as a table"):
    st.dataframe(
        matches[["played_at", "map", "won", "kills", "deaths", "assists", "kd", "hs_pct", "adr"]]
        .sort_values("played_at", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    f"Data from the FACEIT Data API · loaded {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC"
)
