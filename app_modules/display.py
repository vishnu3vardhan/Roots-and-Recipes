import streamlit as st
import os
from app_modules.utils import get_comments, get_recipe_of_the_day


def display_stats(df):
    st.subheader("Regional Telangana Recipes")

    total = len(df)
    languages = df["language"].nunique() if "language" in df.columns else 0
    contributors = df["name"].nunique() if "name" in df.columns else 0

    st.markdown(f"- **Total Recipes:** {total}")
    st.markdown(f"- **Languages Represented:** {languages}")
    st.markdown(f"- **Contributors:** {contributors}")
    st.markdown("----")


def show_recipes(df):
    st.header("🍽️ Explore Regional Recipes")

    # Show Recipe of the Day above recipes list
    recipe_of_the_day = get_recipe_of_the_day()
    if recipe_of_the_day:
        st.subheader("Recipe of the Day")
        st.markdown(f"**Dish Name:** {recipe_of_the_day['dish_name']}")
        st.markdown(f"**Taste Description:** {recipe_of_the_day['taste_description']}")
        st.markdown("---")

    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            search_query = st.text_input("🔍 Search recipes by dish name or ingredient").strip().lower()
        with col2:
            sort_option = st.selectbox("Sort recipes by", ["Most Recent", "Alphabetical"])

        df_filtered = df.copy()

        if search_query:
            df_filtered = df_filtered[df_filtered.apply(
                lambda row: search_query in str(row.get("dish_name", "")).lower()
                            or search_query in str(row.get("ingredients", "")).lower(),
                axis=1
            )]

        if sort_option == "Most Recent":
            df_filtered = df_filtered.sort_values(by="timestamp", ascending=False)
        else:
            df_filtered = df_filtered.sort_values(by="dish_name")

        if not df_filtered.empty:
            from app_modules.forms import comment_form  # import here to avoid circular imports

            for _, row in df_filtered.iterrows():
                with st.expander(f"🍽️ {row['dish_name']}", expanded=False):
                    if row.get("name"):
                        st.markdown(f"**👤 Submitted by:** {row['name']}")
                    st.markdown(f"**📂 Category:** {row.get('category', '')}")
                    st.markdown(f"**🌍 Country:** {row.get('country', '')}")
                    st.markdown(f"**🧂 Ingredients:**\n{row.get('ingredients', '')}")
                    st.markdown(f"**👩‍🍳 Instructions:**\n{row.get('instructions', '')}")
                    if row.get("story"):
                        st.markdown(f"**📖 Story:** {row['story']}")

                    # Display image if it exists and is valid
                    img_path = row.get("image_path")
                    if img_path and os.path.exists(img_path):
                        try:
                            st.image(img_path, caption=f"{row['dish_name']} image")
                        except Exception as e:
                            st.warning(f"⚠️ Couldn't display image: {e}")

                    # Show comments
                    comments = get_comments(row["id"])
                    st.markdown("### 💬 Comments")
                    if comments:
                        for commenter_name, comment_text, timestamp in comments:
                            ts_display = timestamp.split("T")[0] if timestamp else ""
                            st.markdown(f"- **{commenter_name}** ({ts_display}): {comment_text}")
                    else:
                        st.info("No comments yet. Be the first to comment!")

                    # Show comment form
                    comment_form(row["id"])

        else:
            st.warning("No recipes matched your search or filters.")
    else:
        st.info("No recipes submitted yet. Be the first to share a taste of your tradition! 🌍")
