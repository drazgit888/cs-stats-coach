"""Tactical-HUD look for the app: CSS + chart colours.

An original design: dark panels, orange/khaki accents, corner brackets.
No game logos, art or official fonts are used.
"""
import base64
import html
import re
from pathlib import Path

import plotly.express as px
import plotly.io as pio
import streamlit as st

ORANGE = "#F2A33A"
KHAKI = "#B8A77A"
OLIVE = "#6E7B4F"
SKY = "#7FA7C9"
WIN = "#7BC67B"
LOSS = "#E0574F"
TEXT = "#E8E2D0"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Share+Tech+Mono&display=swap');

h1, h2, h3, [data-testid="stMetricLabel"], [data-baseweb="tab"] p, [data-baseweb="tab"] div {{
    font-family: 'Rajdhani', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}
h1 {{ color: {ORANGE} !important; }}
h3 {{ border-left: 4px solid {ORANGE}; padding-left: 0.6rem; }}

/* HUD metric cards with corner brackets */
[data-testid="stMetric"] {{
    background: linear-gradient(180deg, rgba(242,163,58,0.08), rgba(0,0,0,0));
    border: 1px solid rgba(184,167,122,0.35);
    padding: 0.7rem 1rem;
    position: relative;
    clip-path: polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px);
}}
[data-testid="stMetricLabel"] {{ color: {KHAKI} !important; }}
[data-testid="stMetricValue"] {{
    font-family: 'Share Tech Mono', monospace !important;
    color: {ORANGE} !important;
}}

/* Tabs look like a buy-menu bar */
button[data-baseweb="tab"] {{ background: rgba(255,255,255,0.03); margin-right: 4px; }}
button[data-baseweb="tab"][aria-selected="true"] p {{ color: {ORANGE} !important; }}

/* Briefing cards */
.tip-card {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(184,167,122,0.25);
    border-left: 4px solid {ORANGE};
    padding: 0.75rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 1.05rem;
}}
.tip-card b {{ color: {ORANGE}; }}
.banner img {{ width: 100%; height: auto; display: block; margin-bottom: 0.5rem; }}

/* Little HUD strip under the title */
.hud-strip {{
    font-family: 'Share Tech Mono', monospace;
    color: {KHAKI};
    border-top: 1px solid rgba(184,167,122,0.35);
    border-bottom: 1px solid rgba(184,167,122,0.35);
    padding: 0.3rem 0;
    margin-bottom: 1rem;
    letter-spacing: 0.08em;
}}
.hud-strip b {{ color: {ORANGE}; }}
</style>
"""


def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)
    template = pio.templates["plotly_dark"]
    template.layout.paper_bgcolor = "rgba(0,0,0,0)"
    template.layout.plot_bgcolor = "rgba(0,0,0,0)"
    template.layout.font.color = TEXT
    template.layout.colorway = [ORANGE, KHAKI, SKY, OLIVE, "#C97F5A", "#9C8FB8"]
    pio.templates["hud"] = template
    px.defaults.template = "hud"


def hud_strip(**items):
    parts = " &nbsp;│&nbsp; ".join(f"{k.upper()} <b>{v}</b>" for k, v in items.items())
    st.markdown(f'<div class="hud-strip">⌖ &nbsp;{parts}</div>', unsafe_allow_html=True)


def banner():
    svg = Path(__file__).parent.joinpath("assets", "banner.svg").read_bytes()
    data = base64.b64encode(svg).decode()
    st.markdown(
        f'<div class="banner"><img src="data:image/svg+xml;base64,{data}" alt="CS Stats Coach banner"></div>',
        unsafe_allow_html=True,
    )


def tip_card(emoji, text):
    """A briefing card. **bold** in the text becomes highlighted orange."""
    safe = html.escape(text)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
    st.markdown(f'<div class="tip-card">{emoji}&nbsp; {safe}</div>', unsafe_allow_html=True)
