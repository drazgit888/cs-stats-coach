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

## 2026-11-20 (evening): Version 1 is online 🎉
- **What I did:** Put the app online on Streamlit Community Cloud and pasted my FACEIT key into the Secrets box.
- **Result:** It loaded my real data: **61 FACEIT matches, level 3, Elo 888, 46% win rate, K/D 0.98, 39% headshots.**
- **What I noticed:** My K/D jumps up and down a lot from match to match, but the 10-match average sits right around 1.0.
- **How I felt:** _[YOUR WORDS: how did it feel to see your own numbers for the first time? Surprised? Proud?]_

![Version 1 of the app](images/v1-live-app.png)

## 2026-11-20: Iteration 2 – "Do I play worse late at night?"
- **Question:** Does the time I play change how well I play?
- **What I built:** A new tab **"When I play"** with my win rate per time of day (morning, afternoon, evening, late night), per day of the week, and my average K/D for every hour.
- **How:** FACEIT gives the time each match finished. I changed it to Dutch time and put every match in a "time bucket".
- **Also fixed:** The two lines in the K/D chart had almost the same colour, so the 10-match average is now a thick orange line.
- **Be careful:** if a bar has only 1 or 2 games, it doesn't really mean anything yet. The labels show how many games each bar is based on.
- **What my data says:** _[YOUR WORDS: look at the tab. Do you win less late at night? Is that what you expected?]_

## 2026-11-20: Iteration 3 – "Which teammates help me win?"
- **Question:** Do I win more when I play with certain friends? Is it better to play with friends or alone?
- **What I built:** A **"Teammates"** tab. It shows everyone I played with at least 2 times, how often we won together, and my K/D when they were on my team. It also compares "with a friend" vs "only strangers".
- **How:** The match list from FACEIT doesn't say who was on my team. So for every match, the app asks FACEIT for the match details (the two teams) and finds the team I was on. This is one extra question to FACEIT per match, so the app saves (caches) the answers for a day to stay fast.
- **Be careful:** a friend I played 3 games with could have a 100% win rate by luck. More games = more trustworthy.
- **What my data says:** _[YOUR WORDS: who is your "lucky" teammate? Did you show them? What did they say?]_

## 2026-11-20: Iteration 4 – "Aim per map"
- **Question:** Is my aim better on some maps than others? And does good aim actually make me win?
- **What I built:** An **"Aim per map"** tab. I can switch between headshot %, K/D and damage per round (ADR) for every map, compared with my overall average. A dot chart shows every match: green = won, red = lost.
- **Why this is interesting:** Win rate per map (in the Overview) depends on my whole team. Aim per map is more about *me*.
- **What my data says:** _[YOUR WORDS: on which map is your aim best? Is that also the map you win most on? Surprising?]_

## 2026-11-20: Iteration 5 – "Coach tips"
- **Question:** Can the app tell me *what to do*, not just show charts?
- **What I built:** A **"Coach tips"** tab (now the first tab). It reads my numbers and writes advice in normal words, for example "Your best map is X, pick it when you can" or "After a loss you win less, take a 10-minute break".
- **The rules the coach uses:**
  1. Best and hardest map (by win rate)
  2. Best and worst time of day (only if the difference is 10% or more)
  3. Am I in form? (K/D of my last 10 games vs the games before)
  4. Tilt check: do I win less in the next game right after a loss? (games less than 2 hours apart)
  5. Lucky teammate (the friend I win most with)
  6. Weakest map for headshots
- **Safety rule:** the coach only talks about groups with **at least 3 games**, so it doesn't give advice based on luck.
- **What I think of the tips:** _[YOUR WORDS: are the tips true for you? Did one surprise you? Will you actually follow one?]_
- **Feedback from friends:** _[YOUR WORDS: show the app to a friend you play with. What did they say?]_

## 2026-11-20: Design experiment – make it look like a CS HUD
- **Question:** Can the app *feel* like the game, so it's more fun to look at? (Fun is 25% of the grade!)
- **What I built:**
  - A dark "tactical" theme with orange and khaki colours (`.streamlit/config.toml` + `theme.py`).
  - A banner I made myself (`assets/banner.svg`): a crosshair, a grid and a small radar that turns around. It's drawn with code, so it's **original**, with no logos or pictures from the real game.
  - HUD-style score cards, briefing cards for the coach tips, and game words in the titles: *Scoreboard, Briefing, Squad, Map pool, Loadout check*.
  - A **📸 Highlights** tab where my own screenshots from the game appear (just put them in `assets/screenshots/`).
- **Copyright choice:** I did not use Valve/CS logos, official art or fonts. The style is *inspired by* shooter games but made by me.
- **Before/after:** version 1 = `images/v1-live-app.png`, new look (with test data) = `images/v3-hud-design-test-data.png`.
- **What I think / what friends think:** _[YOUR WORDS: does it feel more like CS now? What would you change?]_

## 2026-11-20: Version 3 – I changed my approach for the design
- **Problem:** I didn't like how version 2 looked. Streamlit's normal building blocks (tabs, metrics, charts) all look a bit the same, and CSS tricks on top of them only go so far.
- **New approach:** Streamlit still does the "secret" work on the server: it holds my FACEIT key, downloads my matches and calculates everything. But the page you see is now **my own HTML/CSS/JavaScript design** (`dashboard.html`), shown inside the Streamlit app. Python sends it only the finished numbers, never the key.
- **What's new in the design:**
  - A **player card**: avatar, nickname, FACEIT level badge and an Elo bar that shows how many points I need for the next level
  - Animated stat cards (numbers count up), a "last 10 games" W/L strip and my current streak
  - **Map cards** with a win-rate ring and BEST / HARDEST map badges
  - A **heatmap** of weekday × time of day (greener = I win more then)
  - **Squad ranking** of teammates and a big "with a friend vs only strangers" comparison
  - Smooth interactive charts (Chart.js), free Google Fonts, a moving grid background
