# Dota 2 Silencer — документация для разработчика / агента

Полное описание проекта: что это, как устроено, что установить и как собрать.
Читать целиком перед любыми изменениями.

---

## 1. Что делает проект

Windows-утилита с GUI (PyQt6), которая отключает раздражающий контент в Dota 2:

- звуки Dota Plus, саундборда и The International;
- реплики кастеров, сообщества и фанатские наборы команд;
- реплики героев в колесе чата, включая безопасный и полный режимы;
- только звуки насмешек героев;
- реплики сезонных событий;
- граффити (спреи) и звук напыления.

**Принцип работы:** Dota 2 подгружает языковую папку `game/dota_russian` поверх основных
архивов. Программа находит целевые файлы в `game/dota/pak01_dir.vpk`, берёт файлы-заглушки
(тишина / прозрачная текстура) и упаковывает их под именами оригиналов в
`game/dota_russian/pak02_dir.vpk`. Оригинальные файлы игры **не изменяются**.
Удаление `pak02_dir.vpk` полностью откатывает мод; в UI для этого есть кнопка
«Восстановить всё» с подтверждением.

**Критичное ограничение:** работает только с русской озвучкой (`AudioLanguage = russian`
в `game/dota/cfg/boot.vcfg`). С июля 2026 язык интерфейса и озвучки в Dota 2 — независимые
настройки; языковая папка монтируется по языку озвучки. Для других языков отдельной папки
нет (`dota_english` не существует) — метод неприменим.

---

## 2. Стек и инструменты

| Инструмент | Версия | Назначение |
|---|---|---|
| Python | 3.11+ | Язык проекта (разработка велась на 3.11) |
| PyQt6 / PyQt6-Qt6 | **6.6.1 (пин обязателен)** | GUI. Пин нужен: на более новых Qt6 были проблемы совместимости |
| PyInstaller | 6.5.0 | Сборка onefile exe |
| `vrf_cli.exe` | последний релиз | Листинг, извлечение и декомпиляция VPK Source 2. Источник: [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/) → `cli-windows-x64.zip` |
| `vpk.exe` | из Source **1** SDK | Упаковка итогового VPK v1. Именно Source 1 — его формат читает `dota_russian` |
| vdf, numpy | см. requirements.txt | Парсинг `libraryfolders.vdf` и официальных `chat_wheel`-скриптов, служебное |

Окружение: Windows 10/11, Git Bash. IDE — PyCharm (`.idea/` в репо).

---

## 3. Установка для разработки

