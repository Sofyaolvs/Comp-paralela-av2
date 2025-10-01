from collections import deque
import concurrent.futures
import time

# Grafo representando departamentos de uma empresa
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
    Implementação do algoritmo BFS para encontrar todos os caminhos
    entre dois nós em um grafo.
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

def buscar_caminhos_sequencial(grafo, start, end):
    """
    Busca sequencial - todos os caminhos são encontrados em um único processo.
    """
    return bfs(grafo, start, end)

def buscar_caminhos_paralelo(grafo, nos_iniciais, destino):
    """
    METODOLOGIA DE FOSTER APLICADA:
    
    Etapa 1 - PARTICIONAMENTO:
    Divide o problema em tarefas independentes. Cada nó inicial representa
    uma tarefa separada de busca de caminhos até o destino.
    
    Etapa 2 - COMUNICAÇÃO:
    As tarefas são completamente independentes - não há necessidade de
    comunicação entre elas durante a execução.
    
    Etapa 3 - AGLOMERAÇÃO:
    Agrupamos tarefas similares para execução paralela usando threads.
    
    Etapa 4 - MAPEAMENTO:
    O ThreadPoolExecutor distribui as tarefas entre os núcleos disponíveis.
    """
    def tarefa_busca(no_inicial):
        """Tarefa independente: busca todos os caminhos de um nó inicial até o destino."""
        caminhos = bfs(grafo, no_inicial, destino)
        return [(no_inicial, caminho) for caminho in caminhos]
    
    resultados = []
    
    # Execução paralela usando ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submete cada tarefa para execução paralela
        futures = {executor.submit(tarefa_busca, no): no for no in nos_iniciais}
        
        # Coleta os resultados conforme ficam prontos
        for future in concurrent.futures.as_completed(futures):
            resultados.extend(future.result())
    
    return resultados

def executar_teste_sequencial(grafo, start, end):
    """Execução sequencial para comparação de desempenho."""
    print(f"\nBuscando caminhos de '{start}' até '{end}'...")
    inicio = time.time()
    caminhos = buscar_caminhos_sequencial(grafo, start, end)
    tempo = time.time() - inicio
    return caminhos, tempo

def executar_teste_paralelo(grafo, nos_iniciais, destino):
    """Execução paralela usando metodologia de Foster."""
    print(f"\nBuscando caminhos de {nos_iniciais} até '{destino}' em paralelo...")
    inicio = time.time()
    resultados = buscar_caminhos_paralelo(grafo, nos_iniciais, destino)
    tempo = time.time() - inicio
    return resultados, tempo

# ============= EXECUÇÃO PRINCIPAL =============

print("=" * 80)
print("SIMULAÇÃO DE BUSCA PARALELA COM BFS E METODOLOGIA DE FOSTER")
print("=" * 80)

# Mostra o grafo
print("\n[GRAFO] Estrutura de departamentos:")
print("-" * 80)
for no, vizinhos in grafo.items():
    print(f"  {no} conecta-se com: {', '.join(vizinhos)}")

# Teste 1: Execução Sequencial
print("\n" + "=" * 80)
print("[TESTE 1] EXECUÇÃO SEQUENCIAL")
print("=" * 80)
caminhos_seq, tempo_seq = executar_teste_sequencial(grafo, 'A', 'F')
print(f"\nCaminhos encontrados: {len(caminhos_seq)}")
for i, caminho in enumerate(caminhos_seq, 1):
    print(f"  {i}. {' -> '.join(caminho)} (tamanho: {len(caminho)})")
print(f"\n⏱️  Tempo de execução: {tempo_seq:.6f} segundos")

# Teste 2: Execução Paralela com Foster
print("\n" + "=" * 80)
print("[TESTE 2] EXECUÇÃO PARALELA - METODOLOGIA DE FOSTER")
print("=" * 80)
nos_para_buscar = ['A', 'B', 'C']
resultados_par, tempo_par = executar_teste_paralelo(grafo, nos_para_buscar, 'F')
print(f"\nCaminhos encontrados: {len(resultados_par)}")
for i, (origem, caminho) in enumerate(resultados_par, 1):
    print(f"  {i}. [De {origem}] {' -> '.join(caminho)} (tamanho: {len(caminho)})")
print(f"\n⏱️  Tempo de execução: {tempo_par:.6f} segundos")

# Análise de Desempenho
print("\n" + "=" * 80)
print("[ANÁLISE] COMPARAÇÃO DE DESEMPENHO")
print("=" * 80)
print(f"Tempo sequencial:  {tempo_seq:.6f}s")
print(f"Tempo paralelo:    {tempo_par:.6f}s")

if tempo_par > 0 and tempo_seq > 0:
    speedup = tempo_seq / tempo_par
    eficiencia = (speedup / len(nos_para_buscar)) * 100
    print(f"\n📊 Speedup: {speedup:.2f}x")
    print(f"📊 Eficiência: {eficiencia:.1f}%")
    
    if speedup > 1:
        print(f"✅ A versão paralela foi {speedup:.2f}x mais rápida!")
    else:
        print(f"⚠️  Para este grafo pequeno, o overhead de paralelização supera os ganhos.")
        print("   Em grafos maiores, o ganho seria significativo!")

print("\n" + "=" * 80)
print("METODOLOGIA DE FOSTER APLICADA COM SUCESSO!")
print("=" * 80)