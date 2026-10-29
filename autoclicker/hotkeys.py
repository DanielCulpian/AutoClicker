"""Registro y limpieza centralizados de atajos globales del sistema."""
from __future__ import annotations
import keyboard
from PySide6.QtCore import QObject, Signal

class HotkeyManager(QObject):
    """Convierte combinaciones globales en señales seguras para la interfaz Qt."""
    start_requested = Signal()
    pause_requested = Signal()
    stop_requested = Signal()
    emergency_requested = Signal()
    capture_requested = Signal()
    error_occurred = Signal(str)

    def __init__(self, hotkeys: dict):
        super().__init__()
        self._handles = []
        self._callbacks = {
            "start": self.start_requested.emit,
            "pause": self.pause_requested.emit,
            "stop": self.stop_requested.emit,
            "emergency": self.emergency_requested.emit,
            "capture": self.capture_requested.emit,
        }
        self.register(hotkeys)

    def register(self, hotkeys: dict):
        """Sustituye el conjunto anterior por el conjunto de atajos solicitado."""
        self.clear()
        seen = set()
        try:
            for action, callback in self._callbacks.items():
                key = str(hotkeys.get(action, "")).strip().lower()
                if not key:
                    raise ValueError(f"Falta un atajo para: {action}")
                if key in seen:
                    raise ValueError(f"El atajo '{key}' esta asignado a mas de una accion.")
                seen.add(key)
                handle = keyboard.add_hotkey(key, callback, suppress=False, trigger_on_release=False)
                self._handles.append(handle)
        except Exception as exc:
            self.clear()
            self.error_occurred.emit(f"No se pudieron registrar los atajos: {exc}")

    def clear(self):
        """Desregistra cada combinacion para evitar callbacks duplicados."""
        for handle in self._handles:
            try:
                keyboard.remove_hotkey(handle)
            except Exception:
                pass
        self._handles.clear()

    def shutdown(self):
        self.clear()
