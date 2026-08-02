import sys
import subprocess
import fnmatch
import re
from pathlib import Path
from typing import List, Optional


class VPKReader:
    def __init__(self, vpk_path: Path):
        self.vpk_path = vpk_path
        self.file_list: List[str] = []
        self.vrf_cli_path: Optional[Path] = None
        self._find_vrf_cli()
        if self.vrf_cli_path:
            self._load_file_list()
        else:
            print("⚠️ VRF CLI не найден. Чтение VPK невозможно.")

    def _find_vrf_cli(self) -> None:
        if getattr(sys, 'frozen', False):
            base = Path(sys.executable).parent
        else:
            base = Path(__file__).parent.parent.parent

        possible = [
            base / "tools" / "vrf" / "vrf_cli.exe",
            base / "vrf_cli.exe",
            Path.cwd() / "tools" / "vrf" / "vrf_cli.exe",
            Path.cwd() / "vrf_cli.exe",
        ]
        for p in possible:
            if p.exists():
                self.vrf_cli_path = p
                print(f"Найден VRF CLI: {p}")
                return
        print("VRF CLI не найден. Проверьте наличие tools/vrf/vrf_cli.exe рядом с программой.")

    def _load_file_list(self):
        try:
            cmd = [str(self.vrf_cli_path), "-i", str(self.vpk_path), "--vpk_list"]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if result.returncode != 0:
                print(f"VRF CLI ошибка: {result.stderr}")
                return
            path_regex = re.compile(r'([a-zA-Z0-9_\-\.]+(?:/[a-zA-Z0-9_\-\.]+)+\.[a-zA-Z0-9_\-]+)')
            for line in result.stdout.splitlines():
                match = path_regex.search(line)
                if match:
                    self.file_list.append(match.group(1).replace('\\', '/'))
            print(f"✓ Загружено {len(self.file_list)} файлов из VPK")
        except Exception as e:
            print(f"Ошибка вызова VRF CLI: {e}")

    def find_files_by_pattern(self, pattern: str) -> List[str]:
        matches = []
        if "**" in pattern:
            parts = pattern.split("**", 1)
            prefix = parts[0].rstrip("/")
            suffix = parts[1].lstrip("/")
            for fp in self.file_list:
                if prefix and not fp.startswith(prefix + "/"):
                    continue
                remainder = fp[len(prefix) + 1:] if prefix else fp
                if fnmatch.fnmatch(remainder, suffix):
                    matches.append(fp)
        else:
            for fp in self.file_list:
                if fnmatch.fnmatch(fp, pattern):
                    matches.append(fp)
        return matches

    def get_sample_files(self, count: int = 10) -> List[str]:
        return self.file_list[:count]