from auxiliares import inversa_matriz, multiplicar_matrizes

def resolver_simplex(c, A, b, inequacoes, num_variaveis_originais):
    
    epsilon = 1e-9  # Tolerancia para comparacoes de ponto flutuante

    # --- Padronizacao do Problema ---
    num_restricoes = len(A)
    
    # Garante que todos os elementos de 'b' sejam nao negativos
    for i in range(num_restricoes):
        if b[i] < 0:
            b[i] *= -1
            A[i] = [-val for val in A[i]]
            if inequacoes[i] == '<=': inequacoes[i] = '>='
            elif inequacoes[i] == '>=': inequacoes[i] = '<='

    c_original = list(c)
    indices_vars_artificiais = []
    
    # Adiciona variaveis de folga, excesso e artificiais
    vars_atuais = num_variaveis_originais
    for i in range(num_restricoes):
        for linha in A: linha.append(0.0)
        if inequacoes[i] == '<=':
            A[i][vars_atuais] = 1.0 # Variavel de folga
            c.append(0.0)
            vars_atuais += 1
        elif inequacoes[i] == '>=':
            A[i][vars_atuais] = -1.0 # Variavel de excesso
            c.append(0.0)
            vars_atuais += 1
            
            for linha in A: linha.append(0.0)
            A[i][vars_atuais] = 1.0 # Variavel artificial
            indices_vars_artificiais.append(vars_atuais)
            c.append(0.0)
            vars_atuais += 1
        elif inequacoes[i] == '=':
            A[i][vars_atuais] = 1.0 # Variavel artificial
            indices_vars_artificiais.append(vars_atuais)
            c.append(0.0)
            vars_atuais += 1
    
    num_total_variaveis = len(c)
    
    # --- Fase I: Encontrar uma solucao basica factivel ---
    if not indices_vars_artificiais:
        # Pula para a Fase II se nao houver variaveis artificiais
        indices_base = list(range(num_variaveis_originais, num_total_variaveis))
    else:
        print("--- Iniciando Fase I ---")
        # Funcao objetivo da Fase I: Minimizar a soma das variaveis artificiais
        c_fase1 = [1.0 if i in indices_vars_artificiais else 0.0 for i in range(num_total_variaveis)]
        
        # Base inicial: variaveis de folga e artificiais que formam a matriz identidade
        indices_base = []
        for i in range(num_restricoes):
            for j in range(num_variaveis_originais, num_total_variaveis):
                 if abs(A[i][j] - 1.0) < epsilon and all(abs(A[k][j]) < epsilon for k in range(num_restricoes) if k != i):
                    indices_base.append(j)
                    break
        
        # Loop do Simplex para Fase I
        c_atual = c_fase1
        while True:
            indices_nao_base = [i for i in range(num_total_variaveis) if i not in indices_base]
            
            # Passo 1: Calcular solucao basica (B e x_B)
            B = [[A[i][j] for j in indices_base] for i in range(num_restricoes)]
            try:
                B_inv = inversa_matriz(B)
            except ValueError: return "Erro: Matriz basica singular na Fase I.", None, None

            # Passo 2: Calcular custos relativos
            c_B = [c_atual[i] for i in indices_base]
            lambda_T = multiplicar_matrizes([c_B], B_inv)[0]
            
            custos_reduzidos = {}
            for j in indices_nao_base:
                coluna_j = [A[i][j] for i in range(num_restricoes)]
                custo = c_atual[j] - sum(lambda_T[i] * coluna_j[i] for i in range(num_restricoes))
                custos_reduzidos[j] = custo

            # Passo 3: Teste de otimalidade
            variavel_entra = min(custos_reduzidos, key=custos_reduzidos.get, default=None)
            if variavel_entra is None or custos_reduzidos[variavel_entra] >= -epsilon:
                break # Otimalidade da Fase I alcancada

            # Passo 4: Calculo da direcao simplex
            coluna_entra = [A[i][variavel_entra] for i in range(num_restricoes)]
            y_direcao_simplex = multiplicar_matrizes(B_inv, coluna_entra)

            # Passo 5: Teste da razao minima para determinar variavel que sai
            x_B = multiplicar_matrizes(B_inv, b)
            razoes = {i: x_B[i] / y_direcao_simplex[i] for i in range(len(y_direcao_simplex)) if y_direcao_simplex[i] > epsilon}
            
            if not razoes: return "Problema da Fase I ilimitado.", None, None

            indice_sai_na_base = min(razoes, key=razoes.get)
            
            # Passo 6: Atualizacao da base
            indices_base[indice_sai_na_base] = variavel_entra

        # Verificacao do fim da Fase I
        x_B = multiplicar_matrizes(inversa_matriz([[A[i][j] for j in indices_base] for i in range(num_restricoes)]), b)
        objetivo_final_fase1 = sum(c_fase1[idx] * val for idx, val in zip(indices_base, x_B))
        if objetivo_final_fase1 > epsilon:
            return "Problema original infactivel.", None, None
        print("--- Fim da Fase I. Solucao factivel encontrada. ---")

    # --- Fase II: Encontrar a solucao otima ---
    print("\n--- Iniciando Fase II ---")
    c_atual = list(c_original) + [0.0] * (num_total_variaveis - len(c_original))
    
    while True:
        indices_nao_base = [i for i in range(num_total_variaveis) if i not in indices_base]
        
        B = [[A[i][j] for j in indices_base] for i in range(num_restricoes)]
        try:
            B_inv = inversa_matriz(B)
        except ValueError: return "Erro: Matriz basica singular na Fase II.", None, None

        c_B = [c_atual[i] for i in indices_base]
        lambda_T = multiplicar_matrizes([c_B], B_inv)[0]
        
        custos_reduzidos = {j: c_atual[j] - sum(lambda_T[i] * A[i][j] for i in range(num_restricoes)) for j in indices_nao_base if j not in indices_vars_artificiais}

        variavel_entra = min(custos_reduzidos, key=custos_reduzidos.get, default=None)
        if variavel_entra is None or custos_reduzidos[variavel_entra] >= -epsilon:
            # Solucao otima encontrada
            x_B = multiplicar_matrizes(B_inv, b)
            solucao = [0.0] * num_total_variaveis
            for i, idx in enumerate(indices_base):
                if idx < num_total_variaveis: solucao[idx] = x_B[i]
            
            valor_objetivo_final = sum(c_atual[i] * solucao[i] for i in range(num_total_variaveis))
            return "Otima", solucao[:num_variaveis_originais], valor_objetivo_final
        
        coluna_entra = [A[i][variavel_entra] for i in range(num_restricoes)]
        y_direcao_simplex = multiplicar_matrizes(B_inv, coluna_entra)

        if all(val <= epsilon for val in y_direcao_simplex): return "Problema ilimitado.", None, None

        x_B = multiplicar_matrizes(B_inv, b)
        razoes = {i: x_B[i] / y_direcao_simplex[i] for i in range(len(y_direcao_simplex)) if y_direcao_simplex[i] > epsilon}
        
        if not razoes: return "Problema ilimitado (sem razao positiva).", None, None

        indice_sai_na_base = min(razoes, key=razoes.get)
        indices_base[indice_sai_na_base] = variavel_entra