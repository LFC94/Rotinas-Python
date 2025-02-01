
import pandas as pd


def busca():
    tabela = pd.read_json('consulta/APPJOB.json')
    tabela = tabela.reset_index()
    for index, row in tabela.iterrows():
        print(row['name'])
        for item in row['item']:

            method = item['request']['method']
            url = item['request']['url']

            obs = (" \n* "+item['name']+" *") if url != item['name'] else ""

            print(f"{method} => {url} {obs}", end="\n")


busca()
