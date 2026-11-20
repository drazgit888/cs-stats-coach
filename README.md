# CS Stats Coach 🎯

An interactive dashboard that looks at **my own Counter-Strike 2 matches** (FACEIT and Premier) and tells me, in plain words, what I am good at and what I should practise.

Made for the HAN minor **Data-Driven Decision Making** (individual assignment), inspired by the course video *"Become a Data Storyteller with Streamlit"*.

## The idea in one sentence
I have played around 210 hours of CS2. Every match leaves numbers behind (kills, deaths, headshots, maps, wins). This app collects those numbers and turns them into a story: *"You win more on Mirage, your aim drops late at night, practise X."*

## What is in this folder
| Folder / file | What it is |
|---|---|
| `app.py` | The Streamlit dashboard (the website you click around in) |
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

## What the app shows (version 1)
- My FACEIT level, Elo, win rate, average K/D and headshot %
- A line chart: is my K/D going up or down over my last 100 matches?
- A bar chart: which maps do I win most?
- A "coach tip" telling me my best map
- A table with every match

## Status
✅ Version 1: loads my last 100 FACEIT matches. Next: more coach tips, Premier data.
