
import datetime

import numpy
import pandas as pd

from src.util.conecta import init_connection, run_execute, run_query
from src.util.uteis import menuTelas

keysNotNullComplemetares = ['st_nomeinstituicao',
                            'id_pessoacomdeficiencia', 'id_etnia', 'id_tipoescola']

keysNotNullPessoa = ['id_usuario', 'id_entidade',
                     'dt_cadastro', 'id_situacao', 'bl_ativo', 'bl_alterado']


def inicio():
    MENU = {
        '1': {'title': 'Diferenca Censo Anteriro Atual', 'function': diferencaCensoAnteriorAtua},
        '2': {'title': 'Atualizar Pessoa dados Complemtar', 'function': atualizarPessoaDadosComplementar},
        '3': {'title': 'Atualizar Polo Censo', 'function': atualizarPoloCenso},
        '4': {'title': 'Atualizar Pessoa Censo', 'function': atualizarPessoa},
        '5': {'title': 'Atualizar Forma de Ingresso', 'function': atualizarFormaIngresso},
        '6': {'title': 'Atualizar Deficiencia', 'function': atualizarDeficiencia}
    }

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
                        f"{key}={str(formatarDadoBanco(valor, key, keysNotNullComplemetares))}")
            if len(update) > 0:
                sql = f"UPDATE tb_pessoadadoscomplementares SET {
                    ', '.join(update)} WHERE id_usuario = {id_usuario}"

        else:
            campo = []
            valores = []
            for key, valor in row.items():
                campo.append(key)
                valores.append(str(formatarDadoBanco(
                    valor, key, keysNotNullComplemetares)))
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
    if valor is None or str(valor).strip().lower() in ('nan', 'nat', 'none', ''):
        return ''

    if isinstance(valor, (int, float, numpy.int64, numpy.float64)):
        return f"{int(valor)}"

    if isinstance(valor, (datetime.datetime, datetime.date, pd.Timestamp)):
        return f"{valor.strftime('%Y-%m-%d')}"

    if isinstance(valor, str):
        return f"{valor.strip().replace("'", "").upper()}"

    return f"{valor}"


def formatarDadoBanco(dado, key="", keysNotNull=[]):
    dado = formatarValor(dado)
    if not dado or str(dado).strip() == 'nan' or str(dado).strip() == 'NaT':
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


def atualizarPoloCenso():
    conn = init_connection()
    tabela = pd.read_excel('consulta/CensoPolo.xlsx')

    ids = []
    for index, row in tabela.iterrows():
        ids.append(str(row['id_polo']))
    cursor = run_execute(
        conn=conn,
        query=f"DELETE FROM tb_censopolo WHERE id_polo in ({','.join(ids)})")

    print(f"DELETE tb_censopolo: {cursor.rowcount}")

    for index, row in tabela.iterrows():
        sql = ''
        id_polo = row['id_polo']
        nu_codigopolo = formatarDadoBanco(
            row['nu_codigopolo'], 'nu_codigopolo')

        if not nu_codigopolo or str(nu_codigopolo).strip() == 'null':
            continue

        sql = f"INSERT INTO tb_censopolo (dt_cadastro, bl_ativo, id_entidade, id_censoinstituicao, nu_codigopolo, id_polo) values (getdate(), 1, 352, 1, {
            nu_codigopolo}, {formatarDadoBanco(id_polo, 'id_polo')})"

        print(index, 'nu_codigopolo', nu_codigopolo, 'sql', sql)
        cursor = run_execute(conn=conn, query=sql)
        print(index, 'rowcount', cursor.rowcount, end="\n\n")

    conn.commit()
    conn.close()


def diferencaCensoAnteriorAtua():

    w = ' cm.id_matricula in (371748, 400073, 424466, 424528, 445542, 445878, 445906, 448134, 448170, 469647, 480857, 497267, 514328, 530257, 564064, 564453, 583085, 584242, 590033, 595832, 634011, 635704, 636959, 637082, 638902, 640208, 643663, 643931, 649860, 650355, 653664, 655570, 655607, 656223, 657506, 659596, 664061, 680237, 896104, 970470, 991097, 1017019, 1042779, 1069503, 1089729, 1098099, 1108265, 1128772, 1142706, 1149808, 1150428, 1172680, 1174436, 1176401, 1178736, 1184398, 1185664, 1187108, 1199383, 1214091, 1237952, 1250835, 1261503, 1268979, 1299129, 1304556, 1307384, 1329825, 1349915)'

    conn = init_connection()
    censoAnterior = run_query(
        conn=conn,
        query=f"SELECT ca.* FROM tb_censo_anterior ca join tb_censomatricula cm on ca.id_matricula = cm.id_matricula where {w} ")
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


def atualizarFormaIngresso():
    conn = init_connection()
    tabela = pd.read_excel('consulta/CensoProdFormaIngresso.xlsx')
    ids = []
    for index, row in tabela.iterrows():
        ids.append(str(row['id_matricula']))
    add = []
    for index, row in tabela.iterrows():

        sql = ''
        id_matricula = formatarDadoBanco(
            row['id_matricula'], 'id_matricula')
        id_tiposelecao = formatarDadoBanco(
            row['id_tiposelecao'], 'id_tiposelecao')

        sql = f"UPDATE tb_vendaproduto SET id_tiposelecao = {id_tiposelecao} WHERE id_matricula = {id_matricula}"
        print(index, "id_matricula", id_matricula, 'sql', sql)

        cursor = run_execute(conn=conn, query=sql)
        print(index, "rowcount", cursor.rowcount, sql)
        add.append({"id_usuario": id_matricula,
                   "rowcount": cursor.rowcount, "sql": sql})

        print("", end="\n\n")
    conn.commit()
    conn.close()
    pd.DataFrame(add).to_excel(
        "retorno/atualizarFormaIngresso.xlsx")


def atualizarDeficiencia():
    conn = init_connection()
    tabela = pd.read_excel('consulta/CensoDeficiencia.xlsx')
    ids = []
    for index, row in tabela.iterrows():
        ids.append(str(row['id_usuario']))

    cursor = run_execute(
        conn=conn,
        query=f"DELETE FROM tb_usuariodeficiencia WHERE id_usuario in ({','.join(ids)})")

    print(f"DELETE tb_usuariodeficiencia: {cursor.rowcount}")

    add = []
    for index, row in tabela.iterrows():
        sql = ''
        id_usuario = formatarDadoBanco(
            row['id_usuario'], 'id_usuario')
        id_deficiencia = formatarDadoBanco(
            row['id_deficiencia'], 'id_deficiencia')

        if id_deficiencia and id_deficiencia != 'null':
            sql = f"INSERT INTO tb_usuariodeficiencia (id_usuario, id_deficiencia) values ({id_usuario}, {id_deficiencia})"
            print(index, "id_usuario", id_usuario, 'sql', sql)
            cursor = run_execute(conn=conn, query=sql)
            print(index, "rowcount", cursor.rowcount)
            add.append({"id_usuario": id_usuario,
                        "rowcount": cursor.rowcount, "sql": sql})
            print("", end="\n\n")

    conn.commit()
    conn.close()
    pd.DataFrame(add).to_excel(
        "retorno/atualizarDeficiencia.xlsx")
