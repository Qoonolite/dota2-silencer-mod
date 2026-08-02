from pathlib import Path

# Путь к вашему .vsnd_c файлу
file_path = Path(r"D:\temp\123044675_2.vsnd_c")

if file_path.exists():
    with open(file_path, "rb") as f:
        data = f.read(100)  # Читаем первые 100 байт
    
    print("Первые 100 байт файла (hex):")
    print(" ".join(f"{b:02x}" for b in data))
    
    print("\nВ формате с адресами:")
    for i in range(0, len(data), 16):
        hex_part = " ".join(f"{b:02x}" for b in data[i:i+16])
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in data[i:i+16])
        print(f"{i:04x}: {hex_part:<48s} {ascii_part}")
else:
    print(f"Файл не найден: {file_path}")