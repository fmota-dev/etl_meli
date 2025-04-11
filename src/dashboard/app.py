import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

# Configuração da página
st.set_page_config(page_title="Pesquisa de Notebooks", layout="wide")

# Estilo personalizado para o selectbox
st.markdown("""
    <style>
    .stSelectbox > div > div {
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# Conectar ao banco e carregar os dados
conn = sqlite3.connect('data/mercadolivre.db')
df = pd.read_sql_query("SELECT * FROM notebook", conn)
conn.close()

# Renomear colunas para português
df = df.rename(columns={
    "brand": "Marca",
    "name": "Modelo",
    "seller": "Vendedor",
    "reviews_rating_number": "Nota de Avaliação",
    "reviews_amount": "Qtd. de Avaliações",
    "old_money": "Preço Antigo (R$)",
    "new_money": "Preço Atual (R$)",
    "_source": "Origem",
    "_datetime": "Data de Coleta"
})

# Limpeza de dados
df["Marca"] = df["Marca"].str.strip().str.title()
df = df.dropna(subset=["Marca", "Preço Atual (R$)", "Nota de Avaliação"])

# Sidebar - filtros
st.sidebar.header("🔍 Filtros")
marcas = sorted(df['Marca'].unique())
marca_selecionada = st.sidebar.selectbox("Marca", options=["Todas"] + marcas)

preco_min, preco_max = int(df['Preço Atual (R$)'].min()), int(
    df['Preço Atual (R$)'].max())
faixa_preco = st.sidebar.slider(
    "Faixa de Preço",
    min_value=preco_min,
    max_value=preco_max,
    value=(preco_min, preco_max),
    step=100,
    format="R$ %d"
)

# Aplicar filtros
df_filtrado = df.copy()
if marca_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Marca'] == marca_selecionada]

df_filtrado = df_filtrado[
    (df_filtrado['Preço Atual (R$)'] >= faixa_preco[0]) &
    (df_filtrado['Preço Atual (R$)'] <= faixa_preco[1])
]

# Título principal
st.title("📊 Pesquisa de Mercado - Notebooks no Mercado Livre")

# KPIs
st.subheader("💡 Indicadores Principais")
col1, col2, col3 = st.columns(3)
col1.metric("🖥️ Total de Notebooks", df_filtrado.shape[0])
col2.metric("🏷️ Marcas Únicas", df_filtrado['Marca'].nunique())
col3.metric("💰 Preço Médio",
            f"R$ {df_filtrado['Preço Atual (R$)'].mean():,.2f}".replace('.', ','))

# Marcas mais encontradas
st.subheader("🏆 Marcas mais encontradas")
top_brands = df_filtrado['Marca'].value_counts().reset_index()
top_brands.columns = ['Marca', 'Qtde']
col1, col2 = st.columns([4, 2])
col1.bar_chart(top_brands.set_index('Marca')['Qtde'])
col2.write(top_brands)

# Preço médio por marca
st.subheader("💵 Preço médio por marca")
media_preco = df_filtrado.groupby('Marca')['Preço Atual (R$)'].mean(
).sort_values(ascending=False).reset_index()
media_preco['Preço Médio'] = media_preco['Preço Atual (R$)'].apply(
    lambda x: f"R$ {x:,.2f}".replace('.', ','))
col1, col2 = st.columns([4, 2])
col1.bar_chart(media_preco.set_index('Marca')['Preço Atual (R$)'])
col2.write(media_preco[['Marca', 'Preço Médio']])

# Satisfação média por marca
st.subheader("⭐ Satisfação média por marca")
media_satisfacao = df_filtrado.groupby(
    'Marca')['Nota de Avaliação'].mean().sort_values(ascending=False).reset_index()
media_satisfacao['Nota Média'] = media_satisfacao['Nota de Avaliação'].round(2)
col1, col2 = st.columns([4, 2])
col1.bar_chart(media_satisfacao.set_index('Marca')['Nota de Avaliação'])
col2.write(media_satisfacao[['Marca', 'Nota Média']])

# Distribuição dos preços
st.subheader("📉 Distribuição dos preços")
hist_chart = alt.Chart(df_filtrado).mark_bar().encode(
    alt.X("Preço Atual (R$)", bin=alt.Bin(maxbins=30), title="Preço"),
    alt.Y('count()', title='Frequência')
).properties(width=700, height=400)
st.altair_chart(hist_chart, use_container_width=True)

# Correlação entre preço e avaliação
st.subheader("📈 Correlação entre preço e avaliação")
scatter = alt.Chart(df_filtrado).mark_circle(size=60).encode(
    x=alt.X('Preço Atual (R$)', title="Preço Atual (R$)"),
    y=alt.Y('Nota de Avaliação', title="Nota"),
    tooltip=['Marca', 'Modelo', 'Preço Atual (R$)', 'Nota de Avaliação']
).interactive()
st.altair_chart(scatter, use_container_width=True)

# Melhor custo-benefício
st.subheader("🥇 Melhor custo-benefício (Revisado)")
df_valid = df_filtrado[(df_filtrado['Preço Atual (R$)'] > 0) & (
    df_filtrado['Nota de Avaliação'] > 0) & (df_filtrado['Qtd. de Avaliações'] > 0)]

# Fórmula revisada para considerar quantidade de avaliações
df_valid['Score'] = (df_valid['Nota de Avaliação'] *
                     df_valid['Qtd. de Avaliações']) / df_valid['Preço Atual (R$)']

# Produto com o maior custo-benefício
melhor = df_valid.sort_values(by='Score', ascending=False).iloc[0]

st.success(f"🔝 {melhor['Marca']} - {melhor['Modelo']}")
st.write(f"💸 Preço: R$ {melhor['Preço Atual (R$)']:.2f}".replace('.', ','))
st.write(f"⭐ Avaliação: {melhor['Nota de Avaliação']}")
st.write(f"📝 Quantidade de Avaliações: {melhor['Qtd. de Avaliações']}")
