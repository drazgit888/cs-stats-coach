"""CS Stats Coach: a Streamlit dashboard for my own CS2 matches."""
import streamlit as st

st.set_page_config(page_title="CS Stats Coach", page_icon="🎯", layout="wide")

st.title("🎯 CS Stats Coach")
st.write(
    "A coach made from my own Counter-Strike 2 numbers. "
    "It will show what I am good at and what I should practise."
)

api_key = st.secrets.get("FACEIT_API_KEY", None)
nickname = st.secrets.get("FACEIT_NICKNAME", None)

if not api_key or not nickname:
    st.info(
        "No FACEIT data connected yet. Add FACEIT_API_KEY and FACEIT_NICKNAME "
        "to .streamlit/secrets.toml (see the .example file) to load my matches."
    )
    st.stop()

st.success(f"Ready to load matches for **{nickname}**. (Coming next!)")
