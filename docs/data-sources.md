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

## Safety and privacy
- The API key is a password. It is stored only in **Streamlit Cloud → Settings → Secrets**, never in the code or on GitHub (`.streamlit/secrets.toml` is in `.gitignore`).
- The app shows teammates' FACEIT nicknames, which are public on FACEIT anyway. _[DECIDE: blur friends' names in your video, or ask them if it's OK.]_

## Possible extra sources (not used yet)
- **Premier / Valve matchmaking:** sites like Leetify or csstats.gg, or my own demo files. Harder to get automatically.
- _[YOUR IDEA?]_
