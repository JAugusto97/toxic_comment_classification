from apiclient.discovery import build
from os import listdir
import datetime
import re
import pandas as pd

def autentica(chave='AIzaSyB05-NW7qOcZOvWDWFwe9M8QNf0QTwM_ls'):
    return build('youtube', 'v3', developerKey=chave)

class categoria:
    def __init__(self):
        self.ncategorias = 0
        self.ntermos = 0
        self.categorias = dict()

    def imprime(self):
        print('Categorias:')
        for categoria, termos in self.categorias.items():
            print(categoria+':', end=' ')
            for termo in termos:
                print(termo, end=' ')
            print('\n')

    def adiciona(self, categoria, termo):
        try:
            self.categorias[categoria].append(termo)
            self.ntermos += 1

        except:
            print(categoria, 'nao existe.')

    def carrega(self, filename='categorias.txt'):
        self.ntermos = 0
        self.ncategorias = 0
        """ Carrega as categorias se o arquivo 'categorias.txt' existir, senao
        escreve o arquivo com as categorias  especificadas nessa funcao. """

        try:
            file_categorias = open(filename, 'r')
            print('Lendo Categorias...', end='\n\n')
            for line in file_categorias.readlines():
                categoria, termos = line.split(':')
                self.categorias[categoria] = termos.split()
                self.ntermos += len(termos.split())
                self.ncategorias += 1

            file_categorias.close()

        except:
            print('Arquivo de categorias nao encontrado.')

    def salva(self, filename='categorias.txt'):
        """ Salva as categorias em um arquivo txt. """

        file_categorias = open(filename, 'w')
        for nome, categoria in self.categorias.items():
            file_categorias.write(nome + ':')
            for termo in categoria:
                file_categorias.write(termo + ' ')
            file_categorias.write('\n')

        file_categorias.close()

class canal:
    def __init__(self):
        self.ncanais = 0
        self.canais = dict()

    def imprime(self):
        print('Canais:')
        for nome in self.canais.keys():
            print(nome, end=' ')
        print('\n')

    def carrega(self, filename='canais.txt'):
        """ Carrega os canais se o arquivo 'canais.txt' existir, senao
        escreve o arquivo com os canais especificados nessa funcao. """

        self.ncanais = 0

        try:
            file_canais = open(filename, 'r')
            print('Lendo Canais...', end='\n\n')
            for line in file_canais.readlines():
                canal, id_canal = line.split(':')
                self.canais[canal] = id_canal[:len(id_canal)-1] # remove /n
                self.ncanais += 1
            file_canais.close()

        except:
            print('Arquivo de canais nao encontrado.')

    def salva(self, filename='canais.txt'):
        try:
            fhandle = open(filename, 'w')
            for nome, id_canal in self.canais.items():
                fhandle.write(nome+':'+id_canal+'\n')

        except:
            print('Nao foi possivel salvar os canais')


    def adiciona(self, nome, id_canal):
        try:
            self.canais[nome] = id_canal
            self.ncanais += 1

        except:
            print('nao foi possivel adicionar o canal.')


def carrega_corpus(filename='corpus.csv', series=False):
    """ Carrega o corpus se o arquivo 'corpus.csv' existir, senao
    gera um novo corpus.

    series == True retorna um objeto pd.Series,
    series == False retorna um dicionario """

    try:
        dados = pd.read_csv(filename, engine='python', header=None)[0]
        print('Lendo Corpus.csv...')

        if series: return dados
        else: return dados.to_dict()
    except:
        dados = dict()
        print('corpus.csv nao encontrado. criando um novo')

        if series: return pd.Series(dados)
        else: return dados


def gera_logfile(ultimo_indice_dados):
    """ Cria um arquivo 'dd-mm-aaaa_hh-mm-ss.txt' com os exemplos coletados nessa data """

    now = datetime.datetime.now()
    date = str(now.day) + '-' + str(now.month) + '-' + str(now.year)
    time = str(now.hour) + '-' + str(now.minute) + '-' + str(now.second)
    nome_logfile = date+'_'+time+'.txt'
    print('Gerando logfile '+nome_logfile)

    log_file = open('logfiles/'+nome_logfile, 'a+')
    log_file.write('tamanho_inicio: ' + str(ultimo_indice_dados) + '\n')

    return log_file

def busca_exemplo(index):
    """ dado um indice do corpus, busca nos logfiles quando e
    em qual canal aquele comentário foi encontrado """

    index = ' ' + str(index) + ' '
    encontrado = False
    try:
        canais = carrega_canais()

        # Abre os logfiles
        openfiles = []
        for arquivo in listdir('logfiles/'):
            try:
                re.findall('\d{1,2}-\d{1,2}-\d{4}', arquivo).pop()
                print(arquivo)
                fhandle = open('logfiles/'+arquivo, 'r')
                openfiles.append(fhandle)

                file_lines = fhandle.readlines()
                for line in file_lines:
                    for canal in canais:
                        if re.findall(canal, line): # Se a linha contém o nome do canal
                            if str(index) in line: # Se o indice está na mesma linha do canal
                                data = re.findall('\d{1,2}-\d{1,2}-\d{4}',fhandle.name).pop()
                                retorno = (canal, data)
                                encontrado = True
                                break
            except:
                pass

        # Fecha todos os logfiles
        for fhandle in openfiles:
            fhandle.close()

        if encontrado: return retorno
        else: return ()

    except Exception as error:
        print(error)

def consulta(dados, categoria, canal, nresultados=100, ordem='time',
             respostas=False, api_key='AIzaSyB05-NW7qOcZOvWDWFwe9M8QNf0QTwM_ls'):
    """ Realiza uma consulta pelos parametros passados como argumento e adiciona os resultados em dados.
        dados = dicionario onde os resultados serao armazenados

        categoria = objeto da classe categoria

        canal = objeto da classe canal

        nresultados = numero no intervalo (1,100) que corresponde ao numero de resultados

        ordem = 'time' ou 'relevance'

        respostas = True retorna comentários e respostas a ele. False retorna somente os comentarios.
                    as respostas podem nao conter o termo buscado

        api_key = chave de autenticacao da api """

    youtube = autentica(chave=api_key)
    ultimo_indice_dados = len(dados)
    logfile = gera_logfile(ultimo_indice_dados)

    if respostas:
        part = 'snippet,replies'
    else:
        part = 'snippet'

    total_coletado = 0
    for nome_canal, id_canal in canal.canais.items(): # Para cada canal
        total_por_canal = 0
        print('Buscando em:', nome_canal)
        logfile.write('\nindices encontrados em ' + nome_canal + ': ')

        for categ in categoria.categorias.values(): # Para cada categoria em um canal
            for termo in categ: # Para cada termo X que pertence a uma categoria Y em um canal Z

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

                    if comentario in dados.values(): # Se já está no corpus ignore
                        continue
                    else:
                        dados[ultimo_indice_dados] = comentario # Senao insira no corpus
                        logfile.write(str(ultimo_indice_dados) + ' ')
                        ultimo_indice_dados += 1
                        total_coletado += 1
                        total_por_canal += 1

        logfile.write('\ntotal em ' + str(nome_canal) + ': ' + str(total_por_canal) + '\n')
        print(total_por_canal, 'novos exemplos em', nome_canal + '\n')

    logfile.write('\ntamanho final: ' + str(ultimo_indice_dados))
    logfile.close()
