# CS Stats Coach: report

**Course:** HAN minor Data-Driven Decision Making (DATDRD05), individual project
**Student:** diana
**App:** https://cs-stats-coach-fencmkvjwvvwbpmx4hwappv.streamlit.app/
**Code:** https://github.com/drazgit888/cs-stats-coach

> This report follows **CRISP-DM** (Chapman et al., 2000), the process model used as the guiding principle in this minor.
> Spots marked **TODO** are for me to fill in with my own observations and real results. No numbers in this report are made up: the only real numbers so far come from the first live run of the app (20 Nov 2026).

---

## 0. Summary
I play Counter-Strike 2 on FACEIT and in Premier (about 210 hours). After every match the platforms show long lists of numbers, but they don't tell me **what to change** to win more. I built **CS Stats Coach**, a Streamlit web app that loads my own FACEIT matches, finds patterns (maps, time of day, teammates, aim) and turns them into plain-language coach tips. Then I test one tip as a real decision with a before/after experiment.

TODO (after the experiment): one sentence with the main result.

---

## 1. Business case
| Question | Answer |
|---|---|
| **What problem do I solve?** | Players have lots of match data but no clear advice. FACEIT shows lists, not answers to "where, when and with whom do I play best?" |
| **Who benefits?** | (1) Me: I want to win more and climb FACEIT levels. (2) My friends I play with: they can type their own nickname in the app. (3) Any amateur FACEIT player who doesn't want to pay for a coaching tool. |
| **What decision does the data support?** | Choices before and between matches: which map to pick or ban, what time to stop playing, whether to queue with a friend, when to take a break after a loss. |
| **How do I know it works?** | A before/after experiment: follow one tip for 10 matches and compare with the 10 matches before (see [experiments.md](experiments.md#experiment-7-no-faceit-after-2300-beforeafter)). |
| **Value** | Free, personal, explained in normal words. Paid tools (for example Leetify Pro) exist, so there is a real need for this kind of help. |

**Why this project:** it is about something I really care about (fun criterion), it uses my own real data, and it ends in a concrete decision, which is the point of the minor.

---

## 2. CRISP-DM phase 1: Business understanding
- **Goal:** win more FACEIT matches by changing *when, where and with whom* I play, based on my own data.
- **Main question:** *What should I change to win more?*
- **Sub-questions** (each became a page in the app):
  1. Is my aim getting better? (K/D trend)
  2. Which maps do I win most and least on?
  3. Do I play worse late at night?
  4. Which teammates help me win? Friends vs strangers?
  5. Does good aim actually mean I win?
  6. Do I play worse right after a loss (tilt)?
- **Success criterion (data mining):** the app gives at least one tip that is based on ≥ 3 games per group and that I can test.
- **Success criterion (business):** after following one tip for 10 matches, my win rate or K/D is better than in the 10 matches before. TODO: was it?
- **Inspiration from the videos:** the data storytelling video (question → evidence → conclusion → action) and the CS2 "aged like fine wine" analysis (a weighted score plus a trend over time). See [video-choice.md](video-choice.md).

Details: [topic-analysis.md](topic-analysis.md).

## 3. CRISP-DM phase 2: Data understanding
- **Source 1: FACEIT Data API** (FACEIT, n.d.): my profile, my last ≤ 100 matches with stats per match, and match details for teammates.
- **Source 2 (optional): Leetify public API** (Leetify, n.d.): Premier and matchmaking matches. Shown separately, never mixed with FACEIT, following Leetify's developer guidelines.
- **First look at the data (20 Nov 2026, real):** 61 FACEIT matches, level 3, Elo 888, 46 % win rate, K/D 0.98, 39 % headshots.
- **What I noticed:** K/D jumps a lot from match to match; the 10-match average sits around 1.0.
- **Data quality and limits:**
  - Max 100 matches per request; only 61 at the start, so many groups are small.
  - FACEIT does not include Premier games.
  - Win/loss depends on 5 players, not only me.
  - Match list has no teams → extra request per match.

Details: [data-sources.md](data-sources.md).

## 4. CRISP-DM phase 3: Data preparation
1. Text → numbers (kills, deaths, K/D, HS %, ADR).
2. Map names cleaned (`de_mirage` → Mirage).
3. Match end time converted to Dutch time; sorted oldest → newest.
4. New columns: time of day (morning / afternoon / evening / late night), weekday, hour, "with a friend or only strangers".
5. Teammates found from match details; answers cached for 24 h to keep the app fast.
6. Groups with fewer than 3 games are excluded from tips.

Details: [methods.md](methods.md).

## 5. CRISP-DM phase 4: Modelling (analysis)
I did not train a machine-learning model; with ~60–100 matches that would overfit. I used descriptive statistics and simple rules, which fit the "math & stats" and "data visualisation" techniques of the minor.

| Technique | Used for |
|---|---|
| Win rate per group (grouping) | maps, time of day, weekday, teammates |
| Rolling average (10 games) | K/D trend without the noise |
| Before/after comparison | "in form": last 10 games vs earlier |
| Conditional win rate | tilt check: win rate after a loss vs after a win (games < 2 h apart) |
| Scatter plot | does K/D or HS % separate won and lost matches? |
| Rule-based coach | 7 rules turn numbers into tips (see [methods.md](methods.md#coach-rules)) |

**Idea for next step (inspired by the CS2 "fine wine" video):** a personal **form index**, a weighted score of K/D, ADR and win rate per 10 matches, with a trend line (slope) to show if I'm getting better. TODO: decide if I build this.

**Why these choices:** simple methods are easy to explain to a player (storytelling), and the "minimum 3 games" rule protects against conclusions from luck.

## 6. CRISP-DM phase 5: Evaluation
- **Technical check:** every version was tested with made-up FACEIT answers before upload, then checked on the live app.
- **Do the tips make sense?** TODO: copy the tips the app gives me and say if they feel true.
- **Feedback from a real user:** TODO: show the app to a friend; what did they understand, what was confusing?
- **Real decision test:** Experiment 7 in [experiments.md](experiments.md). TODO: fill in the results table and conclusion.
- **Limits of my evaluation:**
  - Small samples (10 vs 10 matches): a difference can be luck.
  - Correlation is not causation: late-night games may also have other opponents.
  - Teammates and opponents change every match.

## 7. CRISP-DM phase 6: Deployment
- **Live app** on Streamlit Community Cloud, deployed from GitHub; anyone with the link can use it with their own nickname.
- **Security:** API keys only in Streamlit Secrets, never in the code or on GitHub.
- **Versions:** v1 (Plotly charts) → v2 (HUD theme) → v3 (own HTML design) → v4 poster style → later redesigns. Screenshots in [images/](images/).
- **Sharing:** code on GitHub, this portfolio in `docs/`, a presentation video (max 15 min). See [presentation-outline.md](presentation-outline.md).
- **Next steps:** TODO (for example: form index, Premier data via Leetify, compare with friends).

---

## 8. Reflection
TODO (my own words):
- What did I learn about data storytelling?
- What was hard? What would I do differently?
- How was working with an AI assistant when I don't code myself? What did I have to check or correct?

---

## References
Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide*. SPSS.

FACEIT. (n.d.). *FACEIT Data API documentation*. Retrieved November 23, 2026, from https://docs.faceit.com

Leetify. (n.d.). *Leetify API developer guidelines*. Retrieved November 23, 2026, from https://leetify.com/blog/leetify-api-developer-guidelines/

Streamlit. (n.d.). *Streamlit documentation*. Retrieved November 23, 2026, from https://docs.streamlit.io

TODO [author/channel]. (TODO year). *Become a Data Storyteller with Streamlit!* [Video]. YouTube. TODO link from course list

TODO [author/channel]. (TODO year). *Realtime Streamlit dashboard* [Video]. YouTube. TODO link from course list

Data Professor. (TODO year). *Building an interactive EDA app with a movies dataset* [Video]. YouTube. TODO link from course list

TODO [author/channel]. (TODO year). *Which CS2 pro aged like fine wine? A data analysis* [Video]. YouTube. https://www.youtube.com/watch?v=-q8b_poGgjQ

> How to fill in a video reference: open the video on YouTube, use the **channel name** as author, the **upload year**, and the exact title. Format: Channel Name. (Year, Month Day). *Title* [Video]. YouTube. URL
