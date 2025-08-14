import os
import pandas as pd
import streamlit as st
from app_modules.utils import (
    is_duplicate,
    add_entry,
    get_timestamp,
    save_image,
    add_comment  # from utils.py, works with DB/CSV
)

# CSV file location if using CSV fallback for comments
COMMENTS_FILE = "data/comments.csv"

# -----------------------
# Recipe submission form
# -----------------------
def recipe_form(df):
    """Display recipe submission form and return updated DataFrame."""
    with st.expander("📝 Submit a New Recipe", expanded=True):
        with st.form(key="recipe_form"):
            st.subheader("Recipe Details")

            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Your Name", placeholder="").strip()
            with col2:
                language = st.text_input(
                    "Language or Dialect",
                    placeholder="e.g., Telugu, Telangana, Andra"
                ).strip()

            dish = st.text_input(
                "Dish Name",
                placeholder="e.g., Pongal, Litti Chokha"
            ).strip().title()

            category = st.selectbox(
                "Recipe Type",
                ["Main Course", "Snack", "Dessert", "Festival Special", "Other"]
            )

            country = st.text_input(
                "Country of Origin",
                placeholder="e.g., India"
            ).strip()

            ingredients = st.text_area(
                "🧂 Ingredients",
                placeholder="List one ingredient per line"
            )

            instructions = st.text_area(
                "👩‍🍳 Cooking Instructions",
                placeholder="Describe how to prepare the dish"
            )

            story = st.text_area(
                "📖 Cultural Story or Memory",
                placeholder="Optional – share a memory or the story behind the dish"
            )

            image_file = st.file_uploader(
                "Upload an image of your dish (optional)",
                type=["png", "jpg", "jpeg"]
            )

            submitted = st.form_submit_button("📤 Submit Recipe")

            if submitted:
                if dish and ingredients and instructions:
                    if is_duplicate(df, name, dish):
                        st.warning("⚠️ This recipe is already submitted.")
                    else:
                        image_path = save_image(image_file, dish) if image_file else None
                        entry = {
                            "name": name,
                            "language": language,
                            "dish_name": dish,
                            "category": category,
                            "country": country,
                            "ingredients": ingredients,
                            "instructions": instructions,
                            "story": story,
                            "image_path": image_path,
                            "timestamp": get_timestamp()
                        }
                        df = add_entry(df, entry)
                        st.success("🎉 Thank you! Your recipe has been submitted.")
                else:
                    st.error("❌ Please fill in at least Dish Name, Ingredients, and Instructions.")

    return df

# -----------------------
# Star rating widget
# -----------------------
def star_rating_widget(label="Rate this recipe", max_stars=5):
    """Display a horizontal star rating selector."""
    return st.radio(label, list(range(1, max_stars + 1)), horizontal=True)

# -----------------------
# Comment form with rating
# -----------------------
def comment_form(recipe_id):
    """Display a comment form for a specific recipe."""
    with st.form(key=f"comment_form_{recipe_id}"):
        st.subheader("💬 Leave a Comment")
        commenter_name = st.text_input("Your Name", placeholder="Anonymous")

        # Star rating for this recipe
        rating = star_rating_widget("Rate this recipe", max_stars=5)

        comment_text = st.text_area("Your Comment")
        submitted = st.form_submit_button("Submit Comment")

        if submitted:
            if comment_text.strip():
                add_comment(
                    recipe_id,
                    commenter_name.strip() or "Anonymous",
                    comment_text.strip(),
                    rating  # save rating too
                )
                st.success(f"Thank you! You rated this recipe {rating}⭐.")
                st.experimental_rerun()
            else:
                st.error("Please write a comment before submitting.")

# -----------------------
# CSV Fallback add_comment
# (only used if not using utils.py DB version)
# -----------------------
def add_comment_csv(recipe_id, name, comment, rating):
    """Fallback: store comment + rating in CSV file."""
    new_comment = pd.DataFrame([{
        "recipe_id": recipe_id,
        "name": name,
        "comment": comment,
        "rating": rating
    }])

    try:
        df = pd.read_csv(COMMENTS_FILE)
        df = pd.concat([df, new_comment], ignore_index=True)
    except FileNotFoundError:
        df = new_comment

    df.to_csv(COMMENTS_FILE, index=False)

def get_top_rated_recipes_csv():
    """Fallback: get top rated recipes from CSV."""
    df = pd.read_csv(COMMENTS_FILE)
    avg_ratings = df.groupby("recipe_id")["rating"].mean().reset_index()
    return avg_ratings.sort_values(by="rating", ascending=False)
