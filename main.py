from collections import deque
import concurrent.futures
import time

def criar_grafo_multiplicacao():

    grafo = {}
    numeros_base = range(1, 21)  # números de 1 a 20
    
    for num in numeros_base:
        grafo[num] = []
        
        # Adiciona multiplicações de 2 a 10
        for multiplicador in range(2, 11):
            resultado = num * multiplicador
            if resultado <= 100:  # limite máximo de 100
                grafo[num].append(resultado)
        
        # Também adiciona divisões se o resultado existir no grafo
        for divisor in range(2, 11):
            if num % divisor == 0:
                resultado = num // divisor
                if resultado >= 1:
                    grafo[num].append(resultado)
    
    # Garante que todos os resultados tenham entrada no grafo
    todos_numeros = set()
    for conexoes in grafo.values():
        todos_numeros.update(conexoes)
    
    for num in todos_numeros:
        if num not in grafo:
            grafo[num] = []
            # Adiciona algumas conexões básicas
            for divisor in range(2, 11):
                if num % divisor == 0:
                    resultado = num // divisor
                    if resultado >= 1:
                        grafo[num].append(resultado)
    
    return grafo

def bfs_multiplicacao(grafo, inicio, fim):

    if inicio not in grafo:
        grafo[inicio] = []
    if fim not in grafo:
        grafo[fim] = []
    
    fila = deque([[inicio]])
    caminhos = []
    
    while fila:
        caminho = fila.popleft()
        numero_atual = caminho[-1]
        if len(caminho) > 6:
            continue
        
        if numero_atual == fim:
            caminhos.append(caminho)
            continue
        
        for proximo in grafo.get(numero_atual, []):
            if proximo not in caminho:
                fila.append(caminho + [proximo])
    
    return caminhos

def busca_sequencial(grafo, inicio, fim):
    tempo_inicio = time.time()
    caminhos = bfs_multiplicacao(grafo, inicio, fim)
    tempo = time.time() - tempo_inicio
    return caminhos, tempo

def processar_origem(args):
    grafo, origem, destino = args
    return origem, bfs_multiplicacao(grafo, origem, destino)

def busca_paralela_foster(grafo, origens, destino):
    tempo_inicio = time.time()
    
    tarefas = [(grafo, origem, destino) for origem in origens]
    resultados = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(processar_origem, tarefa) for tarefa in tarefas]
        
        for future in concurrent.futures.as_completed(futures):
            origem, caminhos = future.result()
            resultados[origem] = caminhos
    
    tempo = time.time() - tempo_inicio
    return resultados, tempo

def mostrar_operacao(num1, num2):

    if num2 > num1:
        if num2 % num1 == 0:
            return f"×{num2//num1}"
    elif num1 > num2:
        if num1 % num2 == 0:
            return f"÷{num1//num2}"
    return "→"

def main():
    print("BUSCA PARALELA COM MULTIPLICAÇÕES (ATÉ 10)")
    print("Metodologia de Foster")
    # Cria o grafo
    grafo = criar_grafo_multiplicacao()
    print(f"Grafo criado com {len(grafo)} números")
    
    # Exemplo de conexões
    print(f"\nExemplo: o número 5 pode ir para: {grafo[5][:5]}...")
    
    # TESTE 1: Pequeno
    print("TESTE 1: Busca Simples")
    
    inicio_seq = 3
    destino = 30
    # Sequencial
    print(f"\n -- EXECUÇÃO SEQUENCIAL --")
    print("-" * 40)
    print(f"Buscando caminhos de {inicio_seq} até {destino}")
    
    caminhos_seq, tempo_seq = busca_sequencial(grafo, inicio_seq, destino)
    print(f"Caminhos encontrados: {len(caminhos_seq)}")
    
    if caminhos_seq:
        for i, caminho in enumerate(caminhos_seq[:3], 1):
            ops = [mostrar_operacao(caminho[j], caminho[j+1]) for j in range(len(caminho)-1)]
            print(f"  Caminho {i}: {caminho[0]} {' '.join(ops)} = {caminho[-1]}")
    
    print(f"Tempo: {tempo_seq:.6f}")
    
    # Paralelo
    print(f"\n -- EXECUÇÃO PARALELA (FOSTER) --")
    print("-" * 40)
    origens = [2, 3, 5, 6]
    print(f"Buscando de {origens} até {destino} em paralelo")
    
    resultados_par, tempo_par = busca_paralela_foster(grafo, origens, destino)
    
    total = sum(len(c) for c in resultados_par.values())
    print(f"Total de caminhos: {total}")
    
    for origem, caminhos in resultados_par.items():
        print(f"  De {origem}: {len(caminhos)} caminhos")
    
    print(f"Tempo: {tempo_par:.6f}")
    
    # Comparação
    print(f"\n -- ANÁLISE --")
    if tempo_par > 0:
        speedup = tempo_seq / tempo_par
        print(f"Speedup: {speedup:.2f}")
        if speedup > 1:
            print("Versão paralela foi mais rápida!")
        else:
            print("Overhead do paralelismo (normal em problemas pequenos)")
    
    # TESTE 2: Maior
    print("TESTE 2: Busca Mais Complexa")
    print("-" * 40)    
    inicio_seq = 2
    destino = 96
    origens = [2, 3, 4, 6, 8, 12]
    
    # Sequencial
    print(f"\n - SEQUENCIAL: {inicio_seq} até {destino}")
    caminhos_seq2, tempo_seq2 = busca_sequencial(grafo, inicio_seq, destino)
    print(f"Caminhos: {len(caminhos_seq2)}, Tempo: {tempo_seq2:.6f}s")
    
    # Paralelo
    print(f"\n - PARALELO: {origens} até {destino}")
    resultados_par2, tempo_par2 = busca_paralela_foster(grafo, origens, destino)
    total2 = sum(len(c) for c in resultados_par2.values())
    print(f"Total de caminhos: {total2}, Tempo: {tempo_par2:.6f}s")
    
    # Análise final
    if tempo_par2 > 0:
        speedup2 = tempo_seq2 / tempo_par2
        print(f"\nSpeedup: {speedup2:.2f}x")
    

if __name__ == "__main__":
    main()