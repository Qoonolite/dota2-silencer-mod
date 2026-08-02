from pathlib import Path
from typing import List, Dict
from core.vpk_reader import VPKReader
from core.vpk_writer import VPKWriterV1
from utils.logger import GUILogger


class SoundProcessor:
    def __init__(self, dota_path: Path, lang_code: str, log: GUILogger):
        self.dota_path = dota_path
        self.log = log
        self.vpk_path = dota_path / "game" / "dota" / "pak01_dir.vpk"
        self.stub_path = Path(__file__).parent.parent / "assets" / "silence_stub.vsnd_c"

        if not self.stub_path.exists():
            raise FileNotFoundError(f"Файл заглушки не найден: {self.stub_path}")

        with open(self.stub_path, "rb") as f:
            self.stub_data = f.read()
        self.log.info(f"Загружен файл-заглушка ({len(self.stub_data)} байт)")

    def process_categories(self, categories: List[str], patterns_map: Dict[str, List[str]]) -> bool:
        try:
            self.log.info("Начало поиска файлов в архиве...")

            if not self.vpk_path.exists():
                self.log.error(f"VPK не найден: {self.vpk_path}")
                return False

            vpk_reader = VPKReader(self.vpk_path)

            target_patterns = []
            for cat_id in categories:
                if cat_id in patterns_map:
                    target_patterns.extend(patterns_map[cat_id])

            files_to_replace = []
            for pattern in target_patterns:
                found = vpk_reader.find_files_by_pattern(pattern)
                self.log.info(f"Паттерн '{pattern}': найдено {len(found)} файлов")
                files_to_replace.extend(found)

            files_to_replace = list(set(files_to_replace))

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

            for i, file_path in enumerate(files_to_replace):
                if (i + 1) % 100 == 0 or i == 0:
                    self.log.progress(f"Добавление {i+1}/{len(files_to_replace)}: {file_path}")
                writer.add_file(file_path, self.stub_data)

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