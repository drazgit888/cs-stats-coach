# Process diary

## 2026-11-20: Picking my idea
- **What I did:** Chose my project idea: a "CS stats coach", a dashboard of my own Counter-Strike 2 matches.
- **Why:** I love playing CS2. I play FACEIT and Premier and have about 210 hours in the game, so I have lots of my own data and I actually care what it says. That makes it fun to work on.
- **Video:** "Become a Data Storyteller with Streamlit". Streamlit lets me turn numbers into an interactive story, which fits a coach that explains my stats.
- **Set up:** Created this GitHub repository with a README, this diary, a docs folder and a first empty Streamlit app.
- **Next:** Get a free FACEIT Data API key and connect my match history.

## 2026-11-20: First data on screen
- **What I did:** Got a free FACEIT Data API key and made the app load my last 100 FACEIT matches (nickname busiks1).
- **First version shows:** level, Elo, win rate, K/D, headshot %, K/D over time, win rate per map and a "best map" tip.
- **How the key stays safe:** it is pasted into Streamlit Cloud's Secrets box, never into the code or GitHub.
- **Next:** put the app online on Streamlit Community Cloud and look at what my numbers say.
