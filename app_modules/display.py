import streamlit as st
import os
import pandas as pd
from app_modules.utils import get_comments, get_recipe_of_the_day

def display_stats(df):
    st.subheader("📊 Community Recipe Stats")

    total = len(df)
    languages = df["language"].nunique() if "language" in df.columns else 0
    contributors = df["name"].nunique() if "name" in df.columns else 0

    st.markdown(f"- 🧾 **Total Recipes:** {total}")
    st.markdown(f"- 🗣️ **Languages Represented:** {languages}")
    st.markdown(f"- 👥 **Contributors:** {contributors}")
    st.markdown("----")

def show_recipes(df):
    st.header("🍽️ Explore Regional Recipes")

    # Show Recipe of the Day
    recipe_of_the_day = get_recipe_of_the_day()
    if recipe_of_the_day:
        with st.container():
            st.subheader("🌟 Recipe of the Day")
            st.markdown(f"**🍛 Dish Name:** {recipe_of_the_day['dish_name']}")
            st.markdown(f"**😋 Taste Description:** {recipe_of_the_day['taste_description']}")
            st.markdown("---")

    if not df.empty:
        # Search and sort filters
        st.markdown("### 🔍 Find Recipes")
        col1, col2 = st.columns([2, 1])
        with col1:
            search_query = st.text_input("Search by dish name or ingredient").strip().lower()
        with col2:
            sort_option = st.selectbox("Sort by", ["Most Recent", "Alphabetical"])

        # Filter recipes
        df_filtered = df.copy()
        if search_query:
            df_filtered = df_filtered[df_filtered.apply(
                lambda row: search_query in str(row.get("dish_name", "")).lower()
                            or search_query in str(row.get("ingredients", "")).lower(),
                axis=1
            )]

        # Sort
        if sort_option == "Most Recent":
            df_filtered = df_filtered.sort_values(by="timestamp", ascending=False)
        else:
            df_filtered = df_filtered.sort_values(by="dish_name")

        # Import comment form
        from app_modules.forms import comment_form

        if not df_filtered.empty:
            for _, row in df_filtered.iterrows():
                with st.expander(f"🍲 {row['dish_name']}", expanded=False):
                    col_main, col_img = st.columns([3, 1])

                    with col_main:
                        st.markdown(f"**👤 Submitted by:** {row.get('name', 'Anonymous')}")
                        st.markdown(f"**📂 Category:** {row.get('category', 'N/A')}")
                        st.markdown(f"**🌍 Country:** {row.get('country', 'N/A')}")
                        st.markdown("**🧂 Ingredients:**")
                        st.markdown(f"{row.get('ingredients', '')}")
                        st.markdown("**👩‍🍳 Instructions:**")
                        st.markdown(f"{row.get('instructions', '')}")
                        if row.get("story"):
                            st.markdown("**📖 Story:**")
                            st.markdown(f"{row.get('story')}")

                    with col_img:
                        img_path = row.get("image_path")
                        if img_path and os.path.exists(img_path):
                            try:
                                st.image(img_path, caption="Dish Image", use_column_width=True)
                            except Exception as e:
                                st.warning(f"⚠️ Couldn't load image: {e}")
                        else:
                            st.caption("📷 No image available")

                    # Comments Section
                    st.markdown("### 💬 Comments")
                    comments = get_comments(row["id"])
                    if comments:
                        ratings_only = [r for _, _, r, _ in comments if not pd.isna(r)]
                        if ratings_only:
                            avg_rating = sum(ratings_only) / len(ratings_only)
                            stars_avg = "⭐" * int(round(avg_rating))
                            st.markdown(f"**Average Rating:** {avg_rating:.1f} {stars_avg}")

                        for commenter_name, comment_text, rating, timestamp in comments:
                            ts_display = timestamp.split("T")[0] if timestamp else ""
                            stars = "⭐" * int(rating) if not pd.isna(rating) else ""
                            st.markdown(f"""
                                <div style='margin-bottom:10px; padding:8px; background-color:#f9f9f9; border-left: 4px solid #ddd;'>
                                    <strong>{commenter_name}</strong> ({ts_display}) {stars}<br>
                                    {comment_text}
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No comments yet. Be the first to share your thoughts!")

                    # Comment form
                    comment_form(row["id"])
        else:
            st.warning("No recipes matched your search or filters.")
    else:
        st.info("No recipes submitted yet. Be the first to share a taste of your tradition! 🌍")
