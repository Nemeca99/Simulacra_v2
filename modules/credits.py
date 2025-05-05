from dataclasses import dataclass
from typing import List, Final
import os
from colorama import Fore, Style

@dataclass(frozen=True)
class CreditEntry:
    """Credit entry structure"""
    name: str
    role: str
    contribution: str
    color: str = Fore.WHITE

CREDITS: Final[List[CreditEntry]] = [
    CreditEntry(
        "Your Name",
        "Lead Developer",
        "Core Systems",
        Fore.CYAN
    ),
    # Add other team members
]

class CreditsDisplay:
    """Handles credit display and formatting"""
    @staticmethod
    def clear_screen() -> None:
        """Clear terminal screen"""
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def display() -> None:
        """Display formatted credits"""
        CreditsDisplay.clear_screen()
        print(f"{Fore.CYAN}{'=' * 44}")
        print(f"{Fore.WHITE}📜 SIMULACRA CREDITS")
        print(f"{Fore.CYAN}{'=' * 44}{Style.RESET_ALL}")

        for entry in CREDITS:
            print(f"\n{entry.color}{entry.name}{Style.RESET_ALL}")
            print(f"Role: {entry.role}")
            print(f"Contribution: {entry.contribution}")

        print(f"\n{Fore.CYAN}{'=' * 44}{Style.RESET_ALL}")
        input("Press Enter to return...")

def display_credits():
    """Display credits screen"""
    CreditsDisplay.display()
