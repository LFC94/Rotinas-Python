
from dotenv import load_dotenv

import censo
import g2
import moodle
import relatorio
import usu
import youtube
from uteis import menuTelas

load_dotenv()


def menu():
    MENU = {
        '1': {'title': 'Robos G2', 'function': g2.inicio},
        '2': {'title': 'Moodle', 'function': moodle.inicio},
        '3': {'title': 'Censo', 'function': censo.inicio},
        '4': {'title': 'Youtube', 'function': youtube.inicio},
        '5': {'title': 'Relatorio', 'function': relatorio.inicio},
        '6': {'title': 'Santa Ursula', 'function': usu.inicio},
    }

    menuTelas(MENU)


if __name__ == "__main__":
    menu()
