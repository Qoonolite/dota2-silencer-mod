import sys
from pathlib import Path
from typing import Optional
from utils.logger import GUILogger


class PathFinder:
    """Ищет установленную Dota 2."""
    
    # Относительный путь от Steam до папки Dota
    DOTAA_SUBPATH = Path("steamapps/common/dota 2 beta")
    
    # Файл-маркер: если он есть — значит, это точно папка Dota 2
    VALIDATION_FILE = Path("game/dota/pak01_dir.vpk")
    
    # Самые популярные места установки Steam
    DEFAULT_PATHS = [
        Path(r"C:\Program Files (x86)\Steam"),
        Path(r"C:\Program Files\Steam"),
        Path(r"D:\Steam"),
        Path(r"D:\SteamLibrary"),
        Path(r"E:\Steam"),
        Path(r"E:\SteamLibrary"),
    ]
    
    def __init__(self):
        self.log = GUILogger()
    
    def find(self) -> Optional[Path]:
        """
        Главная функция. Пробует все способы поиска по очереди.
        Возвращает путь к папке Dota 2 или None.
        """
        self.log.info("Поиск Dota 2...")
        
        # Способ 1: через реестр Windows
        path = self._from_registry()
        if path:
            return path
        
        # Способ 2: через libraryfolders.vdf
        path = self._from_vdf()
        if path:
            return path
        
        # Способ 3: перебираем стандартные пути
        path = self._from_defaults()
        if path:
            return path
        
        self.log.info("Dota 2 не найдена автоматически")
        return None
    
    def _from_registry(self) -> Optional[Path]:
        """Читает путь установки Steam из реестра Windows."""
        if sys.platform != 'win32':
            return None
        try:
            import winreg  # Модуль для работы с реестром Windows
            
            # Пробуем два места в реестре (для 32- и 64-битных систем)
            for key_path in [
                r"SOFTWARE\Valve\Steam",
                r"SOFTWARE\WOW6432Node\Valve\Steam",
            ]:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                        steam = Path(install_path)
                        result = self._validate_steam(steam)
                        if result:
                            self.log.info(f"Найдена через реестр: {result}")
                            return result
                except FileNotFoundError:
                    # Ключа нет — пробуем следующий
                    continue
        except Exception as e:
            self.log.debug(f"Ошибка чтения реестра: {e}")
        return None
    
    def _from_vdf(self) -> Optional[Path]:
        """
        Читает libraryfolders.vdf — файл, где Steam хранит список всех
        папок с играми. Ищем там AppID 570 (это Dota 2).
        """
        try:
            import vdf
        except ImportError:
            self.log.debug("Библиотека vdf не установлена")
            return None
        
        # Сначала нужно найти сам Steam
        steam_paths = []
        reg_path = self._steam_install_from_registry()
        if reg_path:
            steam_paths.append(reg_path)
        steam_paths.extend(self.DEFAULT_PATHS)
        
        # Перебираем все возможные пути к Steam
        for steam in steam_paths:
            vdf_path = steam / "steamapps/libraryfolders.vdf"
            if not vdf_path.exists():
                continue
            
            try:
                # Парсим VDF-файл (формат Valve, похож на JSON)
                data = vdf.loads(vdf_path.read_text(encoding='utf-8'))
                folders = data.get("libraryfolders", {})
                
                # Ищем папку, где установлена Dota 2 (AppID 570)
                for folder_id, folder_data in folders.items():
                    if not isinstance(folder_data, dict):
                        continue
                    apps = folder_data.get("apps", {})
                    if "570" in apps:  # 570 = AppID Dota 2
                        dota_path = Path(folder_data["path"]) / self.DOTAA_SUBPATH
                        if self._validate_dota(dota_path):
                            self.log.info(f"Найдена через VDF: {dota_path}")
                            return dota_path
            except Exception as e:
                self.log.debug(f"Ошибка парсинга {vdf_path}: {e}")
        
        return None
    
    def _steam_install_from_registry(self) -> Optional[Path]:
        """Вспомогательная: получает путь к Steam из реестра."""
        if sys.platform != 'win32':
            return None
        try:
            import winreg
            for key_path in [
                r"SOFTWARE\Valve\Steam",
                r"SOFTWARE\WOW6432Node\Valve\Steam",
            ]:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                        install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                        return Path(install_path)
                except FileNotFoundError:
                    continue
        except Exception:
            pass
        return None
    
    def _from_defaults(self) -> Optional[Path]:
        """Перебирает стандартные пути установки Steam."""
        for steam in self.DEFAULT_PATHS:
            result = self._validate_steam(steam)
            if result:
                self.log.info(f"Найдена в дефолтном пути: {result}")
                return result
        return None
    
    def _validate_steam(self, steam_path: Path) -> Optional[Path]:
        """Проверяет, есть ли в этой папке Steam папка Dota 2."""
        dota_path = steam_path / self.DOTAA_SUBPATH
        if self._validate_dota(dota_path):
            return dota_path
        return None
    
    def _validate_dota(self, dota_path: Path) -> bool:
        """Проверяет, что это действительно папка Dota 2."""
        return (dota_path / self.VALIDATION_FILE).exists()
    
    @staticmethod
    def validate_user_path(path: Path) -> bool:
        """Проверяет путь, который указал пользователь вручную."""
        return (path / PathFinder.VALIDATION_FILE).exists()