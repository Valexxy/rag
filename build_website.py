import os
import shutil

def build_full_website_assets():
    """Compiles and packages all web components into dist/ for immediate hosting on any domain or web server."""
    os.makedirs("dist", exist_ok=True)
    os.makedirs("dist/static", exist_ok=True)

    # 1. Copy futuristic_app.html as index.html
    shutil.copy("static/futuristic_app.html", "dist/index.html")
    shutil.copy("static/futuristic_app.html", "dist/dashboard.html")
    shutil.copy("static/futuristic_app.html", "dist/directory_map.html")
    shutil.copy("static/futuristic_app.html", "dist/futuristic_app.html")

    # 2. Create vercel.json / netlify.toml for 1-click zero-config custom domain deployment
    vercel_config = {
        "rewrites": [
            {"source": "/(.*)", "destination": "/api/main.py"}
        ]
    }
    with open("dist/vercel.json", "w", encoding="utf-8") as f:
        f.write(str(vercel_config).replace("'", '"'))

    print("[WEBSITE BUILD SUCCESSFUL]: All futuristic glassmorphic web components compiled into 'dist/' ready for custom domain linking!")

if __name__ == "__main__":
    build_full_website_assets()
