from __future__ import annotations
import time
import threading
import pyautogui
from PySide6.QtCore import QThread, Signal

# Mantiene los clics sin una pausa artificial añadida por PyAutoGUI.
pyautogui.PAUSE = 0

class ClickEngine(QThread):
    """Ejecuta los clics en un hilo separado para no bloquear la interfaz.

    La velocidad se consulta entre clics, de modo que los cambios realizados
    durante una pausa se aplican al reanudar sin recrear el motor.
    """
    status_changed = Signal(str)
    count_changed = Signal(int)
    elapsed_changed = Signal(float)
    finished_reason = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, config: dict):
        super().__init__()
        self.config = dict(config)
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._stop_event = threading.Event()
        self._started_at = 0.0
        self._count = 0
        self._paused_total = 0.0
        self._pause_started = None
        self._config_lock = threading.Lock()

    @property
    def is_paused(self) -> bool:
        return not self._pause_event.is_set()

    @property
    def count(self) -> int:
        return self._count

    def elapsed_seconds(self) -> float:
        if not self._started_at:
            return 0.0
        end = self._pause_started if self._pause_started is not None else time.monotonic()
        return max(0.0, end - self._started_at - self._paused_total)

    def pause(self):
        if self._pause_event.is_set():
            self._pause_started = time.monotonic()
            self._pause_event.clear()
            self.status_changed.emit("En pausa")

    def resume(self):
        if not self._pause_event.is_set():
            if self._pause_started is not None:
                self._paused_total += time.monotonic() - self._pause_started
                self._pause_started = None
            self._pause_event.set()
            self.status_changed.emit("Ejecutando")

    def update_speed(self, cps: float):
        """Actualiza la velocidad de forma segura mientras el motor esta pausado."""
        with self._config_lock:
            self.config["cps"] = max(0.1, min(100.0, float(cps)))

    def stop(self):
        self._stop_event.set()
        self._pause_event.set()

    def _wait_interruptibly(self, seconds: float) -> bool:
        """Espera en pequeños tramos para responder a pausa o detencion."""
        remaining = max(0.0, seconds)
        while remaining > 0:
            if self._stop_event.is_set():
                return False
            if not self._pause_event.is_set():
                pause_at = time.monotonic()
                self._pause_event.wait()
                if self._stop_event.is_set():
                    return False
                # Al reanudar, comienza de nuevo el intervalo para evitar rafagas.
                remaining = max(0.0, seconds)
                continue
            step = min(0.02, remaining)
            before = time.monotonic()
            time.sleep(step)
            if self._pause_event.is_set():
                remaining -= max(0.0, time.monotonic() - before)
        return not self._stop_event.is_set()

    def _wait_click_interval(self) -> bool:
        """Espera entre clics y recalcula la velocidad tras cada pausa."""
        while not self._stop_event.is_set():
            # Si el usuario pausa, el nuevo CPS se leera al reanudar.
            if not self._pause_event.is_set():
                self._pause_event.wait()
                continue
            with self._config_lock:
                cps = max(0.1, min(100.0, float(self.config.get("cps", 10.0))))
            deadline = time.monotonic() + (1.0 / cps)
            while time.monotonic() < deadline:
                if self._stop_event.is_set():
                    return False
                if not self._pause_event.is_set():
                    # Descarta el intervalo anterior: al reanudar se calcula uno nuevo.
                    break
                time.sleep(min(0.02, max(0.0, deadline - time.monotonic())))
            else:
                return True
        return False

    def run(self):
        """Bucle principal: hace clic, actualiza estadisticas y verifica limites."""
        reason = "Detenido"
        try:
            delay = max(0.0, float(self.config.get("delay_seconds", 0)))
            if delay:
                self.status_changed.emit(f"Retardo inicial: {delay:g} s")
                if not self._wait_interruptibly(delay):
                    self.finished_reason.emit("Detenido antes de empezar")
                    return

            self._started_at = time.monotonic()
            self.status_changed.emit("Ejecutando")
            limited = bool(self.config.get("click_limit_enabled", False))
            limit = max(1, int(self.config.get("click_limit", 100)))
            button = self.config.get("button", "left")
            fixed = self.config.get("position_mode", "fixed") == "fixed"
            x, y = int(self.config.get("x", 500)), int(self.config.get("y", 400))

            while not self._stop_event.is_set():
                self._pause_event.wait()
                if self._stop_event.is_set():
                    break
                if fixed:
                    pyautogui.click(x=x, y=y, button=button)
                else:
                    pyautogui.click(button=button)
                self._count += 1
                self.count_changed.emit(self._count)
                self.elapsed_changed.emit(self.elapsed_seconds())

                if limited and self._count >= limit:
                    reason = "Limite de clics alcanzado"
                    break
                if not self._wait_click_interval():
                    break
            if self._stop_event.is_set():
                reason = "Detenido"
        except pyautogui.FailSafeException:
            reason = "Parada de seguridad de PyAutoGUI"
        except Exception as exc:
            reason = "Error"
            self.error_occurred.emit(f"{type(exc).__name__}: {exc}")
        finally:
            self.finished_reason.emit(reason)
