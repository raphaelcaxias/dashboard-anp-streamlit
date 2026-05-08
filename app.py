except Exception as e:

    st.error(f"Erro ao carregar os dados: {e}")

    st.info("""
Possiveis causas:

- Problema de encoding
- Nome das colunas diferente
- Planilha privada
- Erro de leitura do Google Sheets
""")
