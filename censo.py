
import datetime
import os

import pandas as pd

from conecta import init_connection, run_execute, run_query
from uteis import menuTelas

keysNotNullComplemetares = ['st_nomeinstituicao',
                            'id_pessoacomdeficiencia', 'id_etnia', 'id_tipoescola']

keysNotNullPessoa = ['id_usuario', 'id_entidade',
                     'dt_cadastro', 'id_situacao', 'bl_ativo', 'bl_alterado']


def inicio():
    MENU = {
        '1': {'title': 'Atualizar Pessoa dados Complemtar', 'function': atualizarPessoaDadosComplementar},
        '2': {'title': 'Atualizar Polo Censo', 'function': atualizarPoloCensso},
        '3': {'title': 'Atualizar Pessoa Censo', 'function': atualizarPessoa},
        '5': {'title': 'Diferenca Censo Anteriro Atual', 'function': diferencaCensoAnteriorAtua}}

    menuTelas(MENU)


def atualizarPessoaDadosComplementar():
    conn = init_connection()
    tabela = pd.read_excel('consulta/CensoProdComplemetar.xlsx')
    ids = []
    for index, row in tabela.iterrows():
        ids.append(str(row['id_usuario']))

    dadosBanco = run_query(
        conn=conn,
        query=f"SELECT * FROM tb_pessoadadoscomplementares WHERE id_usuario in ({','.join(ids)})")

    add = []
    for index, row in tabela.iterrows():
        update = []
        sql = ''
        id_usuario = row['id_usuario']
        busca = filtrarDadosBanco(
            dadosBanco=dadosBanco, id_usuario=id_usuario, key="id_usuario")

        print(index, "busca:", len(busca) > 0)
        if len(busca) > 0:
            for key, valor in row.items():
                if not compararCampos(valor, busca.get(key)):
                    update.append(
                        f"{key}={str(formatarDadoBanco(valor, key))}")
            if len(update) > 0:
                sql = f"UPDATE tb_pessoadadoscomplementares SET {
                    ', '.join(update)} WHERE id_usuario = {id_usuario}"

        else:
            campo = []
            valores = []
            for key, valor in row.items():
                campo.append(key)
                valores.append(str(formatarDadoBanco(valor, key)))
            sql = f"INSERT INTO tb_pessoadadoscomplementares ({', '.join(campo)}) values ({
                ', '.join(valores)})"

        if sql:
            print(index, "update: ", len(update) > 0, sql)
            run_execute(conn=conn, query=sql)
        add.append({"id_usuario": id_usuario, "busca:": len(busca) > 0,
                    "update: ": len(update) > 0, "sql": sql})

        print("", end="\n\n")
    conn.commit()
    conn.close()
    pd.DataFrame(add).to_excel(
        "retorno/atualizarPessoaDadosComplementar.xlsx")


def formatarValor(valor):
    if not valor or str(valor).strip() == 'nan':
        return ''

    if str(valor).isdigit() or type(valor) in [int, float]:
        return int(valor)

    if type(valor) is str:
        return valor.strip().replace("'", "").upper()

    return valor


def formatarDadoBanco(dado, key="", keysNotNull=keysNotNullComplemetares):
    dado = formatarValor(dado)
    if not dado or str(dado).strip() == 'nan':
        return 'null' if key not in keysNotNull else "''"

    if not type(dado) is str:
        return f"'{str(dado)}'"

    return f"'{dado}'"


def compararCampos(campo1, campo2):
    return formatarValor(campo1) == formatarValor(campo2)


def filtrarDadosBanco(dadosBanco, id_usuario, key='id_usuario'):
    for dados in dadosBanco:
        if dados.get(key) == id_usuario:
            return dados

    return []


