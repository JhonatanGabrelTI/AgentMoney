"""
Uploader para Instagram.
Suporta Reels, Posts e Stories.
"""

from typing import Dict, Any
from core_engine.config import Config
from core_engine.uploaders.base import BaseUploader, VideoMetadata, UploadResult


class InstagramUploader(BaseUploader):
    """Uploader para Instagram via Graph API."""
    
    PLATFORM_NAME = "instagram"
    MAX_FILE_SIZE_MB = 100  # 100MB para Reels
    SUPPORTED_FORMATS = (".mp4", ".mov")
    
    # Ratio specs
    REELS_RATIO = (9, 16)  # 9:16 vertical
    POST_RATIO = (1, 1)    # 1:1 square ou 4:5
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = Config()
        super().__init__(config)
        self.access_token = getattr(config, 'INSTAGRAM_ACCESS_TOKEN', '')
        self.account_id = getattr(config, 'INSTAGRAM_ACCOUNT_ID', '')
        self.app_id = getattr(config, 'INSTAGRAM_APP_ID', '')
        self.app_secret = getattr(config, 'INSTAGRAM_APP_SECRET', '')
    
    def authenticate(self) -> bool:
        """Autentica com Instagram Graph API."""
        if not all([self.access_token, self.account_id]):
            self.logger.warning("Credenciais Instagram não configuradas")
            return False
        
        # TODO: Validar token
        self.authenticated = True
        return True
    
    def upload(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        """Faz upload como Reel (formato mais engajado)."""
        return self.upload_reel(video_path, metadata)
    
    def upload_reel(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        """Faz upload especificamente como Reel."""
        valid, error = self.validate_video(video_path)
        if not valid:
            return UploadResult(success=False, platform=self.PLATFORM_NAME, error_message=error)
        
        metadata.is_short = True
        
        config = Config()
        if config.IS_DEMO:
            return self._simulate_upload(video_path, metadata)
        
        # TODO: Implementar via Instagram Graph API
        # 1. Criar container
        # POST /{ig-user-id}/media
        # 2. Fazer upload do vídeo
        # 3. Publicar container
        # POST /{ig-user-id}/media_publish
        
        self.logger.info("Instagram Reels upload não implementado em produção")
        return self._simulate_upload(video_path, metadata)
    
    def upload_post(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        """Faz upload como post no feed (vídeo quadrado)."""
        metadata.is_short = False
        
        # Ajusta ratio para 1:1 se necessário
        # TODO: Implementar conversão de ratio
        
        return self.upload(video_path, metadata)
    
    def upload_story(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        """Faz upload como Story."""
        # Stories têm duração máxima de 15s por segmento
        # TODO: Implementar splitting se necessário
        
        config = Config()
        if config.IS_DEMO:
            result = self._simulate_upload(video_path, metadata)
            result.metadata["type"] = "story"
            return result
        
        return self._simulate_upload(video_path, metadata)
    
    def delete(self, media_id: str) -> bool:
        """Remove mídia do Instagram."""
        # TODO: DELETE /{media-id}
        return True
    
    def get_analytics(self, media_id: str) -> Dict[str, Any]:
        """Recupera estatísticas da mídia."""
        # TODO: GET /{ig-media-id}/insights
        return {
            "impressions": 0,
            "reach": 0,
            "engagement": 0,
            "saves": 0
        }
