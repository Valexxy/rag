import uvicorn
import os
import sys
from keep_alive_worker import start_keep_alive_background_thread

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"[SERVER START]: Starting Sovereign AI Commerce Web Server on port {port}...")
    start_keep_alive_background_thread()
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
