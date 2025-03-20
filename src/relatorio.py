

import pandas as pd

from src.util.uteis import formatCPF, menuTelas, openFile


def inicio():
    menu = {
        '1': {'title': 'RELATORIO ENADE', 'function': enade},
        '2': {'title': 'RELATORIO Renovação', 'function': mediaRenovaca},
    }
    menuTelas(menu)


def enade():
    print('Processando ...', end="")
    tabela = pd.read_excel('consulta/consultaenade.xlsx')
    json_file = {}
    for index, row in tabela.iterrows():
        print('.' if index % 2 == 0 else '', end="")
        id_matricula = f"{row.get('id_matricula')}"
        doc = json_file[id_matricula] if id_matricula in json_file else {}
        if id_matricula not in json_file:
            doc = {
                'CPF': formatCPF(row.get('st_cpf')),
                'Nome': row.get('st_nomecompleto'),
                'Matricula': row.get('id_matricula'),
                'Curso': row.get('st_projetopedagogico'),
                'Evolução': row.get('st_evolucaograduacao'),
                # 'Ano de Conclusão Ensino Médio': row.get('st_anoconclusaoensinomedio'),
                'Polo': row.get('st_polo'),
                'Polo Mec': row.get('st_polomec'),
                'Polo Mec': row.get('st_codemec'),
                # 'Email': row.get('st_email'),
                # 'Telefone': row.get('st_telefone'),
                # 'Carga Horária Total do Curso': row.get('st_cargahoraria'),
                # 'Carga Horária Integralizada Pelo Aluno': row.get('st_cargahorariointegralizadapeloaluno'),
                # 'Carga Horária Cursando': row.get('st_cargahorariacursando'),
                # 'Carga Horária à Cursar': row.get('st_cargahorariaacursar'),
                # 'Percentual De Conclusão': row.get('nu_percentualcargahorariaintegralizada'),
                # 'Percentual Enade': row.get('nu_percentualenade'),
                # 'Total Atividade Complementar': row.get('st_horasatividades'),
                # 'Total Horas Aluno Atividade Complementar': row.get('st_cargahorariaatividadealuno'),
                # 'Total De Horas Atividade complementar à Concluir': row.get('st_horasatividadefaltante'),
                # 'Ano da Matricula': row.get('st_anoinicioturma'),
                # 'Renovação': row.get('dt_renovacao'),
                # 'TCC': '',
                # 'TCC Status': '',
                # 'TCC Abertura': '',
                # 'TCC Encerramento': '',
                'Estágio I': '',
                'Estágio I Status': '',
                'Estágio II': '',
                'Estágio II Status': '',
            }

        disciplina = f"{row.get('st_disciplina')}"
        if row.get('id_tipodisciplina') == 4:
            if 'II' in disciplina:
                doc['Estágio II'] = disciplina
                doc['Estágio II Status'] = row.get('st_statusdisciplina')
                doc['Estágio II Abertura'] = row.get('dt_abertura')
                doc['Estágio II Encerramento'] = row.get('dt_encerramento')
            else:
                doc['Estágio I'] = disciplina
                doc['Estágio I Status'] = row.get('st_statusdisciplina')
                doc['Estágio I Abertura'] = row.get('dt_abertura')
                doc['Estágio I Encerramento'] = row.get('dt_encerramento')
        elif row.get('id_tipodisciplina') == 2:
            doc['TCC'] = disciplina
            doc['TCC Status'] = row.get('st_statusdisciplina')
            doc['TCC Abertura'] = row.get('dt_abertura')
            doc['TCC Encerramento'] = row.get('dt_encerramento')
        elif row.get('id_tipodisciplina') == '':
            doc[disciplina] = disciplina

        json_file[id_matricula] = doc

    print("\n Salvando .....")
    pd.DataFrame(json_file.values()).to_excel("retorno/relatorioenade.xlsx")


def mediaRenovaca():

    # file_path, _ = openFile()
    # print(file_path)
    xls = pd.ExcelFile("C:/Users/dev/Downloads/ofer.xlsx")
    df = xls.parse('sheet1')  # Ajuste o nome da aba conforme necessário

    # Contar o número de id_venda únicos
    num_id_venda_unico = df["id_venda"].nunique()

    # Calcular a média de id_venda repetidos
    total_vendas = df["id_venda"].count()
    media_id_venda_repetido = total_vendas / num_id_venda_unico

    # Calcular o percentual de "id_prematriculadisciplina" sendo vazio
    percentual_id_prematricula_vazio = df["id_prematriculadisciplina"].isna(
    ).mean() * 100

    # Converter a coluna de data para datetime
    df["dt_confirmacao"] = pd.to_datetime(df["dt_confirmacao"])

    # Criar a coluna de ano/mês
    df["ano_mes"] = df["dt_confirmacao"].dt.to_period("M")

    # Calcular a média de id_venda única por mês/ano
    media_id_venda_unica_por_mes = df.groupby(
        "ano_mes")["id_venda"].nunique().mean()

    # Contar o número de matrículas únicas
    num_matriculas_unicas = df["id_matricula"].nunique()

    # Identificar o mês com mais vendas únicas
    mes_mais_vendas = df.groupby("ano_mes")["id_venda"].nunique().idxmax()

    # Exibir os resultados
    results = {
        "Numero de id_venda unico": num_id_venda_unico,
        "Media de id_venda repetido": media_id_venda_repetido,
        "Percentual de id_prematriculadisciplina Vazio": percentual_id_prematricula_vazio,
        "Media de id_venda unica por mes/ano": media_id_venda_unica_por_mes,
        "Numero de matriculas unicas": num_matriculas_unicas,
        "Mes com mais vendas unicas": str(mes_mais_vendas)
    }

    for key, item in results.items():
        print(f"{key}: {item}")
