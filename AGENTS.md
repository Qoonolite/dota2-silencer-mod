# Dota 2 Silencer — документация для разработчика / агента

Полное описание проекта: что это, как устроено, что установить и как собрать.
Читать целиком перед любыми изменениями.

---

## 1. Что делает проект

Windows-утилита с GUI (PyQt6), которая отключает раздражающий контент в Dota 2:

- **Звуковые фразы колеса чата** (компендиумы, фанатские наборы, саундборд, события);
- **Граффити (спреи)** — текстуры и звук напыления.

**Принцип работы:** Dota 2 подгружает языковую папку `game/dota_russian` поверх основных
архивов. Программа находит целевые файлы в `game/dota/pak01_dir.vpk`, берёт файлы-заглушки
(тишина / прозрачная текстура) и упаковывает их под именами оригиналов в
`game/dota_russian/pak02_dir.vpk`. Оригинальные файлы игры **не изменяются**.
Удаление `pak02_dir.vpk` полностью откатывает мод.

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
| `vrf_cli.exe` | последний релиз | Чтение/листинг VPK-архивов Source 2. Источник: [ValveResourceFormat](https://github.com/ValveResourceFormat/ValveResourceFormat/) → `cli-windows-x64.zip` |
| `vpk.exe` | из Source **1** SDK | Упаковка итогового VPK v1. Именно Source 1 — его формат читает `dota_russian` |
| vdf, numpy | см. requirements.txt | Парсинг `libraryfolders.vdf` (поиск Steam-библиотек), служебное |

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
│   ├── app.py                 ← QMainWindow: заголовок, иконка, размеры окна
│   ├── core/
│   │   ├── processor.py       ← SoundProcessor: поиск файлов по паттернам, сборка pak02_dir.vpk.
│   │   │                        Поддерживает типы заглушек: STUB_FILES = {sound, texture}
│   │   ├── vpk_reader.py      ← VPKReader: листинг pak01_dir.vpk через vrf_cli,
│   │   │                        find_files_by_pattern (fnmatch + **)
│   │   ├── vpk_writer.py      ← VPKWriterV1: обёртка над vpk.exe (Source 1),
│   │   │                        ищет vpk.exe в tools/vpk/ рядом с exe/проектом
│   │   └── path_finder.py     ← автопоиск dota 2 beta: реестр Steam, libraryfolders.vdf,
│   │                            стандартные пути; validate_user_path()
│   ├── ui/
│   │   ├── main_window.py     ← главное окно: CATEGORIES (паттерны+заглушки), чекбоксы,
│   │   │                        ProcessWorker (QThread), прогресс, лог. СМ. РАЗДЕЛ 6
│   │   ├── path_dialog.py     ← диалог ручного выбора пути к игре
│   │   ├── progress_dialog.py ← (legacy, не используется в основном потоке)
│   │   └── styles.py          ← DARK_THEME: вся QSS-тема (Google Material dark gray)
│   ├── utils/
│   │   ├── config.py          ← Config (синглтон, JSON): путь к игре, cat_<id> чекбоксы
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

Проверка паттернов против реального архива игры:

```bash
.venv/Scripts/python.exe -c "
import sys; sys.path.insert(0, 'src')
from pathlib import Path
from core.vpk_reader import VPKReader
r = VPKReader(Path('D:/SteamLibrary/steamapps/common/dota 2 beta/game/dota/pak01_dir.vpk'))
print(len(r.find_files_by_pattern('materials/particle/sprays/**/*.vtex_c')))
"
```

---

## 6. Ключевая логика: категории и заглушки

Категории объявлены в `src/ui/main_window.py` → `CATEGORIES`:

```python
CATEGORIES = {
    "wheel_sounds": {
        "label": "Звуковые фразы колеса чата",
        "patterns": [
            ("sounds/talentcontent/**/*.vsnd_c", "sound"),
            ("sounds/teamfancontent/**/*.vsnd_c", "sound"),
            ("sounds/misc/chatwheel/**/*.vsnd_c", "sound"),
            ("sounds/misc/soundboard/**/*.vsnd_c", "sound"),
            ("sounds/misc/crownfall/**/*.vsnd_c", "sound"),
        ],
    },
    "sprays": {
        "label": "Граффити (спреи) и их звук",
        "patterns": [
            ("materials/particle/sprays/**/*.vtex_c", "texture"),
            ("sounds/misc/spraypaint.vsnd_c", "sound"),
        ],
    },
}
```

- Каждый паттерн привязан к типу заглушки (`sound` | `texture`), типы → файлы в
  `STUB_FILES` в `src/core/processor.py`.
- Чекбоксы и их персистентность (`cat_<id>` в конфиге) создаются автоматически из
  этого словаря — **новая категория = одна запись в CATEGORIES + заглушка, если нужен
  новый тип**.
- Результат всегда один файл: `game/dota_russian/pak02_dir.vpk` (содержит только
  выбранные категории). Перед записью старый файл удаляется.

Как добавить категорию (пример): отключить музыку —
добавить запись `"music": {"label": "Музыка", "patterns": [("sounds/music/**/*.vsnd_c", "sound")]}`
и проверить паттерн скриптом из раздела 5.

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
Текущая версия отображается в шапке окна (`main_window.py`, label `version`) —
**не забыть поднять перед сборкой**.

---

## 8. Конфиг и логи (runtime)

| Что | Запуск из исходников | Запуск exe |
|---|---|---|
| `config.json` | `%APPDATA%\DotaSoundSilencer\` | `<папка exe>\DotaSoundSilencer\` |
| `app.log` | `%APPDATA%\DotaSoundSilencer\logs\` | тот же `%APPDATA%` |

Ключи конфига: `dota_path`, `cat_wheel_sounds`, `cat_sprays` (bool, по умолчанию true).

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
6. **Паттерны** матчатся по полному списку файлов pak01 (~500 тыс. записей), `**`
   поддерживается реализацией в `vpk_reader.py`. Новые паттерны всегда проверять на
   реальном архиве (раздел 5).
7. После обновлений Dota 2 мод надо переприменять — по дизайну, не баг.
8. `git bash`: пути Windows в кавычках, trailing backslash перед кавычкой ломает quoting.

---

## 10. Конвенции

- Язык UI и логов — русский; код и комментарии — на английском/русском вперемешку
  (исторически), новые комментарии не добавлять без нужды.
- Логирование только через `GUILogger` (синглтон) — оно дублируется в GUI и файл.
- Долгие операции — только в `ProcessWorker(QThread)`, GUI не блокировать.
- Тестов нет; проверка = py_compile + превью UI + smoke-тест exe + верификация паттернов
  на реальном pak01.
- `.gitignore`: `build/`, `dist/`, `tools/vpk`, `tools/vrf`, `*.spec`-артефакты сборки.
- Репозиторий: https://github.com/Qoonolite/dota2-silencer-mod (ветка `master`).
