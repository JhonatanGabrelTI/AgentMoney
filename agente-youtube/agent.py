"""
Agente principal de canais YouTube "faceless".
Produz e publica vídeos de música/automação completamente automatizado.
"""

import random
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core_engine.config import Config
from core_engine.logger import get_logger
from core_engine.database import Database, Video

from .research import NicheResearcher
from .audio import AudioGenerator
from .thumbnail import ThumbnailGenerator
from .video import VideoAssembler
from .uploader import YouTubeUploader

logger = get_logger(__name__)


class YouTubeAgent:
    """
    Agente de automação YouTube Faceless.
    
    Nichos suportados:
    - Lo-fi Hip Hop (estudo/trabalho)
    - Meditação/Relaxamento
    - Orações/Devocional
    - Sons da natureza
    - Ambient/Space Music
    
    Fluxo:
    1. Research → Analisa nichos e tendências
    2. Audio → Gera música com IA
    3. Thumbnail → Cria imagem de capa
    4. Video → Monta vídeo final
    5. Upload → Publica no YouTube
    """
    
    # Nichos pré-configurados
    NICHES = [
        {
            "id": "lofi",
            "name": "Lo-fi Hip Hop - Música para Estudar",
            "keywords": ["lofi", "study", "chill beats", "relax", "concentration"],
            "duration": "3:00:00",  # Live longa
            "upload_time": "08:00",
            "competition": "alta",
            "potential": "médio"
        },
        {
            "id": "meditation",
            "name": "Meditação e Relaxamento",
            "keywords": ["meditation", "relax", "sleep", "healing", "zen"],
            "duration": "1:00:00",
            "upload_time": "21:00",
            "competition": "média",
            "potential": "alto"
        },
        {
            "id": "prayer",
            "name": "Orações e Momento com Deus",
            "keywords": ["prayer", "worship", "gospel", "oração", "fé"],
            "duration": "30:00",
            "upload_time": "06:00",
            "competition": "baixa",
            "potential": "alto"
        },
        {
            "id": "nature",
            "name": "Sons da Natureza - Chuva e Florestas",
            "keywords": ["rain", "nature sounds", "forest", "sleep", "asmr"],
            "duration": "10:00:00",
            "upload_time": "22:00",
            "competition": "alta",
            "potential": "médio"
        },
        {
            "id": "ambient",
            "name": "Ambient Space Music",
            "keywords": ["ambient", "space", "cosmic", "meditation", "deep"],
            "duration": "2:00:00",
            "upload_time": "20:00",
            "competition": "baixa",
            "potential": "médio"
        }
    ]
    
    def __init__(self):
        self.config = Config()
        self.db = Database()
        
        # Componentes
        self.researcher = NicheResearcher()
        self.audio_gen = AudioGenerator()
        self.thumb_gen = ThumbnailGenerator()
        self.video_asm = VideoAssembler()
        self.uploader = YouTubeUploader()
        
        logger.info("Agente YouTube inicializado")
    
    def research_niche(self) -> Dict[str, Any]:
        """
        Pesquisa e seleciona nicho com melhor oportunidade.
        
        Returns:
            Dicionário com informações do nicho
        """
        logger.info("Pesquisando nichos...")
        
        if self.config.IS_DEMO:
            # Seleciona aleatoriamente em demo
            niche = random.choice(self.NICHES)
            logger.info(f"[DEMO] Nicho selecionado: {niche['name']}")
            return niche
        
        # Implementação real analisaria:
        # 1. Canais concorrentes
        # 2. Volume de buscas
        # 3. Competição
        # 4. Taxa de crescimento
        
        return self.researcher.analyze_best_niche()
    
    def generate_audio(self, niche: Dict[str, Any]) -> str:
        """
        Gera trilha de áudio para o vídeo.
        
        Args:
            niche: Nicho selecionado
            
        Returns:
            Caminho do arquivo de áudio
        """
        logger.info(f"Gerando áudio para: {niche['name']}")
        
        if self.config.IS_DEMO:
            # Cria arquivo de texto indicando mock
            audio_path = self.config.AUDIO_DIR / f"audio_{niche['id']}_{uuid.uuid4().hex[:8]}.txt"
            audio_path.write_text(f"[MOCK AUDIO] {niche['name']}\nDuration: {niche['duration']}\nGenerated: {datetime.now().isoformat()}")
            logger.info(f"[DEMO] Áudio mock criado: {audio_path}")
            return str(audio_path)
        
        # Implementação real usaria:
        # - Suno API
        # - Udio API
        # - Ou bibliotecas locais (pydub + samples)
        
        return self.audio_gen.generate(niche)
    
    def generate_thumbnail(self, niche: Dict[str, Any]) -> str:
        """
        Cria thumbnail minimalista e emocional.
        
        Args:
            niche: Nicho selecionado
            
        Returns:
            Caminho da imagem
        """
        logger.info(f"Criando thumbnail para: {niche['name']}")
        
        if self.config.IS_DEMO:
            # Cria arquivo indicando mock
            thumb_path = self.config.THUMBNAILS_DIR / f"thumb_{niche['id']}_{uuid.uuid4().hex[:8]}.txt"
            
            thumb_concepts = {
                "lofi": "Anime + Lo-fi girl + Vinyl record",
                "meditation": "Buddha + Nature + Soft colors",
                "prayer": "Light rays + Cross + Serenity",
                "nature": "Rain drops + Forest + Dark",
                "ambient": "Galaxy + Stars + Purple tones"
            }
            
            concept = thumb_concepts.get(niche['id'], "Minimalist + Emotional")
            thumb_path.write_text(f"[MOCK THUMBNAIL] {niche['name']}\nConcept: {concept}\nGenerated: {datetime.now().isoformat()}")
            logger.info(f"[DEMO] Thumbnail mock criada: {thumb_path}")
            return str(thumb_path)
        
        # Implementação real usaria:
        # - Midjourney API
        # - DALL-E API
        # - Canva API
        
        return self.thumb_gen.generate(niche)
    
    def assemble_video(self, audio_path: str, thumbnail_path: str, 
                       niche: Dict[str, Any]) -> str:
        """
        Monta vídeo final combinando áudio e imagem.
        
        Args:
            audio_path: Caminho do áudio
            thumbnail_path: Caminho da thumbnail
            niche: Nicho do vídeo
            
        Returns:
            Caminho do vídeo final
        """
        logger.info("Montando vídeo...")
        
        if self.config.IS_DEMO:
            video_path = self.config.VIDEO_DIR / f"video_{niche['id']}_{uuid.uuid4().hex[:8]}.txt"
            video_path.write_text(f"[MOCK VIDEO]\nAudio: {audio_path}\nThumbnail: {thumbnail_path}\nNiche: {niche['name']}\nGenerated: {datetime.now().isoformat()}")
            logger.info(f"[DEMO] Vídeo mock criado: {video_path}")
            return str(video_path)
        
        # Implementação real usaria:
        # - ffmpeg (via ffmpeg-python)
        # - moviepy
        # - ou templates pré-renderizados
        
        return self.video_asm.assemble(audio_path, thumbnail_path, niche)
    
    def upload_video(self, video_path: str, niche: Dict[str, Any]) -> str:
        """
        Faz upload do vídeo para o YouTube.
        
        Args:
            video_path: Caminho do vídeo
            niche: Nicho do vídeo
            
        Returns:
            ID do vídeo no YouTube
        """
        logger.info("Fazendo upload para YouTube...")
        
        # Gera metadados
        metadata = self._generate_metadata(niche)
        
        if self.config.IS_DEMO:
            video_id = f"demo_{uuid.uuid4().hex[:11]}"
            
            # Salva no banco
            video = Video(
                id=str(uuid.uuid4()),
                title=metadata['title'],
                description=metadata['description'],
                tags=metadata['tags'],
                category=niche['id'],
                audio_path=video_path.replace('.txt', '_audio.txt'),
                thumbnail_path=video_path.replace('.txt', '_thumb.txt'),
                video_path=video_path,
                youtube_id=video_id,
                status="published"
            )
            self.db.save_video(video)
            
            logger.info(f"[DEMO] Vídeo 'publicado' com ID: {video_id}")
            return video_id
        
        # Implementação real usaria:
        # - YouTube Data API v3
        # - OAuth2 flow
        
        return self.uploader.upload(video_path, metadata)
    
    def _generate_metadata(self, niche: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera título, descrição e tags otimizadas.
        
        Args:
            niche: Nicho do vídeo
            
        Returns:
            Dicionário com metadados
        """
        templates = {
            "lofi": {
                "titles": [
                    "Lo-Fi Hip Hop Radio 📚 - Beats to Study/Relax to",
                    "Chill Study Beats 🎵 3 Hours of Lo-Fi Music",
                    "Lo-Fi for Focus 🧠 Study & Work Music"
                ],
                "desc_template": """🎵 {title}

The perfect soundtrack for studying, working, or relaxing.

⏰ Timestamps:
00:00 - Intro
00:30 - Track 1
...

🔔 Subscribe for daily lo-fi beats!

#lofi #studybeats #chillmusic"""
            },
            "meditation": {
                "titles": [
                    "🧘 1 Hour Deep Meditation Music - Healing & Relaxation",
                    "Sleep Meditation Music 🌙 Calm Your Mind",
                    "Zen Meditation Sounds 🍃 Find Inner Peace"
                ],
                "desc_template": """🧘 {title}

Find your inner peace with this calming meditation music.
Perfect for:
✨ Deep meditation
✨ Stress relief
✨ Better sleep
✨ Yoga practice

Subscribe for weekly healing music! 🙏

#meditation #relaxation #healing"""
            },
            "prayer": {
                "titles": [
                    "🙏 Oração da Manhã - Momento com Deus",
                    "Louvor e Adoração 🕊️ 30 Minutos de Paz",
                    "Momento Devocional 📖 Comece o Dia com Fé"
                ],
                "desc_template": """🙏 {title}

"O Senhor é o meu pastor, nada me faltará." Salmos 23:1

Que esta oração traga paz ao seu coração hoje.

Compartilhe com quem precisa de conforto. 🕊️

#oração #fé #gospel"""
            },
            "nature": {
                "titles": [
                    "🌧️ Heavy Rain Sounds for Sleeping - 10 Hours",
                    "Forest Rain & Thunder 🌲 Nature Sleep Sounds",
                    "Gentle Rain on Leaves 🍃 ASMR Sleep Aid"
                ],
                "desc_template": """🌧️ {title}

Drift off to sleep with these soothing nature sounds:
🌧️ Gentle rain
🌲 Forest ambience
⛈️ Distant thunder

Perfect for:
💤 Deep sleep
📚 Study focus
🧘 Meditation

#rainsounds #nature #sleep"""
            },
            "ambient": {
                "titles": [
                    "🌌 Cosmic Ambient Music - Space Journey",
                    "Deep Space Ambience 🚀 2 Hours of Cosmic Sounds",
                    "Stellar Meditation 🌠 Space Ambient Music"
                ],
                "desc_template": """🌌 {title}

Embark on a cosmic journey through the stars.

Best experienced with headphones 🎧

#ambient #space #cosmic"""
            }
        }
        
        template = templates.get(niche['id'], templates['lofi'])
        
        title = random.choice(template['titles'])
        description = template['desc_template'].format(title=title)
        
        # Adiciona data para variar
        today = datetime.now().strftime("%Y-%m-%d")
        title += f" [{today}]"
        
        return {
            "title": title,
            "description": description,
            "tags": niche['keywords'] + ["music", "relax", "2024", "hd"],
            "category": niche['id']
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do agente."""
        return self.db.get_stats()
