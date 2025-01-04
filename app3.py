import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta
import plotly.express as px

# Configurar o layout para usar largura total
st.set_page_config(layout="wide", page_title="Preços de Ações", page_icon="📈")

# Função para carregar dados de ações com cache
@st.cache_data
def carregar_dados(empresas, start="2018-01-01", end="2024-07-01"):
    """
    Carrega os dados das ações selecionadas entre as datas especificadas.
    """
    dados_acao = yf.Tickers(" ".join(empresas))
    cotacoes_acao = dados_acao.history(period='1mo', start=start, end=end)
    return cotacoes_acao["Close"]

# Função para carregar tickers de ações com cache
@st.cache_data
def carregar_tickers_acoes():
    """
    Carrega os códigos das ações do arquivo CSV.
    """
    base_tickers = pd.read_csv("IBOV.csv", sep=";")
    return [ticker + ".SA" for ticker in base_tickers["Código"]]

# Carregar dados iniciais
acoes = carregar_tickers_acoes()
dados = carregar_dados(acoes)

# Interface do Streamlit
st.title("Valor das Ações ao Longo do Tempo")
st.markdown("Visualize a evolução do preço das ações ao longo do tempo com filtros interativos.")

# Configuração da barra lateral
st.sidebar.header("🔍 Filtros")
lista_acoes = st.sidebar.multiselect(
    "Escolha as ações para visualizar:",
    options=acoes,
    default=[]
)

data_inicial = dados.index.min().to_pydatetime()
data_final = dados.index.max().to_pydatetime()
intervalo_datas = st.sidebar.slider(
    "Selecione o intervalo de datas:",
    min_value=data_inicial,
    max_value=data_final,
    value=(data_inicial, data_final),
    step=timedelta(days=7)
)

# Filtrar dados com base nos filtros
dados = dados.loc[intervalo_datas[0]:intervalo_datas[1]]
if lista_acoes:
    dados_filtrados = dados[lista_acoes]

    # Gráfico interativo
    if not dados_filtrados.empty:
        fig = px.line(
            dados_filtrados,
            title="Evolução dos Preços das Ações",
            labels={"value": "Preço", "variable": "Ação"}
        )
        fig.update_layout(
            legend=dict(
                orientation="h", y=-0.2, x=0.5, xanchor="center", yanchor="top"
            ),
            width=1200, height=600
        )
        st.plotly_chart(fig, use_container_width=True)

# Calcular e exibir performance dos ativos
if lista_acoes:
    st.markdown("###  Performance dos Ativos Selecionados")
    texto_performance = ""
    for acao in lista_acoes:
        performance = (dados[acao].iloc[-1] / dados[acao].iloc[0] - 1) * 100
        cor = ":green" if performance > 0 else ":red" if performance < 0 else ""
        texto_performance += f"{acao}: {cor}[{performance:.2f}%]  \n"
    st.markdown(texto_performance)
else:
    st.markdown("###  Performance dos Ativos Selecionados")
    st.write("Nenhuma ação selecionada.")

# Aplicar estilos CSS
st.markdown("""
    <style>
    /* Remover espaços laterais */
    .css-18e3th9 {
        padding: 0rem 1rem;
    }
    /* Título principal */
    .css-10trblm {
        color: #1F77B4;
    }
    /* Sidebar */
    .css-1d391kg {
        background-color: #F8F9FA;
    }
    </style>
""", unsafe_allow_html=True)
