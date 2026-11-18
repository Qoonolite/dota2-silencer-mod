import json
import os
import sys
from pathlib import Path
from typing import Any, Optional


def _config_path() -> Path:
    """Возвращает путь к файлу config.json."""
    # Определяем базовую папку:
    # - Если программа запущена как .exe — рядом с exe
    # - Если как скрипт — в AppData
    if getattr(sys, 'frozen', False):
        # Запущено как .exe (PyInstaller)
        base = Path(sys.executable).parent
    else:
        # Запущено как скрипт
        if sys.platform == 'win32':
            base = Path(os.environ.get('APPDATA', Path.home()))
        else:
            base = Path.home()
    
    cfg_dir = base / "DotaSoundSilencer"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir / "config.json"


class Config:
    """
    Синглтон — класс, у которого может быть только один экземпляр.
    Это удобно: из любой части программы можно вызвать Config() 
    и получить те же самые настройки.
    """
    _instance: Optional['Config'] = None
    _data: dict
    
    def __new__(cls):
        # Магия синглтона: если объект ещё не создан — создаём
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        """Загружает настройки из файла."""
        path = _config_path()
        if path.exists():
            try:
                self._data = json.loads(path.read_text(encoding='utf-8'))
            except Exception:
                self._data = {}
        else:
            self._data = {}
        self._migrate()

    def _migrate(self):
        changed = False
        legacy_categories = {
            "cat_wheel_sounds": (
                "cat_dota_plus",
                "cat_international",
                "cat_community",
                "cat_team_fans",
                "cat_seasonal_events",
            ),
            "cat_sprays": ("cat_sprays",),
        }
        for legacy_key, new_keys in legacy_categories.items():
            if legacy_key not in self._data:
                continue
            for key in new_keys:
                if key not in self._data:
                    self._data[key] = bool(self._data[legacy_key])
                    changed = True
        if "hero_full" not in self._data:
            self._data["hero_full"] = False
            changed = True
        if changed:
            self.save()
    
    def save(self):
        """Сохраняет настройки в файл."""
        path = _config_path()
        path.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False), 
            encoding='utf-8'
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение по ключу."""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Установить значение и сразу сохранить."""
        self._data[key] = value
        self.save()