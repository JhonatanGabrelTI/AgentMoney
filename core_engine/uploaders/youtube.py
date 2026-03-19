"""
Uploader para YouTube.
Suporta vídeos longos e Shorts.
"""

from typing import Dict, Any
from core_engine.config import Config
from core_engine.uploaders.base import BaseUploader, VideoMetadata, UploadResult


class YouTubeUploader(BaseUploader):
    """Uploader para YouTube via API v3."""
    
    PLATFORM_NAME = "youtube"
    MAX_FILE_SIZE_MB = 5120  # 5GB para canais verificados
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = Config()
        super().__init__(config)
        self.client_id = getattr(config, 'YOUTUBE_CLIENT_ID', '')
        self.client_secret = getattr(config, 'YOUTUBE_CLIENT_SECRET', '')
        self.refresh_token = getattr(config, 'YOUTUBE_REFRESH_TOKEN', '')
        self.channel_id = getattr(config, 'YOUTUBE_CHANNEL_ID', '')
    
    def authenticate(self) -> bool:
        """Autentica com OAuth2."""
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            self.logger.warning("Credenciais YouTube não configuradas")
            return False
        
        # TODO: Implementar OAuth2 flow
        # from google.auth.transport.requests import Request
        # from google.oauth2.credentials import Credentials
        # 
        # credentials = Credentials.from_authorized_user_info({...})
        # self.youtube = build('youtube', 'v3', credentials=credentials)
        
        self.authenticated = True
        return True
    
    def upload(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        """Faz upload para YouTube."""
        # Validação
        valid, error = self.validate_video(video_path)
        if not valid:
            return UploadResult(success=False, platform=self.PLATFORM_NAME, error_message=error)
        
        # Modo DEMO
        config = Config()
        if config.IS_DEMO:
            return self._simulate_upload(video_path, metadata)
        
        # TODO: Implementar upload real
        # body = {
        #     'snippet': {
        #         'title': metadata.title,
        #         'description': metadata.description,
        #         'tags': metadata.tags,
        #         'categoryId': self._get_category_id(metadata.category)
        #     },
        #     'status': {
        #         'privacyStatus': metadata.visibility,
        #         'selfDeclaredMadeForKids': False
        #     }
        # }
        
        self.logger.info("YouTube upload não implementado em produção")
        return self._simulate_upload(video_path, metadata)
    
    def upload_short(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        """Faz upload como YouTube Short."""
        # Adiciona #Shorts na descrição
        if "#shorts" not in metadata.description.lower():
            metadata.description += "\n\n#Shorts"
        
        metadata.is_short = True
        return self.upload(video_path, metadata)
    
    def delete(self, video_id: str) -> bool:
        """Remove vídeo do YouTube."""
        # TODO: youtube.videos().delete(id=video_id).execute()
        return True
    
    def _get_category_id(self, category: str) -> str:
        """Mapeia categoria para ID do YouTube."""
        categories = {
            "music": "10",
            "entertainment": "24",
            "education": "27",
            "people": "22"
        }
        return categories.get(category, "22")  # Padrão: People & Blogs
    
    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Define thumbnail customizada."""
        # TODO: Implementar
        return True
    
    def add_to_playlist(self, video_id: str, playlist_id: str) -> bool:
        """Adiciona vídeo a playlist."""
        # TODO: Implementar
        return True
