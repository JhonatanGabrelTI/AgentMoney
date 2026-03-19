"""
Classe base abstrata para uploaders de vídeo.
Define a interface comum para todas as plataformas.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

from core_engine.logger import get_logger

logger = get_logger(__name__)


@dataclass
class UploadResult:
    """Resultado de um upload."""
    success: bool
    platform: str
    video_id: Optional[str] = None
    url: Optional[str] = None
    error_message: Optional[str] = None
    uploaded_at: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.uploaded_at is None:
            self.uploaded_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class VideoMetadata:
    """Metadados de vídeo para upload."""
    title: str
    description: str
    tags: list
    category: str
    thumbnail_path: Optional[str] = None
    # Configurações específicas por plataforma
    visibility: str = "public"  # public, unlisted, private, friends
    allow_comments: bool = True
    allow_duet: bool = True  # TikTok/Kwai
    allow_stitch: bool = True  # TikTok
    scheduled_time: Optional[str] = None  # ISO format
    # Shorts/Reels específico
    is_short: bool = False


class BaseUploader(ABC):
    """
    Classe base para todos os uploaders de vídeo.
    
    Cada plataforma deve implementar:
    - authenticate()
    - upload()
    - delete()
    - get_analytics() (opcional)
    """
    
    PLATFORM_NAME: str = "base"
    MAX_FILE_SIZE_MB: int = 500
    SUPPORTED_FORMATS: tuple = (".mp4", ".mov", ".avi")
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.authenticated = False
        self.logger = get_logger(f"{self.PLATFORM_NAME}_uploader")
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Autentica na plataforma.
        
        Returns:
            True se autenticado com sucesso
        """
        pass
    
    @abstractmethod
    def upload(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        """
        Faz upload de um vídeo.
        
        Args:
            video_path: Caminho do arquivo de vídeo
            metadata: Metadados do vídeo
            
        Returns:
            UploadResult com status e detalhes
        """
        pass
    
    def upload_short(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        """
        Faz upload como vídeo curto (Shorts/Reels).
        Por padrão delega para upload() com flag is_short.
        
        Args:
            video_path: Caminho do arquivo
            metadata: Metadados
            
        Returns:
            UploadResult
        """
        metadata.is_short = True
        return self.upload(video_path, metadata)
    
    @abstractmethod
    def delete(self, video_id: str) -> bool:
        """
        Remove um vídeo da plataforma.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            True se removido com sucesso
        """
        pass
    
    def get_analytics(self, video_id: str) -> Dict[str, Any]:
        """
        Recupera estatísticas do vídeo.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Dicionário com métricas
        """
        # Opcional - não todas as plataformas suportam
        return {}
    
    def validate_video(self, video_path: str) -> tuple[bool, str]:
        """
        Valida se o vídeo pode ser uploadado.
        
        Args:
            video_path: Caminho do arquivo
            
        Returns:
            (válido, mensagem de erro)
        """
        from pathlib import Path
        
        path = Path(video_path)
        
        # Verifica existência
        if not path.exists():
            return False, f"Arquivo não encontrado: {video_path}"
        
        # Verifica formato
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return False, f"Formato não suportado: {path.suffix}"
        
        # Verifica tamanho
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            return False, f"Arquivo muito grande: {size_mb:.1f}MB (max: {self.MAX_FILE_SIZE_MB}MB)"
        
        return True, "OK"
    
    def _simulate_upload(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        """
        Simula upload para modo DEMO.
        
        Args:
            video_path: Caminho do vídeo
            metadata: Metadados
            
        Returns:
            UploadResult simulado
        """
        import uuid
        
        video_id = f"demo_{self.PLATFORM_NAME}_{uuid.uuid4().hex[:8]}"
        
        self.logger.info(f"[DEMO] Upload simulado para {self.PLATFORM_NAME}")
        self.logger.info(f"  Titulo: {metadata.title[:50]}...")
        self.logger.info(f"  Video ID: {video_id}")
        
        return UploadResult(
            success=True,
            platform=self.PLATFORM_NAME,
            video_id=video_id,
            url=f"https://{self.PLATFORM_NAME}.com/watch/{video_id}",
            metadata={
                "title": metadata.title,
                "description": metadata.description,
                "tags": metadata.tags,
                "is_short": metadata.is_short
            }
        )
