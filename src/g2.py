
import os
import platform
import subprocess
from datetime import datetime, timedelta
from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.util.conecta import init_connection, run_execute, run_query
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


def scripts():
    conn = init_connection()
    tabela = pd.read_excel('consulta/query.xlsx')
    totalLinhas = 0
    for index, sql in enumerate(tabela['query']):
        print(index)
        cursor = run_execute(conn=conn, query=sql)
        totalLinhas += cursor.rowcount
        print(index, f"resultado {cursor.rowcount}")

    print(f"tatal {totalLinhas}")


def buscar_assesou_como():
    # Converte as strings para datas
    inicio = input("\nInforme o periodo inicial (Y-m-d): ")
    data_inicio = datetime.strptime(inicio, "%Y-%m-%d")
    fim = input("\nInforme o periodo final (Y-m-d): ")
    data_fim = datetime.strptime(fim, "%Y-%m-%d") if fim else data_inicio
    palavra_chave = input("\nInforme o nome procurado: ")

    # Lista para armazenar resultados
    resultados = []
    url_base = "https://g2s.unyleya.com.br/tmp/como_acessou_{data}.csv"
    nome_saida = 'retorno/acessou_como.csv'

    # Loop por todas as datas no intervalo
    data_atual = data_inicio
    while data_atual <= data_fim:
        data_formatada = data_atual.strftime("%Y%m%d")
        url = url_base.replace("{data}", data_formatada)

        try:
            print(f"🔄 Baixando: {url}")
            response = requests.get(url)
            response.raise_for_status()

            df = pd.read_csv(StringIO(response.text),
                             sep=';', on_bad_lines='skip')
            if 'Login/E-mail' in df.columns:
                filtrado = df[df['Login/E-mail'].str.contains(
                    palavra_chave, case=False, na=False)].copy()

                if not filtrado.empty:
                    filtrado['data_csv'] = data_formatada
                    resultados.append(filtrado)
            else:
                print(
                    f"⚠️ Coluna 'Login/E-mail' não encontrada em {data_formatada}")

        except requests.RequestException as e:
            print(f"❌ Erro ao baixar {url}: {e}")
        except Exception as e:
            print(f"❌ Erro ao processar {url}: {e}")

        data_atual += timedelta(days=1)

    if resultados:
        df_resultado = pd.concat(resultados, ignore_index=True)

        # Garante que a pasta existe
        os.makedirs(os.path.dirname(nome_saida), exist_ok=True)

        df_resultado.to_csv(nome_saida, index=False)
        print(f"\n✅ Resultado salvo em: {nome_saida}")

        # Tenta abrir automaticamente o arquivo
        sistema = platform.system()
        try:
            if sistema == 'Windows':
                os.startfile(os.path.abspath(nome_saida))
            elif sistema == 'Darwin':  # macOS
                subprocess.run(['open', nome_saida])
            elif sistema == 'Linux':
                subprocess.run(['xdg-open', nome_saida])
            else:
                print(f"⚠️ Sistema operacional não suportado: {sistema}")
        except Exception as e:
            print(f"❌ Não foi possível abrir o arquivo automaticamente: {e}")
    else:
        print("\n⚠️ Nenhuma linha encontrada contendo a palavra na coluna 'Login/E-mail'.")


def inicio():
    MENU = {
        '1': {'title': 'Encerrar Alunos Sala Perene', 'function': roboEncerrarAlunosSalaPerene},
        '2': {'title': 'Robo Geral', 'function': roboGeral},
        '3': {'title': 'Robo Lista', 'function': roboLista},
        '4': {'title': 'Robo Script', 'function': scripts},
        '5': {'title': 'Acessou como', 'function': buscar_assesou_como}
    }

    menuTelas(MENU)
