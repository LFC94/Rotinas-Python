
import os
from datetime import datetime

import pandas as pd

from src.util.conecta import init_connection, run_query
from src.util.uteis import (limpar_caracteres_especiais, limpar_cpf, menuTelas,
                            openFile, salvar_em_xlsx)


def inicio():
    menu = {
        '1': {'title': 'Compara Consultas', 'function': comparar_consulta},
        '2': {'title': 'Busca Alunos Matricula Lote', 'function': buscaAlunosLote},
    }
    menuTelas(menu)


def compare(df_a, df_b, idx_a, idx_b):
    print(f"🔛 {idx_a} com {idx_b} -> {datetime.now().strftime('%H%M%S')}")
    # 1. Normaliza os DataFrames para garantir comparação correta
    fullcolunm = [
        chave
        for obj in df_a
        for chave in obj.keys()
        if chave.startswith(("id_", "nu_"))
    ]

    def normalize_df(lista_de_objetos):
        for obj in lista_de_objetos:
            valorfull = []
            for colun in fullcolunm:
                valorfull.append(obj[colun])
            obj['full'] = "_".join(map(str, valorfull))
            obj['mat_ent'] = f"{obj['id_matricula']}_{obj['id_entidade']}_{obj['id_saladeaula']}"
            obj['sal_ent'] = f"{obj['id_entidade']}_{obj['id_saladeaula']}"

        return lista_de_objetos

    grupo1 = normalize_df(df_a)
    grupo2 = normalize_df(df_b)

    # Conjuntos com os valores "concatenado"
    mat_ent1 = set(obj['mat_ent'] for obj in grupo1)
    sal_ent1 = set(obj['sal_ent'] for obj in grupo1)
    full1 = set(obj['full'] for obj in grupo1)
    mat_ent2 = set(obj['mat_ent'] for obj in grupo2)
    sal_ent2 = set(obj['sal_ent'] for obj in grupo2)
    full2 = set(obj['full'] for obj in grupo2)

    # Diferenças
    retgrupo1 = []
    for obj in grupo1:
        obj[f'bl_mat_ent_{idx_b}'] = obj['mat_ent'] in mat_ent2
        obj[f'bl_sal_ent_{idx_b}'] = obj['sal_ent'] in sal_ent2
        obj[f'bl_full_{idx_b}'] = obj['full'] in full2
        retgrupo1.append(obj)

    retgrupo2 = []
    for obj in grupo2:
        obj[f'bl_mat_ent{idx_a}'] = obj['mat_ent'] in mat_ent1
        obj[f'bl_sal_ent{idx_a}'] = obj['sal_ent'] in sal_ent1
        obj[f'bl_full_{idx_a}'] = obj['full'] in full1
        retgrupo2.append(obj)

    return retgrupo1, retgrupo2


def load_queries_from_files(query_files):
    queries = {}
    for file in query_files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                query = f.read().strip()
                basename_with_extension = os.path.basename(file)
                filename_without_extension, _ = os.path.splitext(
                    basename_with_extension)
                queries[filename_without_extension] = query
        else:
            print(f"Arquivo {file} não encontrado.")
    return queries


def comparar_consulta():
    print(f"Inicio {datetime.now().strftime('%H%M%S')}")

    query_files = [
        'consulta/consulta1.sql',
        'consulta/consulta2.sql',
        'consulta/consulta3.sql',
        'consulta/consulta4.sql',
        'consulta/nova.sql',
    ]

    queries = load_queries_from_files(query_files)

    if not queries:
        print("Nenhuma consulta foi carregada. Verifique os arquivos de consulta.")
        return

    pool = init_connection()
    querys = {key: run_query(pool, value, key=key)
              for key, value in queries.items()}
    results = []
    keys = []
    for key, value in querys.items():
        results.append(value)
        keys.append(key)

    # Comparações em pares
    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            results[i], results[j] = compare(
                results[i], results[j], keys[i], keys[j])

    datetime_string = datetime.now().strftime("%M%S")

    for i in range(len(results)):
        salvar_em_xlsx(results[i], f"df_{keys[i]}_{datetime_string}")

    pool.close()
    exit()


def buscaAlunosLote():
    caminho_arquivo, _ = openFile()
    if (not caminho_arquivo):
        return

    abas = pd.read_excel(caminho_arquivo, sheet_name=None, dtype=str)

    resultado = {}

    for nome_aba, df in abas.items():
        colunas_norm = {limpar_caracteres_especiais(col.lower().replace(
            " ", "")): col for col in df.columns}
        if "cpf" in colunas_norm:
            coluna_cpf = colunas_norm["cpf"]

            cpfs = df[coluna_cpf].map(limpar_cpf).dropna().tolist()

            resultado[nome_aba] = cpfs

    conn = init_connection()
    for aba, cpf in resultado.items():
        query = f"SELECT DISTINCT st_cpf 'st_cpf', dt_nascimento 'dt_nascimento', st_nomecompleto 'st_nomecompleto', st_sexo 'st_sexo', st_nomemae 'st_nomemae', st_nomepai 'st_nomepai', st_rg 'st_rg', st_orgaoexpeditor 'st_orgaoexpeditor', dt_dataexpedicao 'dt_dataexpedicao', st_cep 'st_cep', st_endereco 'st_endereco', nu_numero 'nu_numero', st_bairro 'st_bairro', st_complemento 'st_complemento', sg_uf 'sg_uf', st_nomemunicipio 'st_municipio', 55 'nu_ddi_residencial', p.nu_ddd 'nu_ddd_residencial', nu_telefone 'nu_telefone_residencial', 55 'nu_ddi_celular', p.nu_ddd 'nu_ddd_celular', nu_telefonealternativo 'nu_telefone_celular', st_email 'st_email' FROM vw_pessoa p WHERE id_entidade = 352 and st_cpf in ('{"', '".join(cpf)}')"
        dados = run_query(conn=conn, query=query, key=aba)
        salvar_em_xlsx(dados=dados, name=aba)
