
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.util.uteis import menuTelas


def roboEncerrarAlunosSalaPerene():
    id = input("\nInforme a sala=>")

    param = 'limit=50'

    if (id):
        param = 'id_saladeaula='+id

    with open('retorno/roboEncerrarAlunos.json', 'a') as arquivo:
        arquivo.write('\nParametro: ' + param)

    url = f"{os.getenv("URL_G2")}/robo/encerrar-alunos-sala-perene?" + param
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
    MENU = {
        '1': {'title': 'Encerrar Alunos Sala Perene', 'function': roboEncerrarAlunosSalaPerene},
        '2': {'title': 'Robo Geral', 'function': roboGeral},
        '3': {'title': 'Robo Lista', 'function': roboLista}}

    menuTelas(MENU)
