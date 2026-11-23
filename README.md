# CS Stats Coach 🎯

An interactive dashboard that looks at **my own Counter-Strike 2 matches** (FACEIT and Premier) and tells me, in plain words, what I am good at and what I should practise.

Made for the HAN minor **Data-Driven Decision Making** (individual assignment), inspired by the course video *"Become a Data Storyteller with Streamlit"*.

## The idea in one sentence
I have played around 210 hours of CS2. Every match leaves numbers behind (kills, deaths, headshots, maps, wins). This app collects those numbers and turns them into a story: *"You win more on Mirage, your aim drops late at night, practise X."*

## What is in this folder
| Folder / file | What it is |
|---|---|
| `app.py` | Gets my FACEIT data and calculates everything (Python + Streamlit) |
| `dashboard.html` | The design of the page you see (HTML, CSS, JavaScript) |
| `requirements.txt` | The list of Python tools the app needs |
| `docs/diary.md` | My process diary: what I did each day and why |
| `docs/` | Everything for the portfolio (data sources, methods, experiments) |
| `sources.py` | Leetify and Steam connections (separate from FACEIT; keys stay on the server) |
| `assets/leetify/` | Official "Data Provided by Leetify" badges, unchanged |
| `tests/` | Automatic checks (run with `pytest`): data the page needs, no keys in the page, Leetify numbers unchanged |
| `docs/design-system.md` | Colours, fonts and layout rules of the v5 design |
| `.streamlit/secrets.toml.example` | Example of where the secret FACEIT key goes (the real one is never uploaded) |

## How to run it
**Online (no installing needed):** the app runs on Streamlit Community Cloud (share.streamlit.io).
The FACEIT key is pasted into the app's **Settings → Secrets** box like this:
```toml
FACEIT_API_KEY = "my-key"
FACEIT_NICKNAME = "busiks1"
```
**Leetify (optional, off by default):** add these lines to the same Secrets box to switch on the Leetify page
(Premier and matchmaking data). Leave `LEETIFY_ENABLED` out or `"false"` and the app works with FACEIT only.
```toml
LEETIFY_ENABLED = "true"
LEETIFY_API_KEY = "my-leetify-key"
STEAM_ID = "my-17-digit-steam-id"   # optional, otherwise the Steam ID from FACEIT is used
```
**Steam (optional):** add `STEAM_API_KEY` (and optionally `STEAM_ID`) to the same Secrets box, and set Steam "Game details" to Public, to show your Steam profile and CS2 hours.

After saving, open the **Leetify** page and check the **Data check** box to see what Leetify returned.

**On a computer:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

## What the app shows
- **Home:** title, FACEIT level/Elo, Premier rating, FACEIT win rate and K/D
- **Profile:** avatar and one separate block per source: FACEIT, CS2 Premier (via Leetify), Steam hours
- **Premier:** Premier rating and Leetify match list, with the "Data Provided by Leetify" badge
- **Steam:** Steam profile and CS2 playtime
- **🧠 Briefing:** concrete coach points from my own matches: the numbers, how many games, and what to do
- **📈 Matches:** is my K/D going up? + scoreboard of my last 20 matches
- **🗺️ Map pool:** map cards with win-rate rings, best and hardest map
- **🕒 Timing:** heatmap of weekday × time of day, win rate by time, K/D by hour
- **👥 Squad:** who I win most with, friends vs strangers
- **🎯 Aim:** does good aim mean I win? Headshot % per map
- **📸 Highlights:** my own screenshots
- **Leetify** (only when switched on): Premier rank, Competitive rank per map, rating and recent matches, shown exactly as Leetify returns them, with the "Data Provided by Leetify" badge

## Status
✅ Version 3 is live: https://cs-stats-coach-fencmkvjwvvwbpmx4hwappv.streamlit.app/
Leetify page (Premier + matchmaking) added, off until switched on in Secrets.
Version 6 design (v4 poster layout in my avatar's pink, FACEIT + Premier as the two main sources) on a test branch; see `docs/design-system.md`.
Next ideas: follow one coach tip for a week and measure the result.

The portfolio is in [`docs/`](docs/README.md).
