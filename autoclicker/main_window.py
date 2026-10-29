from __future__ import annotations
import time
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QComboBox, QDoubleSpinBox, QSpinBox, QCheckBox, QGroupBox,
    QRadioButton, QButtonGroup, QMessageBox, QFormLayout, QLineEdit, QScrollArea
)
from PySide6.QtGui import QCloseEvent
from .click_engine import ClickEngine
from .hotkeys import HotkeyManager
from .settings import DEFAULTS, default_settings, load_settings, save_settings

DARK_QSS = '''
QWidget { background: #171a21; color: #edf0f7; font-size: 10pt; }
QGroupBox { border: 1px solid #353b49; border-radius: 10px; margin-top: 10px; padding: 12px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }
QPushButton { background: #303747; border: 0; border-radius: 7px; padding: 9px 14px; }
QPushButton:hover { background: #414b60; }
QPushButton:disabled { color: #7d8492; background: #252a34; }
QPushButton#danger { background: #b83e4b; color: white; font-weight: 700; }
QPushButton#primary { background: #4778e6; color: white; font-weight: 700; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { background: #222733; border: 1px solid #3b4352; border-radius: 6px; padding: 6px; }
QSpinBox::up-button, QDoubleSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 20px; border-left: 1px solid #3b4352; }
QSpinBox::down-button, QDoubleSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 20px; border-left: 1px solid #3b4352; }
QLabel#bigCount { font-size: 27pt; font-weight: 700; }
QRadioButton { spacing: 9px; padding: 9px; border: 1px solid #3b4352; border-radius: 7px; }
QRadioButton:checked { background: #263b60; border: 2px solid #80aaff; color: #ffffff; font-weight: 700; }
QRadioButton::indicator { width: 18px; height: 18px; border-radius: 10px; border: 2px solid #9aa6bb; background: #171a21; }
QRadioButton::indicator:checked { background: #6d9cff; border: 3px solid #d9e6ff; }
'''
LIGHT_QSS = '''
QWidget { background: #f5f7fb; color: #202635; font-size: 10pt; }
QGroupBox { border: 1px solid #d7dce6; border-radius: 10px; margin-top: 10px; padding: 12px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }
QPushButton { background: #e5eaf3; border: 0; border-radius: 7px; padding: 9px 14px; }
QPushButton:hover { background: #d7dfed; }
QPushButton:disabled { color: #8b91a0; background: #eceff5; }
QPushButton#danger { background: #b83242; color: white; font-weight: 700; }
QPushButton#primary { background: #3267d5; color: white; font-weight: 700; }
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox { background: white; border: 1px solid #cbd2df; border-radius: 6px; padding: 6px; }
QSpinBox::up-button, QDoubleSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 20px; border-left: 1px solid #cbd2df; }
QSpinBox::down-button, QDoubleSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 20px; border-left: 1px solid #cbd2df; }
QLabel#bigCount { font-size: 27pt; font-weight: 700; }
QRadioButton { spacing: 9px; padding: 9px; border: 1px solid #aebbd0; border-radius: 7px; background: #ffffff; }
QRadioButton:checked { background: #dce8ff; border: 2px solid #245ecb; color: #173b80; font-weight: 700; }
QRadioButton::indicator { width: 18px; height: 18px; border-radius: 10px; border: 2px solid #66748a; background: #ffffff; }
QRadioButton::indicator:checked { background: #245ecb; border: 3px solid #ffffff; }
QCheckBox { spacing: 8px; padding: 5px; }
QCheckBox::indicator { width: 18px; height: 18px; border: 2px solid #66748a; border-radius: 4px; background: #ffffff; }
QCheckBox::indicator:checked { background: #245ecb; border: 2px solid #245ecb; }
'''


