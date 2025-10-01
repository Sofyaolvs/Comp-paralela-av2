from collections import deque
import concurrent.futures
import time

# Função para verificar se um número é par ou ímpar usando operação matemática
def verificar_paridade(numero):
    """
    Verifica se um número é par ou ímpar usando o operador módulo (%)
    Retorna 'par' se numero % 2 == 0, caso contrário retorna 'ímpar'
    """
    return 'par' if numero % 2 == 0 else 'ímpar'

# Construção do Grafo
grafo = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}

def bfs(grafo, start, end):
    """
    Implementa o algoritmo de Busca em Largura (BFS)
    Retorna todos os caminhos possíveis entre start e end
    """
    fila = deque([[start]])
    caminhos = []
    
    while fila:
        caminho = fila.popleft()
        no = caminho[-1]
        
        if no == end:
            caminhos.append(caminho)
        
        for vizinho in grafo.get(no, []):
            if vizinho not in caminho:
                fila.append(caminho + [vizinho])
    
    return caminhos

def analisar_caminhos(caminhos):
    """
    Analisa os caminhos encontrados e verifica a paridade do tamanho
    """
    print("\n=== ANÁLISE DE CAMINHOS COM VERIFICAÇÃO DE PARIDADE ===")
    for i, caminho in enumerate(caminhos, 1):
        tamanho = len(caminho)
        paridade = verificar_paridade(tamanho)
        print(f"Caminho {i}: {' -> '.join(caminho)}")
        print(f"  Tamanho: {tamanho} nós ({paridade})")
        print(f"  Arestas: {tamanho - 1}")
        print()

def buscar_sequencial(grafo, start, end):
    """
    Executa a busca de forma sequencial
    """
    print(f"\n--- BUSCA SEQUENCIAL: {start} até {end} ---")
    inicio = time.time()
    caminhos = bfs(grafo, start, end)
    fim = time.time()
    
    print(f"Caminhos encontrados: {len(caminhos)}")
    print(f"Tempo de execução: {fim - inicio:.6f} segundos")
    
    analisar_caminhos(caminhos)
    return caminhos

def buscar_subgrafo(args):
    """
    Função auxiliar para buscar em um subgrafo
    """
    grafo, start, end, subgrafo_id = args
    caminhos = bfs(grafo, start, end)
    return (subgrafo_id, caminhos)

def buscar_paralelo(grafo, start, end, num_workers=3):
    """
    Executa a busca de forma paralela usando múltiplos workers
    """
    print(f"\n--- BUSCA PARALELA: {start} até {end} ---")
    print(f"Número de workers: {num_workers}")
    
    inicio = time.time()
    
    # Criar tarefas para execução paralela
    tarefas = [(grafo, start, end, i) for i in range(num_workers)]
    
    todos_caminhos = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(buscar_subgrafo, tarefa) for tarefa in tarefas]
        
        for future in concurrent.futures.as_completed(futures):
            subgrafo_id, caminhos = future.result()
            if caminhos:
                todos_caminhos.extend(caminhos)
    
    # Remover duplicatas
    caminhos_unicos = []
    for caminho in todos_caminhos:
        if caminho not in caminhos_unicos:
            caminhos_unicos.append(caminho)
    
    fim = time.time()
    
    print(f"Caminhos encontrados: {len(caminhos_unicos)}")
    print(f"Tempo de execução: {fim - inicio:.6f} segundos")
    
    analisar_caminhos(caminhos_unicos)
    return caminhos_unicos

def estatisticas_paridade(caminhos):
    """
    Calcula estatísticas sobre a paridade dos caminhos
    """
    pares = sum(1 for c in caminhos if len(c) % 2 == 0)
    impares = len(caminhos) - pares
    
    print("\n=== ESTATÍSTICAS DE PARIDADE ===")
    print(f"Total de caminhos: {len(caminhos)}")
    print(f"Caminhos com tamanho PAR: {pares} ({pares/len(caminhos)*100:.1f}%)")
    print(f"Caminhos com tamanho ÍMPAR: {impares} ({impares/len(caminhos)*100:.1f}%)")

# Execução Principal
if __name__ == "__main__":
    print("=" * 60)
    print("SIMULAÇÃO DE BUSCA PARALELA COM BFS")
    print("Metodologia de Foster + Verificação de Paridade")
    print("=" * 60)
    
    # Teste 1: Busca Sequencial
    caminhos_seq = buscar_sequencial(grafo, 'A', 'F')
    estatisticas_paridade(caminhos_seq)
    
    print("\n" + "=" * 60)
    
    # Teste 2: Busca Paralela
    caminhos_par = buscar_paralelo(grafo, 'A', 'F', num_workers=3)
    estatisticas_paridade(caminhos_par)
    
    print("\n" + "=" * 60)
    print("CONCLUSÃO")
    print("=" * 60)
    print(f"Ambas as buscas encontraram {len(caminhos_seq)} caminhos")
    print("A verificação de paridade permite classificar e analisar os caminhos")
    print("Operação matemática usada: número % 2 (módulo)")