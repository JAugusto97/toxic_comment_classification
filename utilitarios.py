from apiclient.discovery import build
from os import listdir
import datetime
import re
import pandas as pd

def gera_logfile(ultimo_indice_corpus):
    """ Cria um arquivo 'dd-mm-aaaa_hh-mm-ss.txt' com os exemplos coletados nessa data """

    now = datetime.datetime.now()
    date = str(now.day) + '-' + str(now.month) + '-' + str(now.year)
    time = str(now.hour) + '-' + str(now.minute) + '-' + str(now.second)
    nome_logfile = date+'_'+time+'.txt'
    print('Gerando logfile '+nome_logfile)

    log_file = open('data/logfiles/'+nome_logfile, 'a+')
    log_file.write('tamanho_inicio: ' + str(ultimo_indice_corpus) + '\n')

    return log_file

def consulta(api_key, corpus, categorias, canais, nresultados=100, ordem='time',
             respostas=False):
    """ Realiza uma consulta pelos parametros passados como argumento e adiciona os resultados em corpus.
        corpus = dicionario onde os resultados serao armazenados
        categoria = objeto da classe categoria
        canal = objeto da classe canal
        nresultados = numero no intervalo (1,100) que corresponde ao numero de resultados
        ordem = 'time' ou 'relevance'
        respostas = True retorna comentários e respostas a ele. False retorna somente os comentarios.
                    as respostas podem nao conter o termo buscado
        api_key = chave de autenticacao da api """

    youtube = build('youtube', 'v3', developerKey=api_key)
    ultimo_indice_corpus = len(corpus)
    logfile = gera_logfile(ultimo_indice_corpus)

    regexes = {'homofobico': '', 'vulgar' : '', 'insulto': ''}
    for categoria, termos in categorias.items():
        for termo in termos.split(','):
            regexes[categoria] += str(termo) + '|'
    # Removendo o ultimo '|'
    for categoria in regexes.keys():
        regexes[categoria] = regexes[categoria][:-1]

    if respostas:
        part = 'snippet,replies'
    else:
        part = 'snippet'

    total_termo = 0
    total_categoria = 0
    for nome_canal, id_canal in canais.items(): # Para cada canal
        total_por_canal = 0
        print('Buscando em:', nome_canal)
        logfile.write('\nindices encontrados em ' + nome_canal + ': ')

        for nome, categ  in categorias.items(): # Para cada categoria em um canal
            print('\t'+nome, end=':\n')
            categ_list = categ.split(',')
            for termo in categ_list: # Para cada termo X que pertence a uma categoria Y em um canal Z
                print('\t\t'+termo, end=': ')
                request = youtube.commentThreads().list(part=part,
                                                        allThreadsRelatedToChannelId=id_canal,
                                                        searchTerms=termo,
                                                        textFormat='plainText',
                                                        maxResults=nresultados,
                                                        order=ordem)
                try:
                    query = request.execute()

                except Exception as error: # Consulta falhou
                    print(error)
                    continue

                n_results = len(query['items'])
                for i in range(n_results):
                    comentario = query['items'][i]['snippet']['topLevelComment']['snippet']['textOriginal']

                    if corpus['comentario'].isin([comentario]).any(): # Se já está no corpus ignore
                        continue
                    else:
                        corpus.loc[ultimo_indice_corpus, 'toxico'] = 0
                        for categoria, regex in regexes.items():
                            if re.search(regex, comentario.lower()):
                                corpus.loc[ultimo_indice_corpus, 'toxico'] = 1
                                corpus.loc[ultimo_indice_corpus, categoria] = 1
                            else:
                                corpus.loc[ultimo_indice_corpus, categoria] = 0

                        corpus.loc[ultimo_indice_corpus, 'comentario'] = comentario # Senao insira no corpus
                        logfile.write(str(ultimo_indice_corpus) + ' ')
                        ultimo_indice_corpus += 1
                        total_termo += 1
                        total_por_canal += 1

                total_categoria += total_termo
                print(total_termo)
                total_termo = 0

            print('\ttotal em ', nome+':', total_categoria, '\n')
            total_categoria = 0

        logfile.write('\ntotal em ' + str(nome_canal) + ': ' + str(total_por_canal) + '\n')
        print(total_por_canal, 'novos exemplos em', nome_canal + '\n')

    logfile.write('\ntamanho final: ' + str(ultimo_indice_corpus))
    logfile.close()
