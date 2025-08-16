import streamlit as st
from app_modules.utils import (
    init_storage, load_data, get_coordinates, save_data,
    get_recipe_of_the_day, set_recipe_of_the_day
)
from app_modules.forms import recipe_form
from app_modules.display import display_stats, show_recipes
import pandas as pd
import random
import time
# Page configuration
st.set_page_config(page_title="Roots & Recipes", page_icon="🍲", layout="centered")

# Initialize storage and load data
init_storage()
df = load_data()

if 'rating_sum' not in df.columns:
    df['rating_sum'] = 0
if 'rating_count' not in df.columns:
    df['rating_count'] = 0

# App title and intro
st.title("🍲 Roots & Recipes")
st.markdown("Share your traditional recipes and stories to help preserve cultural heritage. Submit yours below!")
st.markdown("💡 You can type in your native language! Use [Google Input Tools](https://www.google.com/inputtools/) if needed.")
st.markdown("----")

# Show Recipe of the Day if available
recipe_of_the_day = get_recipe_of_the_day()
if recipe_of_the_day:
    st.markdown("""
        <div style="
            background-color: #f9f9f9;
            border-left: 6px solid #FFA500;
            padding: 1.2em;
            border-radius: 8px;
            margin-bottom: 1.5em;
        ">
            <h3 style="margin-top: 0">🌟 Recipe of the Day 🌟</h3>
            <p><strong>Dish Name:</strong> {dish_name}</p>
            <p><strong>Taste Description:</strong> {taste}</p>
        </div>
    """.format(
        dish_name=recipe_of_the_day['dish_name'],
        taste=recipe_of_the_day['taste_description']
    ), unsafe_allow_html=True)

# Admin section to set Recipe of the Day
with st.expander("🔧 Admin: Set Recipe of the Day"):
    password = st.text_input("Enter admin password to set Recipe of the Day", type="password")
    if password == "admin123":
        recipe_options = df[["id", "dish_name"]].apply(
            lambda row: f"{row['dish_name']} (ID: {row['id']})", axis=1).tolist()
        selected = st.selectbox("Select a Recipe", options=recipe_options)
        taste_description = st.text_area("Describe how it tastes")

        if st.button("Set Recipe of the Day"):
            recipe_id = int(selected.split("ID: ")[1].strip(")"))
            set_recipe_of_the_day(recipe_id, taste_description)
            st.success(f"Recipe of the Day updated to '{selected.split(' (ID')[0]}'!")
    elif password:
        st.error("Incorrect password")

# Recipe submission form
df = recipe_form(df)

# Stats
display_stats(df)

# Map Integration
st.markdown("## 🗺️ Recipe Map (Country of Origin)")

if "country" in df.columns:
    if "latitude" not in df.columns or "longitude" not in df.columns or df["latitude"].isnull().all():
        coords = df["country"].apply(lambda c: get_coordinates(c) if c else (None, None))
        valid_coords = coords.apply(lambda x: x if isinstance(x, tuple) and len(x) == 2 else (None, None))

        if len(valid_coords) > 0:
            df["latitude"], df["longitude"] = zip(*valid_coords)
        else:
            df["latitude"], df["longitude"] = pd.Series(dtype=float), pd.Series(dtype=float)

        save_data(df)

    map_df = df.dropna(subset=["latitude", "longitude"])
    if not map_df.empty:
        st.map(map_df[["latitude", "longitude"]])
    else:
        st.info("No valid location data available yet.")
else:
    st.warning("🌍 Country field is missing from the data.")

# Search and filter + Show recipes with comments
show_recipes(df)
st.markdown("---")
st.caption("Made with ❤️ using Streamlit")

