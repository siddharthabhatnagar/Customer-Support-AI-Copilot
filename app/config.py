import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    def __init__(self):
        self.groq_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
        self.nvidia_api_key: str = os.getenv("NVIDIA_API_KEY", "").strip()
        self.groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        self.nvidia_embedding_model: str = os.getenv("NVIDIA_EMBEDDING_MODEL", "nvidia/nv-embedqa-e5-v5").strip()
        self.port: int = int(os.getenv("PORT", "8000"))

    def update_keys(self, groq_key: str = None, nvidia_key: str = None, groq_model: str = None, nvidia_model: str = None):
        if groq_key is not None:
            self.groq_api_key = groq_key.strip()
            os.environ["GROQ_API_KEY"] = self.groq_api_key
        if nvidia_key is not None:
            self.nvidia_api_key = nvidia_key.strip()
            os.environ["NVIDIA_API_KEY"] = self.nvidia_api_key
        if groq_model is not None and groq_model.strip():
            self.groq_model = groq_model.strip()
            os.environ["GROQ_MODEL"] = self.groq_model
        if nvidia_model is not None and nvidia_model.strip():
            self.nvidia_embedding_model = nvidia_model.strip()
            os.environ["NVIDIA_EMBEDDING_MODEL"] = self.nvidia_embedding_model

        # Optionally persist to .env
        try:
            env_file = BASE_DIR / ".env"
            lines = []
            if env_file.exists():
                with open(env_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            
            key_map = {
                "GROQ_API_KEY": self.groq_api_key,
                "NVIDIA_API_KEY": self.nvidia_api_key,
                "GROQ_MODEL": self.groq_model,
                "NVIDIA_EMBEDDING_MODEL": self.nvidia_embedding_model,
            }
            
            new_lines = []
            written_keys = set()
            for line in lines:
                matched = False
                for k, v in key_map.items():
                    if line.startswith(f"{k}="):
                        new_lines.append(f"{k}={v}\n")
                        written_keys.add(k)
                        matched = True
                        break
                if not matched:
                    new_lines.append(line)
            
            for k, v in key_map.items():
                if k not in written_keys:
                    new_lines.append(f"{k}={v}\n")
            
            with open(env_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except Exception:
            pass

    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key and self.groq_api_key.startswith("gsk_"))

    @property
    def has_nvidia(self) -> bool:
        return bool(self.nvidia_api_key and self.nvidia_api_key.startswith("nvapi-"))

settings = Settings()
