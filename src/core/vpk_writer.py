import sys
import shutil
import subprocess
from pathlib import Path


class VPKWriterV1:
    def __init__(self, output_path: Path):
        self.output_path = output_path
        self.files = {}
        self.vpk_exe = self._find_vpk_exe()

    def _find_vpk_exe(self) -> Path:
        if getattr(sys, 'frozen', False):
            base = Path(sys.executable).parent
        else:
            base = Path(__file__).parent.parent.parent

        possible = [
            base / "tools" / "vpk" / "vpk.exe",
            base / "tools" / "vpk.exe",
            base / "vpk.exe",
            Path.cwd() / "tools" / "vpk" / "vpk.exe",
            Path.cwd() / "vpk.exe",
        ]
        for p in possible:
            if p.exists():
                return p
        raise FileNotFoundError(
            "vpk.exe не найден. Убедитесь, что он есть в папке tools/vpk/ рядом с программой."
        )

    def add_file(self, internal_path: str, data: bytes):
        clean_path = internal_path.replace("\\", "/").lstrip("/")
        self.files[clean_path] = data

    def build(self) -> Path:
        print(f"Подготовка {len(self.files)} файлов для упаковки...")
        pack_dir = self.output_path.parent / self.output_path.stem
        if pack_dir.exists():
            shutil.rmtree(pack_dir)
        pack_dir.mkdir(parents=True)

        for internal_path, data in self.files.items():
            target_file = pack_dir / internal_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            with open(target_file, "wb") as f:
                f.write(data)

        print("Упаковка через vpk.exe...")
        cmd = [str(self.vpk_exe), pack_dir.name]
        result = subprocess.run(
            cmd,
            cwd=str(pack_dir.parent),
            capture_output=True,
            text=True
        )
        shutil.rmtree(pack_dir, ignore_errors=True)

        if result.returncode != 0:
            print(f"vpk.exe stdout: {result.stdout}")
            print(f"vpk.exe stderr: {result.stderr}")
            raise RuntimeError(f"vpk.exe завершился с кодом {result.returncode}")

        if not self.output_path.exists():
            raise RuntimeError(f"vpk.exe не создал файл: {self.output_path}")

        size_mb = self.output_path.stat().st_size / (1024 * 1024)
        print(f"✅ VPK создан: {self.output_path} ({size_mb:.2f} МБ)")
        return self.output_path