import base64
import os

import pandas as pd
import requests

from uteis import menuTelas, validateJSON


def montarUrlUsu(IDDiploma, dip=None):
    payload = ''
    headers = {
        'Authorization': os.getenv("AUTH_USU")
    }
    url = f"{os.getenv("URL_USU")}/api/diploma/set/?EMEC=3876&TipoColacao=1&IDDiploma=" + \
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


def inicio():
    MENU = {'1': {'title': 'Buscar Dipllomas USU', 'function': buscaUsu},
            '2': {'title': 'Buscar XML Dipllomas USU', 'function': buscaXmlUsu}
            }

    menuTelas(MENU)
