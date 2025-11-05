"""
Logger - Logging de l'application

Module pour gérer les logs :
- Logging console
- Logging fichier
- Niveaux (DEBUG, INFO, WARNING, ERROR)
- Format standardisé
"""

import logging
import os
from pathlib import Path
from datetime import datetime


class Logger:
    """
    Gère le logging de l'application
    Console + fichier avec rotation
    """
    
    _loggers = {}  # Cache des loggers créés
    
    # Répertoire logs
    LOGS_DIR = "logs"
    
    @staticmethod
    def _ensure_logs_dir():
        """Créer dossier logs s'il n'existe pas"""
        logs_path = Path(__file__).parent.parent.parent / Logger.LOGS_DIR
        logs_path.mkdir(exist_ok=True)
        return logs_path
    
    @staticmethod
    def get_logger(name, level=logging.INFO, to_file=True):
        """
        Récupérer logger
        
        Args:
            name (str): Nom du logger (ex: "core.recognizer")
            level (int): Niveau logging (DEBUG, INFO, WARNING, ERROR)
            to_file (bool): Écrire aussi en fichier ?
        
        Returns:
            logging.Logger: Logger configuré
        
        Exemple:
            >>> logger = Logger.get_logger("core.recognizer")
            >>> logger.info("Message")
        """
        # Retourner logger existant si déjà créé
        if name in Logger._loggers:
            return Logger._loggers[name]
        
        # Créer nouveau logger
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Format standard
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Handler fichier (optionnel)
        if to_file:
            try:
                logs_path = Logger._ensure_logs_dir()
                log_file = logs_path / f"{name.replace('.', '_')}.log"
                
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception as e:
                logger.warning(f"Impossible créer log fichier : {e}")
        
        # Cacher logger
        Logger._loggers[name] = logger
        
        return logger
    
    @staticmethod
    def debug(message, logger_name="app"):
        """Log DEBUG"""
        logger = Logger.get_logger(logger_name)
        logger.debug(message)
    
    @staticmethod
    def info(message, logger_name="app"):
        """Log INFO"""
        logger = Logger.get_logger(logger_name)
        logger.info(message)
    
    @staticmethod
    def warning(message, logger_name="app"):
        """Log WARNING"""
        logger = Logger.get_logger(logger_name)
        logger.warning(message)
    
    @staticmethod
    def error(message, logger_name="app"):
        """Log ERROR"""
        logger = Logger.get_logger(logger_name)
        logger.error(message)
    
    @staticmethod
    def critical(message, logger_name="app"):
        """Log CRITICAL"""
        logger = Logger.get_logger(logger_name)
        logger.critical(message)
    
    @staticmethod
    def log_section(title, logger_name="app"):
        """
        Log une section (titre avec séparation)
        
        Exemple:
            >>> Logger.log_section("DÉMARRAGE CHECKLIST")
            # → "============ DÉMARRAGE CHECKLIST ============"
        """
        logger = Logger.get_logger(logger_name)
        separator = "=" * (len(title) + 4)
        logger.info(separator)
        logger.info(f"  {title}")
        logger.info(separator)
    
    @staticmethod
    def log_execution(func_name, status, duration=None):
        """
        Log exécution d'une fonction
        
        Args:
            func_name (str): Nom fonction
            status (str): "start", "end", "error"
            duration (float): Durée exécution (optionnel)
        
        Exemple:
            >>> Logger.log_execution("run_checklist", "start")
            >>> # ... exécution ...
            >>> Logger.log_execution("run_checklist", "end", 12.5)
        """
        logger = Logger.get_logger("app.execution")
        
        if status == "start":
            logger.info(f"▶️  Démarrage {func_name}")
        elif status == "end":
            duration_str = f" - {duration:.2f}s" if duration else ""
            logger.info(f"✅ Fin {func_name}{duration_str}")
        elif status == "error":
            duration_str = f" - {duration:.2f}s" if duration else ""
            logger.error(f"❌ Erreur {func_name}{duration_str}")
    
    @staticmethod
    def log_validation(item_id, recognized, status, score):
        """
        Log résultat validation
        
        Args:
            item_id (int): ID item
            recognized (str): Texte reconnu
            status (str): "VALIDÉ" ou "ÉCHOUÉ"
            score (int): Score (%)
        """
        logger = Logger.get_logger("app.validation")
        icon = "✅" if "VALIDÉ" in status else "❌"
        logger.info(f"{icon} Item {item_id}: '{recognized}' - {status} ({score}%)")
    
    @staticmethod
    def clear_old_logs(days=7):
        """
        Supprimer logs plus anciens que X jours
        
        Args:
            days (int): Nombre de jours de rétention
        """
        try:
            logs_path = Logger._ensure_logs_dir()
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            
            for log_file in logs_path.glob("*.log"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    Logger.info(f"Supprimé ancien log : {log_file.name}")
        
        except Exception as e:
            Logger.warning(f"Erreur suppression logs : {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    print("=== Logger Tests ===\n")
    
    # Créer loggers
    logger_app = Logger.get_logger("app")
    logger_core = Logger.get_logger("core.recognizer")
    logger_validation = Logger.get_logger("validation")
    
    # Test messages
    print("Messages test :\n")
    
    Logger.log_section("DÉMARRAGE APPLICATION")
    
    logger_app.info("Application démarrée")
    logger_app.debug("Message debug")
    logger_app.warning("Message avertissement")
    
    Logger.log_execution("load_config", "start")
    Logger.log_execution("load_config", "end", 0.5)
    
    Logger.log_validation(1, "marie dupont", "VALIDÉ", 100)
    Logger.log_validation(6, "aucun concept", "ÉCHOUÉ", 0)
    
    print("\n✅ Tests terminés")
