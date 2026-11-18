from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.categories import CATEGORIES
from core.category_resolver import CategoryResolver
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
        self.lang_code = lang_code
        self.log = log
        self.vpk_path = dota_path / "game" / "dota" / "pak01_dir.vpk"
        self.stubs: Dict[str, bytes] = {}
        assets_dir = Path(__file__).parent.parent / "assets"

        for stub_name, filename in STUB_FILES.items():
            stub_path = assets_dir / filename
            if not stub_path.exists():
                raise FileNotFoundError(f"Файл заглушки не найден: {stub_path}")
            with open(stub_path, "rb") as handle:
                self.stubs[stub_name] = handle.read()
            self.log.info(f"Загружена заглушка '{stub_name}' ({len(self.stubs[stub_name])} байт)")

    @staticmethod
    def output_path(dota_path: Path, lang_code: str = "russian") -> Path:
        return dota_path / "game" / f"dota_{lang_code}" / "pak02_dir.vpk"

    @classmethod
    def restore(cls, dota_path: Path, lang_code: str, log: GUILogger) -> bool:
        output_vpk = cls.output_path(dota_path, lang_code)
        if not output_vpk.exists():
            log.info(f"Архив мода не найден: {output_vpk}")
            return False
        output_vpk.unlink()
        log.success(f"Архив мода удалён: {output_vpk}")
        return True

    def process_categories(
        self,
        categories: List[str],
        on_progress=None,
        hero_full: bool = False,
        output_path: Optional[Path] = None,
    ) -> bool:
        try:
            self.log.info("Начало поиска файлов в архиве...")
            if not self.vpk_path.exists():
                self.log.error(f"VPK не найден: {self.vpk_path}")
                return False
            if not categories:
                self.log.warning("Не выбрано ни одной категории.")
                return False

            vpk_reader = VPKReader(self.vpk_path)
            resolver = CategoryResolver(vpk_reader, self.log)
            resolved = resolver.resolve(categories, hero_full=hero_full)

            files_to_replace: Dict[str, str] = {}
            for cat_id in categories:
                category_files = resolved.get(cat_id, {})
                self.log.info(f"{CATEGORIES[cat_id].label}: {len(category_files)} файлов")
                for file_path, stub_name in category_files.items():
                    files_to_replace.setdefault(file_path, stub_name)

            if not files_to_replace:
                self.log.warning("Файлы для замены не найдены.")
                return False

            self.log.info(f"Всего уникальных файлов к замене: {len(files_to_replace)}")
            output_vpk = output_path or self.output_path(self.dota_path, self.lang_code)
            output_vpk.parent.mkdir(parents=True, exist_ok=True)
            self.log.info(f"Используем папку: {output_vpk.parent}")

            if output_vpk.exists():
                output_vpk.unlink()
                self.log.info(f"Старый архив удалён: {output_vpk.name}")

            writer = VPKWriterV1(output_vpk)
            items: List[Tuple[str, str]] = sorted(files_to_replace.items())
            for index, (file_path, stub_name) in enumerate(items, start=1):
                if on_progress:
                    on_progress(index, len(items))
                if index % 100 == 0 or index == 1:
                    self.log.progress(f"Добавление {index}/{len(items)}: {file_path}")
                writer.add_file(file_path, self.stubs[stub_name])

            writer.build()
            if not output_vpk.exists():
                self.log.error(f"Архив НЕ создан по пути: {output_vpk.resolve()}")
                return False

            size_mb = output_vpk.stat().st_size / (1024 * 1024)
            self.log.success(f"Архив создан: {output_vpk.resolve()}")
            self.log.info(f"Размер архива: {size_mb:.2f} МБ")
            self.log.info("Перезапустите Dota 2 (русская версия) для применения изменений.")
            return True
        except Exception as exc:
            self.log.error(f"Критическая ошибка: {exc}")
            import traceback
            self.log.error(traceback.format_exc())
            return False
