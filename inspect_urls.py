import os, re

for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith(('.py', '.env', '.json', '.md')):
            fp = os.path.join(root, f)
            try:
                content = open(fp, 'r', encoding='utf-8', errors='ignore').read()
                matches = re.findall(r'https?://[^\s\"\'\`]+', content)
                render_urls = [m for m in matches if 'render' in m or 'ngrok' in m]
                if render_urls:
                    print(f"{fp}:")
                    for u in set(render_urls):
                        print("  ", u)
            except Exception:
                pass
