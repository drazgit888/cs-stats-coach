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

## 2026-11-21: Steam connected – my CS2 hours
- **Why:** my profile showed "Steam: Not connected". I wanted my real CS2 playtime on the profile.
- **What I did:** made a Steam Web API key, put it in the app's Secrets (`STEAM_API_KEY`, plus `STEAM_ID`) and set my Steam "Game details" to Public.
- **What was built:** a Steam part in `sources.py`, separate from FACEIT and Leetify. The Profile now shows my total CS2 hours and hours in the last 2 weeks, and the Steam page shows my Steam profile and playtime. If Steam is down or private, the page says so and FACEIT keeps working.
- **How I tested it:** 13 extra automatic checks with fake Steam answers (normal, private game details, CS2 not in library, wrong key, rate limit, no internet), including that the key never ends up in the page. Then I checked it live in my own app.
- **Picture:** `images/v5-steam-test-data.png` (test data)
- **What I think / what I learned:** _[YOUR WORDS]_

## 2026-11-21: Version 6 – back to the poster, now in pink
- **What happened:** I looked at v5 in my test app and didn't like it: it felt too mixed together and less like a game. I also found the coach tips too general.
- **My decisions:**
  - Go back to the v4 poster design (top menu, big italic titles, icon cards, drawn backgrounds), but in the colours of my avatar: charcoal and hot pink, with violet as second colour. Orange is only for FACEIT now.
  - Only **two main numbers matter: FACEIT and Premier.** Leetify was only connected to get my Premier data, so Leetify's own scores (aim, positioning, utility) are not shown anymore.
  - One topic per page. Profile = me + one separate block for FACEIT, Premier and Steam.
- **Concrete coach points:** the Briefing now says things like "you win 25% on Ancient (4 games) against 48% overall, your ADR there is 73 (usually 84)" with one "Do this" action and how many games it is based on. New checks: hardest/best map, do I lose by dying more or killing less, after 23:00, long sessions, tilt after two losses, last 10 games vs before, best teammate. A point only appears with 3+ games.
- **What I learned:** trying a design and rejecting it is also a result. v5 was more "professional" but v4's style fits me and my project better. Asking myself "what are my 2 main numbers?" made the site simpler.
- **Tests:** 34 automatic checks pass (also: no Leetify scores on the page, the Leetify badge stays next to Premier, coach points always have numbers and 3+ games).
- **Pictures:** `images/v6-home-test-data.png`, `images/v6-profile-test-data.png`, `images/v6-briefing-test-data.png`, `images/v6-premier-test-data.png`, `images/v6-maps-test-data.png`, `images/v6-profile-mobile-test-data.png` (test data)
- **What I think / what friends think:** _[YOUR WORDS]_

## 2026-11-22: Version 7 – 7 things I changed after testing on my phone
- **What happened:** I looked at the v6 test site on my phone and wrote down 7 things I didn't like. For each one I first asked what is possible with the data and what is not.
- **The 7 changes:**
  1. **Leetify on my own site.** Aim, Positioning, Utility, Clutch, Opening and the Leetify Rating per match are now shown on the site, exactly as Leetify sends them (not stored, not recalculated), with the official badge.
  2. **Glossary.** Every page ends with "What do these words mean?" (K/D, ADR, HS%, Elo…). Short words also have a tooltip when you hover or tap them.
  3. **Simpler chart.** The confusing line chart is now one bar per game: pink = win, grey = loss, a dashed line at K/D = 1, and one sentence explaining it.
  4. **Best vs worst game.** Two cards side by side (picked by K/D, ADR breaks a tie) and a sentence comparing them.
  5. **Find teammates.** I mostly play solo. FACEIT has no public player search in the data I use, so the page lists players who were on my team 2+ times, with their FACEIT level, wins together and a link to their profile.
  6. **Clickable maps.** Tapping a map opens a panel: wins/losses, K/D, ADR, HS%, my last games there, my best game there and a tip.
  7. **Tactics page.** Real tactics need demo files, so this page only uses play-style numbers FACEIT/Leetify really send (opening duels, clutches, flashes, utility damage, multi-kills) and says how each one is counted, what I do best, what is weakest and what to train. If a field is missing, it is not shown.
