from utilitarios import gera_logfile, consulta
import pandas as pd

API_KEY = 'AIzaSyB05-NW7qOcZOvWDWFwe9M8QNf0QTwM_ls'
PATH_CHANNELS = 'data/canais.txt'
PATH_CATEGORIES = 'data/categorias.txt'
PATH_CORPUS = 'data/corpus.csv'

canais = {}
with open(PATH_CHANNELS, 'r') as file_canais:
    print('Lendo Canais...', end='\n\n')
    for line in file_canais.readlines():
        canal, id_canal = line.split(':')
        canais[canal] = id_canal[:len(id_canal)-1] # remove /n

categorias = {}
with open(PATH_CATEGORIES, 'r') as file_categorias:
    print('Lendo Categorias...', end='\n\n')
    for line in file_categorias.readlines():
        categoria, termos = line.split(':')
        categorias[categoria] = termos.split(',')

corpus = pd.DataFrame(columns=['comentario','toxico','homofobico','vulgar','insulto'])
#corpus = pd.read_csv(PATH_CORPUS, engine='python', names=['comentario','toxico','homofobico','vulgar','insulto']).to_dict()
consulta(api_key=API_KEY, corpus=corpus, categorias=categorias, canais=canais,
         nresultados=100, ordem='time', respostas=False)

print(corpus.head(10))
corpus.to_csv(PATH_CORPUS, index=False, header=True)
