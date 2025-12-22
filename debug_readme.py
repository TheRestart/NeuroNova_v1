
import sys

file_path = r"d:\1222\NeuroNova_v1\NeuroNova_02_back_end\README.md"
try:
    with open(file_path, "rb") as f:
        content = f.read()
    print(f"Length: {len(content)}")
    print(f"First 20 bytes: {content[:20]}")
    print(f"Content repr: {repr(content)}")
except Exception as e:
    print(f"Error: {e}")
