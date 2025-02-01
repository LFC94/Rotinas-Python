import pandas as pd
import requests

headers = {
    'Authorization': 'Bearer aW50ZWdyYWNhby51bnlsZXlhQGFsdW5vZGlnaXRhbC5jb20uYnI6SDQ3S3A5N2Zz'
}

payload = {
    'Acao':  'CONSULTARDIPLOMA',
    'Cliente': '3743464537484677536a733d',
    'AluRA':  'id_matricul',
    'AluCPF':  'st_cpf',
    'IDDiploma':  'st_iddiploma'
}

url = "https://unyleya.alunodigital.com.br/API_105/ConsultarDiploma"
tabela = pd.read_excel('consulta/consulta.xlsx')


json_file = []

for index, id_matricula in enumerate(tabela['id_matricula']):

    payload['AluRA'] = f"{id_matricula}"
    payload['AluCPF'] = f"{tabela.loc[index, 'st_cpf']}"
    payload['IDDiploma'] = f"{tabela.loc[index, 'st_iddiploma']}"
    print(f"Indice: {index} Nome: {tabela.loc[index, 'st_nomecompleto']}")

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        retorno = response.json()
        if retorno.get('UrlXMLDiploma'):
            # download = requests.get(retorno.get('UrlXMLDiploma'))
            # if download.status_code == 200:
            #     numero = download.text.count('CN=UNYEAD')
            #     solange = download.text.count('CN=SOLANGE')
            #     json_file.append(
            #         {**payload, **retorno, 'unyead': numero, 'solange': solange, 'erro': ''})
            # else:
            json_file.append(
                {**payload,  **retorno, 'erro': ''})
        else:
            json_file.append({**payload,  **retorno, 'erro': 'nao finalidado'})
    else:
        print(f"Erro: {response.text}")
        json_file.append({**payload, 'erro': response.text})

df = pd.DataFrame(json_file).to_excel("Busca Cloddosc.xlsx")
