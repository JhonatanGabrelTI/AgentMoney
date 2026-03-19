"""
Uploader para YouTube.
Suporta vídeos longos e Shorts.
"""

from typing import Dict, Any, List
from core_engine.config import Config
from core_engine.uploaders.base import BaseUploader, VideoMetadata, UploadResult


class YouTubeUploader(BaseUploader):
    """Uploader para YouTube via API v3."""
    
    PLATFORM_NAME = "youtube"
    MAX_FILE_SIZE_MB = 5120  # 5GB para canais verificados
    
    # Categorias do YouTube
    CATEGORIES = {
        "music": "10",
        "entertainment": "24", 
        "education": "27",
        "people": "22",
        "film": "1",
        "autos": "2",
        "pets": "15",
        "sports": "17",
        "travel": "19",
        "gaming": "20",
        "comedy": "23",
        "news": "25",
        "science": "28"
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        if config is None:
            config = Config()
        super().__init__(config)
        self.api_key = getattr(config, 'YOUTUBE_API_KEY', '')
        self.client_id = getattr(config, 'YOUTUBE_CLIENT_ID', '')
        self.client_secret = getattr(config, 'YOUTUBE_CLIENT_SECRET', '')
        self.refresh_token = getattr(config, 'YOUTUBE_REFRESH_TOKEN', '')
        self.channel_id = getattr(config, 'YOUTUBE_CHANNEL_ID', '')
        self.youtube = None
        
        # Tenta inicializar APIs
        self._init_api()
    
    def _init_api(self):
        """Inicializa APIs do YouTube."""
        try:
            from googleapiclient.discovery import build
            
            # API Key para dados publicos (pesquisa)
            if self.api_key:
                self.youtube_data = build('youtube', 'v3', developerKey=self.api_key)
                self.logger.info("YouTube Data API inicializada (API Key)")
            
            # OAuth2 para upload (requer credenciais adicionais)
            if all([self.client_id, self.client_secret, self.refresh_token]):
                from google.oauth2.credentials import Credentials
                credentials = Credentials(
                    token=None,
                    refresh_token=self.refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.youtube = build('youtube', 'v3', credentials=credentials)
                self.logger.info("YouTube API inicializada (OAuth2)")
                
        except ImportError:
            self.logger.warning("google-api-python-client nao instalado. Rode: pip install google-api-python-client google-auth-oauthlib")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar YouTube API: {e}")
    
    def authenticate(self) -> bool:
        """
        Verifica autenticacao disponivel.
        API Key: apenas leitura (OK)
        OAuth2: upload de videos (necessario para publicar)
        """
        has_api_key = bool(self.api_key)
        has_oauth = all([self.client_id, self.client_secret, self.refresh_token])
        
        if has_oauth:
            self.authenticated = True
            self.logger.info("YouTube autenticado com OAuth2 (upload habilitado)")
            return True
        elif has_api_key:
            self.logger.info("YouTube com API Key (apenas leitura/dados)")
            return True
        else:
            self.logger.warning("YouTube: nenhuma credencial configurada")
            return False
    
    def search_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Pesquisa videos no YouTube (requer API Key).
        
        Args:
            query: Termo de busca
            max_results: Numero maximo de resultados
            
        Returns:
            Lista de videos encontrados
        """
        if not self.api_key or not hasattr(self, 'youtube_data'):
            self.logger.warning("API Key do YouTube nao configurada para pesquisa")
            return []
        
        try:
            response = self.youtube_data.search().list(
                q=query,
                part='snippet',
                maxResults=max_results,
                type='video',
                order='viewCount'  # Mais populares primeiro
            ).execute()
            
            videos = []
            for item in response.get('items', []):
                video = {
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt']
                }
                videos.append(video)
            
            return videos
            
        except Exception as e:
            self.logger.error(f"Erro na pesquisa YouTube: {e}")
            return []
    
    def get_video_stats(self, video_id: str) -> Dict[str, Any]:
        """
        Obtem estatisticas de um video.
        
        Args:
            video_id: ID do video
            
        Returns:
            Estatisticas do video
        """
        if not self.api_key or not hasattr(self, 'youtube_data'):
            return {}
        
        try:
            response = self.youtube_data.videos().list(
                part='statistics,snippet',
                id=video_id
            ).execute()
            
            if response['items']:
                item = response['items'][0]
                return {
                    'views': int(item['statistics'].get('viewCount', 0)),
                    'likes': int(item['statistics'].get('likeCount', 0)),
                    'comments': int(item['statistics'].get('commentCount', 0)),
                    'title': item['snippet']['title']
                }
            return {}
            
        except Exception as e:
            self.logger.error(f"Erro ao obter stats: {e}")
            return {}
    
    def get_trending_videos(self, region_code: str = 'BR', 
                          video_category_id: str = '10') -> List[Dict]:
        """
        Obtem videos em alta.
        
        Args:
            region_code: Codigo do pais (BR, US, etc)
            video_category_id: ID da categoria (10 = Musica)
            
        Returns:
            Lista de videos em alta
        """
        if not self.api_key or not hasattr(self, 'youtube_data'):
            return []
        
        try:
            response = self.youtube_data.videos().list(
                part='snippet,statistics',
                chart='mostPopular',
                regionCode=region_code,
                videoCategoryId=video_category_id,
                maxResults=10
            ).execute()
            
            videos = []
            for item in response.get('items', []):
                videos.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'views': int(item['statistics'].get('viewCount', 0)),
                    'channel': item['snippet']['channelTitle']
                })
            
            return videos
            
        except Exception as e:
            self.logger.error(f"Erro ao obter trending: {e}")
            return []
    
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
        
        # Verifica se tem OAuth2 para upload real
        if not self.youtube:
            self.logger.warning("OAuth2 nao configurado. Upload simulado.")
            return self._simulate_upload(video_path, metadata)
        
        # Upload real via API
        try:
            from googleapiclient.http import MediaFileUpload
            
            body = {
                'snippet': {
                    'title': metadata.title,
                    'description': metadata.description,
                    'tags': metadata.tags,
                    'categoryId': self._get_category_id(metadata.category)
                },
                'status': {
                    'privacyStatus': metadata.visibility,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True
            )
            
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request.execute()
            video_id = response['id']
            
            self.logger.info(f"Video publicado: https://youtube.com/watch/{video_id}")
            
            return UploadResult(
                success=True,
                platform=self.PLATFORM_NAME,
                video_id=video_id,
                url=f"https://youtube.com/watch/{video_id}"
            )
            
        except Exception as e:
            self.logger.error(f"Erro no upload: {e}")
            return UploadResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error_message=str(e)
            )
    
    def upload_short(self, video_path: str, metadata: VideoMetadata) -> UploadResult:
        """Faz upload como YouTube Short."""
        if "#shorts" not in metadata.description.lower():
            metadata.description += "\n\n#Shorts"
        
        metadata.is_short = True
        return self.upload(video_path, metadata)
    
    def delete(self, video_id: str) -> bool:
        """Remove video do YouTube."""
        if not self.youtube:
            self.logger.warning("OAuth2 necessario para deletar")
            return False
        
        try:
            self.youtube.videos().delete(id=video_id).execute()
            self.logger.info(f"Video {video_id} removido")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao deletar: {e}")
            return False
    
    def _get_category_id(self, category: str) -> str:
        """Mapeia categoria para ID do YouTube."""
        return self.CATEGORIES.get(category, "22")  # Padrao: People & Blogs
    
    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Define thumbnail customizada."""
        if not self.youtube:
            self.logger.warning("OAuth2 necessario para thumbnails")
            return False
        
        try:
            from googleapiclient.http import MediaFileUpload
            
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            
            self.logger.info(f"Thumbnail atualizada para {video_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na thumbnail: {e}")
            return False
    
    def add_to_playlist(self, video_id: str, playlist_id: str) -> bool:
        """Adiciona video a playlist."""
        if not self.youtube:
            return False
        
        try:
            self.youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            ).execute()
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar playlist: {e}")
            return False
