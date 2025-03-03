import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Retorna la ruta absoluta del archivo en modo
    ejecutable (.exe) o en desarrollo con Python.
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # PyInstaller
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
