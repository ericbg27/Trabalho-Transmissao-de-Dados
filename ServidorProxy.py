import sys
import socket
import time
import _thread

#Definicoes das listas
BlackList = ['www.clubedohardware.com.br', 'youtube.com']
WhiteList = ['www.falstad.com']
Deny_terms = ['Jim Kurose']

#Definindo porta como 80 e IP do host como localhost
porta = 80
host = '127.0.0.1'

def main():
    #Printando numero de porta e IP do servidor
    print('Servidor Proxy', host, ':', porta)

    try: #Criando socket
        http_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        http_socket.bind((host, porta)) #Associando socket com porta e IP definidos
        http_socket.listen(110) #Numero maximo de conexoes simultaneas

    except (valor, mensagem): #Caso nao seja possivel abrir o socket
        if http_socket:
            http_socket.close() 

        print('Não foi possível abrir o socket: ', mensagem)
        sys.exit(1)

    while True:
        try:
            conexao, endereco = http_socket.accept() #Aceitando conexao do cliente
            _thread.start_new_thread(proxy, (conexao, endereco)) #Iniciando uma nova thread

        except KeyboardInterrupt: #Caso o usuario use a interrupcao do teclado (ctrl+C) no terminal, interromper o programa
            http_socket.close()
            arquivo.close()
            print('\n[1] - Finalizando o Servidor Proxy\n\n')
            sys.exit(1)

def proxy(conexao, endereco):
    Data = [] #Lista com os dados de cada requisicao
    requisicao = conexao.recv(4096) #Recebendo dados HTTP
    primeira_linha_aux = str(requisicao) #Convertendo dados para string
    primeira_linha = primeira_linha_aux.split('\n') #Pegando URL
    url = primeira_linha_aux.split(' ',1) 
    arquivo = open("Log.txt", "a") #Abrindo arquivo de escrita para o log

    if(len(url) > 1): #Definindo o que sera a URL, dependendo do formato da mensagem
        url = url[1]
    else:
        url = url[0]
    
    #print("\n\n\n\n" + url + "\n\n\n\n")
    http_pos = url.find("://") #Procurando onde comeca o nome do dominio (www) e armazenando em uma variavel temporaria
    if (http_pos == -1):
        temp = url
    else:
        temp = url[(http_pos+3):]

    position = temp.find("/") #Procurando pela barra apos o dominio, caso haja

    if position == -1: #Armazenando dominio (www.dominio.com) na variavel servidor web
        servidor_web = temp
    else:
        servidor_web = temp[:position]
    
    #Autorizado = Flag para a Whitelist / Flag = Flag para indicar que nao esta em nenhuma das listas (Whitelist,Blacklist e Deny_Terms)
    Autorizado = 0 #Zerando flags
    Flag = 0 

    for i in range(0, len(WhiteList)): #Se o dominio esta na Whitelist, setar ambas as flags e escrever no log
        if WhiteList[i] in str(servidor_web):
            Autorizado = 1
            Flag = 1
            arquivo.write(time.strftime('%d/%m/%Y %H:%M:%S') +": Acesso Realizado - Termo na White List. URL: " + url + "\n\n")

    if Autorizado == 0: #Se nao estiver na Whitelist, procurar na Blacklist
        for i in range(0,len(BlackList)): #Caso esteja na Blacklist, setar flag "Flag", enviar codigo HTTP 403 no formato HTML 
            if BlackList[i] in str(servidor_web): #Alem disso, escreve-se no log
                conexao.send(str.encode('<html><head><link rel="alternate stylesheet" type="text/css" href="resource://gre-resources/plaintext.css" title="Quebrar linhas"></head><body><pre>403 Forbidden</pre></body></html>'))
                arquivo.write(time.strftime('%d/%m/%Y %H:%M:%S') + ": Acesso Negado - Termo na Black List. URL: " + url + "\n\n")
                Flag = 1
                conexao.close()

    try:
        web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Abrindo socket para conexao com servidor web
        web_socket.connect((servidor_web, porta)) #Conectando no IP do dominio e porta 80
        web_socket.send(requisicao) #Enviando requisicao recebida pelo cliente

        while True:
            dado = web_socket.recv(4096) #Recebendo dado do servidor Web
            if Autorizado == 0: #Se o dominio nao estiver nem na Whitelist e nem na Blacklist, procurar pelos Deny_Terms
                for index in range(0,len(Deny_terms)):
                    if Deny_terms[index] in str(dado): #Caso encontre, enviar codigo HTTP 403 no formato HTML, setar flag e escrever no log
                        conexao.send(str.encode('<html><head><link rel="alternate stylesheet" type="text/css" href="resource://gre-resources/plaintext.css" title="Quebrar linhas"></head><body><pre>403 Forbidden</pre></body></html>'))
                        del Data #Se esta nos Deny_Terms, limpar lista de dados. (Nao sera enviado nenhum dado de volta para o cliente)
                        conexao.close()
                        Flag = 1
                        arquivo.write(time.strftime('%d/%m/%Y %H:%M:%S') + ": Acesso Negado - Termo dentro do Deny Terms. URL: " + url + "\n\n")

            if(len(dado) > 0):
                if (Flag != 1): #Se nao entrou em nenhuma das listas, escrever no log
                    arquivo.write(time.strftime('%d/%m/%Y %H:%M:%S') + ": Acesso Realizado. URL: " + url + "\n\n")
                Data.append(dado) #Colocando dado na lista
            
            else:
                length = len(Data) 
                for i in range(0,len(Data)): #Enviando dados da pagina
                    conexao.send(Data[i])
                if i == len(Data)-1: #Quando chegar no ultimo dado, limpar lista de dados e pegar nova requisicao
                    del Data 
                    break

    except: #Caso nao seja possivel abrir o socket
        if web_socket:
            web_socket.close()
        if conexao:
            conexao.close()
        sys.exit(1)

if __name__ == '__main__':
    main()
