import streamlit as st
import numpy as np

st.title("Programação Linear")

opcoes = ["Simplex", "Big M", "Método gráfico"]
barraLateral = st.sidebar.selectbox("Método", opcoes)

####### Simplex ########

if barraLateral == "Simplex":
    num_variaveis = st.number_input("Quantas variáveis?", min_value=1)

    num_variaveis = int(num_variaveis)  # converte de float para inteiro

    maxOrMin = st.selectbox("Tipo de otimização", ["Maximizar", "Minimizar"])

    ###### Função Objetivo #######

    st.subheader("Função Objetivo")
    colunas_fo = st.columns(num_variaveis + 1)  # +1 para a constante
    for i in range(num_variaveis):
        colunas_fo[i].number_input('x' + str(i + 1), key='fo_' + str(i))

    colunas_fo[num_variaveis].number_input('Constante', key='fo_constante')


    ##### Restricoes #####

    st.subheader("Restrições")
    num_restricoes = st.number_input("Quantas restrições?", min_value=1)
    num_restricoes = int(num_restricoes)

    # Cabeçalho das colunas
    cabecalho_restricoes = st.columns(num_variaveis + 2)
    for j in range(num_variaveis):
        cabecalho_restricoes[j].markdown(f'**x{j+1}**')
    cabecalho_restricoes[num_variaveis].markdown('**Tipo**')
    cabecalho_restricoes[num_variaveis + 1].markdown('**b**')

    # Uma linha por restrição
    for i in range(num_restricoes):
        colunas_restricoes = st.columns(num_variaveis + 2)

        for j in range(num_variaveis):
            colunas_restricoes[j].number_input('', key='restricao_' + str(i) + '_' + str(j), label_visibility='collapsed')

        colunas_restricoes[num_variaveis].selectbox('', ['<=', '>=', '='], key='tipo_' + str(i), label_visibility='collapsed')

        colunas_restricoes[num_variaveis + 1].number_input('', key='b_' + str(i), label_visibility='collapsed')
    
    resolver = st.button("Resolver")


    ###### Armazenando os valores de FO dentro de uma lista c ######

    c = []

    for i in range(num_variaveis):
        c.append(st.session_state['fo_' + str(i)])

    constante = st.session_state['fo_constante']

    ###### Armazenando coeficientes das restrições ###
    
    A = []

    for i in range(num_restricoes):
        linha = []
        for j in range(num_variaveis):
            linha.append(st.session_state['restricao_' + str(i) + '_' + str(j)])
            A.append(linha)
        
        tipos = []
        b = []

        for i in range(num_restricoes):
            tipos.append(st.session_state['tipo_' + str(i)])
            b.append(st.session_state['b_' + str(i)])

    if resolver:
        