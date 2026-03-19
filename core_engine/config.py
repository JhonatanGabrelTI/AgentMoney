"""
Configuração central do AgentMoney.
Carrega variáveis de ambiente e define constantes.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega .env se existir
load_dotenv()

class Config:
    """Configurações do sistema AgentMoney."""
    
    # Modo de operação
    MODE = os.getenv("AGENTMONEY_MODE", "demo")
    LOG_LEVEL = os.getenv("AGENTMONEY_LOG_LEVEL", "INFO")
    
    # Diretórios
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
    LOGS_DIR = BASE_DIR / os.getenv("LOGS_DIR", "logs")
    ASSETS_DIR = BASE_DIR / os.getenv("ASSETS_DIR", "assets")
    
    # Subdiretórios de assets
    AUDIO_DIR = ASSETS_DIR / "audio"
    VIDEO_DIR = ASSETS_DIR / "video"
    THUMBNAILS_DIR = ASSETS_DIR / "thumbnails"
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "demo-key")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Música IA
    SUNO_API_KEY = os.getenv("SUNO_API_KEY", "demo-key")
    UDIO_API_KEY = os.getenv("UDIO_API_KEY", "demo-key")
    
    # Imagem IA
    MIDJOURNEY_API_KEY = os.getenv("MIDJOURNEY_API_KEY", "demo-key")
    DALL_E_API_KEY = os.getenv("DALL_E_API_KEY", "demo-key")
    
    # YouTube
    YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
    YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
    YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")
    YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")
    
    # Shopee
    SHOPEE_AFFILIATE_ID = os.getenv("SHOPEE_AFFILIATE_ID", "")
    SHOPEE_AFFILIATE_TOKEN = os.getenv("SHOPEE_AFFILIATE_TOKEN", "")
    SHOPEE_APP_KEY = os.getenv("SHOPEE_APP_KEY", "")
    SHOPEE_APP_SECRET = os.getenv("SHOPEE_APP_SECRET", "")
    SHOPEE_REGION = os.getenv("SHOPEE_REGION", "BR")
    SHOPEE_COOKIES_PATH = BASE_DIR / os.getenv("SHOPEE_COOKIES_PATH", "data/shopee_cookies.json")
    
    # Redes Sociais
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
    
    # Limites diários
    SHOPEE_DAILY_PRODUCT_LIMIT = int(os.getenv("SHOPEE_DAILY_PRODUCT_LIMIT", "10"))
    YOUTUBE_DAILY_VIDEO_LIMIT = int(os.getenv("YOUTUBE_DAILY_VIDEO_LIMIT", "1"))
    
    # Browser
    BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
    BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/agentmoney.db")
    
    # Flags
    IS_DEMO = MODE == "demo"
    
    @classmethod
    def ensure_directories(cls):
        """Cria diretórios necessários se não existirem."""
        dirs = [
            cls.DATA_DIR,
            cls.LOGS_DIR,
            cls.ASSETS_DIR,
            cls.AUDIO_DIR,
            cls.VIDEO_DIR,
            cls.THUMBNAILS_DIR
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Valida configurações essenciais."""
        if cls.IS_DEMO:
            return True, "Modo DEMO ativo - APIs simuladas"
        
        missing = []
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "demo-key":
            missing.append("OPENAI_API_KEY")
        if not cls.YOUTUBE_CLIENT_ID:
            missing.append("YOUTUBE_CLIENT_ID")
        if not cls.SHOPEE_AFFILIATE_ID:
            missing.append("SHOPEE_AFFILIATE_ID")
            
        if missing:
            return False, f"Variáveis ausentes: {', '.join(missing)}"
        return True, "Configuração válida"
