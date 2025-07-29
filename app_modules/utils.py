import os
import datetime
import sqlite3
import pandas as pd
from geopy.geocoders import Nominatim

DB_FILE = "data/recipes.db"
IMAGE_DIR = "data/images"

def init_storage():
    os.makedirs("data", exist_ok=True)
    os.makedirs(IMAGE_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Recipes table
    c.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            language TEXT,
            dish_name TEXT,
            category TEXT,
            country TEXT,
            ingredients TEXT,
            instructions TEXT,
            story TEXT,
            image_path TEXT,
            timestamp TEXT,
            latitude REAL,
            longitude REAL
        )
    """)
    # Comments table
    c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            commenter_name TEXT,
            comment_text TEXT,
            timestamp TEXT,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )
    """)
    # Recipe of the Day table
    c.execute("""
        CREATE TABLE IF NOT EXISTS recipe_of_the_day (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            recipe_id INTEGER UNIQUE,
            taste_description TEXT,
            date TEXT UNIQUE,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )
    """)
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM recipes", conn)
    conn.close()
    return df

def save_data(df):
    pass  # No direct save needed

def is_duplicate(df, name, dish):
    if not name or not dish:
        return False
    return not df[
        (df["dish_name"].str.lower() == dish.lower()) &
        (df["name"].str.lower() == name.lower())
    ].empty

def add_entry(df, entry):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    lat, lon = get_coordinates(entry.get("country", ""))
    c.execute("""
        INSERT INTO recipes (name, language, dish_name, category, country,
            ingredients, instructions, story, image_path, timestamp, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry.get("name"),
        entry.get("language"),
        entry.get("dish_name"),
        entry.get("category"),
        entry.get("country"),
        entry.get("ingredients"),
        entry.get("instructions"),
        entry.get("story"),
        entry.get("image_path"),
        entry.get("timestamp"),
        lat,
        lon
    ))

    conn.commit()
    conn.close()

    return load_data()

def get_timestamp():
    return datetime.datetime.now().isoformat()

def get_coordinates(location_name):
    if not location_name or not isinstance(location_name, str):
        return (None, None)
    try:
        geolocator = Nominatim(user_agent="roots_and_recipes")
        location = geolocator.geocode(location_name)
        if location:
            return (location.latitude, location.longitude)
    except Exception:
        pass
    return (None, None)

def save_image(image_file, dish_name):
    os.makedirs(IMAGE_DIR, exist_ok=True)
    safe_name = dish_name.lower().replace(" ", "_") if dish_name else "image"
    ext = image_file.name.split(".")[-1]
    timestamp = int(datetime.datetime.now().timestamp())
    filename = f"{safe_name}_{timestamp}.{ext}"
    filepath = os.path.join(IMAGE_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(image_file.getbuffer())
    return filepath

# Comment functions

def add_comment(recipe_id, commenter_name, comment_text):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = get_timestamp()
    c.execute("""
        INSERT INTO comments (recipe_id, commenter_name, comment_text, timestamp)
        VALUES (?, ?, ?, ?)
    """, (recipe_id, commenter_name, comment_text, timestamp))
    conn.commit()
    conn.close()

def get_comments(recipe_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT commenter_name, comment_text, timestamp FROM comments
        WHERE recipe_id = ?
        ORDER BY timestamp DESC
    """, (recipe_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# Recipe of the Day functions

def set_recipe_of_the_day(recipe_id, taste_description):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.datetime.now().date().isoformat()

    c.execute("""
        INSERT INTO recipe_of_the_day (id, recipe_id, taste_description, date)
        VALUES (1, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            recipe_id=excluded.recipe_id,
            taste_description=excluded.taste_description,
            date=excluded.date
    """, (recipe_id, taste_description, today))

    conn.commit()
    conn.close()

def get_recipe_of_the_day():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.datetime.now().date().isoformat()

    c.execute("""
        SELECT r.id, r.dish_name, r.language, r.category, r.country, r.ingredients,
               r.instructions, r.story, r.image_path, r.timestamp,
               rod.taste_description
        FROM recipe_of_the_day rod
        JOIN recipes r ON rod.recipe_id = r.id
        WHERE rod.date = ?
        LIMIT 1
    """, (today,))

    row = c.fetchone()
    conn.close()

    if row:
        keys = ["id", "dish_name", "language", "category", "country", "ingredients",
                "instructions", "story", "image_path", "timestamp", "taste_description"]
        return dict(zip(keys, row))
    else:
        return None
