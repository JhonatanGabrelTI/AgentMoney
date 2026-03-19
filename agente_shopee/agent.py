"""
Agente principal de afiliados Shopee.
Orquestra scraping, geração de conteúdo e distribuição.
"""

import random
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core_engine.config import Config
from core_engine.logger import get_logger
from core_engine.database import Database, Product

from .scraper import ShopeeScraper
from .content import ContentGenerator

logger = get_logger(__name__)


class ShopeeAgent:
    """
    Agente de automação Shopee Affiliate.
    
    Fluxo de trabalho:
    1. Scraper: Busca produtos com critérios de lucratividade
    2. Análise: Classifica por nicho e potencial
    3. Conteúdo: Gera copy, scripts e materiais
    4. Distribuição: Posta em Telegram, WhatsApp, etc
    """
    
    # Critérios de seleção de produtos
    MIN_SALES = 500
    MIN_RATING = 4.5
    MIN_COMMISSION = 5.0  # %
    
    # Nichos para categorização
    NICHOS = {
        "casa": ["decoração", "cozinha", "organização", "limpeza", "móveis"],
        "tech": ["eletrônicos", "gadgets", "cabeamento", "acessórios", "smart"],
        "moda": ["vestuário", "acessórios", "calçados", "beleza", "cuidados"],
        "auto": ["carro", "moto", "acessórios automotivos", "manutenção"],
        "pet": ["pet", "cachorro", "gato", "animais", "ração"]
    }
    
    def __init__(self):
        self.config = Config()
        self.db = Database()
        self.scraper = ShopeeScraper()
        self.content_gen = ContentGenerator()
        
        logger.info("Agente Shopee inicializado")
    
    def scrape_products(self, limit: int = 10) -> List[Product]:
        """
        Executa scraping de produtos no Shopee.
        
        Args:
            limit: Quantidade máxima de produtos
            
        Returns:
            Lista de produtos encontrados
        """
        logger.info(f"Iniciando scraping (limite: {limit})...")
        
        # Usa scraper real ou mock conforme modo
        if self.config.IS_DEMO:
            products = self._generate_mock_products(limit)
        else:
            products = self.scraper.scrape(
                min_sales=self.MIN_SALES,
                min_rating=self.MIN_RATING,
                limit=limit
            )
        
        # Salva no banco
        saved = 0
        for product in products:
            if self.db.save_product(product):
                saved += 1
        
        logger.info(f"{saved} produtos salvos no banco")
        return products
    
    def _generate_mock_products(self, limit: int) -> List[Product]:
        """Gera produtos mock para modo demo."""
        mock_products = []
        
        templates = [
            ("Fone de Ouvido Bluetooth 5.3", "tech", 49.90, 129.90, 62),
            ("Organizador de Geladeira", "casa", 29.90, 59.90, 50),
            ("Luminária LED Touch", "casa", 39.90, 89.90, 56),
            ("Cabo USB-C Reforçado 2m", "tech", 19.90, 49.90, 60),
            ("Garrafa Térmica 500ml", "casa", 34.90, 79.90, 44),
            ("Suporte Celular Carro", "auto", 24.90, 59.90, 58),
            ("Brinquedo Interativo Pet", "pet", 32.90, 69.90, 53),
            ("Kit 5 Pinceis Maquiagem", "moda", 27.90, 59.90, 47),
            ("Carregador Turbo 30W", "tech", 45.90, 99.90, 54),
            ("Tapete Absorvente Pet", "pet", 41.90, 89.90, 49),
        ]
        
        for i in range(min(limit, len(templates))):
            name, category, price, original, commission_rate = templates[i]
            discount = int((1 - price / original) * 100)
            
            product = Product(
                id=f"mock_{datetime.now().strftime('%Y%m%d')}_{i}",
                name=name,
                price=price,
                original_price=original,
                discount=discount,
                rating=round(random.uniform(4.5, 5.0), 1),
                sales=random.randint(500, 5000),
                commission_rate=commission_rate,
                commission_value=round(price * (commission_rate / 100), 2),
                category=category,
                affiliate_link=f"https://shopee.com.br/product/mock/{i}",
                image_url=f"https://cf.shopee.com.br/mock/product_{i}.jpg"
            )
            mock_products.append(product)
        
        return mock_products
    
    def generate_content(self, products: List[Product]) -> List[Dict[str, Any]]:
        """
        Gera conteúdo de marketing para produtos.
        
        Args:
            products: Lista de produtos
            
        Returns:
            Lista de conteúdos gerados
        """
        contents = []
        
        for product in products:
            logger.info(f"Gerando conteúdo para: {product.name}")
            
            # Gera copy via API ou template
            if self.config.IS_DEMO:
                content = self._generate_mock_content(product)
            else:
                content = self.content_gen.generate(product)
            
            contents.append(content)
            
            # Marca como processado
            self.db.mark_product_content_generated(product.id)
        
        return contents
    
    def _generate_mock_content(self, product: Product) -> Dict[str, Any]:
        """Gera conteúdo mock para demo."""
        
        # Headlines magnéticas (clickbait ético)
        headlines = [
            f"🔥 {product.name} com {product.discount}% OFF! Só hoje!",
            f"⚡ PROMOÇÃO RELÂMPAGO: {product.name} por R${product.price:.2f}",
            f"🚨 ALERTA DE OFERTA: {product.name} - {product.discount}% desconto",
            f"✨ {product.name}: O mais vendido com desconto incrível!",
            f"💥 IMPERDÍVEL: {product.name} saindo por R${product.price:.2f}",
        ]
        
        # Copys para WhatsApp/Telegram
        copy_whatsapp = f"""🛒 *OFERTA EXCLUSIVA*

*{product.name}*

❌ De: ~R${product.original_price:.2f}~
✅ Por: *R${product.price:.2f}*
📉 Economia: *{product.discount}%*
⭐ Avaliação: {product.rating}/5
📦 {product.sales}+ vendas

🔗 Compre aqui: {product.affiliate_link}

⚡ Oferta por tempo limitado!
💰 Comissão: {product.commission_rate}% para afiliados"""
        
        copy_telegram = f"""🎯 {product.name}

💰 <b>R${product.price:.2f}</b> <s>R${product.original_price:.2f}</s>
📊 {product.discount}% OFF | ⭐ {product.rating}

{product.affiliate_link}

#oferta #{product.category} #shopee"""
        
        # Script de vídeo curto (30-60s)
        script_video = f"""[HOOK - 0-3s]
"Você não vai acreditar nesse preço..."

[PROBLEMA - 3-8s] 
Mostrar dificuldade sem o produto

[SOLUÇÃO - 8-20s]
Apresentar {product.name}
Destacar: {product.discount}% desconto

[PROVA SOCIAL - 20-25s]
"{product.sales} pessoas já compraram"

[CTA - 25-30s]
"Link na bio/bio - Corre antes que acabe!"
"""
        
        return {
            "product_id": product.id,
            "headlines": headlines,
            "copy_whatsapp": copy_whatsapp,
            "copy_telegram": copy_telegram,
            "script_video": script_video,
            "hashtags": [f"#{product.category}", "#oferta", "#promocao", "#shopee", "#desconto"],
            "created_at": datetime.now().isoformat()
        }
    
    def distribute_content(self, contents: List[Dict]) -> int:
        """
        Distribui conteúdo nas redes sociais.
        Em modo demo, apenas simula o envio.
        
        Args:
            contents: Lista de conteúdos
            
        Returns:
            Número de posts simulados
        """
        if self.config.IS_DEMO:
            logger.info(f"[DEMO] Simulando postagem de {len(contents)} conteúdos")
            for content in contents:
                headline = content['headlines'][0][:50] if content['headlines'] else "Sem headline"
                logger.info(f"  📤 [DEMO] Telegram: {headline}...")
            return len(contents)
        
        # Implementação real com APIs
        # TODO: Integrar Telegram Bot API
        # TODO: Integrar WhatsApp Business API
        
        return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do agente."""
        return self.db.get_stats()
