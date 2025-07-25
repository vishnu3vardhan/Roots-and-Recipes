import pandas as pd
import os
import datetime

DATA_FILE = "data/recipes.csv"
COLUMNS = ["Name", "Language", "Dish Name", "Category", "Ingredients", "Instructions", "Story", "Timestamp"]

def init_storage():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def is_duplicate(df, name, dish):
    if not name:
        return False
    return not df[
        (df["Dish Name"].str.lower() == dish.lower()) &
        (df["Name"].str.lower() == name.lower())
    ].empty

def add_entry(df, entry):
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    save_data(df)
    return df

def get_timestamp():
    return datetime.datetime.now().isoformat()
