import fnmatch
import re
import tempfile
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import vdf

from core.categories import CATEGORIES, Category, ChatSelector, PathSelector
from core.vpk_reader import VPKReader
from utils.logger import GUILogger


EVENT_BLOCK_RE = re.compile(
    r'^[ \t]*(?:"([^"]+)"|([A-Za-z0-9_.\-]+))[ \t]*=[ \t]*(?:\r?\n[ \t]*)?\{',
    re.MULTILINE,
)
VSND_FILES_RE = re.compile(r'\bvsnd_files\s*=\s*(\[.*?\]|"[^"]*")', re.DOTALL)
SOUND_PATH_RE = re.compile(r'"(sounds/[^"]+)"', re.IGNORECASE)


def _block_end(text: str, opening_brace: int) -> int:
    depth = 0
    in_string = False
    escaped = False
    for index in range(opening_brace, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
    return len(text)


def _compiled_file_path(path: str) -> str:
    normalized = path.replace("\\", "/").lstrip("/")
    if "." in normalized.rsplit("/", 1)[-1]:
        normalized = normalized.rsplit(".", 1)[0]
    return f"{normalized}.vsnd_c".lower()


class ChatCatalog:
    def __init__(self, definitions_dir: Path, file_lookup: Dict[str, str], log: GUILogger):
        self.definitions_dir = definitions_dir
        self.file_lookup = file_lookup
        self.log = log
        self._scripts = {}
        self._selector_cache: Dict[ChatSelector, Set[str]] = {}
        self._event_files: Dict[str, Set[str]] = {}

    def _load_script(self, script: str) -> dict:
        if script in self._scripts:
            return self._scripts[script]
        path = self.definitions_dir / script
        if not path.exists():
            raise FileNotFoundError(f"Официальный скрипт не извлечён: {script}")
        with path.open("r", encoding="utf-8-sig") as handle:
            data = vdf.parse(handle)
        root = data.get("chat_wheel", data)
        self._scripts[script] = root
        return root

    def _messages(self, script: str) -> Dict[str, dict]:
        root = self._load_script(script)
        messages = dict(root.get("messages", {}))
        for group in root.get("hero_messages", {}).values():
            if isinstance(group, dict):
                messages.update(group)
        return messages

    def required_scripts(self, selectors: Iterable[ChatSelector]) -> Set[str]:
        scripts = set()
        for selector in selectors:
            scripts.add(selector.script)
            if selector.categories:
                scripts.add(selector.category_script)
        return scripts

    def build_event_index(self, selectors: Sequence[ChatSelector]) -> None:
        target_events = {
            message["sound"]
            for selector in selectors
            for message in self._messages(selector.script).values()
            if isinstance(message, dict) and message.get("sound")
        }
        event_files: Dict[str, Set[str]] = {}
        soundevent_files = sorted(self.definitions_dir.glob("soundevents/**/*.vsndevts"))
        if not soundevent_files:
            raise FileNotFoundError("Не удалось декомпилировать soundevents из pak01_dir.vpk")

        for path in soundevent_files:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            for match in EVENT_BLOCK_RE.finditer(text):
                event_name = match.group(1) or match.group(2)
                if event_name not in target_events:
                    continue
                opening_brace = text.find("{", match.start(), match.end())
                block = text[opening_brace:_block_end(text, opening_brace)]
                files_match = VSND_FILES_RE.search(block)
                if not files_match:
                    continue
                for sound_path in SOUND_PATH_RE.findall(files_match.group(1)):
                    compiled = _compiled_file_path(sound_path)
                    actual_path = self.file_lookup.get(compiled)
                    if actual_path:
                        event_files.setdefault(event_name, set()).add(actual_path)

        self._event_files = event_files
        self.log.info(
            f"Sound events: разрешено {len(event_files)} событий из {len(target_events)} запрошенных"
        )

    def resolve(self, selector: ChatSelector) -> Set[str]:
        if selector in self._selector_cache:
            return set(self._selector_cache[selector])
        if not self._event_files:
            raise RuntimeError("Индекс sound events ещё не построен")

        messages = self._messages(selector.script)
        selected_ids: Set[str] = set()
        if selector.categories:
            categories_root = self._load_script(selector.category_script)
            categories = categories_root.get("categories", {})
            for category_id in selector.categories:
                selected_ids.update(categories.get(category_id, {}).get("messages", {}))

        include_re = re.compile(selector.include_regex, re.IGNORECASE) if selector.include_regex else None
        exclude_re = re.compile(selector.exclude_regex, re.IGNORECASE) if selector.exclude_regex else None
        resolved: Set[str] = set()
        missing_events: Set[str] = set()
        selected_messages = 0

        for message_id, message in messages.items():
            if not isinstance(message, dict) or not message.get("sound"):
                continue
            event_name = message["sound"]
            event_files = self._event_files.get(event_name, set())
            search_text = "\n".join((message_id, event_name, *sorted(event_files)))
            if selector.categories or include_re:
                if message_id not in selected_ids and not (include_re and include_re.search(search_text)):
                    continue
            if exclude_re and exclude_re.search(search_text):
                continue
            selected_messages += 1
            if event_files:
                resolved.update(event_files)
            else:
                missing_events.add(event_name)

        if missing_events:
            self.log.warning(
                f"{selector.script}: не найдено {len(missing_events)} sound events; "
                "соответствующие файлы пропущены"
            )
            self.log.debug("Отсутствующие sound events: " + ", ".join(sorted(missing_events)))
        self.log.info(
            f"{selector.script}: выбрано {selected_messages} сообщений, "
            f"найдено {len(resolved)} уникальных файлов"
        )
        self._selector_cache[selector] = set(resolved)
        return resolved


class CategoryResolver:
    def __init__(self, reader: VPKReader, log: GUILogger):
        self.reader = reader
        self.log = log
        self.file_lookup = {path.lower(): path for path in reader.file_list}

    def resolve(self, selected_ids: Sequence[str], hero_full: bool = False) -> Dict[str, Dict[str, str]]:
        unknown = [cat_id for cat_id in selected_ids if cat_id not in CATEGORIES]
        if unknown:
            raise ValueError(f"Неизвестные категории: {', '.join(unknown)}")

        required_ids = list(dict.fromkeys(selected_ids))
        for cat_id in list(required_ids):
            for dependency in CATEGORIES[cat_id].exclude_categories:
                if dependency not in required_ids:
                    required_ids.append(dependency)

        chat_selectors = [
            selector
            for cat_id in required_ids
            for selector in CATEGORIES[cat_id].selectors
            if isinstance(selector, ChatSelector)
        ]
        catalog = self._build_catalog(chat_selectors) if chat_selectors else None
        resolved = {
            cat_id: self._resolve_category(CATEGORIES[cat_id], catalog, hero_full)
            for cat_id in required_ids
        }

        for cat_id in selected_ids:
            category = CATEGORIES[cat_id]
            for excluded_id in category.exclude_categories:
                before = len(resolved[cat_id])
                excluded_files = set(resolved[excluded_id])
                resolved[cat_id] = {
                    path: stub
                    for path, stub in resolved[cat_id].items()
                    if path not in excluded_files
                }
                excluded_count = before - len(resolved[cat_id])
                if excluded_count:
                    self.log.info(
                        f"{category.label}: исключено {excluded_count} файлов категории "
                        f"'{CATEGORIES[excluded_id].label}'"
                    )

        result = {cat_id: resolved[cat_id] for cat_id in selected_ids}
        self._log_overlaps(result)
        return result

    def _build_catalog(self, selectors: Sequence[ChatSelector]) -> ChatCatalog:
        unique_selectors = list(dict.fromkeys(selectors))
        scripts: Set[str] = set()
        for selector in unique_selectors:
            scripts.add(selector.script)
            if selector.categories:
                scripts.add(selector.category_script)

        with tempfile.TemporaryDirectory(prefix="dota_silencer_defs_") as temp_dir:
            definitions_dir = Path(temp_dir)
            self.log.info("Извлечение официальных chat_wheel и soundevents из архива...")
            self.reader.extract(
                definitions_dir,
                [*sorted(scripts), "soundevents/"],
                decompile=True,
            )
            catalog = ChatCatalog(definitions_dir, self.file_lookup, self.log)
            catalog.build_event_index(unique_selectors)
            for selector in unique_selectors:
                catalog.resolve(selector)
        return catalog

    def _resolve_category(
        self,
        category: Category,
        catalog: Optional[ChatCatalog],
        hero_full: bool,
    ) -> Dict[str, str]:
        files: Dict[str, str] = {}
        for selector in category.selectors:
            if isinstance(selector, PathSelector):
                found = self.reader.find_files_by_pattern(selector.pattern)
                exclude_path_re = (
                    re.compile(selector.exclude_regex, re.IGNORECASE)
                    if selector.exclude_regex else None
                )
                found = [
                    path for path in found
                    if not any(path.startswith(prefix) for prefix in selector.exclude_prefixes)
                    and not (exclude_path_re and exclude_path_re.search(path))
                ]
                self.log.info(f"Паттерн '{selector.pattern}': найдено {len(found)} файлов")
                for path in found:
                    files[path] = selector.stub
            else:
                if catalog is None:
                    raise RuntimeError("Каталог sound events не инициализирован")
                for path in catalog.resolve(selector):
                    files[path] = "sound"

        if category.safe_file_pattern and not hero_full:
            before = len(files)
            files = {
                path: stub for path, stub in files.items()
                if fnmatch.fnmatch(Path(path).name, category.safe_file_pattern)
            }
            self.log.info(
                f"{category.label}: безопасный режим, {len(files)} из {before} файлов"
            )
        elif category.safe_file_pattern:
            self.log.warning(f"{category.label}: включён полный режим, обычные реплики также будут заглушены")
        return files

    def _log_overlaps(self, resolved: Dict[str, Dict[str, str]]) -> None:
        for first_id, second_id in combinations(resolved, 2):
            overlap = set(resolved[first_id]) & set(resolved[second_id])
            if not overlap:
                continue
            first = CATEGORIES[first_id].label
            second = CATEGORIES[second_id].label
            self.log.warning(
                f"Пересечение категорий '{first}' и '{second}': {len(overlap)} общих файлов"
            )
            self.log.debug(
                f"Общие файлы категорий {first_id}/{second_id}: " + ", ".join(sorted(overlap))
            )