# Traducciones de la interfaz. Se mantienen en un único lugar para facilitar futuras mejoras.
TRANSLATIONS = {
    "Autoclicker": "Autoclicker", "Creado por Daniel Culpian ↗": "Created by Daniel Culpian ↗",
    "Tema": "Theme", "Oscuro": "Dark", "Claro": "Light", "Idioma": "Language",
    "Estado de la aplicación": "Application status", "Listo": "Ready",
    "Estadísticas de ejecución": "Run statistics", "Clics realizados": "Clicks performed",
    "Tiempo activo": "Active time", "CPS medio": "Average CPS", "Motor de clics": "Click engine",
    "Botón del ratón": "Mouse button", "Izquierdo": "Left", "Derecho": "Right", "Central": "Middle",
    "Velocidad (clics por segundo)": "Speed (clicks per second)", "Limitar cantidad de clics": "Limit number of clicks",
    "Retardo inicial": "Initial delay", "Posición del clic": "Click position",
    "Posición fija (coordenadas)": "Fixed position (coordinates)", "Seguir posición actual del cursor": "Follow current cursor position",
    "Capturar en 3 s": "Capture in 3 s", "Mantenimiento": "Maintenance",
    "Reiniciar contador y estadísticas": "Reset counter and statistics", "Restablecer valores predeterminados": "Restore defaults",
    "Atajos globales": "Global hotkeys", "Iniciar / reanudar": "Start / resume", "Pausar": "Pause",
    "Detener": "Stop", "Parada de emergencia": "Emergency stop", "Capturar coordenadas": "Capture coordinates",
    "p. ej. f6 o ctrl+alt+f9": "e.g. f6 or ctrl+alt+f9", "Aplicar atajos": "Apply hotkeys",
    "La emergencia es global: funciona aunque la ventana no esté enfocada.": "Emergency stop is global and works even when the window is not focused.",
    "Preparado": "Ready", "⚠  PARADA DE EMERGENCIA  ·  Ctrl+Alt+F9": "⚠  EMERGENCY STOP  ·  Ctrl+Alt+F9",
    "⚠  PARADA DE EMERGENCIA  ·  CTRL+ALT+F9": "⚠  EMERGENCY STOP  ·  CTRL+ALT+F9",
    "En pausa": "Paused", "Ejecutando": "Running", "Detenido": "Stopped",
    "Límite de clics alcanzado": "Click limit reached", "Detenido antes de empezar": "Stopped before starting",
    "Parada de seguridad de PyAutoGUI": "PyAutoGUI safety stop", "Error": "Error",
    "Retardo inicial: ": "Initial delay: ", "Posición capturada: X=": "Position captured: X=",
    "Deteniendo…": "Stopping…", "PARADA DE EMERGENCIA solicitada": "EMERGENCY STOP requested",
    "Contador y estadísticas reiniciados. La configuración se conserva.": "Counter and statistics reset. Settings were preserved.",
    "Valores predeterminados restaurados.": "Default settings restored.",
    "Atajos actualizados. Comprueba la combinación de emergencia.": "Hotkeys updated. Test the emergency shortcut.",
    "No se pudieron guardar los ajustes: ": "Could not save settings: ",
    "Capturando: ": "Capturing: ",
    "Error del motor": "Engine error", "Atajos incompletos": "Incomplete hotkeys",
    "Cada acción necesita un atajo.": "Every action needs a hotkey.", "Atajos duplicados": "Duplicate hotkeys",
    "Cada acción debe tener un atajo diferente.": "Each action must have a different hotkey.",
    "Motor en ejecución": "Engine running", "Detén el motor antes de reiniciar las estadísticas.": "Stop the engine before resetting statistics.",
    "Detén el motor antes de restablecer la configuración.": "Stop the engine before restoring settings.",
    "Restablecer valores predeterminados": "Restore default settings",
    "Se restaurarán todos los ajustes, tema y atajos. ¿Continuar?": "All settings, theme, language and hotkeys will be restored. Continue?",
    "Listo. Ejecuta con el atajo configurado en el panel de atajos.": "Ready. Use the configured hotkey to start.",
}

