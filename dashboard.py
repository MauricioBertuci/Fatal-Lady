# dashboard.py
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "app"))

from app.database import DATABASE_URL  # reaproveita a URL já usada no app

st.set_page_config(page_title="Dashboard Fatal Lady", layout="wide")
st.title("📊 Dashboard Administrativo - Fatal Lady")

# criar engine SQLAlchemy
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


# executar query e retornar DataFrame
def query_df(sql: str, params: dict = None) -> pd.DataFrame:
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(sql=text(sql), con=conn, params=params)
        return df
    except Exception as e:
        st.error(f"Erro ao executar query: {e}")
        return pd.DataFrame()


# CONSULTAS BASE 

# 1 Vendas 
sql_vendas = "SELECT id, data, valortotal FROM pedidos WHERE data IS NOT NULL"
df_vendas = query_df(sql_vendas)
if not df_vendas.empty:
    df_vendas["data"] = pd.to_datetime(df_vendas["data"])

# 2 Top 5 produtos mais vendidos
sql_top_produtos = """
SELECT p.nome, SUM(i.quantidade) AS total_vendido
FROM itens_pedido i
JOIN produtos p ON p.id_produto = i.produto_id
GROUP BY p.nome
ORDER BY total_vendido DESC
LIMIT 5
"""
df_produtos = query_df(sql_top_produtos)

# 3 Vendas por categoria
sql_categoria = """
SELECT c.nome AS categoria, SUM(i.quantidade * i.preco_unitario) AS total_categoria
FROM itens_pedido i
JOIN produtos p ON p.id_produto = i.produto_id
JOIN categoria c ON c.id = p.id_categoria
GROUP BY c.nome
ORDER BY total_categoria DESC
"""
df_categoria = query_df(sql_categoria)

# 4 Vendas por fabricante
sql_fabricante = """
SELECT f.nome AS fabricante, SUM(i.quantidade * i.preco_unitario) AS total_fabricante
FROM itens_pedido i
JOIN produtos p ON p.id_produto = i.produto_id
JOIN fabricantes f ON f.id = p.id_fabricante
GROUP BY f.nome
ORDER BY total_fabricante DESC
"""
df_fabricante = query_df(sql_fabricante)

# 5 Métodos de pagamento
sql_pagamento = """
SELECT metodo_pagamento, COUNT(*) AS total
FROM pagamentos
GROUP BY metodo_pagamento
ORDER BY total DESC
"""
df_pagamento = query_df(sql_pagamento)

# 6 Avaliações médias por produto
sql_avaliacoes = """
SELECT p.nome, AVG(a.nota) AS media_nota, COUNT(a.*) as qtd
FROM avaliacoes a
JOIN produtos p ON p.id_produto = a.id_produto
GROUP BY p.nome
ORDER BY media_nota DESC
"""
df_avaliacoes = query_df(sql_avaliacoes)

# 7 Total de produtos (simples KPI)
sql_total_produtos = "SELECT COUNT(*) as total FROM produtos"
df_total_produtos = query_df(sql_total_produtos)
total_products = int(df_total_produtos["total"].iloc[0]) if not df_total_produtos.empty else 0




# -------------------------
# filtros

st.sidebar.header("Filtros")

# Data range (vendas)
if not df_vendas.empty:
    min_date = df_vendas["data"].min().date()
    max_date = df_vendas["data"].max().date()
    date_range = st.sidebar.date_input("Período (vendas)", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
        df_vendas = df_vendas[(df_vendas["data"].dt.date >= start_date) & (df_vendas["data"].dt.date <= end_date)]
else:
    st.sidebar.info("Sem dados de vendas para filtros de data.")

# Categoria filter (if available)
categorias_opts = df_categoria["categoria"].tolist() if not df_categoria.empty else []
categoria_sel = st.sidebar.multiselect("Categoria", options=categorias_opts, default=categorias_opts)


# -------------------------
# KPI Cards (top row)
col1, col2, col3, col4 = st.columns(4)
# total revenue
total_revenue = float(df_vendas["valortotal"].sum()) if not df_vendas.empty else 0.0
total_orders = int(df_vendas.shape[0]) if not df_vendas.empty else 0
avg_rating = float(df_avaliacoes["media_nota"].mean()) if not df_avaliacoes.empty else 0.0

col1.metric("Faturamento (R$)", f"R$ {total_revenue:,.2f}")
col2.metric("Pedidos", f"{total_orders}")
col3.metric("Produtos cadastrados", f"{total_products}")
col4.metric("Avaliação média", f"{avg_rating:.2f}")

# -------------------------
# Abas com gráficos
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Faturamento",
    "🛒 Produtos & Categorias",
    "🏭 Fabricantes & Pagamentos",
    "📋 Tabela / Detalhes"
])


