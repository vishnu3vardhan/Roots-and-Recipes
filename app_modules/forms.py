import streamlit as st
from app_modules.utils import is_duplicate, add_entry, get_timestamp, save_image, add_comment

def recipe_form(df):
    with st.expander("📝 Submit a New Recipe", expanded=True):
        with st.form("recipe_form"):
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

def comment_form(recipe_id):
    with st.form(f"comment_form_{recipe_id}"):
        st.subheader("💬 Leave a Comment")
        commenter_name = st.text_input("Your Name", placeholder="Anonymous")
        comment_text = st.text_area("Your Comment")
        submitted = st.form_submit_button("Submit Comment")

        if submitted:
            if comment_text.strip():
                add_comment(recipe_id, commenter_name.strip() or "Anonymous", comment_text.strip())
                st.success("Thank you for your comment!")
                st.experimental_rerun()
            else:
                st.error("Please write a comment before submitting.")
