import streamlit as st
from streamlit.utils import init_storage, load_data
from streamlit.forms import recipe_form
from streamlit.display import display_stats, show_recipes

# Page configuration
st.set_page_config(page_title="Roots & Recipes", page_icon="🍲", layout="centered")

# Initialize storage and load data
init_storage()
df = load_data()

# App title and intro
st.title("🍲 Roots & Recipes")
st.markdown("Share your traditional recipes and stories to help preserve cultural heritage. Submit yours below!")
st.markdown("💡 You can type in your native language! Use [Google Input Tools](https://www.google.com/inputtools/) if needed.")
st.markdown("----")

# Recipe submission
df = recipe_form(df)

# Stats
display_stats(df)

# Recipes
show_recipes(df)

# Footer
st.markdown("----")
st.caption("Made with ❤️ using Streamlit")
