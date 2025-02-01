
import censo
import moodle
import relatorio
import usu
import youtube
from uteis import menuTelas


def menu():
    MENU = {
        '1': {'title': 'Robos', 'function': usu.inicio},
        '2': {'title': 'Moodle', 'function': moodle.inicio},
        '3': {'title': 'Censo', 'function': censo.inicio},
        '4': {'title': 'Youtube', 'function': youtube.inicio},
        '5': {'title': 'Relatorio', 'function': relatorio.inicio}}

    menuTelas(MENU)


if __name__ == "__main__":
    menu()
