# Topic study: data storytelling with Streamlit

This page explains the topic of my video in my own words, and how I used it in my project.

## 1. What is data storytelling?
Data storytelling means **explaining data so a person understands it and knows what to do next**. It has three parts:

| Part | What it means | In my app |
|---|---|---|
| **Data** | The real numbers | My FACEIT matches: kills, deaths, headshots, maps, times, teammates |
| **Visuals** | Charts that make patterns easy to see | K/D line, win-rate bars per map, time of day, teammate charts, aim scatter |
| **Narrative** | Words that explain what it means | Chart titles are questions ("Do I play worse late at night?") and the **Coach tips** tab gives advice in normal sentences |

A dashboard with only charts makes the viewer do all the thinking. A *story* guides them: question → evidence → conclusion → action.

## 2. How I built the story
My app follows a simple story line:
1. **Hello, this is you** – big numbers at the top (level, Elo, win rate, K/D, headshot %).
2. **What should I do?** – Coach tips come first, because that's what a player wants to know.
3. **Why?** – Every tip can be checked in the other tabs (Overview, When I play, Teammates, Aim per map).
4. **Explore yourself** – change the nickname in the sidebar, switch the aim metric, open the full table.

Design choices I made for storytelling:
- Every chart title is a **question a player would ask**.
- Every bar shows **how many games** it is based on, so you don't trust a bar with 1 game.
- Dotted **reference lines** (50% win rate, K/D 1, "my average") so you can see quickly if something is good or bad.
- Colours with meaning: green = won, red = lost; the important line (10-game average) is thick and orange.

## 3. What is Streamlit?
Streamlit is a free Python library that turns a Python script into a website.
- You write normal Python (`st.title`, `st.metric`, `st.plotly_chart`, `st.tabs`) and Streamlit draws the page.
- When you click something, Streamlit runs the script again from top to bottom with the new choice.
- **Caching** (`@st.cache_data`) remembers slow answers (like FACEIT data) so the app stays fast.
- **Secrets** keep passwords like my API key out of the code.
- **Streamlit Community Cloud** puts the app online for free, straight from GitHub.

### Strengths and weaknesses (my opinion)
| 👍 Good | 👎 Less good |
|---|---|
| Very fast to build: working app online on day 1 | Less control over the exact layout than a real website |
| Only Python needed | Re-running the whole script can be slow with lots of data (caching solves most of it) |
| Free hosting from GitHub | Free apps "fall asleep" after a while without visitors |
| Lots of chart libraries work (I used Plotly) | |

### Alternatives
_[OPTIONAL: Power BI / Tableau (drag and drop, but less flexible and not free), Dash (more control, more code), a Jupyter notebook (good for analysing, but not interactive for others).]_ I chose Streamlit because it's in my video and because it lets someone who isn't a programmer make an interactive app.

## 4. Pitfalls I ran into (data storytelling risks)
- **Small numbers lie.** One map with 2 games and 100% wins looks amazing but is just luck. → I show game counts and the coach ignores groups with fewer than 3 games.
- **Correlation is not causation.** If I lose more late at night, it may be because I'm tired, *or* because different (better) players are online late. The app can't tell which.
- **Team game.** Win rate depends on 5 players. That's why I also look at aim per map, which is more about *me*.

## 5. Sources
- The course video: "Become a Data Storyteller with Streamlit" _[link]_
- Streamlit documentation: https://docs.streamlit.io
- FACEIT Data API documentation: https://docs.faceit.com
- _[FILL IN: any other article/video you watched]_