class MainWindow(QMainWindow):
    """Ventana principal: configuracion, estadisticas, temas e idioma."""
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.engine = None
        self._capture_timer = None
        self._capture_remaining = 3
        self.language = self.settings.get("language", "en")
        self._loading_controls = True  # Evita guardar valores parciales al restaurar controles.
        self.setWindowTitle("Autoclicker Moderno")
        self.setMinimumSize(800, 650)
        self._build_ui()
        self._load_controls()
        self._loading_controls = False
        self._apply_theme()
        self.apply_language()

        self.hotkeys = HotkeyManager(self.settings.get("hotkeys", {}))
        self.hotkeys.start_requested.connect(self.start_or_resume)
        self.hotkeys.pause_requested.connect(self.pause)
        self.hotkeys.stop_requested.connect(self.stop)
        self.hotkeys.emergency_requested.connect(self.emergency_stop)
        self.hotkeys.capture_requested.connect(self.capture_position)
        self.hotkeys.error_occurred.connect(self.show_status)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_elapsed)
        self.refresh_timer.start(200)
        self.showMaximized()
        self.show_status("Listo. Ejecuta con el atajo configurado en el panel de atajos.")

    def _build_ui(self):
        """Construye los controles y conecta sus acciones a los métodos del controlador."""
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(22, 18, 22, 14)
        root.setSpacing(12)

        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title = QLabel("Autoclicker")
        title.setStyleSheet("font-size: 22pt; font-weight: 750;")
        subtitle = QLabel('<a href="https://github.com/DanielCulpian" style="color: #8b96aa; text-decoration: none;">Creado por Daniel Culpian ↗</a>')
        subtitle.setOpenExternalLinks(True)
        subtitle.setTextFormat(Qt.TextFormat.RichText)
        subtitle.setStyleSheet("color: #8b96aa;")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addLayout(title_col)
        header.addStretch()
        header.addWidget(QLabel("Tema"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Oscuro", "dark")
        self.theme_combo.addItem("Claro", "light")
        self.theme_combo.currentIndexChanged.connect(self.theme_changed)
        header.addWidget(self.theme_combo)
        header.addWidget(QLabel("Idioma"))
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Español", "es")
        self.language_combo.currentIndexChanged.connect(self.language_changed)
        header.addWidget(self.language_combo)
        root.addLayout(header)

        status_box = QGroupBox("Estado de la aplicación")
        status_layout = QHBoxLayout(status_box)
        self.status_label = QLabel("Listo")
        self.status_label.setStyleSheet("font-size: 11pt; font-weight: 700;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        root.addWidget(status_box)

        stats = QGroupBox("Estadísticas de ejecución")
        grid = QGridLayout(stats)
        self.count_label = QLabel("0")
        self.count_label.setObjectName("bigCount")
        self.elapsed_label = QLabel("00:00:00")
        self.actual_cps_label = QLabel("0,0")
        grid.addWidget(QLabel("Clics realizados"), 0, 0)
        grid.addWidget(self.count_label, 1, 0)
        grid.addWidget(QLabel("Tiempo activo"), 0, 1)
        grid.addWidget(self.elapsed_label, 1, 1)
        grid.addWidget(QLabel("CPS medio"), 0, 2)
        grid.addWidget(self.actual_cps_label, 1, 2)
        root.addWidget(stats)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        body = QHBoxLayout(content)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(14)
        left, right = QVBoxLayout(), QVBoxLayout()

        motor = QGroupBox("Motor de clics")
        form = QFormLayout(motor)
        self.button_combo = QComboBox()
        for label, value in [("Izquierdo", "left"), ("Derecho", "right"), ("Central", "middle")]:
            self.button_combo.addItem(label, value)
        form.addRow("Botón del ratón", self.button_combo)

        speed_row = QWidget()
        speed_layout = QHBoxLayout(speed_row)
        speed_layout.setContentsMargins(0, 0, 0, 0)
        self.cps_spin = QDoubleSpinBox()
        self.cps_spin.setRange(0.1, 100.0)
        self.cps_spin.setDecimals(1)
        self.cps_spin.setSingleStep(0.5)
        self.cps_spin.setSuffix(" CPS")
        self.cps_spin.setMinimumWidth(150)
        speed_layout.addWidget(self.cps_spin, 1)
        form.addRow("Velocidad (clics por segundo)", speed_row)
        self.cps_spin.valueChanged.connect(self.speed_value_changed)

        self.limit_check = QCheckBox("Limitar cantidad de clics")
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 10_000_000)
        form.addRow(self.limit_check, self.limit_spin)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(0, 3600)
        self.delay_spin.setSuffix(" s")
        form.addRow("Retardo inicial", self.delay_spin)
        left.addWidget(motor)

        position = QGroupBox("Posición del clic")
        pos_layout = QVBoxLayout(position)
        self.fixed_radio = QRadioButton("Posición fija (coordenadas)")
        self.current_radio = QRadioButton("Seguir posición actual del cursor")
        self.position_group = QButtonGroup(self)
        self.position_group.addButton(self.fixed_radio)
        self.position_group.addButton(self.current_radio)
        pos_layout.addWidget(self.fixed_radio)
        pos_layout.addWidget(self.current_radio)
        coords = QHBoxLayout()
        self.x_spin = QSpinBox()
        self.x_spin.setRange(-10000, 10000)
        self.x_spin.setPrefix("X ")
        self.y_spin = QSpinBox()
        self.y_spin.setRange(-10000, 10000)
        self.y_spin.setPrefix("Y ")
        self.capture_button = QPushButton("Capturar en 3 s")
        self.capture_button.clicked.connect(self.capture_position)
        coords.addWidget(self.x_spin)
        coords.addWidget(self.y_spin)
        coords.addWidget(self.capture_button)
        pos_layout.addLayout(coords)
        left.addWidget(position)

        maintenance = QGroupBox("Mantenimiento")
        maintenance_layout = QVBoxLayout(maintenance)
        self.reset_counter_button = QPushButton("Reiniciar contador y estadísticas")
        self.reset_counter_button.clicked.connect(self.reset_counter)
        self.defaults_button = QPushButton("Restablecer valores predeterminados")
        self.defaults_button.clicked.connect(self.reset_defaults)
        maintenance_layout.addWidget(self.reset_counter_button)
        maintenance_layout.addWidget(self.defaults_button)
        left.addWidget(maintenance)
        left.addStretch()

        hotkeys = QGroupBox("Atajos globales")
        hotkey_form = QFormLayout(hotkeys)
        self.hotkey_edits = {}
        labels = [
            ("start", "Iniciar / reanudar"),
            ("pause", "Pausar"),
            ("stop", "Detener"),
            ("emergency", "Parada de emergencia"),
            ("capture", "Capturar coordenadas"),
        ]
        for key, label in labels:
            edit = QLineEdit()
            edit.setPlaceholderText("p. ej. f6 o ctrl+alt+f9")
            self.hotkey_edits[key] = edit
            hotkey_form.addRow(label, edit)
        self.apply_hotkeys_button = QPushButton("Aplicar atajos")
        self.apply_hotkeys_button.setObjectName("primary")
        self.apply_hotkeys_button.clicked.connect(self.apply_hotkeys)
        hotkey_form.addRow(self.apply_hotkeys_button)
        emergency_info = QLabel("La emergencia es global: funciona aunque la ventana no esté enfocada.")
        emergency_info.setWordWrap(True)
        emergency_info.setStyleSheet("color: #8b96aa;")
        hotkey_form.addRow(emergency_info)
        right.addWidget(hotkeys)
        right.addStretch()

        body.addLayout(left, 3)
        body.addLayout(right, 2)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        self.footer = QLabel("Preparado")
        self.footer.setStyleSheet("color: #8b96aa; padding: 4px;")
        root.addWidget(self.footer)

        self.emergency_button = QPushButton("⚠  PARADA DE EMERGENCIA  ·  Ctrl+Alt+F9")
        self.emergency_button.setObjectName("danger")
        self.emergency_button.clicked.connect(self.emergency_stop)
        root.addWidget(self.emergency_button)

    def _load_controls(self):
        s = self.settings
        self._set_combo_data(self.button_combo, s.get("button", "left"))
        self.cps_spin.setValue(float(s.get("cps", 10)))
        self.limit_check.setChecked(bool(s.get("click_limit_enabled", False)))
        self.limit_spin.setValue(int(s.get("click_limit", 100)))
        self.delay_spin.setValue(int(s.get("delay_seconds", 0)))
        self.fixed_radio.setChecked(s.get("position_mode", "fixed") == "fixed")
        self.current_radio.setChecked(s.get("position_mode") == "current")
        self.x_spin.setValue(int(s.get("x", 500)))
        self.y_spin.setValue(int(s.get("y", 400)))
        self._set_combo_data(self.theme_combo, s.get("theme", "dark"))
        self._set_combo_data(self.language_combo, s.get("language", "en"))
        self.language = s.get("language", "en")
        for key, edit in self.hotkey_edits.items():
            edit.setText(str(s.get("hotkeys", {}).get(key, "")))
        self.apply_language()

    @staticmethod
    def _set_combo_data(combo, data):
        idx = combo.findData(data)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _apply_theme(self):
        self.setStyleSheet(DARK_QSS if self.theme_combo.currentData() == "dark" else LIGHT_QSS)

    def theme_changed(self, *_):
        self._apply_theme()
        if not self._loading_controls:
            self.save_current_settings()

    def language_changed(self, *_):
        self.language = self.language_combo.currentData() or "en"
        self.apply_language()
        if not self._loading_controls:
            self.save_current_settings()

    def apply_language(self):
        """Actualiza los textos visibles sin reconstruir la ventana ni perder su estado."""
        reverse = {english: spanish for spanish, english in TRANSLATIONS.items()}
        mapping = TRANSLATIONS if self.language == "en" else reverse
        for widget in self.findChildren(QLabel) + self.findChildren(QPushButton) + self.findChildren(QCheckBox) + self.findChildren(QRadioButton) + self.findChildren(QGroupBox):
            if isinstance(widget, QGroupBox):
                old = widget.title()
                widget.setTitle(mapping.get(old, old))
            else:
                old = widget.text()
                widget.setText(mapping.get(old, old))
        # Los combos contienen textos propios que no son widgets hijos independientes.
        for combo in (self.button_combo, self.theme_combo):
            for index in range(combo.count()):
                old = combo.itemText(index)
                combo.setItemText(index, mapping.get(old, old))
        for edit in self.findChildren(QLineEdit):
            placeholder = edit.placeholderText()
            edit.setPlaceholderText(mapping.get(placeholder, placeholder))
        self.setWindowTitle("Modern Clicker" if self.language == "en" else "Autoclicker Moderno")
        credit_text = "Created by Daniel Culpian ↗" if self.language == "en" else "Creado por Daniel Culpian ↗"
        for label in self.findChildren(QLabel):
            if "github.com/DanielCulpian" in label.text():
                label.setText(f'<a href="https://github.com/DanielCulpian" style="color: #8b96aa; text-decoration: none;">{credit_text}</a>')
        hotkey = self.hotkey_edits.get("emergency")
        hotkey_text = hotkey.text().upper() if hotkey and hotkey.text().strip() else "CTRL+ALT+F9"
        button_text = "⚠  EMERGENCY STOP" if self.language == "en" else "⚠  PARADA DE EMERGENCIA"
        self.emergency_button.setText(f"{button_text}  ·  {hotkey_text}")
        self.save_language_setting()

    def tr(self, spanish: str, english: str) -> str:
        """Devuelve un texto segun el idioma seleccionado para dialogos dinamicos."""
        return english if self.language == "en" else spanish

    def save_language_setting(self):
        self.settings["language"] = self.language

    def speed_value_changed(self, *_):
        # Ignora señales emitidas durante la carga inicial de preferencias.
        if self._loading_controls:
            return
        # La velocidad puede editarse detenido o en pausa; nunca mientras hace clics.
        if self.engine and self.engine.isRunning() and self.engine.is_paused:
            self.engine.update_speed(self.cps_spin.value())
        self.save_current_settings()

    def set_speed_editable(self, editable: bool):
        self.cps_spin.setEnabled(editable)

    def current_config(self):
        """Devuelve una instantanea de los parametros que consume el motor."""
        return {
            "button": self.button_combo.currentData(),
            "cps": self.cps_spin.value(),
            "click_limit_enabled": self.limit_check.isChecked(),
            "click_limit": self.limit_spin.value(),
            "delay_seconds": self.delay_spin.value(),
            "position_mode": "fixed" if self.fixed_radio.isChecked() else "current",
            "x": self.x_spin.value(),
            "y": self.y_spin.value(),
        }

    def save_current_settings(self):
        self.settings.update(self.current_config())
        self.settings["theme"] = self.theme_combo.currentData()
        self.settings["language"] = self.language
        self.settings["hotkeys"] = {k: edit.text().strip().lower() for k, edit in self.hotkey_edits.items()}
        try:
            save_settings(self.settings)
        except OSError as exc:
            self.show_status(f"No se pudieron guardar los ajustes: {exc}")

    def start_or_resume(self):
        """Inicia un motor nuevo o reanuda el que esta pausado."""
        if self.engine and self.engine.isRunning():
            if self.engine.is_paused:
                self.engine.update_speed(self.cps_spin.value())
                self.engine.resume()
                self.set_speed_editable(False)
            return
        self.save_current_settings()
        self.count_label.setText("0")
        self.elapsed_label.setText("00:00:00")
        self.actual_cps_label.setText("0,0")
        self.engine = ClickEngine(self.current_config())
        self.engine.status_changed.connect(self.show_status)
        self.engine.count_changed.connect(self.update_count)
        self.engine.elapsed_changed.connect(self.update_elapsed)
        self.engine.finished_reason.connect(self.engine_finished)
        self.engine.error_occurred.connect(self.show_error)
        self.engine.start()
        self.set_speed_editable(False)

    def pause(self):
        if self.engine and self.engine.isRunning() and not self.engine.is_paused:
            self.engine.pause()
            self.set_speed_editable(True)

    def stop(self):
        if self.engine and self.engine.isRunning():
            self.engine.stop()
            self.set_speed_editable(True)
            self.show_status("Deteniendo…")

    def emergency_stop(self):
        if self.engine and self.engine.isRunning():
            self.engine.stop()
        self.show_status("PARADA DE EMERGENCIA solicitada")

    def update_count(self, count):
        self.count_label.setText(f"{count:,}")

    def update_elapsed(self, elapsed):
        self._show_elapsed(elapsed)
        if elapsed > 0 and self.engine:
            self.actual_cps_label.setText(f"{self.engine.count / elapsed:.1f}".replace(".", ","))

    def refresh_elapsed(self):
        if self.engine and self.engine.isRunning():
            elapsed = self.engine.elapsed_seconds()
            self._show_elapsed(elapsed)
            if elapsed > 0:
                self.actual_cps_label.setText(f"{self.engine.count / elapsed:.1f}".replace(".", ","))

    def _show_elapsed(self, seconds):
        total = max(0, int(seconds))
        hours, rem = divmod(total, 3600)
        minutes, secs = divmod(rem, 60)
        self.elapsed_label.setText(f"{hours:02}:{minutes:02}:{secs:02}")

    def engine_finished(self, reason):
        self.show_status(reason)
        self.engine = None
        self.set_speed_editable(True)
        self.save_current_settings()

    def show_status(self, message):
        # Los estados que llegan del motor estan en español; se traducen al vuelo.
        if self.language == "en":
            for spanish, english in TRANSLATIONS.items():
                if message == spanish:
                    message = english
                    break
                if message.startswith(spanish) and spanish.endswith((": ", "X=")):
                    message = english + message[len(spanish):]
                    break
        self.status_label.setText(message)
        self.footer.setText(message)

    def show_error(self, message):
        self.show_status(message)
        QMessageBox.warning(self, self.tr("Error del motor", "Engine error"), message)

    def capture_position(self):
        if self._capture_timer:
            return
        self._capture_remaining = 3
        self.capture_button.setEnabled(False)
        self.capture_button.setText(self.tr("Capturando: 3…", "Capturing: 3…"))
        self._capture_timer = QTimer(self)
        self._capture_timer.timeout.connect(self._capture_tick)
        self._capture_timer.start(1000)
        self.show_status(self.tr("Coloca el cursor en la posición deseada…", "Move the cursor to the desired position…"))

    def _capture_tick(self):
        self._capture_remaining -= 1
        if self._capture_remaining > 0:
            self.capture_button.setText(self.tr(f"Capturando: {self._capture_remaining}…", f"Capturing: {self._capture_remaining}…"))
            return
        import pyautogui
        point = pyautogui.position()
        self.x_spin.setValue(point.x)
        self.y_spin.setValue(point.y)
        self._capture_timer.stop()
        self._capture_timer.deleteLater()
        self._capture_timer = None
        self.capture_button.setEnabled(True)
        self.capture_button.setText(self.tr("Capturar en 3 s", "Capture in 3 s"))
        self.show_status(f"Posición capturada: X={point.x}, Y={point.y}")
        self.save_current_settings()

    def apply_hotkeys(self):
        values = {key: edit.text().strip().lower() for key, edit in self.hotkey_edits.items()}
        if any(not value for value in values.values()):
            QMessageBox.warning(self, self.tr("Atajos incompletos", "Incomplete hotkeys"), self.tr("Cada acción necesita un atajo.", "Every action needs a hotkey."))
            return
        if len(set(values.values())) != len(values):
            QMessageBox.warning(self, self.tr("Atajos duplicados", "Duplicate hotkeys"), self.tr("Cada acción debe tener un atajo diferente.", "Every action must have a different hotkey."))
            return
        self.hotkeys.register(values)
        self.settings["hotkeys"] = values
        self.save_current_settings()
        self.apply_language()  # Actualiza tambien el texto del boton con el nuevo atajo.
        self.show_status("Atajos actualizados. Comprueba la combinación de emergencia.")

    def reset_counter(self):
        """Reinicia solo las estadísticas; no modifica ajustes ni atajos."""
        if self.engine and self.engine.isRunning():
            QMessageBox.information(self, self.tr("Motor en ejecución", "Engine running"), self.tr("Detén el motor antes de reiniciar las estadísticas.", "Stop the engine before resetting statistics."))
            return
        self.count_label.setText("0")
        self.elapsed_label.setText("00:00:00")
        self.actual_cps_label.setText("0,0")
        self.show_status("Contador y estadísticas reiniciados. La configuración se conserva.")

    def reset_defaults(self):
        if self.engine and self.engine.isRunning():
            QMessageBox.warning(self, self.tr("Motor en ejecución", "Engine running"), self.tr("Detén el motor antes de restablecer la configuración.", "Stop the engine before restoring settings."))
            return
        answer = QMessageBox.question(
            self, self.tr("Restablecer valores predeterminados", "Restore default settings"),
            self.tr("Se restauraran todos los ajustes, tema, idioma y atajos. ¿Continuar?", "All settings, theme, language and hotkeys will be restored. Continue?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.settings = default_settings()
        self._load_controls()
        self._loading_controls = False
        self._apply_theme()
        self.hotkeys.register(self.settings["hotkeys"])
        self.apply_language()  # Restaura textos en ingles, el idioma predeterminado.
        self.save_current_settings()
        self.show_status("Valores predeterminados restaurados.")

    def closeEvent(self, event: QCloseEvent):
        if self.engine and self.engine.isRunning():
            self.engine.stop()
            self.engine.wait(1500)
        if self._capture_timer:
            self._capture_timer.stop()
        self.hotkeys.shutdown()
        self.save_current_settings()
        event.accept()
