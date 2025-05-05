from typing import Optional
import os
import time
import sys
from colorama import Fore, Style, Back, init

init(autoreset=True)


class MenuScreen:
    TITLE_ART = """
╔═══════════════════════════════════════════════════════════════════════════╗
║ ███████╗██╗███╗   ███╗██╗   ██╗██╗      █████╗  ██████╗██████╗  █████╗  ║
║ ██╔════╝██║████╗ ████║██║   ██║██║     ██╔══██╗██╔════╝██╔══██╗██╔══██╗ ║
║ ███████╗██║██╔████╔██║██║   ██║██║     ███████║██║     ██████╔╝███████║ ║
║ ╚════██║██║██║╚██╔╝██║██║   ██║██║     ██╔══██║██║     ██╔══██╗██╔══██║ ║
║ ███████║██║██║ ╚═╝ ██║╚██████╔╝███████╗██║  ██║╚██████╗██║  ██║██║  ██║ ║
║ ╚══════╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ║
╚═══════════════════════════════════════════════════════════════════════════╝"""

    MENU_OPTIONS = [
        (1, "Start Game", Fore.GREEN),
        (2, "View Credits", Fore.CYAN),
        (3, "Exit", Fore.RED)
    ]

    @classmethod
    def show(cls) -> Optional[int]:
        """Display menu and return selection"""
        os.system('cls' if os.name == 'nt' else 'clear')

        # Animate title
        for line in cls.TITLE_ART.split('\n'):
            print(Fore.CYAN + line + Style.RESET_ALL)
            time.sleep(0.05)

        # Show version and tagline
        print(f"\n{Fore.YELLOW}v2.0 - Entropy Awaits{Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'═' * 65}{Style.RESET_ALL}\n")

        # Show menu options
        for num, text, color in cls.MENU_OPTIONS:
            print(f"{color}[{num}] {text}{Style.RESET_ALL}")

        try:
            choice = input(f"\n{Fore.CYAN}Select your fate: {Style.RESET_ALL}")
            return int(choice) if choice.isdigit() else None
        except (ValueError, KeyboardInterrupt):
            return None
