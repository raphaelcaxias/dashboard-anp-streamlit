import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard ANP",
    page_icon="⛽",
    layout="wide"
)

st.title("Dashboard de Combustiveis - ANP")

st.markdown("""
## Contexto do Projeto

Este dashboard foi desenvolvido para analisar dados publicos da ANP sobre movimentacao de combustiveis em terminais aquaviarios brasileiros.

O objetivo do projeto e transformar dados brutos em informacoes visuais para apoiar analises estrategicas sobre distribuicao e movimentacao de combustiveis no Brasil.

### Competencias demonstradas

- Python
- Pandas
- Streamlit
- Plotly
- Data Visualization
- Data Storytelling
""")

@st.cache_data
def carregar_dados():

    url = "https://docs.google.com/spreadsheets/d/1NfAnK7mtfJhasc3vVPhMlPvfuF_OT6OrshFwRBZcNyA/export?format=csv"

    try:
        df = pd.read_csv(url, encoding="latin1")
    except:
        df = pd.read_csv(url, encoding="cp1252")

    df.columns = df.columns.str.strip().str.lower()

    return df

try:

    df = carregar_dados()

    st.sidebar.subheader("Colunas Encontradas")
    st.sidebar.write(df.columns.tolist())

    coluna_ano = None
    coluna_uf = None
    coluna_volume = None

    for col in df.columns:

        nome = col.lower()

        if "ano" in nome:
            coluna_ano = col

        if nome == "uf" or "estado" in nome:
            coluna_uf = col

        if "volume" in nome:
            coluna_volume = col

    if coluna_ano is None:
        st.error("Coluna de ANO nao encontrada")
        st.stop()

    if coluna_uf is None:
        st.error("Coluna UF nao encontrada")
        st.stop()

    if coluna_volume is None:
        st.error("Coluna de VOLUME nao encontrada")
        st.stop()

    df[coluna_volume] = (
        df[coluna_volume]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    df[coluna_volume] = pd.to_numeric(
        df[coluna_volume],
        errors="coerce"
    )

    df = df.dropna(subset=[coluna_volume])

    st.sidebar.header("Filtros")

    anos = sorted(df[coluna_ano].dropna().unique())

    anos_selecionados = st.sidebar.multiselect(
        "Selecione os anos",
        anos,
        default=anos
    )

    df_filtrado = df[df[coluna_ano].isin(anos_selecionados)]

    total_volume = df_filtrado[coluna_volume].sum()
    total_estados = df_filtrado[coluna_uf].nunique()
    total_registros = len(df_filtrado)

    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(
        "Volume Total",
        f"{total_volume:,.0f}"
    )

    kpi2.metric(
        "Estados",
        total_estados
    )

    kpi3.metric(
        "Registros",
        f"{total_registros:,}"
    )

    st.markdown("---")

    st.subheader("Principais Insights")

    st.markdown("""
- O volume movimentado apresenta forte concentracao regional.
- Alguns estados lideram grande parte da movimentacao de combustiveis.
- O painel permite explorar tendencias historicas de forma interativa.
- Os dados ajudam a visualizar polos logisticos relevantes do setor energetico.
""")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Volume por Ano")

        df_ano = (
            df_filtrado
            .groupby(coluna_ano)[coluna_volume]
            .sum()
            .reset_index()
        )

        fig_ano = px.bar(
            df_ano,
            x=coluna_ano,
            y=coluna_volume,
            text_auto=True
        )

        st.plotly_chart(
            fig_ano,
            use_container_width=True
        )

    with col2:

        st.subheader("Top 10 Estados")

        df_uf = (
            df_filtrado
            .groupby(coluna_uf)[coluna_volume]
            .sum()
            .reset_index()
            .sort_values(
                by=coluna_volume,
                ascending=False
            )
            .head(10)
        )

        fig_uf = px.bar(
            df_uf,
            x=coluna_volume,
            y=coluna_uf,
            orientation="h",
            text_auto=True
        )

        st.plotly_chart(
            fig_uf,
            use_container_width=True
        )

    st.markdown("---")

    st.subheader("Dados Detalhados")

    st.dataframe(
        df_filtrado.head(100),
        use_container_width=True
    )

except Exception as e:

    st.error(f"Erro ao carregar os dados: {e}")
