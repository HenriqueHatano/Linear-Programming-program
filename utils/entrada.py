import numpy as np

""" Extrair dados da interface através do session_state """

def extrair_dados_formulario(num_variaveis, num_restricoes, session_state):
    c = []
    for j in range(num_variaveis):
        c.append(float(session_state.get(f"fo_{j}", 0.0)))
    
    c = np.array(c, dtype = float)

    """ Constante FO """
    constante = float(session_state.get("fo_constante", 0.0))


    """ Matriz de Restrições (A), Tipos de desigualdade e Lado Direito (b) """
    A = []
    tipos = []
    b = []

    for i in range(num_restricoes):
        linha_A = []
        for j in range(num_variaveis):
            linha_A.append(float(session_state.get(f"restricao_{i}_{j}", 0.0)))
        
        A.append(linha_A)
        tipos.append(session_state.get(f"tipo_{i}", "<="))
        b.append(float(session_state.get(f"b_{i}", 0.0)))

    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)

    return c, constante, A, tipos, b

""" Valida as regras mnatemáticas do problema de acordo com o método escolhido """

def validar_dados(metodo, num_variaveis, c, A, tipos, b):

    """ Validar Método gráfico """

    if metodo == "Método gráfico":
        if num_variaveis != 2:
            return False, "O Método Gráfico só aceita exatamente 2 variáveis de decisão."
    
    """ Validar Método Simplex Padrão """

    if metodo == "Simplex":
        tipos_invalidos = [t for t in tipos if t != "<="]
        if len(tipos_invalidos) > 0:
            return False, "O Simplex padrão só aceita restrições do tipo '<='. Para restrições '>=' ou '=', use o Big-M."

    for i, linha in enumerate(b):
        if np.all(linha == 0):
            return False, f"A restrição {i + 1} possui todos os coeficientes zerados."

    for i, valor_b in enumerate(b):
        if valor_b < 0 and metodo == "Simplex":
            return False, f"A restrição {i + 1} possui lado direito negativo (b = {valor_b}). Multiplique a restrição por -1 antes de aplicar o Simplex padrão."

    return True, "Dados válidos"