```bash
git clone https://github.com/Qoonolite/dota2-silencer-mod.git
cd dota2-silencer-mod
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

**Внешние инструменты (в репозиторий НЕ входят — размер и лицензии):**

```
tools/vpk/vpk.exe (+ tier0.dll, vstdlib.dll и др. из Source SDK)
tools/vrf/vrf_cli.exe (+ все dll из cli-windows-x64.zip)
```

Без них чтение и запись VPK невозможны: `VPKReader` и `VPKWriterV1` ищут их
в `tools/` рядом с проектом (из исходников) или рядом с exe (в сборке).

Для полноценного теста нужна установленная Dota 2 (путь вида
`...\steamapps\common\dota 2 beta`).

---

## 4. Структура проекта

```
dota-sound-silencer/
├── AGENTS.md                  ← этот файл
├── README.md                  ← пользовательская документация (GitHub)
├── requirements.txt           ← PyQt6==6.6.1, PyQt6-Qt6==6.6.1, numpy, vdf, pyinstaller
├── buildbuild.spec            ← АКТУАЛЬНЫЙ spec PyInstaller (имя exe: DotaSoundSilencer)
├── main.spec                  ← устаревший spec (собирает main.exe), не использовать
├── find_sounds.py, hex_dump.py← разовые отладочные скрипты
│
├── src/
│   ├── main.py                ← вход: QApplication + DARK_THEME + App
│   ├── app.py                 ← QMainWindow: 860x780, минимум 760x640, заголовок и иконка
│   ├── core/
│   │   ├── categories.py      ← data-driven CATEGORIES: 8 категорий, PathSelector/ChatSelector,
│   │   │                        defaults, описания, safe hero mode и межкатегорийные исключения
│   │   ├── category_resolver.py ← CategoryResolver: паттерны, официальные chat_wheel/soundevents,
│   │   │                          точные пути .vsnd_c, дедупликация и логирование пересечений
│   │   ├── processor.py       ← SoundProcessor: сборка pak02_dir.vpk, output_path(), restore()
│   │   ├── vpk_reader.py      ← VPKReader: листинг pak01_dir.vpk через vrf_cli,
│   │   │                        find_files_by_pattern (fnmatch + **), extract() с опцией -d
│   │   ├── vpk_writer.py      ← VPKWriterV1: обёртка над vpk.exe (Source 1),
│   │   │                        ищет vpk.exe в tools/vpk/ рядом с exe/проектом
│   │   └── path_finder.py     ← автопоиск dota 2 beta: реестр Steam, libraryfolders.vdf,
│   │                            стандартные пути; validate_user_path()
│   ├── ui/
│   │   ├── main_window.py     ← двухколоночные категории, scroll, select all/none, счётчик,
│   │   │                        hero full toggle, ProcessWorker(QThread), прогресс,
│   │   │                        сворачиваемый журнал и Restore all
│   │   ├── path_dialog.py     ← диалог ручного выбора пути к игре
│   │   ├── progress_dialog.py ← (legacy, не используется в основном потоке)
│   │   └── styles.py          ← DARK_THEME: вся QSS-тема (Google Material dark gray)
│   ├── utils/
│   │   ├── config.py          ← Config (синглтон, JSON): путь, cat_<id>, hero_full, миграция v2.1
│   │   └── logger.py          ← GUILogger (синглтон): pyqtSignal(level,msg) + файл app.log
│   ├── data/                  ← пусто (зарезервировано, пакуется в exe)
│   └── assets/
│       ├── app_icon.png/.ico  ← иконка приложения (генерируется tools/make_icon.py)
│       ├── silence_stub.vsnd_c     ← заглушка-тишина (<1 сек) для .vsnd_c
│       └── transparent_stub.vtex_c ← прозрачная текстура движка для .vtex_c
│
├── tools/
│   ├── vpk/                   ← vpk.exe + dll (НЕ в git)
│   ├── vrf/                   ← vrf_cli.exe + dll (НЕ в git)
│   ├── make_icon.py           ← генератор иконки (PyQt6 QPainter)
│   ├── preview_ui.py          ← оффскрин-рендер окна в tools/ui_preview.png
│   └── ui_preview.png         ← артефакт превью (в git не коммитить)
│
├── build/                     ← кэш PyInstaller (в git не входит)
└── dist/                      ← результат сборки (в git не входит)
    ├── DotaSoundSilencer.exe
    └── tools/                 ← копия tools/ для релизного архива
