"""Local entrypoint script to launch Customer Support AI Copilot server."""
import os
import uvicorn
from app.config import settings

if __name__ == "__main__":
    port = int(os.environ.get("PORT", settings.port or 8000))
    print(f"Starting Customer Support AI Copilot on http://localhost:{port}")
    print(f"Groq Model: {settings.groq_model}")
    print(f"NVIDIA Model: {settings.nvidia_embedding_model}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