- **What is not possible (and why):** a real social network or player search, Elo history per match, and real positioning/rotation analysis (needs demos).
- **Tests:** 45 automatic checks pass (new: best/worst rule, map details match the raw games, teammates need 2+ games, tactics are counted from the real fields and disappear when FACEIT doesn't send them, Leetify values only shown "as returned").
- **Pictures:** `images/v7-d-profile-test-data.png`, `images/v7-d-matches-test-data.png`, `images/v7-d-tactics-test-data.png`, `images/v7-d-squad-test-data.png`, `images/v7-m-maps-test-data.png`, `images/v7-p-tactics-test-data.png` (test data, not my real numbers)
- **What I think / what I learned:** _[YOUR WORDS]_

## 2026-11-23: Leetify numbers per game on the Tactics page
- **Why:** the Data check showed FACEIT does not send entry, clutch or flash numbers for my matches, but Leetify sends a lot per game (reaction time, preaim, flashes, trades, utility left when dying, rounds survived). I didn't like that Leetify mostly showed links on my site.
- **What I built:** a "Leetify · my last games" table on Tactics: one column per game, the numbers exactly as Leetify sends them (no averages, because Leetify's rules say not to recalculate), with the field name under each label and every word in the glossary.
- **Decision:** I kept Leetify instead of using only FACEIT, because it is the only source for Premier and has the most detailed play-style data.
- **Tests:** 46 automatic checks, including that these per-game values pass through unchanged.
- **Picture:** `images/v7-tactics-leetify-games-test-data.png` (test data)
- **What I think:** _[YOUR WORDS]_

## 2026-11-23: My 10-point review of the live site
- **What happened:** after v7 went live I went through every page and wrote 10 points: too much text always open, Premier had no stats next to FACEIT, Leetify looked like a boring list, some charts were empty or unclear, the Premier page had almost no information, and I didn't want my 2-week playtime visible.
- **What changed:**
  - "What do these words mean?" is now closed by default on every page and opens when you tap it.
  - Home and Profile show Premier win rate, K/D, HS%, ADR and streak next to FACEIT. These are calculated by the site from the kills, deaths, headshots, damage and rounds Leetify sends for each Premier game (Leetify's own ratings are never changed). FACEIT and Premier stay in separate blocks.
  - Leetify on Profile now looks more like leetify.com: a rating circle, Aim/Positioning/Utility squares with 0–100 bars, and "Top stats" cards (reaction time, preaim, head accuracy, counter-strafing, trades, flashes) with the last game's value and a mini line of the last 10 games.
  - Steam shows only total hours.
  - Maps: the confusing scatter plot is gone; one chart shows wins and losses per map.
  - Tactics: donut of multi-kill rounds, radar of Aim/Positioning/Utility, Leetify Rating per game and reaction time per game.
  - Progress: "K/D by hour" (empty on the live site) became "K/D by time of day" with the number of games under each bar.
  - Premier: my Premier stats, Leetify Rating per game, kills vs deaths per game, a donut of which maps I play and win rate per map, and readable dates.
  - Charts are now drawn one by one, so if one fails the page shows a short message instead of an empty box.
- **What is not possible:** Premier rating history and "better than X% of players" are only on leetify.com, not in their public API.
- **Tests:** 50 automatic checks (new: Premier stats only count Premier games and match the raw kills/deaths, Leetify ratings unchanged, 2-week hours never reach the page).
- **Pictures:** `images/v8-d-profile-test-data.png`, `images/v8-d-premier-test-data.png`, `images/v8-d-tactics-test-data.png`, `images/v8-d-progress-test-data.png`, `images/v8-d-maps-test-data.png`, `images/v8-m-home-test-data.png` (test data)
- **What I think:** _[YOUR WORDS]_
