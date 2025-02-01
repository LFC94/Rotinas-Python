import base64
from codecs import encode

import pandas as pd
import requests
from bs4 import BeautifulSoup

from uteis import menuTelas, validateJSON


def montarUrlUsu(IDDiploma, dip=None):
    payload = ''
    headers = {
        'Authorization': 'Bearer b356efe6c0e9a65c3cd56f51835c5ccbce05b187'
    }
    url = "http://diploma.virtualclass.com.br/api/diploma/set/?EMEC=3876&TipoColacao=1&IDDiploma=" + \
        f"{IDDiploma}"

    if (dip):
        url += dip

    return requests.request("POST", url, headers=headers, data=payload)


def buscaXmlUsu():
    tabela = pd.read_excel('retorno/Busca USU.xlsx')
    for index, id_matricula in enumerate(tabela['id_matricula']):
        st_iddiploma = tabela.loc[index, 'st_iddiploma']
        st_nomecompleto = tabela.loc[index, 'st_nomecompleto']
        if (tabela.loc[index, 'status'] == 'Registrado'):
            response = montarUrlUsu(st_iddiploma, tabela.loc[index, 'url'])
            if validateJSON(response.text):
                print(f"Valido:{id_matricula} - {st_nomecompleto}", end='')
                json = response.json()
                decode = base64.b64decode(json.get('diploma'))
                decoded_string = decode.decode('utf-8')
                numero = decoded_string.count('CN=UNYEAD')
                solange = decoded_string.count('CN=SOLANGE')
                print(f" numero: {numero}, solange: {solange}", end='\n')
                with open(f"retorno/xml/{st_nomecompleto}_{id_matricula}.xml", "wb") as file:
                    file.write(decode)
            else:
                print(f"Invalido: {st_nomecompleto}")


def buscaUsu():
    tabela = pd.read_excel('consulta/consultausu.xlsx')
    json_file = []
    for index, row in tabela.iterrows():
        st_iddiploma = row['st_iddiploma']
        st_nomecompleto = row['st_nomecompleto']
        print(f'{index} Nome:{st_nomecompleto}')
        response = montarUrlUsu(st_iddiploma)
        resposta = {}
        if validateJSON(response.text):
            resposta = {**row, **
                        response.json(), "texo": response.text}
        else:
            resposta = {**row, 'id': 'erro', 'emec': 'erro', 'idstatus': 'erro',
                        'status': 'erro', 'msg': 'erro', 'obs': 'erro', 'url': 'erro', 'host': 'erro', 'local': 'erro', "texo": response.text}
        json_file.append(resposta)

    df = pd.DataFrame(json_file).to_excel("retorno/Busca USU.xlsx")


def roboEncerrarAlunosSalaPerene():
    id = input("\nInforme a sala=>")

    param = 'limit=50'

    if (id):
        param = 'id_saladeaula='+id

    with open('retorno/roboEncerrarAlunos.json', 'a') as arquivo:
        arquivo.write('\nParametro: ' + param)

    url = "https://g2robos.unyleya.com.br/robo/encerrar-alunos-sala-perene?" + param
    print(url)
    response = requests.get(url, timeout=None)
    print("Retorno: " + response.status_code)

    soup = BeautifulSoup(response.text, 'lxml')
    table1 = soup.find('table')

    headers = []
    for i in table1.find_all('th'):
        title = i.text
        headers.append(title)
    mydata = pd.DataFrame(columns=headers)

    # Create a for loop to fill mydata

    for j in table1.find_all('tr'):
        row_data = j.find_all('td')
        row = [i.text for i in row_data]
        length = len(mydata)
        mydata.append = row

    with open('retorno/roboEncerrarAlunos.json', 'a') as arquivo:
        arquivo.write(mydata.join)


def roboLista():
    tabela = pd.read_excel('consulta/robolista.xlsx')

    for index, id in enumerate(tabela['id']):
        print(f"Executando:{index} id({id})")

        url = tabela.loc[index, 'url']
        if (not url):
            print("Url vazia")
            continue

        with open('retorno/robolista.txt', 'a') as arquivo:
            arquivo.write('\nurl: ' + url)

        response = requests.get(url, timeout=None)
        print(f"Retorno: {response.status_code}")

        text = response.text

        with open('retorno/robolista.txt', 'a') as arquivo:
            arquivo.write(
                f"\nRodou:{index} id({id}): {text.replace("<br/>", "\n")}")


def roboGeral():
    url = input("\nInforme a Url do robo=>")

    if (not url):
        print("Url nao informada")
        return

    metodo = int(input("\nInforme o metodo(1: GET ou 2: POST)=>"))

    repete = int(input("\nInforme o numero de repetição=>"))

    # with open('/retorno/roboGeral.txt', 'ab') as arquivo:
    #     arquivo.write('\nurl: ' + url)

    print(url)
    count = 0
    while (repete == -1 or count < repete):
        count += 1
        print(f"Rodou:{count} ")
        if metodo == 1:
            response = requests.get(url, timeout=None)
        else:
            response = requests.post(url, timeout=None)

        print(f"Retorno: {response.status_code}")

        text = response.text

        print(text.replace("<br/>", "\n"))
        # with open('/retorno/roboGeral.txt', 'ab') as arquivo:
        #     arquivo.write(
        #         f"\n\n Rodou:{count} : {text.replace("<br/>", "\n")}")


def inicio():
    MENU = {'1': {'title': 'Buscar Dipllomas USU', 'function': buscaUsu},
            '2': {'title': 'Buscar XML Dipllomas USU', 'function': buscaXmlUsu},
            '4': {'title': 'Encerrar Alunos Sala Perene', 'function': roboEncerrarAlunosSalaPerene},
            '5': {'title': 'Robo Geral', 'function': roboGeral},
            '6': {'title': 'Robo Lista', 'function': roboLista}}

    menuTelas(MENU)
