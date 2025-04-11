import pandas as pd
import sqlite3
from datetime import datetime

df = pd.read_json("data/data.json")

df["_source"] = "https://lista.mercadolivre.com.br/notebook"

df["_datetime"] = datetime.now()

df = df.dropna()

df["old_money"] = df["old_money"].astype(str).str.replace(".", "", regex=False)
df["new_money"] = df["new_money"].astype(str).str.replace(".", "", regex=False)
df["reviews_amount"] = df["reviews_amount"].astype(
    str).str.replace(r"[\(\)]", "", regex=True)

df["old_money"] = df["old_money"].astype(float)
df["new_money"] = df["new_money"].astype(float)
df["reviews_rating_number"] = df["reviews_rating_number"].astype(float)
df["reviews_amount"] = df["reviews_amount"].astype(int)

df = df[
    (df["old_money"] >= 1000) & (df["old_money"] <= 10000) &
    (df["new_money"] >= 1000) & (df["new_money"] <= 10000)
]

conn = sqlite3.connect("data/mercadolivre.db")

df.to_sql("notebook", conn, if_exists='replace', index=False)

conn.close()

print(df.info())