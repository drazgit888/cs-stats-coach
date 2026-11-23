# Design system (v6, "pink poster")

**Current version: v6.** v5 ("analyst's console", sidebar, quiet surfaces) was tried and rejected: it felt too mixed and less fun. v6 brings back the v4 poster layout (top menu, big bold italic titles, icon cards, drawn background scenes) in the colours of my avatar.

## v6 colours
| Token | HEX | Used for |
|---|---|---|
| `--bg` | `#0E0B11` | Background (charcoal with a plum tint) |
| `--pink` | `#FF4FA3` | Main accent: titles, buttons, wins, bars, charts |
| `--pink-2` | `#FF86C4` | Hover, light pink |
| `--violet` | `#A35CFF` | Second accent: night scenes, lower bars |
| `--text` / `--muted` | `#F7EEF4` / `#A898A8` | Text |
| `--faceit` | `#FF5500` | FACEIT only (level, Elo, FACEIT block) |
| `--premier` | `#4FD1E8` | CS2 Premier only |
| `--steam` | `#8FB3D9` | Steam only |

## v6 rules
- Two main sources: **FACEIT** and **CS2 Premier**. Each has its own block and colour; they are never mixed or compared.
- Premier comes through Leetify, so every place with Premier data shows the official "Data Provided by Leetify" badge. Leetify's own metrics (aim, positioning, utility, Leetify rating) are not shown.
- One topic per page: Home, Profile, Briefing, Matches, Maps, Squad, Progress, Premier, Steam, Highlights.
- Coach points are concrete: real numbers, how many games they are based on (3+), and one "Do this" action.
- Font: Barlow Condensed (titles) + Barlow (text), from Google Fonts.

---

# Earlier: v5 design system (rejected)

The goal: a premium esports analytics look, somewhere between FACEIT, Leetify and HLTV, built from the colours of my own avatar (charcoal, violet, magenta). Quiet surfaces, colour only where it means something.

All tokens live at the top of `dashboard.html` (`:root { ... }`).

## Colours

| Token | HEX | Used for |
|---|---|---|
| `--bg` | `#0E0D12` | Page background (deep charcoal) |
| `--s1` | `#17151E` | Cards, sidebar |
| `--s2` | `#1F1C28` | Tiles inside cards |
| `--s3` | `#29253A` | Hover and active menu item |
| `--line` | `#2D2A3A` | Thin lines, only inside tables and stat strips |
| `--text` | `#F4F2F8` | Main text |
| `--text2` | `#C4C1CF` | Secondary text (cool light grey) |
| `--muted` | `#8E8A9C` | Labels |
| `--violet` | `#8B5CF6` | Primary: menu, buttons, my own trend lines |
| `--violet-hi` | `#A78BFA` | Violet text and the 10-match average line |
| `--violet-deep` | `#5B3BB8` | Per-match lines, quiet bars |
| `--magenta` | `#E055C8` | Rare highlights ("best map") |
| `--win` | `#3DD68C` | Win / better than my average |
| `--loss` | `#F0606A` | Loss / worse than my average |

### One colour per data source
| Source | HEX | Rule |
|---|---|---|
| FACEIT | `#FF5500` | Only FACEIT level, Elo and FACEIT labels |
| Leetify | `#F84982` | Sampled from the official badge file; the badge itself is never changed |
| Steam | `#8FB3D9` | Steam status and (later) playtime |
| Premier | `#4FD1E8` | Premier rating, kept apart from FACEIT and from Competitive |

Source colours appear as a small dot + label, a thin line on top of that source's card, and that source's chart. They never fill a whole card. Numbers from different sources are never mixed or compared directly.

## Typography
| Role | Font | Size |
|---|---|---|
| Headings and big numbers | Space Grotesk 600 | 14 to 26px |
| Body text | Inter 400 / 500 | 12 to 14px |
| Small source tags | JetBrains Mono 500, caps | 10.5 to 11px |

All numbers use tabular figures so columns line up. Nothing is larger than about 32px.

## Spacing and shape
- 4px grid: 4, 8, 12, 16, 24
- Card padding 16px, gaps 10 to 16px
- Corner radius: 8 (buttons), 10 (tiles), 14 (cards)
- No borders around cards: the three surface shades separate blocks

## Components
Card, stat tile, KPI strip, source tag, result bar (green win / red loss), last-10 form bar, segmented control (chart metric switch), ghost and primary buttons, "Not connected" / "Not available" empty states.

## Charts
- Chart.js with one shared theme (faint grid, muted axis text, dark tooltip)
- Per match: thin deep-violet line, dots green (won) or red (lost)
- 10-match average: dashed light violet
- Each chart has a one-line caption saying what it answers and what is calculated

## Layout
- Sidebar (220px) grouped: Player, Performance, Sources, Media
- Top bar: page name, last update time, live status of each source
- Below 860px the sidebar becomes a scrolling tab row; tiles and stats go into 2 columns

## Honesty rules
- Never show a number that a source did not give; show "Not available" or "Not connected" instead
- Leetify values exactly as returned (no renaming, rescaling or recalculating), with the official badge
- Elo history is not drawn, because the FACEIT Data API does not give Elo per match
