import numpy as np
import matplotlib.pyplot as plt
from utils.entrada import extrair_dados_formulario, validar_dados

def ponto_eh_viavel(ponto, A, tipos, b):
    x1, x2 = ponto[0], ponto[1]

    """ Não-negatividade """
    if x1 < 0 or x2 < 0:
        return False

    """Testa cada uma das restrições """
    for i in range(len(b)):
        lado_esquerdo = A[i][0] * x1 + A[i][1] * x2  # lado esquerdo: a1*x1 + a2*x2
        lado_direito = b[i]                         # lado direito: b

        if tipos[i] == "<=" and lado_esquerdo > lado_direito:
            return False
        elif tipos[i] == ">=" and lado_esquerdo < lado_direito:
            return False
        elif tipos[i] == "=" and lado_esquerdo != lado_direito:
            return False

    return True

def encontrar_vertices(A, tipos, b):

    """ Junta as restrições com as retas dos eixos (x1=0 e x2=0) """
    todas_linhas = list(A) + [[1, 0], [0, 1]]
    todos_b = list(b) + [0, 0]

    num_retas = len(todos_b)
    vertices = []

    for i in range (num_retas):
        for j in range(i + 1, num_retas):
            M = np.array([todas_linhas[i], todas_linhas[j]], dtype = float)
            lado_direito = np.array([todos_b[i], todos_b[j]], dtype = float)

            if np.linalg.det(M) != 0:
                ponto = np.linalg.solve(M, lado_direito)

                if ponto_eh_viavel(ponto, A, tipos, b):
                    if not any(np.array_equal(ponto, v) for v in vertices):
                        vertices.append(ponto)
        
    return vertices

def resolver_grafico(c, constante, A, tipos, b, tipo_otimizacao="Maximizar"):
    vertices = encontrar_vertices(A, tipos, b)

    if len(vertices) == 0:
        return None, None, None  # Região inviável

    # 1. Avalia Z em cada vértice
    valores_z = []
    for v in vertices:
        z = c[0] * v[0] + c[1] * v[1] + constante
        valores_z.append(z)

    # 2. Escolhe o ótimo
    if tipo_otimizacao == "Maximizar":
        melhor_posicao = np.argmax(valores_z)
    else:
        melhor_posicao = np.argmin(valores_z)

    ponto_otimo = vertices[melhor_posicao]
    z_otimo = valores_z[melhor_posicao]

    # 3. Desenha o gráfico simples
    fig, ax = plt.subplots()

    # Define o tamanho dos eixos
    max_x = max([v[0] for v in vertices] + [10]) * 1.2
    x_vals = np.linspace(0, max_x, 100)

    # Desenha as retas de restrição
    for i in range(len(b)):
        a1, a2 = A[i][0], A[i][1]
        limite = b[i]
        if a2 != 0:
            y_vals = (limite - a1 * x_vals) / a2
            ax.plot(x_vals, y_vals, label=f"R{i+1}: {a1}x1 + {a2}x2 = {limite}")
        else:
            ax.axvline(x=limite / a1, label=f"R{i+1}: {a1}x1 = {limite}")

    # Marca todos os vértices viáveis
    for v in vertices:
        ax.plot(v[0], v[1], "bo")  # bolinhas azuis

    # Destaca o ponto ótimo
    ax.plot(ponto_otimo[0], ponto_otimo[1], "r*", markersize=12, label=f"Ótimo ({ponto_otimo[0]}, {ponto_otimo[1]})")

    ax.set_xlim(0, max_x)
    ax.set_ylim(0, max_x)
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.legend()
    ax.grid(True)

    return ponto_otimo, z_otimo, fig