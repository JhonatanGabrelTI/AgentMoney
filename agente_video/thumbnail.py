"""
Geração de thumbnails usando APIs de imagem IA.
Suporta DALL-E 3 (OpenAI), Stability AI, Leonardo.ai.

NOTA: Midjourney NÃO tem API pública - usa Discord apenas.
"""

from pathlib import Path
from typing import Dict, Any
from core_engine.logger import get_logger
from core_engine.config import Config

logger = get_logger(__name__)


class ThumbnailGenerator:
    """
    Cria thumbnails otimizadas para CTR (Click-Through Rate).
    
    Providers suportados:
    - DALL-E 3 (OpenAI) - RECOMENDADO (você já tem a chave!)
    - Stability AI (Stable Diffusion)
    - Leonardo.ai
    - Ideogram
    """
    
    # Prompts otimizados por nicho para DALL-E 3
    PROMPTS = {
        "lofi": (
            "A cozy anime-style lo-fi girl sitting by a rainy window with a vinyl record player, "
            "warm ambient lighting, pastel color palette, highly detailed, "
            "peaceful study atmosphere, 16:9 aspect ratio, cinematic composition"
        ),
        "meditation": (
            "Serene Buddha statue with lotus flowers, golden light rays streaming through clouds, "
            "misty mountain background, zen garden, warm earth tones, peaceful atmosphere, "
            "minimalist composition, spiritual tranquility, 16:9 cinematic"
        ),
        "prayer": (
            "Divine light rays breaking through clouds, hands in prayer position, "
            "soft golden glow, inspirational heavenly atmosphere, warm colors, "
            "cinematic lighting, hope and faith theme, 16:9 aspect ratio"
        ),
        "nature": (
            "Rain drops on vibrant green leaves, dark forest background, soft focus bokeh, "
            "moody atmospheric lighting, nature photography style, peaceful and calming, "
            "highly detailed 4k, serene environment, 16:9"
        ),
        "ambient": (
            "Cosmic nebula with deep space stars, purple and blue gradient colors, "
            "ethereal glow effects, abstract space art, cinematic composition, "
            "mysterious universe atmosphere, 4k detailed, 16:9 aspect ratio"
        ),
        "short_lofi": (
            "Retro lo-fi aesthetic, vintage cassette tapes, warm orange and pink sunset, "
            "anime character silhouette, nostalgic 90s vibes, vertical 9:16 composition"
        ),
        "short_motivation": (
            "Inspirational success imagery, person on mountain peak at sunrise, "
            "bold dramatic lighting, achievement and determination theme, "
            "vertical 9:16 format for short video"
        )
    }
    
    # Tamanhos recomendados por plataforma
    SIZES = {
        "youtube": ("1792x1024", "landscape"),      # 16:9
        "youtube_shorts": ("1024x1792", "portrait"), # 9:16
        "tiktok": ("1024x1792", "portrait"),         # 9:16
        "instagram": ("1024x1792", "portrait"),      # 9:16 Reels
        "facebook": ("1792x1024", "landscape"),      # 16:9
        "kwai": ("1024x1792", "portrait"),           # 9:16
    }
    
    def __init__(self):
        self.config = Config()
        self.provider = self._select_provider()
        self.client = None
        
        if self.provider == "dalle":
            self._init_openai()
    
    def _select_provider(self) -> str:
        """Seleciona provider de imagem disponível."""
        # DALL-E 3 é o padrão se tiver OpenAI configurada
        if self.config.OPENAI_API_KEY and self.config.OPENAI_API_KEY != "demo-key":
            logger.info("Usando DALL-E 3 (OpenAI)")
            return "dalle"
        elif self.config.STABILITY_API_KEY and self.config.STABILITY_API_KEY != "demo-key":
            logger.info("Usando Stability AI")
            return "stability"
        
        logger.warning("Nenhuma API de imagem configurada - usando modo DEMO")
        return "template"
    
    def _init_openai(self):
        """Inicializa cliente OpenAI."""
        try:
            import openai
            openai.api_key = self.config.OPENAI_API_KEY
            self.client = openai
            logger.info("Cliente OpenAI inicializado para DALL-E 3")
        except ImportError:
            logger.error("Biblioteca OpenAI não instalada. Rode: pip install openai")
            self.provider = "template"
    
    def generate(self, niche: Dict[str, Any], platform: str = "youtube") -> str:
        """
        Gera thumbnail para o nicho e plataforma.
        
        Args:
            niche: Dados do nicho
            platform: Plataforma de destino (youtube, tiktok, instagram, etc)
            
        Returns:
            Caminho da imagem gerada
        """
        logger.info(f"Gerando thumbnail via {self.provider} para {platform}")
        
        prompt = self.PROMPTS.get(niche['id'], self.PROMPTS['lofi'])
        
        if self.provider == "dalle":
            return self._generate_dalle(prompt, niche, platform)
        elif self.provider == "stability":
            return self._generate_stability(prompt, niche, platform)
        else:
            return self._generate_template(niche, platform)
    
    def _generate_dalle(self, prompt: str, niche: Dict, platform: str) -> str:
        """
        Gera usando DALL-E 3 da OpenAI.
        Você já tem a chave configurada! 🎉
        """
        if self.config.IS_DEMO:
            logger.info("[DEMO] Simulando geração DALL-E 3")
            return self._generate_template(niche, platform)
        
        try:
            logger.info("Chamando DALL-E 3 API...")
            
            # DALL-E 3 só suporta 1024x1024, 1792x1024 (landscape), 1024x1792 (portrait)
            size, _ = self.SIZES.get(platform, ("1792x1024", "landscape"))
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",  # ou "hd" para qualidade premium
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Download da imagem
            import requests
            output_path = self.config.THUMBNAILS_DIR / f"{niche['id']}_{platform}_dalle.png"
            
            response = requests.get(image_url)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Thumbnail DALL-E 3 salva: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Erro DALL-E 3: {e}")
            logger.info("Fallback para template local")
            return self._generate_template(niche, platform)
    
    def _generate_stability(self, prompt: str, niche: Dict, platform: str) -> str:
        """Gera usando Stability AI (Stable Diffusion)."""
        if self.config.IS_DEMO:
            return self._generate_template(niche, platform)
        
        # TODO: Implementar Stability AI API
        logger.info("Stability AI não implementado ainda")
        return self._generate_template(niche, platform)
    
    def _generate_template(self, niche: Dict, platform: str = "youtube") -> str:
        """
        Cria template local como fallback.
        Usa PIL/Pillow para criar uma imagem básica.
        """
        logger.info("Criando thumbnail local com Pillow...")
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Define dimensões por plataforma
            if platform in ["tiktok", "instagram", "youtube_shorts", "kwai"]:
                width, height = 1080, 1920  # 9:16 vertical
            else:
                width, height = 1280, 720   # 16:9 horizontal
            
            # Cria imagem gradiente
            img = Image.new('RGB', (width, height), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            
            # Adiciona texto do nicho
            title = niche.get('name', 'Video')
            
            # Tenta usar fonte padrão ou default
            try:
                font = ImageFont.truetype("arial.ttf", 60)
                subtitle_font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            
            # Desenha texto centralizado
            text = title[:30] + "..." if len(title) > 30 else title
            
            # Calcula posição central
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = height // 3
            
            # Desenha com sombra
            draw.text((x+2, y+2), text, fill='#000000', font=font)
            draw.text((x, y), text, fill='#ffffff', font=font)
            
            # Adiciona subtítulo
            subtitle = f"{platform.upper()} | {niche.get('category', 'Music')}"
            bbox2 = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            sub_width = bbox2[2] - bbox2[0]
            draw.text(((width - sub_width) // 2, y + 100), 
                     subtitle, fill='#aaaaaa', font=subtitle_font)
            
            # Salva
            output_path = self.config.THUMBNAILS_DIR / f"{niche['id']}_{platform}_thumb.png"
            img.save(output_path)
            
            logger.info(f"Thumbnail local criada: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.warning("Pillow não instalado. Criando arquivo placeholder.")
            output_path = self.config.THUMBNAILS_DIR / f"{niche['id']}_{platform}_thumb.txt"
            output_path.write_text(f"[THUMBNAIL PLACEHOLDER]\nNicho: {niche['name']}\nPlataforma: {platform}")
            return str(output_path)
    
    def add_text_overlay(self, image_path: str, text: str, 
                         style: str = "modern") -> str:
        """
        Adiciona texto sobre a imagem usando Pillow.
        
        Args:
            image_path: Imagem base
            text: Texto a adicionar
            style: Estilo do texto
            
        Returns:
            Caminho da imagem final
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Fonte grande e bold
            try:
                font = ImageFont.truetype("arialbd.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            # Posição (canto inferior)
            width, height = img.size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = height - 150
            
            # Background semi-transparente
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([x-20, y-10, x+text_width+20, y+100], 
                                  fill=(0, 0, 0, 128))
            
            # Combina
            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(img)
            
            # Texto
            draw.text((x, y), text, fill='#ffffff', font=font)
            
            # Salva
            output_path = Path(image_path).parent / f"{Path(image_path).stem}_text.png"
            img.save(output_path)
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Erro ao adicionar texto: {e}")
            return image_path
    
    def generate_variations(self, niche: Dict[str, Any], 
                           platforms: list = None) -> Dict[str, str]:
        """
        Gera variações da thumbnail para múltiplas plataformas.
        
        Args:
            niche: Dados do nicho
            platforms: Lista de plataformas
            
        Returns:
            Dict {plataforma: caminho_da_imagem}
        """
        platforms = platforms or ["youtube"]
        results = {}
        
        for platform in platforms:
            path = self.generate(niche, platform)
            results[platform] = path
        
        return results
