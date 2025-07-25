import streamlit as st

def display_stats(df):
    st.subheader("📊 Community Stats")
    st.markdown(f"- **Total Recipes:** {len(df)}")
    st.markdown(f"- **Languages Represented:** {df['Language'].nunique()}")
    st.markdown(f"- **Contributors:** {df['Name'].nunique() if 'Name' in df else 'N/A'}")
    st.markdown("----")

def show_recipes(df):
    st.header("📚 Explore Community Recipes")

    if not df.empty:
        col1, col2 = st.columns(2)
        with col1:
            search_query = st.text_input("🔍 Search recipes by dish name, language, or ingredient").strip().lower()
        with col2:
            sort_option = st.selectbox("📁 Sort recipes by", ["Most Recent", "Alphabetical"])

        languages = sorted(df["Language"].dropna().unique())
        lang_filter = st.selectbox("🌐 Filter by Language", ["All"] + languages)

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
