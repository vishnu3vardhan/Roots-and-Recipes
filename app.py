import streamlit as st
import pandas as pd
import os
import datetime

# Constants
DATA_FILE = "data/recipes.csv"
os.makedirs("data", exist_ok=True)

# Initialize CSV file if it doesn't exist
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Name", "Language", "Dish Name", "Ingredients", "Instructions", "Story", "Timestamp"])
    df.to_csv(DATA_FILE, index=False)

# App Title & Intro
st.set_page_config(page_title="Roots & Recipes", page_icon="🍲", layout="centered")
st.title("🍲 Roots & Recipes")
st.markdown("Share your traditional recipes and stories to help preserve cultural heritage. Submit yours below!")

st.markdown("----")

# Recipe Submission Form
with st.expander("📝 Submit a New Recipe", expanded=True):
    with st.form("recipe_form"):
        st.subheader("Recipe Details")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name", placeholder="Optional").strip()
        with col2:
            language = st.text_input("Language or Dialect", placeholder="e.g., Punjabi, Swahili, Cajun").strip()

        dish = st.text_input("Dish Name", placeholder="e.g., Biryani, Gumbo, Jollof Rice").strip()
        ingredients = st.text_area("🧂 Ingredients", placeholder="List one ingredient per line")
        instructions = st.text_area("👩‍🍳 Cooking Instructions", placeholder="Describe how to prepare the dish")
        story = st.text_area("📖 Cultural Story or Memory", placeholder="Optional – share a memory or the story behind the dish")

        submitted = st.form_submit_button("📤 Submit Recipe")

        if submitted:
            new_entry = {
                "Name": name,
                "Language": language,
                "Dish Name": dish,
                "Ingredients": ingredients,
                "Instructions": instructions,
                "Story": story,
                "Timestamp": datetime.datetime.now().isoformat()
            }

            df = pd.read_csv(DATA_FILE)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)

            st.success("🎉 Thank you! Your recipe has been submitted.")

st.markdown("----")

# Display Recipes with Search Filter
st.header("📚 Explore Community Recipes")

df = pd.read_csv(DATA_FILE)

if not df.empty:
    # Search Filter
    search_query = st.text_input("🔍 Search recipes by dish name, language, or ingredient").strip().lower()

    if search_query:
        df_filtered = df[df.apply(
            lambda row: search_query in str(row["Dish Name"]).lower() 
                        or search_query in str(row["Language"]).lower()
                        or search_query in str(row["Ingredients"]).lower(),
            axis=1
        )]
    else:
        df_filtered = df

    if not df_filtered.empty:
        for i, row in df_filtered.iterrows():
            with st.expander(f"🍽️ {row['Dish Name']} ({row['Language']})", expanded=False):
                if row["Name"]:
                    st.markdown(f"**Submitted by:** {row['Name']}")
                st.markdown(f"**🧂 Ingredients:**\n{row['Ingredients']}")
                st.markdown(f"**👩‍🍳 Instructions:**\n{row['Instructions']}")
                if row["Story"]:
                    st.markdown(f"**📖 Story:** {row['Story']}")
    else:
        st.warning("No recipes matched your search. Try a different keyword.")
else:
    st.info("No recipes submitted yet. Be the first to share a taste of your tradition! 🌍")

# Footer
st.markdown("----")
st.caption("Made with ❤️ using Streamlit")
