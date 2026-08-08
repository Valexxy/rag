import os

def create_pwa_icons():
    os.makedirs("static", exist_ok=True)
    os.makedirs("dist/static", exist_ok=True)
    
    # Simple valid 1x1 PNG bytes as fallback PWA icon
    png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x00\x05\xfe\x02\xfe\xa7\x9a\x9a\xe7\x00\x00\x00\x00IEND\xaeB`\x82'
    
    for path in ["static/icon-192.png", "static/icon-512.png", "dist/static/icon-192.png", "dist/static/icon-512.png"]:
        with open(path, "wb") as f:
            f.write(png_bytes)

if __name__ == "__main__":
    create_pwa_icons()
    print("[ICONS CREATED SUCCESSFUL]")
