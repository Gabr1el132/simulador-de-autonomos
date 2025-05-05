import json
import csv
import time
from collections import defaultdict, deque

def carregar_automato_de_arquivo(caminho_do_arquivo_do_automato):
    with open(caminho_do_arquivo_do_automato, 'r', encoding='utf-8') as arquivo:
        return json.load(arquivo)

def identificar_tipo_de_automato(dados_do_automato):
    dicionario_de_transicoes = defaultdict(set)
    for transicao in dados_do_automato["transitions"]:
        if transicao["read"] is None:
            return "epsilon_nfa"
        chave = (transicao["from"], transicao["read"])
        if chave in dicionario_de_transicoes:
            return "nfa"
        dicionario_de_transicoes[chave].add(transicao["to"])
    return "dfa"

def simular_dfa(dados_do_automato, palavra_de_entrada):
    estado_atual = dados_do_automato["initial"]
    conjunto_de_estados_finais = set(dados_do_automato["final"])
    tabela_de_transicoes = defaultdict(dict)

    for transicao in dados_do_automato["transitions"]:
        if transicao["read"] is not None:
            tabela_de_transicoes[transicao["from"]][transicao["read"]] = transicao["to"]

    for simbolo in palavra_de_entrada:
        if simbolo in tabela_de_transicoes[estado_atual]:
            estado_atual = tabela_de_transicoes[estado_atual][simbolo]
        else:
            return 0
    return 1 if estado_atual in conjunto_de_estados_finais else 0

def simular_nfa(dados_do_automato, palavra_de_entrada):
    conjunto_de_estados_finais = set(dados_do_automato["final"])
    tabela_de_transicoes = defaultdict(lambda: defaultdict(set))

    for transicao in dados_do_automato["transitions"]:
        if transicao["read"] is not None:
            tabela_de_transicoes[transicao["from"]][transicao["read"]].add(transicao["to"])

    conjunto_de_estados_atuais = set([dados_do_automato["initial"]])
    for simbolo in palavra_de_entrada:
        conjunto_de_estados_proximos = set()
        for estado in conjunto_de_estados_atuais:
            conjunto_de_estados_proximos |= tabela_de_transicoes[estado][simbolo]
        conjunto_de_estados_atuais = conjunto_de_estados_proximos

    return 1 if conjunto_de_estados_atuais & conjunto_de_estados_finais else 0

def calcular_fecho_epsilon(estado_inicial, tabela_de_transicoes):
    conjunto_fecho = set()
    fila_de_estados = deque([estado_inicial])

    while fila_de_estados:
        estado_atual = fila_de_estados.popleft()
        if estado_atual not in conjunto_fecho:
            conjunto_fecho.add(estado_atual)
            fila_de_estados.extend(tabela_de_transicoes[estado_atual][None])
    return conjunto_fecho

def simular_epsilon_nfa(dados_do_automato, palavra_de_entrada):
    conjunto_de_estados_finais = set(dados_do_automato["final"])
    tabela_de_transicoes = defaultdict(lambda: defaultdict(set))

    for transicao in dados_do_automato["transitions"]:
        tabela_de_transicoes[transicao["from"]][transicao["read"]].add(transicao["to"])

    conjunto_de_estados_atuais = calcular_fecho_epsilon(dados_do_automato["initial"], tabela_de_transicoes)

    for simbolo in palavra_de_entrada:
        conjunto_de_estados_proximos = set()
        for estado in conjunto_de_estados_atuais:
            conjunto_de_estados_proximos |= tabela_de_transicoes[estado][simbolo]
        conjunto_de_estados_atuais = set()
        for estado in conjunto_de_estados_proximos:
            conjunto_de_estados_atuais |= calcular_fecho_epsilon(estado, tabela_de_transicoes)

    return 1 if conjunto_de_estados_atuais & conjunto_de_estados_finais else 0

def simular_palavra(dados_do_automato, palavra_de_entrada):
    tipo_do_automato = identificar_tipo_de_automato(dados_do_automato)
    if tipo_do_automato == "dfa":
        return simular_dfa(dados_do_automato, palavra_de_entrada)
    elif tipo_do_automato == "nfa":
        return simular_nfa(dados_do_automato, palavra_de_entrada)
    else:
        return simular_epsilon_nfa(dados_do_automato, palavra_de_entrada)

def processar_arquivo_de_testes(dados_do_automato, caminho_do_arquivo_de_entrada, caminho_do_arquivo_de_saida):
    with open(caminho_do_arquivo_de_entrada, 'r', encoding='utf-8') as arquivo_entrada, open(caminho_do_arquivo_de_saida, 'w', newline='', encoding='utf-8') as arquivo_saida:
        leitor_csv = csv.reader(arquivo_entrada, delimiter=';')
        escritor_csv = csv.writer(arquivo_saida, delimiter=';')
        for linha in leitor_csv:
            if not linha or len(linha) < 2:
                continue
            palavra_de_entrada, resultado_esperado = linha[0], int(linha[1])
            tempo_inicial = time.time()
            resultado_obtido = simular_palavra(dados_do_automato, palavra_de_entrada)
            tempo_decorrido = round(time.time() - tempo_inicial, 6)
            escritor_csv.writerow([palavra_de_entrada, resultado_esperado, resultado_obtido, tempo_decorrido])

if __name__ == "__main__":
    caminho_do_automato = "automato.aut"
    caminho_de_entrada = "teste.in"
    caminho_de_saida = "resultado.out"

    try:
        dados_do_automato = carregar_automato_de_arquivo(caminho_do_automato)
        processar_arquivo_de_testes(dados_do_automato, caminho_de_entrada, caminho_de_saida)
        print(f"Simulação concluída com sucesso. Resultados armazenados em: {caminho_de_saida}")
    except Exception as erro:
        print(f"Erro ao executar a simulação: {erro}")
