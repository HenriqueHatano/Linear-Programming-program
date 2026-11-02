import numpy as np

def criar_tabela_inicial(coeficientes_objetivo, constante_objetivo, matriz_restricoes, vetor_lado_direito, tipo_otimizacao="Maximizar"):
    """
    Monta o primeiro Tableau (tabela) do Simplex adicionando as variáveis de folga.
    """
    numero_restricoes, numero_variaveis = matriz_restricoes.shape
    
    ### Se for Minimizar Z, transformamos em Maximizar (-Z) invertendo os sinais ###

    coeficientes_ajustados = np.array(coeficientes_objetivo, dtype=float)
    if tipo_otimizacao == "Minimizar":
        coeficientes_ajustados = -coeficientes_ajustados

    ### Cria a matriz identidade para as variáveis de folga (uma folga para cada restrição) ###

    matriz_folgas = np.eye(numero_restricoes)

    ### Transforma o vetor do lado direito em uma coluna vertical ###
    coluna_lado_direito = vetor_lado_direito.reshape(-1, 1)

    # 4. Junta as restrições originais com as folgas e a coluna do lado direito
    # Formato de cada linha: [ coeficientes das variáveis | variáveis de folga | lado direito ]
    linhas_das_restricoes = np.hstack([matriz_restricoes, matriz_folgas, coluna_lado_direito])

    # 5. Monta a última linha da tabela (Linha da Função Objetivo Z)
    # Na convenção do Simplex, os coeficientes de Z entram com sinal negativo
    zeros_das_folgas = np.zeros(numero_restricoes)
    linha_funcao_objetivo = np.hstack([-coeficientes_ajustados, zeros_das_folgas, -constante_objetivo])

    # 6. Empilha as restrições com a linha da função objetivo para formar a tabela completa
    tabela_simplex = np.vstack([linhas_das_restricoes, linha_funcao_objetivo])
    
    return tabela_simplex


def resolver_simplex(coeficientes_objetivo, constante_objetivo, matriz_restricoes, tipos_restricoes, vetor_lado_direito, tipo_otimizacao="Maximizar"):
    """
    Executa o algoritmo Simplex passo a passo até encontrar a solução ótima.
    """
    numero_restricoes, numero_variaveis = matriz_restricoes.shape

    # 1. Monta a tabela inicial
    tabela = criar_tabela_inicial(coeficientes_objetivo, constante_objetivo, matriz_restricoes, vetor_lado_direito, tipo_otimizacao)

    # Lista para salvar o estado da tabela a cada iteração (útil para exibir na interface)
    historico_tabelas = [tabela.copy()]
    
    # A base inicial contém apenas as variáveis de folga (uma para cada linha de restrição)
    # Exemplo: se temos 2 variáveis originais, as folgas são 2, 3...
    indices_base = [numero_variaveis + i for i in range(numero_restricoes)]

    limite_maximo_repeticoes = 100
    numero_iteracao = 0

    while numero_iteracao < limite_maximo_repeticoes:
        numero_iteracao += 1

        # Pega a linha da Função Objetivo (última linha), ignorando a última coluna (lado direito)
        coeficientes_linha_objetivo = tabela[-1, :-1]

        # --- PASSO A: Critério de Parada (Otimalidade) ---
        # Se nenhum valor na linha objetivo for negativo, chegamos na solução ótima!
        if np.all(coeficientes_linha_objetivo >= 0):
            break

        # --- PASSO B: Escolher a Coluna Pivô (Variável que entra na base) ---
        # É a coluna que possui o valor mais negativo na linha da função objetivo
        coluna_pivo = int(np.argmin(coeficientes_linha_objetivo))

        # --- PASSO C: Escolher a Linha Pivô (Variável que sai da base) - Teste da Razão Mínima ---
        menor_razao = float("inf")
        linha_pivo = -1

        for i in range(numero_restricoes):
            elemento_coluna = tabela[i, coluna_pivo]
            valor_lado_direito = tabela[i, -1]

            # A razão só é calculada para elementos estritamente positivos (> 0)
            if elemento_coluna > 0:
                razao = valor_lado_direito / elemento_coluna
                if razao < menor_razao:
                    menor_razao = razao
                    linha_pivo = i

        # Se não encontramos nenhum elemento positivo na coluna pivô, o problema é ilimitado
        if linha_pivo == -1:
            return None, None, historico_tabelas, "Problema Ilimitado: a função objetivo pode crescer infinitamente."

        # Atualiza qual variável agora ocupa essa posição na base
        indices_base[linha_pivo] = coluna_pivo

        # --- PASSO D: Pivotamento (Eliminação de Gauss-Jordan) ---
        elemento_pivo = tabela[linha_pivo, coluna_pivo]

        # 1. Divide a linha pivô inteira pelo valor do pivô (para que o pivô vire 1)
        tabela[linha_pivo] = tabela[linha_pivo] / elemento_pivo

        # 2. Zera todos os outros elementos daquela coluna (nas outras linhas e na linha de Z)
        numero_total_linhas = numero_restricoes + 1
        for i in range(numero_total_linhas):
            if i != linha_pivo:
                fator_multiplicador = tabela[i, coluna_pivo]
                tabela[i] = tabela[i] - fator_multiplicador * tabela[linha_pivo]

        # Guarda a tabela atualizada no histórico
        historico_tabelas.append(tabela.copy())

    # --- PASSO E: Extração dos Resultados Finais ---
    valores_variaveis = {}
    
    # Inicializa todas as variáveis de decisão originais com valor zero (não-básicas)
    for j in range(numero_variaveis):
        nome_variavel = f"x{j + 1}"
        valores_variaveis[nome_variavel] = 0.0

    # Atualiza o valor das variáveis que terminaram na base
    for i in range(numero_restricoes):
        indice_variavel_na_base = indices_base[i]
        # Se a variável na base for uma das variáveis de decisão originais (x1, x2, ...)
        if indice_variavel_na_base < numero_variaveis:
            nome_variavel = f"x{indice_variavel_na_base + 1}"
            valores_variaveis[nome_variavel] = float(tabela[i, -1])

    # O valor ótimo de Z fica na última linha e última coluna
    valor_z_otimo = float(tabela[-1, -1])
    
    # Se o problema original era de Minimizar, corrigimos o sinal de Z de volta
    if tipo_otimizacao == "Minimizar":
        valor_z_otimo = -valor_z_otimo

    return valores_variaveis, valor_z_otimo, historico_tabelas, "Solução Ótima Encontrada com Sucesso!"