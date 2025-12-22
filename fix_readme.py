
file_path = r"d:\1222\NeuroNova_v1\NeuroNova_02_back_end\README.md"
try:
    with open(file_path, "rb") as f:
        content = f.read()
    
    # Replace null bytes with '0'
    new_content = content.replace(b'\x00', b'0')
    
    with open(file_path, "wb") as f:
        f.write(new_content)
        
    print("Fixed file. New length:", len(new_content))
except Exception as e:
    print(f"Error: {e}")
