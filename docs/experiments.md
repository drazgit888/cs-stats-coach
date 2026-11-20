# Experiments log

Each experiment: **what I wanted to know → what I tried → what happened → what I learned.**
Fill in the _[RESULT]_ parts by looking at the live app with your real data.

## Experiment 1: Can I get my own CS data at all?
- **Question:** Can I load my matches automatically instead of copying them by hand?
- **Tried:** FACEIT Data API with a free key, nickname busiks1.
- **Result:** ✅ Worked on the first try. 61 matches, level 3, Elo 888, 46% win rate, K/D 0.98, 39% headshots.
- **Learned:** An API is like a library card: with the key, I can ask for my data any time.

## Experiment 2: Is my aim getting better? (K/D over time)
- **Tried:** Line chart of K/D per match. It was too jumpy to read, so I added a 10-game rolling average.
- **Problem found:** In the first version, both lines had almost the same blue colour (see screenshot `images/v1-live-app.png`). → Made the average line thick and orange.
- **Result:** _[RESULT: is the orange line going up, down or flat?]_
- **Learned:** Raw data is noisy; an average shows the trend. Colour choices matter for the story.

## Experiment 3: Do I play worse late at night?
- **Hypothesis:** _[YOUR GUESS before looking: e.g. "I think I play worse after 23:00 because I'm tired."]_
- **Tried:** Grouped matches into morning / afternoon / evening / late night (Dutch time) and per weekday and hour.
- **Result:** _[RESULT: win rate per time of day + number of games]_
- **Was my guess right?** _[YES/NO + why]_
- **Learned:** Watch the number of games per bar.

## Experiment 4: Which teammates help me win?
- **Tried:** The match list doesn't include teams, so the app asks FACEIT for the details of every match (one extra request per match) and finds my team.
- **Technical issue:** That's up to 100 extra requests, which is slow. → Saved (cached) the answers for 24 hours.
- **Result:** _[RESULT: best teammate, friends vs strangers win rate]_
- **Learned:** _[YOUR WORDS]_

## Experiment 5: Aim per map and "does good aim mean I win?"
- **Tried:** Headshot %, K/D and ADR per map compared with my average; scatter plot of every match (green = won, red = lost).
- **Result:** _[RESULT: best/worst aim map; do the green dots sit higher (K/D) or more to the right (HS%)?]_
- **Learned:** _[e.g. "K/D matters much more for winning than headshot %"]_

## Experiment 6: Coach tips: can the app give advice?
- **Tried:** 6 simple rules that turn numbers into sentences.
- **Choice I made:** Minimum of 3 games per group. With a lower minimum, the coach gave "advice" based on 1-game flukes.
- **Result:** _[RESULT: copy the tips the app gives you]_
- **Test with a real person:** _[Did a friend read the tips? Did they understand them? Did you follow one in your next games, and what happened?]_

## Ideas for next experiments
- Follow one tip for a week (e.g. no FACEIT after 23:00) and compare before/after. ← a real data-driven decision!
- Add Premier matches.
- Compare myself with friends using the nickname box.
