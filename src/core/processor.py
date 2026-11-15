from pathlib import Path
from typing import List, Dict, Tuple
from core.vpk_reader import VPKReader
from core.vpk_writer import VPKWriterV1
from utils.logger import GUILogger

STUB_FILES = {
    "sound": "silence_stub.vsnd_c",
    "texture": "transparent_stub.vtex_c",
}


class SoundProcessor:
    def __init__(self, dota_path: Path, lang_code: str, log: GUILogger):
        self.dota_path = dota_path
        self.log = log
        self.vpk_path = dota_path / "game" / "dota" / "pak01_dir.vpk"
        self.stubs: Dict[str, bytes] = {}
        assets_dir = Path(__file__).parent.parent / "assets"

        for stub_name, filename in STUB_FILES.items():
            stub_path = assets_dir / filename
            if not stub_path.exists():
                raise FileNotFoundError(f"Файл заглушки не найден: {stub_path}")
            with open(stub_path, "rb") as f:
                self.stubs[stub_name] = f.read()
            self.log.info(f"Загружена заглушка '{stub_name}' ({len(self.stubs[stub_name])} байт)")

    def process_categories(self, categories: List[str], categories_map: Dict,
                           on_progress=None) -> bool:
        try:
            self.log.info("Начало поиска файлов в архиве...")

            if not self.vpk_path.exists():
                self.log.error(f"VPK не найден: {self.vpk_path}")
                return False

            vpk_reader = VPKReader(self.vpk_path)

            # файл -> имя заглушки
            files_to_replace: Dict[str, str] = {}
            for cat_id in categories:
                category = categories_map.get(cat_id)
                if not category:
                    continue
                for pattern, stub_name in category["patterns"]:
                    found = vpk_reader.find_files_by_pattern(pattern)
                    self.log.info(f"Паттерн '{pattern}': найдено {len(found)} файлов")
                    for file_path in found:
                        files_to_replace.setdefault(file_path, stub_name)

            if not files_to_replace:
                self.log.warning("Файлы для замены не найдены.")
                return False

            self.log.info(f"Всего файлов к замене: {len(files_to_replace)}")

            lang_folder = self.dota_path / "game" / "dota_russian"
            lang_folder.mkdir(parents=True, exist_ok=True)
            self.log.info(f"Используем папку: {lang_folder}")

            output_vpk = lang_folder / "pak02_dir.vpk"

            if output_vpk.exists():
                output_vpk.unlink()
                self.log.info(f"Старый архив удалён: {output_vpk.name}")

            writer = VPKWriterV1(output_vpk)
            items: List[Tuple[str, str]] = sorted(files_to_replace.items())

            for i, (file_path, stub_name) in enumerate(items):
                if on_progress:
                    on_progress(i + 1, len(items))
                if (i + 1) % 100 == 0 or i == 0:
                    self.log.progress(f"Добавление {i+1}/{len(items)}: {file_path}")
                writer.add_file(file_path, self.stubs[stub_name])

            writer.build()

            if output_vpk.exists():
                size_mb = output_vpk.stat().st_size / (1024 * 1024)
                self.log.success(f"Архив создан: {output_vpk.resolve()}")
                self.log.info(f"Размер архива: {size_mb:.2f} МБ")
                self.log.info("Перезапустите Dota 2 (русская версия) для применения изменений.")
            else:
                self.log.error(f"Архив НЕ создан по пути: {output_vpk.resolve()}")
                return False

            return True

        except Exception as e:
            self.log.error(f"Критическая ошибка: {e}")
            import traceback
            self.log.error(traceback.format_exc())
            return False
