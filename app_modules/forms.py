import os
import pandas as pd
import streamlit as st
from app_modules.utils import (
    is_duplicate,
    add_entry,
    get_timestamp,
    save_image,
    add_comment
)

COMMENTS_FILE = "data/comments.csv"

# -----------------------
# Recipe submission form
# -----------------------
def recipe_form(df):
    """Display recipe submission form and return updated DataFrame."""
    with st.expander("📝 Submit a New Recipe", expanded=True):
        st.markdown("Fill out the form below to share your delicious tradition with the world 🌍")

        with st.form(key="recipe_form"):
            st.subheader("📋 Recipe Details")

            # Name and Language
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("👤 Your Name", placeholder="").strip()
            with col2:
                language = st.text_input("🗣️ Language or Dialect", placeholder="e.g., Telugu, Awadhi").strip()

            # Dish and Category
            col3, col4 = st.columns(2)
            with col3:
                dish = st.text_input("🍛 Dish Name *", placeholder="e.g., Pongal").strip().title()
            with col4:
                category = st.selectbox(
                    "📂 Recipe Type",
                    ["Main Course", "Snack", "Dessert", "Festival Special", "Other"]
                )

            # Country of Origin
            country = st.text_input("🌍 Country of Origin", placeholder="e.g., India").strip()

            # Ingredients
            ingredients = st.text_area("🧂 Ingredients *", placeholder="List one ingredient per line")

            # Instructions
            instructions = st.text_area("👩‍🍳 Cooking Instructions *", placeholder="Step-by-step guide")

            # Story / Memory
            story = st.text_area("📖 Cultural Story or Memory", placeholder="Optional – Share a memory or background")

            # Image upload
            image_file = st.file_uploader("📷 Upload an image of your dish (optional)", type=["png", "jpg", "jpeg"])
            if image_file:
                st.image(image_file, width=200, caption="Image Preview")

            # Submit button
            submitted = st.form_submit_button("📤 Submit Recipe")

            # Validation & submission
            if submitted:
                if dish and ingredients and instructions:
                    if is_duplicate(df, name, dish):
                        st.warning("⚠️ This recipe has already been submitted.")
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
                        st.success("🎉 Thank you! Your recipe has been submitted successfully.")
                else:
                    st.error("❌ Please fill in all required fields marked with *.")

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

        col1, col2 = st.columns([2, 1])
        with col1:
            commenter_name = st.text_input("📝 Your Name", placeholder="Anonymous")
        with col2:
            rating = star_rating_widget("⭐ Rate this recipe")

        comment_text = st.text_area("🗨️ Your Comment")

        submitted = st.form_submit_button("📬 Submit Comment")

        if submitted:
            if comment_text.strip():
                add_comment(
                    recipe_id,
                    commenter_name.strip() or "Anonymous",
                    comment_text.strip(),
                    rating
                )
                st.success(f"✅ Thank you! You rated this recipe {rating}⭐.")
                st.experimental_rerun()
            else:
                st.error("❌ Please write a comment before submitting.")

# -----------------------
# CSV fallback
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
