"""Pruebas basicas de los valores predeterminados y su independencia."""
from autoclicker.settings import DEFAULTS, default_settings

def test_default_emergency_hotkey_is_chord():
    assert DEFAULTS["hotkeys"]["emergency"] == "ctrl+alt+f9"

def test_default_settings_are_independent_copies():
    first = default_settings()
    first["hotkeys"]["start"] = "f12"
    assert default_settings()["hotkeys"]["start"] == "f6"


def test_default_language_is_english_and_speed_has_one_control():
    settings = default_settings()
    assert settings["language"] == "en"
    assert "cps" in settings
    assert "interval_ms" not in settings
    assert "speed_mode" not in settings
