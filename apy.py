import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------

st.set_page_config(
    page_title="Dashboard ANP",
    page_icon="?",
    layout="wide"
)

st.title("? Dashboard de Combustíveis - ANP")
st.markdown(
    """
    Dashboard interativo desenvolvido por **Raphael Pires** usando Python + Streamlit.
    
    Dados públicos da ANP sobre movimentação de combustíveis em terminais aquaviários.
    """
)

# ---------------------------------------------------
# CARREGAMENTO DOS DADOS
# ---------------------------------------------------

@st.cache_data
def carregar_dados():

    url = "https://docs.google.com/spreadsheets/d/1NfAnK7mtfJhasc3vVPhMlPvfuF_OT6OrshFwRBZcNyA/export?format=csv"

    df = pd.read_csv(url)

    # Padronizar nomes das colunas
    df.columns = df.columns.str.strip().str.lower()

    return df

# ---------------------------------------------------
# TENTAR CARREGAR
# ---------------------------------------------------

try:

    df = carregar_dados()

    # DEBUG TEMPORÁRIO
    st.sidebar.subheader("Colunas Encontradas")
    st.sidebar.write(df.columns.tolist())

    # ---------------------------------------------------
    # AJUSTE AUTOMÁTICO DAS COLUNAS
    # ---------------------------------------------------

    # Tenta identificar colunas automaticamente
    coluna_ano = None
    coluna_uf = None
    coluna_volume = None

    for col in df.columns:

        if "ano" in col:
            coluna_ano = col

        if col == "uf" or "estado" in col:
            coluna_uf = col

        if "volume" in col:
            coluna_volume = col

    # ---------------------------------------------------
    # VALIDAR
    # ---------------------------------------------------

    if not coluna_ano:
        st.error("Não encontrei coluna de ANO.")
        st.stop()

    if not coluna_uf:
        st.error("Não encontrei coluna de UF/Estado.")
        st.stop()

    if not coluna_volume:
        st.error("Não encontrei coluna de VOLUME.")
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
    # FILTRO DE ANOS
    # ---------------------------------------------------

    st.sidebar.header("?? Filtros")

    anos = sorted(df[coluna_ano].dropna().unique())

    anos_selecionados = st.sidebar.multiselect(
        "Selecione os anos",
        anos,
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
        f"{total_volume:,.0f} m³"
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

    # -----------------------------------
    # VOLUME POR ANO
    # -----------------------------------

    with col1:

        st.subheader("?? Volume por Ano")

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

    # -----------------------------------
    # TOP 10 ESTADOS
    # -----------------------------------

    with col2:

        st.subheader("??? Top 10 Estados")

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

    st.subheader("?? Dados Detalhados")

    st.dataframe(
        df_filtrado.head(100),
        use_container_width=True
    )

except Exception as e:

    st.error(f"Erro ao carregar os dados: {e}")

    st.info(
        """
        Possíveis causas:
        
        - Planilha não está pública
        - Nome das colunas mudou
        - Problema de formatação
        - Google Sheets demorou responder
        
        Porque dados públicos brasileiros nunca perdem a chance de testar nossa sanidade.
        """
    )