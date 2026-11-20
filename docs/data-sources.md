# Data sources

## Main source: FACEIT Data API
- **What it is:** FACEIT is the platform where I play competitive CS2. Its Data API lets apps ask for player and match information.
- **Website:** https://developers.faceit.com (docs: https://docs.faceit.com)
- **Cost:** free, you need a (server-side) API key.
- **My player:** nickname `busiks1`.

### What I ask FACEIT for
| Question to FACEIT | Endpoint | What I get |
|---|---|---|
| "Who is busiks1?" | `GET /players?nickname=busiks1&game=cs2` | player id, FACEIT level, Elo |
| "What were their last matches?" | `GET /players/{id}/games/cs2/stats?limit=100` | per match: map, result, kills, deaths, assists, K/D, headshot %, ADR, time |
| "Who played in this match?" | `GET /matches/{match_id}` | both teams and their players → my teammates |

### Data I use (one row = one match)
| Column | Meaning |
|---|---|
| `map` | Map name (Mirage, Inferno, Dust2...) |
| `won` | Did my team win? |
| `kills`, `deaths`, `assists` | My numbers in that match |
| `kd` | Kills ÷ deaths (above 1 = more kills than deaths) |
| `hs_pct` | % of my kills that were headshots |
| `adr` | Average damage per round |
| `played_at` | When the match ended (changed to Dutch time) |
| `time_of_day`, `weekday`, `hour` | Made from `played_at` |
| `teammate` | Made from the match details |

### Limits of this data
- FACEIT gives at most **100 matches** per question. When I first loaded it I had **61 matches**.
- Only **FACEIT** matches. My **Premier** (Valve matchmaking) games are not in it.
- Win/loss depends on the whole team, not only me.

## Second source: Leetify API (Premier and matchmaking)
Leetify reads my Valve matches (Premier and Competitive), which FACEIT cannot see. It is a **separate source**: its numbers are never mixed with FACEIT numbers.

- **Switched on with** `LEETIFY_ENABLED = "true"` in Secrets (default: off). Also `LEETIFY_API_KEY` and optionally `STEAM_ID`.
- **What I ask for:** my profile (`/v3/profile`: ranks, rating, winrate, recent matches) and my match list (`/v3/profile/matches`).
- **Leetify's rules I follow** ([API Developer Guidelines](https://leetify.com/blog/leetify-api-developer-guidelines/)):
  - **No storing or caching:** the data is fetched fresh on every visit and never saved.
  - **No changing metrics:** values are shown exactly as returned (no renaming, rescaling or recalculating).
  - **Credit:** the official "Data Provided by Leetify" badge (unchanged file) links to leetify.com, and every card has a "View on Leetify" link.
- **Premier and Competitive are kept separate:** Premier is one rating; Competitive is a rank per map.
- **If Leetify fails** (wrong key, no profile, rate limit, timeout): the Leetify page shows a short safe message and the FACEIT pages keep working.
- **Limits:** the endpoint details come from an unofficial description of the API, so field names may change; the exact rate limit is unknown; only matches Leetify has processed are included.

## Safety and privacy
- API keys (FACEIT and Leetify) are passwords. The Leetify key is only sent in a request header, never shown on the page, in error messages or in logs.
- The API key is a password. It is stored only in **Streamlit Cloud → Settings → Secrets**, never in the code or on GitHub (`.streamlit/secrets.toml` is in `.gitignore`).
- The app shows teammates' FACEIT nicknames, which are public on FACEIT anyway. _[DECIDE: blur friends' names in your video, or ask them if it's OK.]_

## Possible extra sources (not used yet)
- **Steam:** playtime (hours) via the Steam Web API. Not built yet.
- **csstats.gg / my own demo files:** harder to get automatically.
- _[YOUR IDEA?]_
