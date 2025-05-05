from typing import List
import time
import sys
from colorama import Fore, Back, Style


class StartScreen:

    @staticmethod
    def show_title() -> None:
        title = """
███████╗██╗███╗   ███╗██╗   ██╗██╗      █████╗  ██████╗██████╗  █████╗
██╔════╝██║████╗ ████║██║   ██║██║     ██╔══██╗██╔════╝██╔══██╗██╔══██╗
███████╗██║██╔████╔██║██║   ██║██║     ███████║██║     ██████╔╝███████║
╚════██║██║██║╚██╔╝██║██║   ██║██║     ██╔══██║██║     ██╔══██╗██╔══██║
███████║██║██║ ╚═╝ ██║╚██████╔╝███████╗██║  ██║╚██████╗██║  ██║██║  ██║
╚══════╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝
"""
        for line in title.split('\n'):
            print(Fore.CYAN + line + Style.RESET_ALL)
            time.sleep(0.1)

        print(f"\n{Fore.YELLOW}Press any key to begin...{Style.RESET_ALL}")
        input()
