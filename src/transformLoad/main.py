import pandas as pd
import sqlite3
from datetime import datetime

# Carregar o JSON extraído
df = pd.read_json("data/data.json")

# Adicionar colunas auxiliares
df["_source"] = "https://lista.mercadolivre.com.br/notebook"
df["_datetime"] = datetime.now()

# Tratar valores 'None' como nulos reais
df.replace("None", pd.NA, inplace=True)

# Redefinir índice do DataFrame
df = df.reset_index(drop=True)

# Substituir preço antigo ausente com o preço atual
df["old_money"] = df["old_money"].fillna(df["new_money"])

# Remover pontos (milhar) dos preços
df["old_money"] = df["old_money"].astype(str).str.replace(".", "", regex=False)
df["new_money"] = df["new_money"].astype(str).str.replace(".", "", regex=False)

# Tratar reviews_amount removendo parênteses e convertendo para número
df["reviews_amount"] = (
    df["reviews_amount"]
    .astype(str)
    .str.replace(r"[\(\)]", "", regex=True)
    .replace("None", pd.NA)
)
df["reviews_amount"] = pd.to_numeric(
    df["reviews_amount"], errors="coerce").fillna(0).astype(int)

# Tratar nota de avaliação (reviews_rating_number)
df["reviews_rating_number"] = pd.to_numeric(
    df["reviews_rating_number"], errors="coerce"
).fillna(0.0).astype(float)

# Converter preços para float
df["old_money"] = pd.to_numeric(df["old_money"], errors="coerce")
df["new_money"] = pd.to_numeric(df["new_money"], errors="coerce")

# Manter apenas registros com marca e preço atual válidos
df = df[df["brand"].notna() & df["new_money"].notna()]

# Filtrar por faixa de preço aceitável
df = df[
    (df["old_money"] >= 1000) & (df["old_money"] <= 10000) &
    (df["new_money"] >= 1000) & (df["new_money"] <= 10000)
]

# Salvar no banco de dados SQLite
conn = sqlite3.connect("data/mercadolivre.db")
df.to_sql("notebook", conn, if_exists="replace", index=False)
conn.close()

# Informações finais
print("Transformação finalizada ✅")
print(df.info())
