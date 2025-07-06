import json
import os
import re
import sys

from InquirerPy import prompt
from InquirerPy.base.control import Choice
from PySide6.QtWidgets import QApplication, QFileDialog


def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True


def menuTelas(MENU={}):
    print("".center(50, "_"))
    print("MENU CENSO".center(50, "-") + "\n")
    MENU['s'] = {'title': 'Sair'}
    choices = []
    for key, item in MENU.items():
        choices.append(Choice(name=item.get('title', '').upper(), value=key))

    opcao = prompt([{
        "type": "rawlist",
        "choices": choices,
        "message": "Selecionar opção desejada:",
    }])[0]

    if opcao not in MENU.keys():
        print(f"{opcao} Operação inválida")

    if opcao in MENU.keys() and MENU[opcao].get('function', False):
        os.system('cls' if os.name == 'nt' else "printf '\033c'")
        print(MENU.get(opcao).get('title').upper().center(50, "-"))
        MENU[opcao].get('function')()
        print("".center(50, "_"))
        menuTelas(MENU)


def printLoading(porcentagem, mensagem=''):
    print(f"⌛ {porcentagem}% " + "".center(porcentagem, "▪") +
          f" {mensagem}", end='\r')


def formatCPF(cpf):
    try:
        cpf = str(int(cpf))
    except ValueError:
        return ''

    if len(cpf) < 11:
        cpf = cpf.zfill(11)
    return '{}.{}.{}-{}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])


def extract_between(text, start, end='', endForm=''):
    if len(text) > 500:
        text = text[:500]
    # Usando expressão regular para capturar texto entre as duas strings
    pattern = re.compile(re.escape(start) + r'(.*?)' +
                         endForm + re.escape(end))
    # matches = pattern.findall(text)
    match = pattern.search(text)
    return match.group(1) if match else None


def extract_start(text, end):
    try:
        if len(text) > 500:
            text = text[:500]
        # Usando expressão regular para capturar texto entre as duas strings
        pattern = re.compile(r'(.*?)' + re.escape(end))
        # matches = pattern.findall(text)
        match = pattern.search(text)
        return match.group(1).strip() if match else None
    except BufferError as err:
        return None


def openFile():
    app = QApplication(sys.argv)
    file_dialog = QFileDialog()
    return file_dialog.getOpenFileName(
        None, "Selecione um arquivo", "", "Arquivos de Excel (*.xlsx)")

class MyLogger(object):
    def debug(self, msg):
        pass  # ignora debug

    def warning(self, msg):
        pass  # ignora warnings

    def error(self, msg):
        print(msg)  # mostra só erros
