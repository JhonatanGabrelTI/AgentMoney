"""
Agente principal de vídeo multi-plataforma.
Produz e publica vídeos em YouTube, TikTok, Instagram, Facebook e Kwai.
"""

import random
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core_engine.config import Config
from core_engine.logger import get_logger
from core_engine.database import Database, Video
from core_engine.uploaders.manager import UploadManager, VideoMetadata

from .research import NicheResearcher
from .audio import AudioGenerator
from .thumbnail import ThumbnailGenerator
from .video import VideoAssembler

logger = get_logger(__name__)


class VideoAgent:
    """
    Agente de automação de vídeo multi-plataforma.
    
    Plataformas suportadas:
    - YouTube (vídeos longos e Shorts)
    - TikTok
    - Instagram Reels
    - Facebook (vídeos e Reels)
    - Kwai
    
    Fluxo:
    1. Research → Analisa nichos e tendências
    2. Audio → Gera música com IA
    3. Thumbnail → Cria imagem de capa
    4. Video → Monta vídeo final
    5. Upload → Publica em todas as plataformas configuradas
    """
    
    # Nichos pré-configurados
    NICHES = [
        {
            "id": "lofi",
            "name": "Lo-fi Hip Hop - Música para Estudar",
            "keywords": ["lofi", "study", "chill beats", "relax", "concentration"],
            "duration": "3:00:00",
            "upload_time": "08:00",
            "best_platforms": ["youtube", "instagram", "tiktok"],
            "content_type": "long"  # long ou short
        },
        {
            "id": "meditation",
            "name": "Meditação e Relaxamento",
            "keywords": ["meditation", "relax", "sleep", "healing", "zen"],
            "duration": "1:00:00",
            "upload_time": "21:00",
            "best_platforms": ["youtube", "instagram", "facebook"],
            "content_type": "long"
        },
        {
            "id": "prayer",
            "name": "Orações e Momento com Deus",
            "keywords": ["prayer", "worship", "gospel", "oração", "fé"],
            "duration": "30:00",
            "upload_time": "06:00",
            "best_platforms": ["youtube", "facebook", "kwai"],
            "content_type": "long"
        },
        {
            "id": "nature",
            "name": "Sons da Natureza - Chuva e Florestas",
            "keywords": ["rain", "nature sounds", "forest", "sleep", "asmr"],
            "duration": "10:00:00",
            "upload_time": "22:00",
            "best_platforms": ["youtube"],
            "content_type": "long"
        },
        {
            "id": "ambient",
            "name": "Ambient Space Music",
            "keywords": ["ambient", "space", "cosmic", "meditation", "deep"],
            "duration": "2:00:00",
            "upload_time": "20:00",
            "best_platforms": ["youtube", "tiktok", "instagram"],
            "content_type": "long"
        },
        {
            "id": "short_lofi",
            "name": "Lo-fi Shorts - 60s Vibes",
            "keywords": ["lofi", "shorts", "quick", "vibe", "chill"],
            "duration": "00:01:00",
            "upload_time": "12:00",
            "best_platforms": ["tiktok", "instagram", "youtube", "kwai"],
            "content_type": "short"
        },
        {
            "id": "short_motivation",
            "name": "Vídeos Motivacionais Curtos",
            "keywords": ["motivation", "inspiration", "success", "mindset"],
            "duration": "00:00:30",
            "upload_time": "07:00",
            "best_platforms": ["tiktok", "instagram", "kwai", "facebook"],
            "content_type": "short"
        }
    ]
    
    def __init__(self, platforms: Optional[List[str]] = None):
        """
        Inicializa o agente de vídeo.
        
        Args:
            platforms: Lista de plataformas para publicar. 
                      Se None, usa todas configuradas.
        """
        self.config = Config()
        self.db = Database()
        
        # Componentes de produção
        self.researcher = NicheResearcher()
        self.audio_gen = AudioGenerator()
        self.thumb_gen = ThumbnailGenerator()
        self.video_asm = VideoAssembler()
        
        # Gerenciador de uploads multi-plataforma
        self.upload_manager = UploadManager(platforms)
        self.platforms = platforms or self.upload_manager.platforms
        
        logger.info(f"Agente Video inicializado para: {', '.join(self.platforms)}")
    
    def research_niche(self, content_type: str = "long") -> Dict[str, Any]:
        """
        Pesquisa e seleciona nicho com melhor oportunidade.
        
        Args:
            content_type: "long" ou "short"
            
        Returns:
            Dicionário com informações do nicho
        """
        logger.info("Pesquisando nichos...")
        
        # Filtra nichos por tipo e plataformas disponíveis
        suitable_niches = [
            n for n in self.NICHES 
            if n.get("content_type") == content_type and
            any(p in self.platforms for p in n.get("best_platforms", []))
        ]
        
        if not suitable_niches:
            suitable_niches = [n for n in self.NICHES if n.get("content_type") == content_type]
        
        if self.config.IS_DEMO:
            niche = random.choice(suitable_niches or self.NICHES)
            logger.info(f"[DEMO] Nicho selecionado: {niche['name']}")
            return niche
        
        return self.researcher.analyze_best_niche(content_type)
    
    def generate_audio(self, niche: Dict[str, Any]) -> str:
        """Gera trilha de áudio para o vídeo."""
        logger.info(f"Gerando áudio para: {niche['name']}")
        
        if self.config.IS_DEMO:
            audio_path = self.config.AUDIO_DIR / f"audio_{niche['id']}_{uuid.uuid4().hex[:8]}.txt"
            audio_path.write_text(f"[MOCK AUDIO] {niche['name']}\nDuration: {niche['duration']}\nGenerated: {datetime.now().isoformat()}")
            logger.info(f"[DEMO] Áudio mock criado: {audio_path}")
            return str(audio_path)
        
        return self.audio_gen.generate(niche)
    
    def generate_thumbnail(self, niche: Dict[str, Any]) -> str:
        """Cria thumbnail minimalista e emocional."""
        logger.info(f"Criando thumbnail para: {niche['name']}")
        
        if self.config.IS_DEMO:
            thumb_path = self.config.THUMBNAILS_DIR / f"thumb_{niche['id']}_{uuid.uuid4().hex[:8]}.txt"
            
            thumb_concepts = {
                "lofi": "Anime + Lo-fi girl + Vinyl record",
                "meditation": "Buddha + Nature + Soft colors",
                "prayer": "Light rays + Cross + Serenity",
                "nature": "Rain drops + Forest + Dark",
                "ambient": "Galaxy + Stars + Purple tones",
                "short_lofi": "Lo-fi character + Retro aesthetic",
                "short_motivation": "Success imagery + Bold text"
            }
            
            concept = thumb_concepts.get(niche['id'], "Minimalist + Emotional")
            thumb_path.write_text(f"[MOCK THUMBNAIL] {niche['name']}\nConcept: {concept}\nGenerated: {datetime.now().isoformat()}")
            logger.info(f"[DEMO] Thumbnail mock criada: {thumb_path}")
            return str(thumb_path)
        
        return self.thumb_gen.generate(niche)
    
    def assemble_video(self, audio_path: str, thumbnail_path: str, 
                       niche: Dict[str, Any]) -> str:
        """Monta vídeo final combinando áudio e imagem."""
        logger.info("Montando vídeo...")
        
        if self.config.IS_DEMO:
            video_path = self.config.VIDEO_DIR / f"video_{niche['id']}_{uuid.uuid4().hex[:8]}.txt"
            video_path.write_text(f"[MOCK VIDEO]\nAudio: {audio_path}\nThumbnail: {thumbnail_path}\nNiche: {niche['name']}\nGenerated: {datetime.now().isoformat()}")
            logger.info(f"[DEMO] Vídeo mock criado: {video_path}")
            return str(video_path)
        
        return self.video_asm.assemble(audio_path, thumbnail_path, niche)
    
    def upload_to_platforms(self, video_path: str, niche: Dict[str, Any],
                           platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Faz upload do vídeo para múltiplas plataformas.
        
        Args:
            video_path: Caminho do vídeo
            niche: Dados do nicho
            platforms: Plataformas específicas (opcional)
            
        Returns:
            Resultados do upload por plataforma
        """
        logger.info("Iniciando upload multi-plataforma...")
        
        # Gera metadados
        metadata = self._generate_metadata(niche)
        
        # Determina se é short ou vídeo longo
        is_short = niche.get("content_type") == "short"
        
        # Seleciona plataformas
        target_platforms = platforms or niche.get("best_platforms", self.platforms)
        target_platforms = [p for p in target_platforms if p in self.platforms]
        
        if not target_platforms:
            target_platforms = self.platforms
        
        logger.info(f"Plataformas alvo: {', '.join(target_platforms)}")
        
        # Faz upload
        if is_short:
            result = self.upload_manager.upload_as_shorts(
                video_path, metadata, target_platforms
            )
        else:
            result = self.upload_manager.upload_to_all(
                video_path, metadata, target_platforms
            )
        
        # Salva no banco
        video = Video(
            id=str(uuid.uuid4()),
            title=metadata.title,
            description=metadata.description,
            tags=metadata.tags,
            category=niche['id'],
            audio_path=video_path.replace('.txt', '_audio.txt'),
            thumbnail_path=video_path.replace('.txt', '_thumb.txt'),
            video_path=video_path,
            status="published" if result.success_count > 0 else "partial" if result.success_count > 0 else "failed"
        )
        
        # Define resultados por plataforma
        for platform, upload_result in result.results.items():
            if upload_result.success:
                video.set_platform_result(
                    platform,
                    upload_result.video_id,
                    "published",
                    upload_result.url
                )
        
        self.db.save_video(video)
        
        # Log do relatório
        report = self.upload_manager.get_upload_report(result)
        logger.info(f"\n{report}")
        
        return {
            "video_id": video.id,
            "results": result.results,
            "all_success": result.all_success,
            "success_count": result.success_count,
            "failed_count": result.failed_count,
            "failed_platforms": result.failed_platforms
        }
    
    def _generate_metadata(self, niche: Dict[str, Any]) -> VideoMetadata:
        """Gera metadados otimizados para multi-plataforma."""
        
        templates = {
            "lofi": {
                "titles": [
                    "Lo-Fi Hip Hop Radio - Beats to Study/Relax to",
                    "Chill Study Beats - 3 Hours of Lo-Fi Music",
                    "Lo-Fi for Focus - Study and Work Music"
                ],
                "desc": "The perfect soundtrack for studying, working, or relaxing. Subscribe for daily beats!"
            },
            "meditation": {
                "titles": [
                    "1 Hour Deep Meditation Music - Healing and Relaxation",
                    "Sleep Meditation Music - Calm Your Mind",
                    "Zen Meditation Sounds - Find Inner Peace"
                ],
                "desc": "Find your inner peace with this calming meditation music. Perfect for deep meditation, stress relief and better sleep."
            },
            "prayer": {
                "titles": [
                    "Oração da Manhã - Momento com Deus",
                    "Louvor e Adoração - 30 Minutos de Paz",
                    "Momento Devocional - Comece o Dia com Fé"
                ],
                "desc": '"O Senhor é o meu pastor, nada me faltará." Salmos 23:1. Que esta oração traga paz ao seu coração.'
            },
            "nature": {
                "titles": [
                    "Heavy Rain Sounds for Sleeping - 10 Hours",
                    "Forest Rain and Thunder - Nature Sleep Sounds",
                    "Gentle Rain on Leaves - ASMR Sleep Aid"
                ],
                "desc": "Drift off to sleep with these soothing nature sounds. Perfect for deep sleep, study focus and meditation."
            },
            "ambient": {
                "titles": [
                    "Cosmic Ambient Music - Space Journey",
                    "Deep Space Ambience - 2 Hours of Cosmic Sounds",
                    "Stellar Meditation - Space Ambient Music"
                ],
                "desc": "Embark on a cosmic journey through the stars. Best experienced with headphones."
            },
            "short_lofi": {
                "titles": [
                    "POV: você está estudando tarde da noite",
                    "Essa música vai te ajudar a focar",
                    "Lo-fi vibes para relaxar"
                ],
                "desc": "Siga para mais vibes lo-fi! #lofi #shorts #study"
            },
            "short_motivation": {
                "titles": [
                    "NUNCA DESISTA! 🔥",
                    "Amanhã vai ser melhor 💪",
                    "Você é mais forte do que imagina"
                ],
                "desc": "Compartilhe com alguém que precisa ver isso! #motivação #shorts"
            }
        }
        
        template = templates.get(niche['id'], templates['lofi'])
        
        title = random.choice(template['titles'])
        description = template['desc']
        
        # Adiciona data para variar
        today = datetime.now().strftime("%Y-%m-%d")
        title += f" [{today}]"
        
        # Tags comuns para todas as plataformas
        base_tags = niche['keywords'] + ["viral", "2024", "trending"]
        
        return VideoMetadata(
            title=title,
            description=description,
            tags=base_tags,
            category=niche['id'],
            visibility="public",
            is_short=niche.get("content_type") == "short"
        )
    
    def run_pipeline(self, content_type: str = "long") -> Dict[str, Any]:
        """
        Executa pipeline completo de produção e upload.
        
        Args:
            content_type: "long" ou "short"
            
        Returns:
            Resultados do processo
        """
        logger.info(f"=== Iniciando Pipeline Video ({content_type}) ===")
        
        # 1. Research
        logger.info("Etapa 1/5: Pesquisando nichos...")
        niche = self.research_niche(content_type)
        logger.info(f"Nicho: {niche['name']}")
        
        # 2. Audio
        logger.info("Etapa 2/5: Produzindo áudio...")
        audio_path = self.generate_audio(niche)
        
        # 3. Thumbnail
        logger.info("Etapa 3/5: Criando thumbnail...")
        thumbnail_path = self.generate_thumbnail(niche)
        
        # 4. Video
        logger.info("Etapa 4/5: Montando vídeo...")
        video_path = self.assemble_video(audio_path, thumbnail_path, niche)
        
        # 5. Upload Multi-Plataforma
        logger.info("Etapa 5/5: Fazendo upload para plataformas...")
        upload_results = self.upload_to_platforms(video_path, niche)
        
        logger.info("=== Pipeline Concluído ===")
        
        return {
            "niche": niche,
            "video_path": video_path,
            "upload_results": upload_results
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do agente."""
        return self.db.get_stats()
