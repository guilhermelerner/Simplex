from auxiliares import interpretar_problema
from simplex import resolver_simplex

if __name__ == "__main__":
    caminho_arquivo = 'problema.txt'
    try:
        # 1. Efetuar a leitura do TXT
        tipo_objetivo, c, A, b, inequacoes, num_variaveis = interpretar_problema(caminho_arquivo)

        print("Problema de Programacao Linear Lido do Arquivo:")
        print(f"Tipo: {tipo_objetivo.capitalize()}")
        
        # Monta a string da funcao objetivo para exibicao
        if tipo_objetivo == "max":
            objetivo_texto = " ".join([f"{'+' if -v >= 0 else ''} {-v}*x{i+1}" for i, v in enumerate(c)]).strip().lstrip('+ ')
        else:
            objetivo_texto = " ".join([f"{'+' if v >= 0 else ''} {v}*x{i+1}" for i, v in enumerate(c)]).strip().lstrip('+ ')
        print(f"Funcao Objetivo: {tipo_objetivo.capitalize()} Z = {objetivo_texto}")
            
        print("Restricoes:")
        for i, linha in enumerate(A):
            restricao_texto = " ".join([f"{'+' if val >= 0 else ''} {val}*x{j+1}" for j, val in enumerate(linha) if val != 0]).strip().lstrip('+ ')
            print(f"  {restricao_texto} {inequacoes[i]} {b[i]}")
        print("-" * 50)

        # 3. Chamar a funcao que implementa o Simplex (Fase I e Fase II)
        status, solucao, valor = resolver_simplex(c, A, b, inequacoes, num_variaveis)
        
        print("\n" + "=" * 20 + " RESULTADO " + "=" * 20)
        print(f"Status: {status}")
        
        if solucao is not None:
            # Ajusta o valor final se o problema original era de maximizacao
            valor_final = -valor if tipo_objetivo == 'max' else valor
            
            print("Solucao Otima (variaveis originais):")
            for i, val in enumerate(solucao):
                print(f"  x{i+1} = {val:.17f}")
            
            print(f"Valor da Funcao Objetivo: {valor_final:.17f}")
        print("=" * 53)

    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' nao encontrado. Por favor, crie o arquivo.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")