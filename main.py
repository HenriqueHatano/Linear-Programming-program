import streamlit as st
import numpy as np
import pandas as pd
from utils.entrada import extrair_dados_formulario, validar_dados
from metodos.simplex import resolver_simplex
from metodos.grafico import resolver_grafico


st.title("Programação Linear")

opcoes = ["Simplex", "Método gráfico"]
barraLateral = st.sidebar.selectbox("Método", opcoes)

""" Simplex """

if barraLateral == "Simplex":
    num_variaveis = st.number_input("Quantas variáveis?", min_value=1)

    num_variaveis = int(num_variaveis)  # converte de float para inteiro

    maxOrMin = st.selectbox("Tipo de otimização", ["Maximizar", "Minimizar"])

    """ Função Objetivo """

    st.subheader("Função Objetivo")
    colunas_fo = st.columns(num_variaveis + 1)  # +1 para a constante
    for i in range(num_variaveis):
        colunas_fo[i].number_input('x' + str(i + 1), key='fo_' + str(i))

    colunas_fo[num_variaveis].number_input('Constante', key='fo_constante')


    """ Restricoes """

    st.subheader("Restrições")
    num_restricoes = st.number_input("Quantas restrições?", min_value=1)
    num_restricoes = int(num_restricoes)

    """ Cabeçalho das colunas"""

    cabecalho_restricoes = st.columns(num_variaveis + 2)
    for j in range(num_variaveis):
        cabecalho_restricoes[j].markdown(f'**x{j+1}**')
    cabecalho_restricoes[num_variaveis].markdown('**Tipo**')
    cabecalho_restricoes[num_variaveis + 1].markdown('**b**')

    """ Número de restrições e variáveis de acordo com o que o usuário selecionar """

    for i in range(num_restricoes):
        colunas_restricoes = st.columns(num_variaveis + 2)

        for j in range(num_variaveis):
            colunas_restricoes[j].number_input('', key='restricao_' + str(i) + '_' + str(j), label_visibility='collapsed')

        colunas_restricoes[num_variaveis].selectbox('', ['<=', '>=', '='], key='tipo_' + str(i), label_visibility='collapsed')

        colunas_restricoes[num_variaveis + 1].number_input('', key='b_' + str(i), label_visibility='collapsed')
    
    resolver = st.button("Resolver")

    if resolver:

        """ Extrai os dados de forma limpa """

        c, constante, A, tipos, b = extrair_dados_formulario(num_variaveis, num_restricoes, st.session_state)

        # 2. Valida os dados antes de rodar os cálculos
        valido, mensagem = validar_dados(barraLateral, num_variaveis, c, A, tipos, b)

        if not valido:
            st.error(mensagem)
        else:
            """ Chamando função Simplex """

            valores_variaveis, valor_z, historico_tabelas, mensagem_resultado = resolver_simplex(
                c, constante, A, tipos, b, maxOrMin
            )

            if valores_variaveis is None:
                st.error(mensagem_resultado)
            else:
                st.success(mensagem_resultado)

                # Exibe o valor de Z
                st.subheader("Resultado")
                st.metric("Valor Ótimo de Z", f"{valor_z:.2f}")

                # Exibe o valor de cada variável (x1, x2, ...)
                st.write("**Valores das Variáveis:**")
                colunas_resultado = st.columns(num_variaveis)
                for j, (nome_var, valor_var) in enumerate(valores_variaveis.items()):
                    colunas_resultado[j].metric(label=nome_var, value=f"{valor_var:.2f}")

                # Exibe o histórico de tabelas (iterações)
                with st.expander("Ver passo a passo das iterações (Tableaux)"):
                    nomes_colunas = [f"x{i+1}" for i in range(num_variaveis)] + \
                                   [f"xf{i+1}" for i in range(num_restricoes)] + \
                                   ["Lado Direito (b)"]

                    for passo, tabela_passo in enumerate(historico_tabelas):
                        st.markdown(f"**Iteração {passo}:**")
                        df_tabela = pd.DataFrame(tabela_passo, columns=nomes_colunas)
                        st.dataframe(df_tabela)


    """ Método Gráfico """

elif barraLateral == "Método gráfico":
    st.info("O Método Gráfico é utilizado para problemas com exatamente 2 variáveis de decisão (x1 e x2).")

    num_variaveis = 2
    maxOrMin = st.selectbox("Tipo de otimização", ["Maximizar", "Minimizar"])

    """ Função Objetivo """

    st.subheader("Função Objetivo")
    colunas_fo = st.columns(3)
    colunas_fo[0].number_input("x1", key="fo_0")
    colunas_fo[1].number_input("x2", key="fo_1")
    colunas_fo[2].number_input("Constante", key="fo_constante")

    """ Restrições """
    
    st.subheader("Restrições")
    num_restricoes = st.number_input("Quantas restrições?", min_value=1)
    num_restricoes = int(num_restricoes)

    cabecalho_restricoes = st.columns(4)
    cabecalho_restricoes[0].markdown("**x1**")
    cabecalho_restricoes[1].markdown("**x2**")
    cabecalho_restricoes[2].markdown("**Tipo**")
    cabecalho_restricoes[3].markdown("**b**")

    for i in range(num_restricoes):
        colunas_restricoes = st.columns(4)
        colunas_restricoes[0].number_input("", key=f"restricao_{i}_0", label_visibility="collapsed")
        colunas_restricoes[1].number_input("", key=f"restricao_{i}_1", label_visibility="collapsed")
        colunas_restricoes[2].selectbox("", ["<=", ">=", "="], key=f"tipo_{i}", label_visibility="collapsed")
        colunas_restricoes[3].number_input("", key=f"b_{i}", label_visibility="collapsed")

    resolver = st.button("Resolver")

    if resolver:
        c, constante, A, tipos, b = extrair_dados_formulario(num_variaveis, num_restricoes, st.session_state)
        valido, mensagem = validar_dados(barraLateral, num_variaveis, c, A, tipos, b)

        if not valido:
            st.error(mensagem)
        else:
            ponto_otimo, valor_z, figura = resolver_grafico(c, constante, A, tipos, b, maxOrMin)

            if ponto_otimo is None:
                st.error("Problema Inviável: não foi encontrada nenhuma região viável.")
            else:
                st.success("Solução Ótima Encontrada!")

                # Exibe Z e as coordenadas (x1, x2)
                st.subheader("Resultado")
                col1, col2, col3 = st.columns(3)
                col1.metric("Valor Ótimo de Z", f"{valor_z:.2f}")
                col2.metric("x1 Ótimo", f"{ponto_otimo[0]:.2f}")
                col3.metric("x2 Ótimo", f"{ponto_otimo[1]:.2f}")

                # Exibe o gráfico gerado
                st.subheader("Gráfico")
                st.pyplot(figura)