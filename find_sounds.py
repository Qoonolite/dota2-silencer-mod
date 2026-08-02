import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.vpk_reader import VPKReader

vpk_path = Path(r"D:\SteamLibrary\steamapps\common\dota 2 beta\game\dota\pak01_dir.vpk")
reader = VPKReader(vpk_path)

# Ищем все .vsnd_c файлы, содержащие 'talentcontent' или 'teamfancontent'
talent_sounds = [f for f in reader.file_list if 'talentcontent' in f.lower() and f.endswith('.vsnd_c')]
teamfan_sounds = [f for f in reader.file_list if 'teamfancontent' in f.lower() and f.endswith('.vsnd_c')]

print(f"Звуков с 'talentcontent': {len(talent_sounds)}")
print(f"Звуков с 'teamfancontent': {len(teamfan_sounds)}")

print("\nПервые 20 звуков talentcontent:")
for f in talent_sounds[:20]:
    print(f"  {f}")

print("\nПервые 20 звуков teamfancontent:")
for f in teamfan_sounds[:20]:
    print(f"  {f}")

# Если не нашли, ищем просто все .vsnd_c в папке sounds/
if not talent_sounds and not teamfan_sounds:
    print("\n=== Не нашли звуки в talentcontent/teamfancontent ===")
    print("Ищем все .vsnd_c файлы в sounds/...")
    
    all_sounds = [f for f in reader.file_list if f.startswith('sounds/') and f.endswith('.vsnd_c')]
    print(f"Всего звуков в sounds/: {len(all_sounds)}")
    
    # Ищем звуки с 'talent' или 'fan' в имени
    talent_like = [f for f in all_sounds if 'talent' in f.lower() or 'fan' in f.lower()]
    print(f"Звуков с 'talent' или 'fan' в имени: {len(talent_like)}")
    
    print("\nПервые 20 таких звуков:")
    for f in talent_like[:20]:
        print(f"  {f}")