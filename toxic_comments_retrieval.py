from utilitarios import (autentica, categoria, canal,
                         carrega_corpus, gera_logfile, busca_exemplo,
                         consulta)

import pandas as pd

categorias = categoria()
categorias.carrega(filename='categorias.txt')
categorias.imprime()

canais = canal()
canais.carrega(filename='canais.txt')
canais.imprime()

corpus = carrega_corpus(series=False)

consulta(dados=corpus, categoria=categorias, canal=canais, nresultados=100, ordem='time', respostas=False) # api_key esta como argumento default

corpus = pd.Series(corpus)
corpus.to_csv('corpus.csv', index=False)
corpus.to_excel('corpus.xlsx', index=False)