# ----- Aba 1: Faturamento mensal -----
with tab1:
    st.subheader("Faturamento Mensal (R$)")
    if df_vendas.empty:
        st.info("Nenhuma venda disponível.")
    else:
        vendas_mensais = (
            df_vendas.groupby(df_vendas["data"].dt.to_period("M"))["valortotal"]
            .sum()
            .reset_index()
        )
        vendas_mensais["data"] = vendas_mensais["data"].astype(str)
        fig = px.line(vendas_mensais, x="data", y="valortotal", markers=True, title="Faturamento por Mês")
        fig.update_layout(xaxis_title="Mês", yaxis_title="Valor (R$)")
        st.plotly_chart(fig, use_container_width=True)



# ----- Aba 2: Produtos e categorias -----
with tab2:
    st.subheader("Top Produtos e Distribuição por Categoria")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("**Top 5 Produtos Mais Vendidos**")
        if df_produtos.empty:
            st.info("Sem dados de vendas por produto.")
        else:
            fig_p = px.bar(df_produtos, x="total_vendido", y="nome", orientation="h", text="total_vendido", title="Top 5 Produtos")
            fig_p.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_p, use_container_width=True)
    with c2:
        st.markdown("**Vendas por Categoria**")
        if df_categoria.empty:
            st.info("Sem dados por categoria.")
        else:
            # se usuario filtrou categorias, aplicar
            if categoria_sel:
                df_cat_plot = df_categoria[df_categoria["categoria"].isin(categoria_sel)]
            else:
                df_cat_plot = df_categoria
            fig_cat = px.pie(df_cat_plot, values="total_categoria", names="categoria", title="Distribuição por Categoria", hole=0.4)
            st.plotly_chart(fig_cat, use_container_width=True)



# ----- Aba 3: Fabricantes e Pagamentos -----
with tab3:
    st.subheader("Fabricantes e Métodos de Pagamento")
    c3, c4 = st.columns(2)
    with c3:
        if df_fabricante.empty:
            st.info("Sem dados de fabricante.")
        else:
            fig_fab = px.bar(df_fabricante, x="fabricante", y="total_fabricante", text=df_fabricante["total_fabricante"].apply(lambda x: f"R$ {x:,.2f}"), title="Vendas por Fabricante")
            st.plotly_chart(fig_fab, use_container_width=True)
    with c4:
        if df_pagamento.empty:
            st.info("Sem dados de pagamento.")
        else:
            fig_pag = px.bar(df_pagamento, x="metodo_pagamento", y="total", text="total", title="Métodos de Pagamento")
            st.plotly_chart(fig_pag, use_container_width=True)




# ----- Aba 4: Tabela de dados e avaliações -----
with tab4:
    st.subheader("Avaliações por Produto")
    if df_avaliacoes.empty:
        st.info("Nenhuma avaliação encontrada.")
    else:
        df_avaliacoes = df_avaliacoes.sort_values("media_nota", ascending=False)
        st.dataframe(df_avaliacoes)

    st.markdown("---")
    st.subheader("Pedidos (exemplo: últimas 200)")
    df_pedidos = query_df("SELECT id, data, id_cliente, valortotal FROM pedidos ORDER BY data DESC LIMIT 200")
    if not df_pedidos.empty:
        df_pedidos["data"] = pd.to_datetime(df_pedidos["data"])
        st.dataframe(df_pedidos)
    else:
        st.info("Nenhum pedido para exibir.")
