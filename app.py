import streamlit as st
import pandas as pd
import os
import datetime

# Constants
DATA_FILE = "data/recipes.csv"
COLUMNS = ["Name", "Language", "Dish Name", "Category", "Ingredients", "Instructions", "Story", "Timestamp"]

# Set up storage
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=COLUMNS)
    df.to_csv(DATA_FILE, index=False)

# Load data once
df = pd.read_csv(DATA_FILE)

# Page configuration
st.set_page_config(page_title="Roots & Recipes", page_icon="🍲", layout="centered")

# Title & intro
st.title("🍲 Roots & Recipes")
st.markdown("Share your traditional recipes and stories to help preserve cultural heritage. Submit yours below!")
st.markdown("💡 You can type in your native language! Use [Google Input Tools](https://www.google.com/inputtools/) if needed.")
st.markdown("----")

# Recipe Submission Form
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
                # Check for duplicates
                duplicate = df[
                    (df["Dish Name"].str.lower() == dish.lower()) &
                    (df["Name"].str.lower() == name.lower())
                ] if name else pd.DataFrame()

                if not duplicate.empty:
                    st.warning("⚠️ You've already submitted this recipe.")
                else:
                    new_entry = {
                        "Name": name,
                        "Language": language,
                        "Dish Name": dish,
                        "Category": category,
                        "Ingredients": ingredients,
                        "Instructions": instructions,
                        "Story": story,
                        "Timestamp": datetime.datetime.now().isoformat()
                    }
                    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)
                    st.success("🎉 Thank you! Your recipe has been submitted.")
            else:
                st.error("❌ Please fill in at least Dish Name, Ingredients, and Instructions.")

st.markdown("----")

# Community Stats
st.subheader("📊 Community Stats")
st.markdown(f"- **Total Recipes:** {len(df)}")
st.markdown(f"- **Languages Represented:** {df['Language'].nunique()}")
st.markdown(f"- **Contributors:** {df['Name'].nunique() if 'Name' in df else 'N/A'}")

st.markdown("----")

# Display Recipes
st.header("📚 Explore Community Recipes")

if not df.empty:
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        search_query = st.text_input("🔍 Search recipes by dish name, language, or ingredient").strip().lower()
    with col2:
        sort_option = st.selectbox("📁 Sort recipes by", ["Most Recent", "Alphabetical"])

    languages = sorted(df["Language"].dropna().unique())
    lang_filter = st.selectbox("🌐 Filter by Language", ["All"] + languages)

    # Filter and sort
    df_filtered = df.copy()

    if search_query:
        df_filtered = df_filtered[df_filtered.apply(
            lambda row: search_query in str(row["Dish Name"]).lower()
                        or search_query in str(row["Language"]).lower()
                        or search_query in str(row["Ingredients"]).lower(),
            axis=1
        )]

    if lang_filter != "All":
        df_filtered = df_filtered[df_filtered["Language"] == lang_filter]

    if sort_option == "Most Recent":
        df_filtered = df_filtered.sort_values(by="Timestamp", ascending=False)
    else:
        df_filtered = df_filtered.sort_values(by="Dish Name")

    if not df_filtered.empty:
        for _, row in df_filtered.iterrows():
            with st.expander(f"🍽️ {row['Dish Name']} ({row['Language']})", expanded=False):
                if row["Name"]:
                    st.markdown(f"**👤 Submitted by:** {row['Name']}")
                st.markdown(f"**📂 Category:** {row['Category']}")
                st.markdown(f"**🧂 Ingredients:**\n{row['Ingredients']}")
                st.markdown(f"**👩‍🍳 Instructions:**\n{row['Instructions']}")
                if row["Story"]:
                    st.markdown(f"**📖 Story:** {row['Story']}")
    else:
        st.warning("No recipes matched your search or filters.")
else:
    st.info("No recipes submitted yet. Be the first to share a taste of your tradition! 🌍")

# Footer
st.markdown("----")
st.caption("Made with ❤️ using Streamlit")