- **Originality:** all graphics are made with code (shapes, gradients, rings). No logos, art or fonts from the real game.
- **What I learned:** sometimes the tool's default look isn't enough, and it's OK to change approach halfway. Version 2 still exists in my GitHub history (commit `51c6282`) so I can compare.
- **Before/after:** `images/v1-live-app.png` → `images/v3-hud-design-test-data.png` (v2) → `images/v3-briefing-test-data.png`, `images/v3-mappool-test-data.png`, `images/v3-matches-test-data.png` (v3, made with test data)
- **What I think / what friends think:** _[YOUR WORDS]_

## 2026-11-20: Version 4 – my own design reference
- **What happened:** I still wanted it more beautiful, so I made a **mockup picture** of what I want (dark, orange, big bold italic titles, a menu at the top, cards with icons and orange progress bars) and used the official CS website as a mood reference.
- **What I built from it:** a new page design with a top menu (**Home, Briefing, Matches, Maps, Squad, Progress, Highlights**):
  - **Home:** big title "Your CS2 stats. Your own progression.", a button to the briefing, and my level/Elo, win rate, K/D and headshot % with line icons
  - **Briefing:** each coach tip is a card with its own icon
  - **Maps:** a card per map with an orange "wins / games" bar, plus aim charts
  - **Squad:** teammate cards with a win bar, friends vs strangers
  - **Progress:** a ring showing how close I am to the next FACEIT level, my current streak with a flame, a "recent wins" checklist, the weekday × time heatmap and K/D by hour
- **Originality rule:** I used the official website only as *inspiration for the mood*. The backgrounds (walls, arches, windows, crates, warm light, dust) are drawn with code, and the font is a free Google font (Barlow Condensed). No logos, game art, map graffiti or official fonts.
- **What I learned:** a picture of what you want ("mockup") makes it much easier to explain a design than words.
- **Pictures:** `images/v4-home-test-data.png`, `images/v4-maps-test-data.png`, `images/v4-progress-test-data.png` (made with test data)
- **What I think / what friends think:** _[YOUR WORDS]_


## 2026-11-20: Leetify – my Premier and matchmaking games
- **Why:** FACEIT only knows my FACEIT games. A big part of my ~210 hours is Premier, so I connected my Steam account to Leetify and added Leetify as a second data source.
- **What I built:** a new **Leetify** page with my Premier rank, my Competitive rank per map (kept separate from Premier), other ranks, my Leetify rating, recent matches and a "Data check" box that shows what Leetify actually sent.
- **Rules I followed:** Leetify's API guidelines. Data is fetched fresh and never stored, numbers are shown exactly as Leetify gives them, and the official "Data Provided by Leetify" badge and "View on Leetify" links are on the page. The page is off until I switch it on in Secrets (`LEETIFY_ENABLED`), and FACEIT keeps working even if Leetify is down.
- **How I tested it:** 53 automatic checks with fake answers (good data, wrong key, no profile, rate limit, timeout, no internet). My FACEIT numbers were exactly the same before and after.
- **Picture:** `images/leetify-page-test-data.png` (made with test data, not my real numbers)
- **What I think / what I learned:** _[YOUR WORDS]_

## 2026-11-20: Version 5 – a real analytics product (Profile page first)
- **Why:** v4 looked like a game poster. I wanted it to feel like a premium esports analytics platform (FACEIT, Leetify, HLTV style), with my own avatar colours: charcoal, violet and magenta.
- **How I worked:** in phases. First an audit of the old design and a written proposal with colours (HEX codes), fonts and a profile layout. I approved it, then the Profile page and the design system were built. The other pages get the full treatment after my review.
- **What changed:**
  - A **sidebar menu** grouped into Player, Performance, Sources and Media, and a top bar that shows which sources are live
  - A new **Profile** start page: avatar, FACEIT level and Elo, Premier and Leetify ratings, Steam status, my key stats, a trend chart I can switch (K/D, win rate, ADR, HS%), a Leetify radar (Aim, Positioning, Utility), recent matches compared with my own average, and my top 3 coach tips
  - **Each source has its own colour** (FACEIT orange, Leetify pink, Steam blue, Premier cyan). Orange is now only for FACEIT.
  - Wins are green and losses red; the drawn background scenes and the big italic font are gone
  - New **Premier** and **Steam** pages that honestly say what is and isn't available
- **Rules I kept:** no made-up numbers ("Not available" instead), Leetify numbers exactly as Leetify gives them with the official badge, no Elo history line because FACEIT doesn't give Elo per match, no API keys in the page.
- **How I tested it:** 17 automatic checks (`tests/`), e.g. the page still gets all its data, no key ends up in the page, Leetify values are unchanged. Screenshots on laptop, tablet and phone width with test data.
- **Pictures:** `images/v5-profile-test-data.png`, `images/v5-profile-mobile-test-data.png`, `images/v5-maps-test-data.png`, `images/v5-leetify-test-data.png`, `images/v5-profile-leetify-off-test-data.png` (made with test data, not my real numbers)
- **Design system:** [design-system.md](design-system.md)
- **What I think / what I learned:** _[YOUR WORDS]_
