from dataclasses import dataclass
from typing import Optional, Tuple, Union


MAIN_CHAT_SCRIPT = "scripts/chat_wheel.txt"
CHAT_CATEGORIES_SCRIPT = "scripts/chat_wheel_categories.txt"
HERO_CHAT_SCRIPT = "scripts/chat_wheel_heroes.txt"
TI2021_CHAT_SCRIPT = "scripts/chat_wheels/ti2021_casters_chat_wheel.txt"

TI_PATTERN = r"(?:^|[_.\-/])ti_?\d+|the_?international|voice_?of_?god|voiceofgod"
EVENT_PATTERN = (
    r"crownfall|dark_carnival|frostivus|diretide|fall_?2021|greevil|"
    r"new_?bloom|new_?year|winter_?2021|halloween|dota_10th_anniversary|"
    r"announcer_dlc_gaben|(?:^|[_.\-/])ddb_"
)


@dataclass(frozen=True)
class PathSelector:
    pattern: str
    stub: str = "sound"
    exclude_prefixes: Tuple[str, ...] = ()
    exclude_regex: Optional[str] = None


@dataclass(frozen=True)
class ChatSelector:
    script: str = MAIN_CHAT_SCRIPT
    categories: Tuple[str, ...] = ()
    category_script: str = CHAT_CATEGORIES_SCRIPT
    include_regex: Optional[str] = None
    exclude_regex: Optional[str] = None


Selector = Union[PathSelector, ChatSelector]


@dataclass(frozen=True)
class Category:
    label: str
    description: str
    default: bool
    selectors: Tuple[Selector, ...]
    tooltip: str = ""
    warning: str = ""
    safe_file_pattern: Optional[str] = None
    exclude_categories: Tuple[str, ...] = ()


CATEGORIES = {
    "dota_plus": Category(
        label="Dota Plus и саундборд",
        description="Классические и общие звуковые эффекты",
        default=True,
        selectors=(
            PathSelector(
                "sounds/misc/soundboard/**/*.vsnd_c",
                exclude_regex=f"{TI_PATTERN}|{EVENT_PATTERN}",
            ),
            ChatSelector(categories=("dota_plus_sounds",)),
            ChatSelector(exclude_regex=f"{TI_PATTERN}|{EVENT_PATTERN}"),
        ),
        tooltip="Барабанная дробь, сверчки, смех, аплодисменты и другие общие эффекты колеса чата.",
    ),
    "international": Category(
        label="The International",
        description="Комментаторы и эффекты TI разных лет",
        default=True,
        selectors=(
            PathSelector("sounds/misc/soundboard/ti*.vsnd_c"),
            ChatSelector(
                categories=(
                    "voice_of_god",
                    "ti13_caster_chat_wheel_legacy",
                    "ti12_caster_chat_wheel_en",
                    "ti12_caster_chat_wheel_sp",
                    "ti12_caster_chat_wheel_pt",
                    "ti12_caster_chat_wheel_ru",
                    "ti12_caster_chat_wheel_cn",
                    "ti12_caster_chat_wheel_legacy",
                ),
                include_regex=TI_PATTERN,
            ),
            ChatSelector(script=TI2021_CHAT_SCRIPT),
        ),
        tooltip="TI10–TI13, старые сообщения TI, отдельный набор комментаторов TI2021 и Voice of God 2025.",
    ),
    "community": Category(
        label="Кастеры и сообщество",
        description="Пакеты личностей сообщества, сезоны 11–13",
        default=True,
        selectors=(PathSelector("sounds/talentcontent/**/*.vsnd_c"),),
        tooltip="Звуковые наборы из sounds/talentcontent. Командные фанатские наборы сюда не входят.",
    ),
    "team_fans": Category(
        label="Фанатские наборы команд",
        description="Сезонные и командные наборы, кроме TI2021",
        default=True,
        selectors=(PathSelector("sounds/teamfancontent/**/*.vsnd_c"),),
        tooltip="Содержимое sounds/teamfancontent. Файлы отдельного набора комментаторов TI2021 относятся к The International.",
        exclude_categories=("international",),
    ),
    "hero_chat": Category(
        label="Реплики героев в колесе",
        description="По умолчанию только специальные реплики",
        default=False,
        selectors=(ChatSelector(script=HERO_CHAT_SCRIPT),),
        tooltip="Официальные сообщения из chat_wheel_heroes.txt. Безопасный режим выбирает только выделенные файлы *_wheel_*.",
        warning="Полный режим также заглушает часть обычных реплик героев вне колеса чата.",
        safe_file_pattern="*_wheel_*",
    ),
    "taunts": Category(
        label="Насмешки героев",
        description="Только звук, без изменения анимаций",
        default=False,
        selectors=(
            PathSelector(
                "sounds/vo/**/*taunt*.vsnd_c",
                exclude_prefixes=("sounds/vo/siltbreaker/",),
            ),
            PathSelector("sounds/weapons/hero/**/*taunt*.vsnd_c"),
        ),
        tooltip="Голосовые и игровые звуки обычных насмешек. Siltbreaker, модели, анимации и частицы не затрагиваются.",
    ),
    "seasonal_events": Category(
        label="Реплики сезонных событий",
        description="Crownfall, Diretide, Frostivus и другие",
        default=True,
        selectors=(
            ChatSelector(
                categories=(
                    "crownfall_chat_wheel",
                    "dark_carnival_chat_wheel",
                    "frostivus_2024_sounds",
                    "dota_10th_anniversary",
                ),
                include_regex=EVENT_PATTERN,
            ),
            PathSelector("sounds/misc/chatwheel/**/*.vsnd_c"),
            PathSelector("sounds/misc/soundboard/fall2021*.vsnd_c"),
            PathSelector("sounds/misc/soundboard/diretide*.vsnd_c"),
            PathSelector("sounds/misc/soundboard/frostivus*.vsnd_c"),
            PathSelector("sounds/misc/soundboard/greevil*.vsnd_c"),
        ),
        tooltip="Точные сообщения Crownfall, Dark Carnival, Frostivus, Dragon's Blood, Diretide, fall2021 и 10-летия Dota 2.",
    ),
    "sprays": Category(
        label="Граффити и звук напыления",
        description="Прозрачные текстуры и тишина при напылении",
        default=True,
        selectors=(
            PathSelector("materials/particle/sprays/**/*.vtex_c", stub="texture"),
            PathSelector("sounds/misc/spraypaint.vsnd_c"),
        ),
        tooltip="Все текстуры из materials/particle/sprays и звук spraypaint. Другие визуальные эффекты не изменяются.",
    ),
}

HERO_FULL_CONFIG_KEY = "hero_full"