```

---

## 5. Запуск из исходников

```bash
.venv/Scripts/python.exe src/main.py
```

Проверка UI без показа окна (сохранит `tools/ui_preview.png`):

```bash
.venv/Scripts/python.exe tools/preview_ui.py
```

Проверка всех селекторов против реального архива игры:

```bash
.venv/Scripts/python.exe -c "
import sys; sys.path.insert(0, 'src')
from pathlib import Path
from core.categories import CATEGORIES
from core.category_resolver import CategoryResolver
from core.vpk_reader import VPKReader
from utils.logger import GUILogger
r = VPKReader(Path('D:/SteamLibrary/steamapps/common/dota 2 beta/game/dota/pak01_dir.vpk'))
resolved = CategoryResolver(r, GUILogger()).resolve(list(CATEGORIES), hero_full=False)
print({key: len(files) for key, files in resolved.items()})
"
```

Для категорий с `ChatSelector` проверка также извлекает нужные скрипты и декомпилирует
`soundevents/` во временную папку. Это занимает несколько секунд и не меняет файлы игры.

---

## 6. Ключевая логика: категории и резолвер

Категории объявлены в `src/core/categories.py` → `CATEGORIES`, а не в QWidget.
Порядок словаря определяет порядок карточек в двух колонках. Текущие ID:

| ID | По умолчанию | Основа выбора |
|---|---|---|
| `dota_plus` | вкл. | Общий саундборд + `dota_plus_sounds`, исключая TI/сезонные классификации |
| `international` | вкл. | TI-пути, официальные TI12/TI13/Voice of God, `ti2021_casters_chat_wheel.txt` |
| `community` | вкл. | `sounds/talentcontent/**/*.vsnd_c` |
| `team_fans` | вкл. | `sounds/teamfancontent/**/*.vsnd_c` минус файлы `international` |
| `hero_chat` | **выкл.** | Все сообщения `chat_wheel_heroes.txt`; safe mode — только `*_wheel_*` |
| `taunts` | **выкл.** | `taunt` только в `sounds/vo` и `sounds/weapons/hero`, Siltbreaker исключён |
| `seasonal_events` | вкл. | Точные события/сообщения + Dragon's Blood и событийные legacy-пути |
| `sprays` | вкл. | `materials/particle/sprays/**/*.vtex_c` + `spraypaint.vsnd_c` |

`PathSelector` задаёт fnmatch-паттерн, тип заглушки и необязательные исключения.
`ChatSelector` выбирает сообщения из официальных скриптов по имени категории и/или regex.
`CategoryResolver`:

1. Определяет зависимости категорий (`team_fans` исключает файлы отдельного TI2021-набора).
2. Через `VPKReader.extract(..., decompile=True)` извлекает нужные `chat_wheel` и `soundevents/`.
3. Парсит VDF и KV3-подобные soundevents, разрешает `sound event -> sounds/*.vsnd_c`.
4. Фильтрует safe/full hero mode, применяет исключения и логирует пересечения категорий.
5. Возвращает файлы каждой категории; `SoundProcessor` объединяет их с дедупликацией.

Широкий `sounds/misc/crownfall/**` использовать нельзя: он захватывает музыку и эффекты
мини-игр. Crownfall выбирается только по официальным сообщениям.

Полный hero mode неизбежно заглушает часть обычной озвучки из-за повторного использования
файлов Valve. Пересечения других категорий также возможны: активная категория означает,
что общий файл будет заглушён. Не обещать независимость таких файлов.

Новая категория обычно требует одну запись `Category` в `CATEGORIES`; чекбокс, конфиг,
счётчик и компоновка создаются автоматически. Сетка рассчитана на 10 пунктов (5 строк),
при нехватке высоты появляется прокрутка. Новые селекторы проверять на реальном pak01.

---

## 7. Сборка релиза

```bash
# 1. Сборка exe (результат: dist/DotaSoundSilencer.exe)
.venv/Scripts/python.exe -m PyInstaller buildbuild.spec --clean --noconfirm

# 2. Проверка запуска (GUI-приложение, stderr не виден — проверять процесс)
./dist/DotaSoundSilencer.exe & sleep 6; tasklist //FI "IMAGENAME eq DotaSoundSilencer.exe"

# 3. Релизный архив = exe + tools/ (пользователю нужны оба)
```

Spec-файл пакует `src/assets` и `src/data` внутрь exe (`_MEIPASS`), поэтому код резолвит
ассеты через `Path(__file__).parent.parent / "assets"` — в frozen-режиме это `_MEIPASS/assets`.
`tools/` намеренно **не** пакуется (120+ МБ, лицензии) — ищется рядом с exe.

Релиз на GitHub: тег `vX.Y.Z` + архив `DotaSoundSilencer_vX.Y.Z.zip` (exe + tools).
В коде текущая версия — **v2.2** (`main_window.py`, `main.py`); последний опубликованный
релиз на момент изменения — v2.1.0. Коммит, push и новый релиз — только по явному запросу.

---

## 8. Конфиг и логи (runtime)

| Что | Запуск из исходников | Запуск exe |
|---|---|---|
| `config.json` | `%APPDATA%\DotaSoundSilencer\` | `<папка exe>\DotaSoundSilencer\` |
| `app.log` | `%APPDATA%\DotaSoundSilencer\logs\` | тот же `%APPDATA%` |

Ключи конфига: `dota_path`, `cat_<id>` для восьми категорий и `hero_full` (bool).
`hero_full`, `cat_hero_chat` и `cat_taunts` по умолчанию **false**.

При загрузке `Config` мигрирует старые `cat_wheel_sounds` и `cat_sprays`: первый задаёт
начальное состояние пяти новым звуковым категориям прежнего назначения, второй — `cat_sprays`.
Уже существующие новые ключи не перезаписываются. Агрессивные функции миграция не включает.

---

## 9. Подводные камни (важно!)

1. **AudioLanguage** — 90% жалоб «не работает» = в игре не выбрана русская озвучка
   (после патча июля 2026 это отдельная настройка). Диагностика: `game/dota/cfg/boot.vcfg`.
2. **`vpk.exe` должен быть из Source 1 SDK**, не Source 2 — формат VPK v1.
3. **Пин `PyQt6-Qt6==6.6.1`** не снимать без причины.
4. **GUI-тесты**: exe — windowed-приложение, ошибки не попадают в консоль. При «молчаливом
   падении» запускать `src/main.py` из терминала за traceback. Учитывать: тестовые окна
   появляются на экране пользователя — он может закрыть их руками (это не падение!).
5. **Заглушка спреев** — родная `materials/dev/transparent_*.vtex_c` из архива игры.
   Если в игре вместо невидимого спрея артефакты (чёрный квадрат/«шахматка») — кандидаты
   на замену: `materials/debug/debugempty_color_*.vtex_c` (извлекаются через
   `vrf_cli -i pak01_dir.vpk -o <dir> -f <путь>`).
6. **Soundevents нужен `-d`**: без декомпиляции остаются бинарные `.vsndevts_c`, которые
   текущий резолвер не читает. В extracted soundevents `.wav`/`.vsnd` соответствует
   фактический `.vsnd_c` в pak01.
7. **Паттерны** матчатся по полному списку файлов pak01, `**` поддерживается реализацией
   в `vpk_reader.py`. Новые паттерны всегда проверять на реальном архиве (раздел 5).
8. После обновлений Dota 2 мод надо переприменять — по дизайну, не баг.
9. Writer по-прежнему удаляет старый `pak02_dir.vpk` перед сборкой нового; не менять это
   поведение попутно без необходимости.
10. `git bash`: пути Windows в кавычках, trailing backslash перед кавычкой ломает quoting.
    Для Python не подставлять Git Bash `/tmp`: использовать Windows-путь или `tempfile`.

---

## 10. Конвенции

- Язык UI и логов — русский; код и комментарии — на английском/русском вперемешку
  (исторически), новые комментарии не добавлять без нужды.
- Логирование только через `GUILogger` (синглтон) — оно дублируется в GUI и файл.
  Диагностические полные списки пересечений/отсутствующих событий — через `debug()`.
- Долгие операции — только в `ProcessWorker(QThread)`, GUI не блокировать.
- Тестов нет; проверка = py_compile + превью UI + smoke-тест exe + верификация селекторов
  на реальном pak01 + проверка содержимого итогового VPK. In-game эффект не считать
  подтверждённым без ручной проверки пользователем.
- `.gitignore`: `build/`, `dist/`, `tools/vpk`, `tools/vrf`, `*.spec`-артефакты сборки.
- Репозиторий: https://github.com/Qoonolite/dota2-silencer-mod (ветка `master`).
