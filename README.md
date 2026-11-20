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
| `.streamlit/secrets.toml.example` | Example of where the secret FACEIT key goes (the real one is never uploaded) |

## How to run it
**Online (no installing needed):** the app runs on Streamlit Community Cloud (share.streamlit.io).
The FACEIT key is pasted into the app's **Settings → Secrets** box like this:
```toml
FACEIT_API_KEY = "my-key"
FACEIT_NICKNAME = "busiks1"
```

**On a computer:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

## What the app shows
- **Player card:** level badge, Elo bar to the next level, animated stats, last 10 games
- **🧠 Briefing:** coach tips in plain words, made from my numbers
- **📈 Matches:** is my K/D going up? + scoreboard of my last 20 matches
- **🗺️ Map pool:** map cards with win-rate rings, best and hardest map
- **🕒 Timing:** heatmap of weekday × time of day, win rate by time, K/D by hour
- **👥 Squad:** who I win most with, friends vs strangers
- **🎯 Aim:** does good aim mean I win? Headshot % per map
- **📸 Highlights:** my own screenshots

## Status
✅ Version 3 is live: https://cs-stats-coach-fencmkvjwvvwbpmx4hwappv.streamlit.app/
Next ideas: Premier data, follow one coach tip for a week and measure the result.

The portfolio is in [`docs/`](docs/README.md).
