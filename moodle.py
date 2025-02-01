import os
import time

import pandas as pd
import requests

from uteis import (extract_between, extract_start, menuTelas, printLoading,
                   validateJSON)


def inicio():
    MENU = {'1': {'title': 'Limpar Moodle', 'function': roboLimparAlunosG2Moodle},
            '2': {'title': 'Remover Usuario Sala', 'function': roboRemoveUsuarioSalaMoodle},
            '3': {'title': 'Regex logMoodle', 'function': gerarlistaRegex},
            '4': {'title': 'Buscar Nota Moodle', 'function': buscarNotaMoodle}
            }

    menuTelas(MENU)


def roboLimparAlunosG2Moodle():
    ids = [
        # {'nome': 'LIC13 - LIBRAS (11)', 'id': '224451'},
    ]
    for index in range(len(ids)):
        id = ids[index]
        with open('retorno/roboLimparAlunos.json', 'a') as arquivo:
            arquivo.write('Nome: ' + id.get('nome'))
        print('Nome:'+id.get('nome'))
        url = f"{os.getenv("URL_G2")}/robo/limpar-alunos-g2-moodle?bl_encerrar=1&id_saladeaula=" + \
            id.get('id')
        response = requests.request("GET", url)
        if validateJSON(response.text):
            print({'err': response.json().get('erro')})
        else:
            print(response.text)
        with open('retorno/roboLimparAlunos.json', 'a') as arquivo:
            arquivo.write(response.text)


def roboRemoveUsuarioSalaMoodle():
    tabela = pd.read_excel('consulta/salaprof.xlsx')
    count = 0
    for index, st_codsistemacurso in enumerate(tabela['st_codsistemacurso']):
        st_saladeaula = tabela.loc[index, 'st_saladeaula']
        count += 1
        print(f'{count} Sala: {st_saladeaula}')

        url = f"{os.getenv("URL_MOODLE")}/webservice/rest/server.php?"
        url += f"wstoken={os.getenv("TOKEN_MOODLE")}"
        # url += "&wsfunction=enrol_manual_enrol_users"
        # url += "&enrolments[0][roleid]=11"
        # url += "&enrolments[0][userid]=54"
        # url += "&enrolments[0][suspend]=1"
        # url += f"&enrolments[0][courseid]={st_codsistemacurso}"

        with open('retorno/roboRemoveUsuarioSalaMoodle.json', 'a') as arquivo:
            arquivo.write(
                f"\nCourseid: {st_codsistemacurso} Sala: {st_saladeaula}"
            )

        payload = {}
        headers = {}

        response = requests.request(
            method="POST", url=url, headers=headers, data=payload)

        print(response)

        with open('retorno/roboRemoveUsuarioSalaMoodle.json', 'a') as arquivo:
            arquivo.write(f" status_code: {response.status_code}")


def gerarlistaRegex():
    file_path = 'consulta/logMoodle.txt'
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    line_count = len(lines)

    BUSCAR = {
        'core_grades_get_grades': [{'start': 'retornarNotaDetalhada', 'end': 'called', }],
        'core_completion_get_activities_completion_status': [{'start': 'retornarDisciplinasAluno', 'end': ',[id_matricula', }],
        'auth_userkey_request_login_url': [{'start': 'requestTokenAcesso', 'end': 'called', }],
        'core_user_get_users_by_field': [{'start': 'retornarUsuarioByUserName', 'end': 'called', }],
        'enrol_manual_enrol_users': [{'start': 'cadastrarPapel', 'end': 'called', }, {'start': 'limparAlunosG2Moodle(', 'end': 'called', }],
        'local_wsunyleya_upload_profileimage': [{'start': 'uploadUserProfileImage', 'end': 'Array', }],
        'core_user_create_users': [{'start': 'cadastrarPapel', 'end': 'called', }],
        'core_user_update_users': [{'start': 'VwPessoaTO Object', 'end': 'st_sexo', }],
        'core_role_unassign_roles': [{'start': 'desvincularPerfil', 'end': 'called', }],

    }

    json_file = []
    result = {}
    wsfunction = None
    line_atua = 0
    porcentagemAnt = 0
    for line in lines:
        line_atua = line_atua + 1
        porcentagem = int(line_atua * 100 / line_count)
        if porcentagem > porcentagemAnt:
            printLoading(porcentagem)
            porcentagemAnt = porcentagem

        testWsfunction = extract_between(line, "wsfunction] => ", "\n")
        if testWsfunction:
            json_file.append(result)
            wsfunction = testWsfunction.strip()
            result = {'datatime': '', 'data': '', 'wsfunction': wsfunction,
                      'request': '', 'text': ''}
            continue

        if wsfunction:
            conttext = 0
            wsfunctions = BUSCAR.get(wsfunction)
            if wsfunctions:
                for row in wsfunctions:
                    text = extract_between(
                        line, row.get('start'), row.get('end'))
                    if text != None and text.strip():
                        if conttext == 0:
                            result.update({'text': text})
                        else:
                            result.update({f'text{conttext}': text})
                        conttext = conttext + 1
                        continue

        text = extract_between(line, ' _POST),[] => ',
                               endForm=r'(?=\?|,|\/id)')
        if text:
            result.update({'request': text})
            continue

        text = extract_start(line, ' | Tempo de exe')
        if text:
            result.update({'datatime': text})
            result.update({'data': text[:8]})
            continue

    print('')
    json_file.append(result)
    pd.DataFrame(json_file).to_excel("retorno/logmoodle.xlsx", index=False)
    print("Gerado o arquivo retorno/logmoodle.xlsx")


def buscarNotaMoodle():
    tabela = pd.read_excel('consulta/salanotamoodle.xlsx')
    retorno = []
    line_count = tabela['st_codsistemacurso'].count()
    line_atua = 0
    porcentagemAnt = 0
    for index, st_codsistemacurso in enumerate(tabela['st_codsistemacurso']):
        id_saladeaula = tabela.loc[index, 'id_saladeaula']
        st_saladeaula = tabela.loc[index, 'st_saladeaula']
        id_saladeaula = tabela.loc[index, 'id_saladeaula']
        line_atua = line_atua + 1
        porcentagem = int(line_atua * 100 / line_count)
        if porcentagem > porcentagemAnt:
            printLoading(porcentagem, f'{line_atua}/{line_count}')
            porcentagemAnt = porcentagem
        st_codsistema = tabela.loc[index, 'st_codsistema']
        url = st_codsistema[:-26]
        url += f'login/grades.php?courseid={st_codsistemacurso}'
        response = requests.request("GET", url)
        for linha in response.text.split('|'):
            res = linha.split('#.#')
            userid = ''
            nota = ''
            if res and len(res) > 1:
                userid = res[0]
                nota = res[1].split('.')
                if nota:
                    nota = nota[0]
            retorno.append({
                'id_saladeaula': id_saladeaula,
                'st_saladeaula': st_saladeaula,
                'st_codsistemacurso': st_codsistemacurso,
                'userid': userid,
                'nota': nota
            })
        pd.DataFrame(retorno).to_excel("retorno/notamoodle.xlsx", index=False)
        time.sleep(0.100)
    print("Gerado o arquivo retorno/notamoodle.xlsx")