def atualizarPoloCensso():
    conn = init_connection()
    tabela = pd.read_excel('consulta/CensoPolo.xlsx')

    for index, row in tabela.iterrows():
        update = []
        sql = ''
        id_polo = row['id_polo']
        id_censopolo = row['id_censopolo']
        nu_codigopolo = row['nu_codigopolo']
        nu_polo = formatarDadoBanco(row['nu_polo'], 'nu_codigopolo')
        print(index)

        if (not id_censopolo or str(id_censopolo).strip() == 'nan') and nu_polo and nu_polo != 'null':
            sql = f"INSERT INTO tb_censopolo (dt_cadastro, bl_ativo, id_entidade, id_censoinstituicao, nu_codigopolo, id_polo) values (getdate(), 1, 352, 1, {
                nu_polo}, {formatarDadoBanco(id_polo, 'id_polo')})"

        if id_censopolo and str(id_censopolo).strip() != 'nan':
            sql = "UPDATE tb_censopolo SET"
            if nu_polo and nu_polo != 'null':
                sql = f"{sql} nu_codigopolo = {nu_polo}, bl_ativo=1 "
            else:
                sql = f"{sql} bl_ativo=0"

            sql = f"{sql} where id_censopolo = {
                formatarDadoBanco(id_censopolo, 'id_censopolo')}"

        if sql:
            print(index, "update: ", len(update) >
                  0, sql, nu_polo, nu_codigopolo)
            run_execute(conn=conn, query=sql)

        print("", end="\n\n")

    conn.commit()
    conn.close()


def diferencaCensoAnteriorAtua():

    conn = init_connection()
    censoAnterior = run_query(
        conn=conn,
        query=f"SELECT * FROM tb_censo_anterior")
    print(f"censoAnterior: {len(censoAnterior)}")
    ids = []
    for row in censoAnterior:
        ids.append(str(row.get('id_matricula')))

    censoAtual = run_query(
        conn=conn,
        query=f"SELECT distinct * FROM vw_censo WHERE id_matricula in ({", ".join(ids)})")
    print(f"vw_censo: {len(censoAtual)}")
    diferenca = []
    for row in censoAnterior:
        censo = filtrarDadosBanco(
            censoAtual, row.get('id_matricula'), 'id_matricula')

        for index, value in row.items():
            if not compararCampos(value, censo.get(index)):
                diferenca.append({
                    "id_matricula": row.get('id_matricula'),
                    "campo": index,
                    "anterior": value,
                    "atual": censo.get(index)
                })
    conn.commit()
    conn.close()
    print(f"diferenca: {len(diferenca)}")
    df = pd.DataFrame(diferenca).to_excel("retorno/Diferenca censo.xlsx")


def atualizarPessoa():
    conn = init_connection()
    tabela = pd.read_excel('consulta/CensoPessoa.xlsx')
    ids = []
    for index, row in tabela.iterrows():
        ids.append(str(row['id_usuario']))

    dadosBanco = run_query(
        conn=conn,
        query=f"SELECT * FROM tb_pessoa WHERE id_usuario in ({','.join(ids)}) and id_entidade = 352")

    add = []
    for index, row in tabela.iterrows():
        update = []
        sql = ''
        id_usuario = row['id_usuario']
        busca = filtrarDadosBanco(
            dadosBanco=dadosBanco, id_usuario=id_usuario, key="id_usuario")

        print(index, "busca:", len(busca) > 0)
        if len(busca) > 0:
            for key, valor in row.items():
                if not compararCampos(valor, busca.get(key)):
                    update.append(
                        f"{key}={str(formatarDadoBanco(dado=valor, key=key, keysNotNull=keysNotNullPessoa))}")
            if len(update) > 0:
                sql = f"UPDATE tb_pessoa SET {
                    ', '.join(update)} WHERE id_usuario = {id_usuario}"

        else:
            campo = []
            valores = []
            for key, valor in row.items():
                campo.append(key)
                valores.append(str(formatarDadoBanco(
                    valor, key, keysNotNull=keysNotNullPessoa)))
            sql = f"INSERT INTO tb_pessoa ({', '.join(campo)}) values ({
                ', '.join(valores)})"

        if sql:
            print(index, "update: ", len(update) > 0, sql)
            run_execute(conn=conn, query=sql)
        add.append({"id_usuario": id_usuario, "busca:": len(busca) > 0,
                    "update: ": len(update) > 0, "sql": sql})

        print("", end="\n\n")
    conn.commit()
    conn.close()
    pd.DataFrame(add).to_excel(
        "retorno/atualizarPessoa.xlsx")
