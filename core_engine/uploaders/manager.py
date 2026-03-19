"""
Gerenciador de uploads para múltiplas plataformas.
Distribui vídeos para todas as plataformas configuradas.
"""

from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from core_engine.config import Config
from core_engine.logger import get_logger
from core_engine.uploaders.base import VideoMetadata, UploadResult
from core_engine.uploaders.youtube import YouTubeUploader
from core_engine.uploaders.tiktok import TikTokUploader
from core_engine.uploaders.instagram import InstagramUploader
from core_engine.uploaders.facebook import FacebookUploader
from core_engine.uploaders.kwai import KwaiUploader

logger = get_logger(__name__)


@dataclass
class MultiPlatformResult:
    """Resultado de upload multi-plataforma."""
    video_id: str
    results: Dict[str, UploadResult]
    all_success: bool
    success_count: int
    failed_count: int
    failed_platforms: List[str]


class UploadManager:
    """
    Gerencia uploads para múltiplas plataformas.
    
    Features:
    - Upload paralelo para várias plataformas
    - Retry automático em falhas
    - Configuração por plataforma
    - Relatório consolidado
    """
    
    # Plataformas disponíveis
    PLATFORMS = {
        "youtube": YouTubeUploader,
        "tiktok": TikTokUploader,
        "instagram": InstagramUploader,
        "facebook": FacebookUploader,
        "kwai": KwaiUploader
    }
    
    def __init__(self, platforms: Optional[List[str]] = None):
        """
        Inicializa o gerenciador.
        
        Args:
            platforms: Lista de plataformas a usar. Se None, usa todas configuradas.
        """
        self.config = Config()
        self.platforms = platforms or self._get_configured_platforms()
        self.uploaders: Dict[str, Any] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        self._initialize_uploaders()
    
    def _get_configured_platforms(self) -> List[str]:
        """Retorna plataformas configuradas no .env."""
        platforms = []
        
        if self.config.YOUTUBE_CLIENT_ID:
            platforms.append("youtube")
        if self.config.TIKTOK_ACCESS_TOKEN:
            platforms.append("tiktok")
        if self.config.INSTAGRAM_ACCESS_TOKEN:
            platforms.append("instagram")
        if self.config.FACEBOOK_ACCESS_TOKEN:
            platforms.append("facebook")
        if self.config.KWAI_ACCESS_TOKEN:
            platforms.append("kwai")
        
        # Se modo DEMO e nenhuma configurada, usa todas em modo simulação
        if self.config.IS_DEMO and not platforms:
            platforms = list(self.PLATFORMS.keys())
        
        return platforms
    
    def _initialize_uploaders(self):
        """Inicializa uploaders para plataformas selecionadas."""
        for platform in self.platforms:
            if platform in self.PLATFORMS:
                try:
                    uploader_class = self.PLATFORMS[platform]
                    uploader = uploader_class(self.config)
                    self.uploaders[platform] = uploader
                    logger.info(f"Uploader {platform} inicializado")
                except Exception as e:
                    logger.error(f"Erro ao inicializar {platform}: {e}")
    
    def upload_to_all(self, video_path: str, metadata: VideoMetadata,
                     platforms: Optional[List[str]] = None) -> MultiPlatformResult:
        """
        Faz upload para todas as plataformas configuradas.
        
        Args:
            video_path: Caminho do vídeo
            metadata: Metadados
            platforms: Plataformas específicas (opcional)
            
        Returns:
            MultiPlatformResult com resultados de todas as plataformas
        """
        platforms = platforms or self.platforms
        results = {}
        failed_platforms = []
        
        logger.info(f"Iniciando upload para {len(platforms)} plataformas...")
        logger.info(f"Plataformas: {', '.join(platforms)}")
        
        # Executa uploads em paralelo
        futures = {}
        for platform in platforms:
            if platform in self.uploaders:
                future = self.executor.submit(
                    self._upload_with_retry,
                    platform,
                    video_path,
                    metadata
                )
                futures[future] = platform
            else:
                logger.warning(f"Uploader {platform} não disponível")
                failed_platforms.append(platform)
        
        # Coleta resultados
        for future in as_completed(futures):
            platform = futures[future]
            try:
                result = future.result(timeout=300)  # 5 min timeout
                results[platform] = result
                
                if result.success:
                    logger.info(f"✅ {platform}: Upload OK - {result.video_id}")
                else:
                    logger.error(f"❌ {platform}: Falha - {result.error_message}")
                    failed_platforms.append(platform)
                    
            except Exception as e:
                logger.error(f"❌ {platform}: Exceção - {e}")
                failed_platforms.append(platform)
                results[platform] = UploadResult(
                    success=False,
                    platform=platform,
                    error_message=str(e)
                )
        
        # Calcula estatísticas
        success_count = sum(1 for r in results.values() if r.success)
        failed_count = len(failed_platforms)
        all_success = failed_count == 0
        
        logger.info(f"Uploads concluídos: {success_count} sucesso, {failed_count} falhas")
        
        return MultiPlatformResult(
            video_id=results.get(platforms[0], UploadResult(False, "")).video_id or "unknown",
            results=results,
            all_success=all_success,
            success_count=success_count,
            failed_count=failed_count,
            failed_platforms=failed_platforms
        )
    
    def _upload_with_retry(self, platform: str, video_path: str, 
                          metadata: VideoMetadata, max_retries: int = 3) -> UploadResult:
        """
        Faz upload com retry automático.
        
        Args:
            platform: Nome da plataforma
            video_path: Caminho do vídeo
            metadata: Metadados
            max_retries: Número máximo de tentativas
            
        Returns:
            UploadResult
        """
        uploader = self.uploaders[platform]
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"{platform}: Tentativa {attempt}/{max_retries}")
                
                # Ajusta metadata específico por plataforma
                adjusted_metadata = self._adjust_metadata_for_platform(metadata, platform)
                
                result = uploader.upload(video_path, adjusted_metadata)
                
                if result.success:
                    return result
                else:
                    last_error = result.error_message
                    logger.warning(f"{platform}: Tentativa {attempt} falhou: {last_error}")
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"{platform}: Exceção na tentativa {attempt}: {e}")
        
        return UploadResult(
            success=False,
            platform=platform,
            error_message=f"Falhou após {max_retries} tentativas: {last_error}"
        )
    
    def _adjust_metadata_for_platform(self, metadata: VideoMetadata, 
                                     platform: str) -> VideoMetadata:
        """
        Ajusta metadados específicos para cada plataforma.
        
        Args:
            metadata: Metadados originais
            platform: Plataforma de destino
            
        Returns:
            Metadados ajustados
        """
        import copy
        adjusted = copy.copy(metadata)
        
        if platform == "youtube":
            # YouTube suporta títulos mais longos
            pass
            
        elif platform == "tiktok":
            # TikTok: título vai na descrição, max 100 caracteres
            if len(adjusted.title) > 100:
                adjusted.description = adjusted.title + "\n" + adjusted.description
                adjusted.title = adjusted.title[:97] + "..."
                
        elif platform == "instagram":
            # Instagram: foco em hashtags
            if not adjusted.tags:
                adjusted.tags = ["#reels", "#viral"]
                
        elif platform == "facebook":
            # Facebook: boa para descrições longas
            pass
            
        elif platform == "kwai":
            # Kwai: hashtags em português performam melhor
            adjusted.tags = ["#kwai", "#viral", "#trending"] + adjusted.tags
        
        return adjusted
    
    def upload_as_shorts(self, video_path: str, metadata: VideoMetadata,
                        platforms: Optional[List[str]] = None) -> MultiPlatformResult:
        """
        Faz upload como vídeo curto (Shorts/Reels) nas plataformas suportadas.
        
        Args:
            video_path: Caminho do vídeo
            metadata: Metadados
            platforms: Plataformas específicas
            
        Returns:
            MultiPlatformResult
        """
        shorts_platforms = ["youtube", "tiktok", "instagram", "facebook", "kwai"]
        
        if platforms:
            shorts_platforms = [p for p in platforms if p in shorts_platforms]
        
        metadata.is_short = True
        
        logger.info(f"Upload como SHORTS para: {', '.join(shorts_platforms)}")
        
        return self.upload_to_all(video_path, metadata, shorts_platforms)
    
    def delete_from_all(self, video_ids: Dict[str, str]) -> Dict[str, bool]:
        """
        Remove vídeo de todas as plataformas.
        
        Args:
            video_ids: Dict {platform: video_id}
            
        Returns:
            Dict {platform: success}
        """
        results = {}
        
        for platform, video_id in video_ids.items():
            if platform in self.uploaders:
                try:
                    success = self.uploaders[platform].delete(video_id)
                    results[platform] = success
                    logger.info(f"{'✅' if success else '❌'} {platform}: Delete {video_id}")
                except Exception as e:
                    logger.error(f"❌ {platform}: Erro ao deletar: {e}")
                    results[platform] = False
            else:
                results[platform] = False
        
        return results
    
    def get_upload_report(self, result: MultiPlatformResult) -> str:
        """
        Gera relatório de upload.
        
        Args:
            result: Resultado do upload
            
        Returns:
            String formatada com relatório
        """
        lines = [
            "=" * 60,
            "RELATÓRIO DE UPLOAD MULTI-PLATAFORMA",
            "=" * 60,
            f"Video ID: {result.video_id}",
            f"Total: {result.success_count} sucesso, {result.failed_count} falhas",
            "",
            "SUCESSOS:"
        ]
        
        for platform, res in result.results.items():
            if res.success:
                lines.append(f"  ✅ {platform}: {res.url or res.video_id}")
        
        if result.failed_platforms:
            lines.extend(["", "FALHAS:"])
            for platform in result.failed_platforms:
                res = result.results.get(platform)
                error = res.error_message if res else "N/A"
                lines.append(f"  ❌ {platform}: {error}")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
