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

## Experiment 7: No FACEIT after 23:00 (before/after)
This is the **real data-driven decision** of my project: I follow one coach tip and measure if it helps.

### 1. Question and hypothesis
- **Question:** Do I win more and play better if I stop playing FACEIT after 23:00?
- **Why this tip:** _[TODO: what does the "When I play" page say about late-night games? Copy win rate and number of games per time of day.]_
- **Hypothesis (write it BEFORE you start):** _[TODO, e.g. "After the rule my win rate and K/D will go up, because I'm less tired."]_

### 2. Rule
- **Decision:** no FACEIT match that **starts after 23:00** (Dutch time). Everything else stays the same as normal (same maps, same friends if possible).
- **Start date:** _[TODO]_  **End date:** _[TODO]_
- If I break the rule, I still write the match down and mark it (see column "Broke rule?").

### 3. Design
| | Before (baseline) | After (with the rule) |
|---|---|---|
| Matches | my **last 15** FACEIT matches before the start date | my **next 15** FACEIT matches after the start date |
| Where I get the numbers | Matches page in the app (or FACEIT match page) | same |

15 vs 15 is small, but it's what I can play in about 1–2 weeks. If there's time, I go up to 20 vs 20.

### 4. What I measure
| Metric | What it means | Why |
|---|---|---|
| **Win rate** | % of matches won | the main goal |
| **K/D** | kills ÷ deaths | my own performance, less dependent on the team |
| **ADR** | average damage per round | performance, also when I don't get the kill |
| **HS %** | % of kills that were headshots | aim quality |
| **Elo change** | Elo at end − Elo at start | does it help me climb? |

### 5. Data: before (last 15 matches)
| # | Date | Start time | Map | Won? (W/L) | K/D | ADR | HS % |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | | | | | | | |
| 9 | | | | | | | |
| 10 | | | | | | | |
| 11 | | | | | | | |
| 12 | | | | | | | |
| 13 | | | | | | | |
| 14 | | | | | | | |
| 15 | | | | | | | |

### 6. Data: after (next 15 matches)
| # | Date | Start time | Map | Won? (W/L) | K/D | ADR | HS % | Broke rule? |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |
| 2 | | | | | | | | |
| 3 | | | | | | | | |
| 4 | | | | | | | | |
| 5 | | | | | | | | |
| 6 | | | | | | | | |
| 7 | | | | | | | | |
| 8 | | | | | | | | |
| 9 | | | | | | | | |
| 10 | | | | | | | | |
| 11 | | | | | | | | |
| 12 | | | | | | | | |
| 13 | | | | | | | | |
| 14 | | | | | | | | |
| 15 | | | | | | | | |

### 7. Results
| Metric | Before | After | Difference (after − before) |
|---|---|---|---|
| Win rate | | | |
| Average K/D | | | |
| Average ADR | | | |
| Average HS % | | | |
| Elo change | | | |

How to calculate: win rate = wins ÷ 15 × 100; averages = sum of the column ÷ 15.

### 8. Conclusion
- **Was my hypothesis right?** _[TODO]_
- **Could it be luck?** With 15 matches, one or two lucky games change the win rate by 7–13 %. A difference of only a few % says almost nothing. _[TODO: is your difference big or small?]_
- **Other things that changed:** _[TODO: new friends in the team, different maps, a new CS update, exams, work shifts…]_
- **My decision:** _[TODO: keep the rule, drop it, or test longer?]_

### 9. What I learned
_[TODO, YOUR WORDS]_

## Ideas for next experiments
- ~~Follow one tip for a week (e.g. no FACEIT after 23:00) and compare before/after.~~ → now Experiment 7.
- A personal **form index** (weighted K/D, ADR and win rate per 10 matches + trend line), inspired by the CS2 "aged like fine wine" video.
- Add Premier matches.
- Compare myself with friends using the nickname box.
