import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------

st.set_page_config(
    page_title="Dashboard ANP",
    page_icon="⛽",
    layout="wide"
)

st.title("⛽ Dashboard de Combustíveis - ANP")

st.markdown("""
Dashboard interativo desenvolvido por Raphael Pires usando Python + Streamlit.

Dados públicos da ANP sobre movimentação de combustíveis.
""")

# ---------------------------------------------------
# CARREGAMENTO DOS DADOS
# ---------------------------------------------------

@st.cache_data
def carregar_dados():

    url = "https://docs.google.com/spreadsheets/d/1NfAnK7mtfJhasc3vVPhMlPvfuF_OT6OrshFwRBZcNyA/export?format=csv"

    try:
        df = pd.read_csv(url, encoding="latin1")
    except:
        df = pd.read_csv(url, encoding="cp1252")

    # Padronizar nomes das colunas
    df.columns = df.columns.str.strip().str.lower()

    return df

# ---------------------------------------------------
# EXECUÇÃO PRINCIPAL
# ---------------------------------------------------

try:

    df = carregar_dados()

    # Mostrar colunas encontradas
    st.sidebar.subheader("Colunas Encontradas")
    st.sidebar.write(df.columns.tolist())

    # ---------------------------------------------------
    # IDENTIFICAÇÃO AUTOMÁTICA DAS COLUNAS
    # ---------------------------------------------------

    coluna_ano = None
    coluna_uf = None
    coluna_volume = None

    for col in df.columns:

        nome = col.lower()

        # Procurar coluna de ano
        if "ano" in nome:
            coluna_ano = col

        # Procurar UF
        if nome == "uf" or "estado" in nome:
            coluna_uf = col

        # Procurar volume
        if "volume" in nome:
            coluna_volume = col

    # ---------------------------------------------------
    # VALIDAÇÕES
    # ---------------------------------------------------

    if coluna_ano is None:
        st.error("Nao foi encontrada coluna de ANO")
        st.stop()

    if coluna_uf is None:
        st.error("Nao foi encontrada coluna de UF")
        st.stop()

    if coluna_volume is None:
        st.error("Nao foi encontrada coluna de VOLUME")
        st.stop()

    # ---------------------------------------------------
    # TRATAMENTO DO VOLUME
    # ---------------------------------------------------

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

    # Remover linhas inválidas
    df = df.dropna(subset=[coluna_volume])

    # ---------------------------------------------------
    # FILTROS
    # ---------------------------------------------------

    st.sidebar.header("Filtros")

    anos = sorted(df[coluna_ano].dropna().unique())

    anos_selecionados = st.sidebar.multiselect(
        "Selecione os anos",
        options=anos,
        default=anos
    )

    df_filtrado = df[df[coluna_ano].isin(anos_selecionados)]

    # ---------------------------------------------------
    # KPIs
    # ---------------------------------------------------

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

    # ---------------------------------------------------
    # GRÁFICOS
    # ---------------------------------------------------

    col1, col2 = st.columns(2)

    # ---------------------------------------------------
    # GRÁFICO 1
    # ---------------------------------------------------

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

    # ---------------------------------------------------
    # GRÁFICO 2
    # ---------------------------------------------------

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

    # ---------------------------------------------------
    # TABELA
    # ---------------------------------------------------

    st.markdown("---")

    st.subheader("Dados Detalhados")

    st.dataframe(
        df_filtrado.head(100),
        use_container_width=True
    )

# ---------------------------------------------------
# TRATAMENTO DE ERROS
# ---------------------------------------------------

except Exception as e:

    st.error(f"Erro ao carregar os dados: {e}")

    st.info("""
Possiveis causas:

- Problema de encoding
- Nome das colunas diferente
- Planilha privada
- Erro de leitura do Google Sheets
""")
