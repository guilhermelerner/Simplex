import re

# ==============================================================================
# Funções de Matriz (Desenvolvidas do Zero) - (sem alteracoes nesta secao)
# ==============================================================================

def obter_menor(matriz, i, j):
    return [linha[:j] + linha[j+1:] for linha in (matriz[:i] + matriz[i+1:])]

def determinante(matriz):
    if len(matriz) != len(matriz[0]):
        raise ValueError("A matriz deve ser quadrada para calcular o determinante.")
    if len(matriz) == 1:
        return matriz[0][0]
    if len(matriz) == 2:
        return matriz[0][0] * matriz[1][1] - matriz[0][1] * matriz[1][0]
    det = 0
    for c in range(len(matriz)):
        sub_determinante = determinante(obter_menor(matriz, 0, c))
        det += ((-1)**c) * matriz[0][c] * sub_determinante
    return det

def inversa_matriz(matriz):
    det = determinante(matriz)
    if abs(det) < 1e-9:
        raise ValueError("A matriz e singular e nao pode ser invertida.")
    cofatores = []
    for r in range(len(matriz)):
        linha_cofator = []
        for c in range(len(matriz)):
            menor = obter_menor(matriz, r, c)
            linha_cofator.append(((-1)**(r+c)) * determinante(menor))
        cofatores.append(linha_cofator)
    adjunta = list(zip(*cofatores))
    inversa = [[elem / det for elem in linha] for linha in adjunta]
    return inversa

def multiplicar_matrizes(matriz_A, matriz_B):
    eh_vetor = not isinstance(matriz_B[0], list)
    if eh_vetor:
        B_como_matriz = [[x] for x in matriz_B]
    else:
        B_como_matriz = matriz_B
    if len(matriz_A[0]) != len(B_como_matriz):
        raise ValueError("Numero de colunas de A deve ser igual ao numero de linhas de B.")
    resultado = [[0] * len(B_como_matriz[0]) for _ in range(len(matriz_A))]
    for i in range(len(matriz_A)):
        for j in range(len(B_como_matriz[0])):
            for k in range(len(B_como_matriz)):
                resultado[i][j] += matriz_A[i][k] * B_como_matriz[k][j]
    if eh_vetor:
        return [linha[0] for linha in resultado]
    return resultado

# ==============================================================================
# Leitura e Parser do Arquivo TXT - (com alteracoes nesta secao)
# ==============================================================================

def interpretar_problema(caminho_arquivo):
    """Le um arquivo de problema e o converte para formato matematico."""
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        linhas = [linha for linha in f if not linha.strip().startswith('#') and linha.strip()]

    linha_objetivo = linhas[0]
    tipo_objetivo = "min" if "min" in linha_objetivo.lower() else "max"
    expressao_objetivo = linha_objetivo.split('=')[1].strip()
    
    indices_variaveis = [int(i) for i in re.findall(r'x(\d+)', expressao_objetivo)]
    num_variaveis = max(indices_variaveis) if indices_variaveis else 0
    
    c = [0.0] * num_variaveis
    
    regex_termo = r'([+\-−]?\s*\d*\.?\d*)\s*\*?\s*x(\d+)'
    
    termos = re.findall(regex_termo, expressao_objetivo)
    for coeff_texto, var_idx_texto in termos:
        var_idx = int(var_idx_texto) - 1
        coeff_texto = coeff_texto.replace(" ", "").replace("*", "")
        coeff_texto = coeff_texto.replace('−', '-') # NOVA LINHA DE CORRECAO
        
        if coeff_texto in ['+', '']: coeficiente = 1.0
        elif coeff_texto == '-': coeficiente = -1.0
        else: coeficiente = float(coeff_texto)
        c[var_idx] = coeficiente

    if tipo_objetivo == "max":
        c = [-val for val in c]

    A, b, inequacoes = [], [], []
    for linha_restricao in linhas[1:]:
        match = re.search(r'(<=|>=|=)', linha_restricao)
        if not match: continue
        
        operador = match.group(1)
        inequacoes.append(operador)
        
        lado_esquerdo, lado_direito = linha_restricao.split(operador)
        b.append(float(lado_direito.strip()))
        
        linha = [0.0] * num_variaveis
        
        termos = re.findall(regex_termo, lado_esquerdo)
        for coeff_texto, var_idx_texto in termos:
            var_idx = int(var_idx_texto) - 1
            coeff_texto = coeff_texto.replace(" ", "").replace("*", "")
            coeff_texto = coeff_texto.replace('−', '-') # NOVA LINHA DE CORRECAO
            
            if coeff_texto in ['+', '']: coeficiente = 1.0
            elif coeff_texto == '-': coeficiente = -1.0
            else: coeficiente = float(coeff_texto)
            linha[var_idx] = coeficiente
        A.append(linha)

    return tipo_objetivo, c, A, b, inequacoes, num_variaveis