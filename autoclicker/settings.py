"""Carga, valida de forma basica y persiste las preferencias locales de la app."""
from __future__ import annotations
import json
from pathlib import Path
from PySide6.QtCore import QStandardPaths

DEFAULTS = {
    "button": "left",
    "cps": 10.0,
    "language": "en",
    "click_limit_enabled": False,
    "click_limit": 100,
    "delay_seconds": 0,
    "position_mode": "fixed",
    "x": 500,
    "y": 400,
    "theme": "dark",
    "hotkeys": {
        "start": "f6",
        "pause": "f7",
        "stop": "f8",
        "emergency": "ctrl+alt+f9",
        "capture": "f10",
    },
}

def settings_path() -> Path:
    """Resuelve la carpeta de configuracion del usuario segun Qt."""
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    folder = Path(base) / "AutoclickerModerno"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "settings.json"

def default_settings() -> dict:
    """Devuelve una copia profunda de los valores iniciales."""
    return json.loads(json.dumps(DEFAULTS))

def load_settings() -> dict:
    """Carga preferencias guardadas y conserva los valores por defecto ausentes."""
    data = default_settings()
    try:
        saved = json.loads(settings_path().read_text(encoding="utf-8"))
        if isinstance(saved, dict):
            for key, value in saved.items():
                if key == "hotkeys" and isinstance(value, dict):
                    data["hotkeys"].update(value)
                elif key in data:
                    data[key] = value
    except (OSError, json.JSONDecodeError):
        pass
    return data

def save_settings(settings: dict) -> None:
    """Guarda de forma atomica para evitar dejar un JSON incompleto."""
    path = settings_path()
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(settings, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)
