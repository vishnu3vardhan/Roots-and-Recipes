import streamlit as st
from app_modules.utils import is_duplicate, add_entry, get_timestamp

def recipe_form(df):
    with st.expander("📝 Submit a New Recipe", expanded=True):
        with st.form("recipe_form"):
            st.subheader("Recipe Details")

            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Your Name", placeholder="Optional").strip()
            with col2:
                language = st.text_input("Language or Dialect", placeholder="e.g., Tamil, Kannada, Garhwali").strip()

            dish = st.text_input("Dish Name", placeholder="e.g., Pongal, Litti Chokha").strip().title()
            category = st.selectbox("Recipe Type", ["Main Course", "Snack", "Dessert", "Festival Special", "Other"])
            ingredients = st.text_area("🧂 Ingredients", placeholder="List one ingredient per line")
            instructions = st.text_area("👩‍🍳 Cooking Instructions", placeholder="Describe how to prepare the dish")
            story = st.text_area("📖 Cultural Story or Memory", placeholder="Optional – share a memory or the story behind the dish")

            submitted = st.form_submit_button("📤 Submit Recipe")

            if submitted:
                if dish and ingredients and instructions:
                    if is_duplicate(df, name, dish):
                        st.warning("⚠️ You've already submitted this recipe.")
                    else:
                        entry = {
                            "Name": name,
                            "Language": language,
                            "Dish Name": dish,
                            "Category": category,
                            "Ingredients": ingredients,
                            "Instructions": instructions,
                            "Story": story,
                            "Timestamp": get_timestamp()
                        }
                        df = add_entry(df, entry)
                        st.success("🎉 Thank you! Your recipe has been submitted.")
                else:
                    st.error("❌ Please fill in at least Dish Name, Ingredients, and Instructions.")
    return df
