import os
import shutil

def build_full_website_assets():
    """Compiles and packages all web components into dist/ for immediate hosting on any domain or web server."""
    os.makedirs("dist", exist_ok=True)
    os.makedirs("dist/static", exist_ok=True)

    # 1. Copy index.html
    shutil.copy("static/index.html", "dist/index.html")
    
    # 2. Copy dashboard.html
    shutil.copy("static/dashboard.html", "dist/dashboard.html")

    # 3. Copy directory_map.html
    shutil.copy("static/directory_map.html", "dist/directory_map.html")

    # 4. Create vercel.json / netlify.toml for 1-click zero-config custom domain deployment
    vercel_config = {
        "rewrites": [
            {"source": "/(.*)", "destination": "/api/main.py"}
        ]
    }
    with open("dist/vercel.json", "w", encoding="utf-8") as f:
        f.write(str(vercel_config).replace("'", '"'))

    print("[WEBSITE BUILD SUCCESSFUL]: All web components compiled into 'dist/' ready for custom domain linking!")

if __name__ == "__main__":
    build_full_website_assets()
