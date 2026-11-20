# Methods and tools

## Tools
| Tool | What I used it for |
|---|---|
| **Python** | The language the app is written in |
| **Streamlit** | Turns the Python script into an interactive website |
| **pandas** | Tables: cleaning data, grouping (per map, per time, per teammate), averages |
| **Plotly** | Charts in versions 1–2 |
| **HTML, CSS, JavaScript** | Version 3: my own page design (`dashboard.html`) shown inside Streamlit |
| **Chart.js** | Version 3: animated, interactive charts |
| **Google Fonts** | Free fonts (Chakra Petch, Inter, JetBrains Mono) |
| **requests** | Asking the FACEIT API for data |
| **GitHub** | Storing the code and its history (every step is a commit) |
| **Streamlit Community Cloud** | Free hosting, so the app is online without installing anything |
| **Claude (AI assistant)** | I don't code myself. I described what I wanted, the AI wrote the code, and I tested it, checked the results and decided what to build next. _[YOUR WORDS: how did working with AI go? What did you have to check or correct?]_ |

## Steps (the "data pipeline")
1. **Collect:** the app asks FACEIT for my profile, my last 100 matches, and the teams of each match.
2. **Clean:** turn text into numbers, remove `de_` from map names, turn the end time into Dutch time, sort oldest → newest.
3. **Add new columns:** time of day (morning/afternoon/evening/late night), weekday, hour, and "with a friend or only strangers".
4. **Group and compare:** win rate, average K/D, headshot % and ADR per map, per time, per teammate.
5. **Show:** charts with question titles, game counts and reference lines. In version 3, Python packs all results into one data package (JSON) and the HTML page draws it. The FACEIT key never goes to the page.
6. **Advise:** simple rules turn the numbers into coach tips.

## Analysis methods (simple explanations)
- **Win rate** = games won ÷ games played.
- **Rolling average (last 10 games):** for each game, the average K/D of the 10 games up to it. It smooths out lucky/unlucky games so you can see the trend.
- **Grouping:** split the matches into groups (e.g. per map) and calculate the win rate of each group.
- **Minimum sample size:** groups with fewer than 3 games are ignored by the coach, because they are mostly luck.
- **Tilt check:** look at pairs of games less than 2 hours apart. Compare the win rate of the second game after a loss vs after a win.
- **Before/after comparison (form):** K/D of the last 10 games vs all games before.

## Coach rules
| Tip | Rule |
|---|---|
| Best map | highest win rate (≥ 3 games) |
| Hardest map | lowest win rate, only if under 45% |
| Best time to play | only if best and worst time differ by ≥ 10% |
| In form / out of form | last-10 K/D differs from earlier by more than 0.05 |
| Tilt | after-loss win rate is ≥ 10% lower than after-win |
| Lucky teammate | highest win rate together (≥ 3 games), above my normal win rate |
| Aim to practise | map where headshot % is > 3 points under my average |

## Testing
Before each upload, the app was tested with **made-up matches** (fake FACEIT answers) to check that every tab works without errors. Then I checked the real app online.
