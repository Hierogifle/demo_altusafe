"""
Display - Affichage console

Module pour afficher dans la console :
- Bannières
- Boîtes de texte
- Listes formatées
- Barres de progression
- Couleurs et formatage
"""

import os
import sys
from typing import List, Optional


class Display:
    """
    Gère l'affichage dans la console
    Format unifié et professionnel
    """
    
    # Couleurs ANSI (si terminal supporte)
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'white': '\033[97m',
    }
    
    # Caractères spéciaux
    CHARS = {
        'corner_tl': '╔',
        'corner_tr': '╗',
        'corner_bl': '╚',
        'corner_br': '╝',
        'line_h': '═',
        'line_v': '║',
        'check': '✅',
        'cross': '❌',
        'arrow': '➡️',
        'warning': '⚠️',
        'info': 'ℹ️',
        'hourglass': '⏳',
        'clock': '⏱️',
    }
    
    @staticmethod
    def clear_screen():
        """Effacer l'écran"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_banner(title: str, subtitle: str = "", width: int = 60):
        """
        Afficher bannière avec titre
        
        Args:
            title (str): Titre principal
            subtitle (str): Sous-titre (optionnel)
            width (int): Largeur (caractères)
        """
        Display.clear_screen()
        print("\n" + "="*width)
        print(f"  {title.center(width-4)}")
        if subtitle:
            print(f"  {subtitle.center(width-4)}")
        print("="*width + "\n")
    
    @staticmethod
    def print_box(text: str, title: str = "", width: int = 60):
        """
        Afficher texte dans une boîte
        
        Args:
            text (str): Texte à afficher
            title (str): Titre optionnel
            width (int): Largeur
        """
        print("\n" + "="*width)
        if title:
            print(f"  {title}")
            print("-"*width)
        print(f"  {text}")
        print("="*width + "\n")
    
    @staticmethod
    def print_section(title: str, width: int = 60):
        """
        Afficher section de titre
        
        Args:
            title (str): Titre section
            width (int): Largeur
        """
        print("\n" + "="*width)
        print(f"  {title}")
        print("="*width + "\n")
    
    @staticmethod
    def print_list(items: List[str], title: str = "", bullet: str = "•"):
        """
        Afficher liste formatée
        
        Args:
            items (list): Items à afficher
            title (str): Titre optionnel
            bullet (str): Caractère bullet
        """
        if title:
            Display.print_section(title)
        
        for item in items:
            print(f"  {bullet} {item}")
        print()
    
    @staticmethod
    def print_table(headers: List[str], rows: List[List[str]], width: int = 60):
        """
        Afficher tableau
        
        Args:
            headers (list): En-têtes colonnes
            rows (list): Lignes de données
            width (int): Largeur totale
        """
        col_width = (width - 4) // len(headers)
        
        # Header
        header_row = " | ".join(h.ljust(col_width) for h in headers)
        print(f"  {header_row}")
        print("  " + "-" * (len(header_row)))
        
        # Rows
        for row in rows:
            row_str = " | ".join(str(cell).ljust(col_width) for cell in row)
            print(f"  {row_str}")
        print()
    
    @staticmethod
    def print_success(message: str):
        """Afficher message succès"""
        print(f"  {Display.CHARS['check']} {message}")
    
    @staticmethod
    def print_error(message: str):
        """Afficher message erreur"""
        print(f"  {Display.CHARS['cross']} {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Afficher message avertissement"""
        print(f"  {Display.CHARS['warning']} {message}")
    
    @staticmethod
    def print_info(message: str):
        """Afficher message info"""
        print(f"  {Display.CHARS['info']} {message}")
    
    @staticmethod
    def print_waiting(message: str):
        """Afficher message attente"""
        print(f"  {Display.CHARS['hourglass']} {message}")
    
    @staticmethod
    def print_progress_bar(current: int, total: int, width: int = 40):
        """
        Afficher barre de progression
        
        Args:
            current (int): Progression courante
            total (int): Total
            width (int): Largeur barre
        
        Exemple:
            >>> Display.print_progress_bar(3, 9)
            Progress: [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 33%
        """
        percent = (current / total) * 100
        filled = int(width * current / total)
        bar = '█' * filled + '░' * (width - filled)
        
        print(f"  Progress: [{bar}] {percent:.0f}% ({current}/{total})")
    
    @staticmethod
    def print_item(item_id: int, question: str, hint: str = ""):
        """
        Afficher item de checklist
        
        Args:
            item_id (int): ID item
            question (str): Question
            hint (str): Indice
        """
        print("\n" + "="*60)
        print(f"  📋 ITEM {item_id}")
        print("="*60)
        print(f"\n  ❓ {question}")
        if hint:
            print(f"  💡 {hint}")
        print()
    
    @staticmethod
    def print_recognition_result(recognized: str, status: str, score: int):
        """
        Afficher résultat reconnaissance
        
        Args:
            recognized (str): Texte reconnu
            status (str): "VALIDÉ" ou "ÉCHOUÉ"
            score (int): Score (%)
        """
        icon = Display.CHARS['check'] if "VALIDÉ" in status else Display.CHARS['cross']
        print("\n" + "="*60)
        print("  📊 RÉSULTAT")
        print("="*60)
        print(f"\n  Reconnu: '{recognized}'")
        print(f"  Score: {score}%")
        print(f"\n  {icon} {status}\n")
        print("="*60 + "\n")
    
    @staticmethod
    def print_summary(valid_count: int, total_count: int, duration: float = None):
        """
        Afficher résumé final
        
        Args:
            valid_count (int): Nombre items validés
            total_count (int): Nombre total items
            duration (float): Durée exécution (optionnel)
        """
        percentage = (valid_count / total_count * 100) if total_count > 0 else 0
        
        print("\n" + "="*60)
        print("  📊 RÉSUMÉ FINAL")
        print("="*60)
        print(f"\n  Items testés: {total_count}")
        print(f"  Items validés: {valid_count}")
        print(f"  Taux de réussite: {percentage:.0f}%")
        if duration:
            print(f"  Durée: {duration:.2f}s")
        print("\n" + "="*60 + "\n")
    
    @staticmethod
    def ask_confirmation(question: str, default=True) -> bool:
        """
        Demander confirmation utilisateur
        
        Args:
            question (str): Question
            default (bool): Réponse par défaut
        
        Returns:
            bool: Réponse utilisateur
        """
        suffix = " [O/n] " if default else " [o/N] "
        response = input(f"  {question}{suffix}").strip().lower()
        
        if response == "":
            return default
        return response in ['o', 'oui', 'yes', 'y']
    
    @staticmethod
    def ask_choice(choices: List[str], question: str = "Choisissez") -> Optional[str]:
        """
        Demander choix parmi plusieurs options
        
        Args:
            choices (list): Liste des choix
            question (str): Question
        
        Returns:
            str: Choix sélectionné ou None
        """
        print(f"\n  {question}\n")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        try:
            response = int(input(f"\n  {Display.CHARS['arrow']} Votre choix (1-{len(choices)}): "))
            if 1 <= response <= len(choices):
                return choices[response - 1]
        except ValueError:
            pass
        
        return None
    
    @staticmethod
    def color_text(text: str, color: str) -> str:
        """
        Colorer texte (si terminal supporte)
        
        Args:
            text (str): Texte à colorer
            color (str): Couleur (red, green, yellow, blue, cyan)
        
        Returns:
            str: Texte coloré
        """
        if color not in Display.COLORS:
            return text
        
        return f"{Display.COLORS[color]}{text}{Display.COLORS['reset']}"


# Exemple d'utilisation
if __name__ == "__main__":
    print("=== Display Tests ===\n")
    
    # Test bannière
    Display.print_banner("CHECKLIST VOCALE", "Test Interface", 60)
    
    # Test messages
    Display.print_success("Configuration chargée")
    Display.print_info("Démarrage reconnaissance")
    Display.print_warning("Volume faible détecté")
    Display.print_error("Modèle non trouvé")
    
    # Test liste
    Display.print_list(
        ["Item 1", "Item 2", "Item 3"],
        "Items Checklist",
        "✓"
    )
    
    # Test barre progression
    Display.print_progress_bar(3, 9)
    
    # Test résultat
    Display.print_recognition_result("marie dupont", "VALIDÉ", 100)
    
    # Test résumé
    Display.print_summary(7, 9, 45.3)
    
    print("✅ Tests terminés")
