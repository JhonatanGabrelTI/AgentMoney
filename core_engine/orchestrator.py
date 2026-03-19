"""
Orquestrador central do AgentMoney.
Coordena a execução dos agentes e gerencia o fluxo de trabalho.
"""

import time
import schedule
from typing import Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from .config import Config
from .logger import get_logger
from .database import Database

logger = get_logger(__name__)


class AgentMoneyOrchestrator:
    """
    Orquestrador principal do sistema AgentMoney.
    
    Responsabilidades:
    - Inicializar e coordenar agentes
    - Gerenciar execuções agendadas
    - Monitorar KPIs e métricas
    - Lidar com erros e retries
    """
    
    def __init__(self):
        self.config = Config()
        self.db = Database()
        self.agents: Dict[str, Any] = {}
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Verifica modo
        if self.config.IS_DEMO:
            logger.warning("🎭 MODO DEMO ATIVO - APIs serão simuladas")
        else:
            logger.info("🚀 MODO PRODUÇÃO ATIVO")
    
    def register_agent(self, name: str, agent_instance):
        """Registra um agente no orquestrador."""
        self.agents[name] = agent_instance
        logger.info(f"Agente registrado: {name}")
    
    def setup_schedule(self):
        """Configura agendamentos de tarefas."""
        # Agente Shopee - a cada 2 horas
        schedule.every(2).hours.do(self.run_shopee_pipeline)
        
        # Agente YouTube - diariamente às 08:00
        schedule.every().day.at("08:00").do(self.run_youtube_pipeline)
        
        # Log de status - a cada 30 minutos
        schedule.every(30).minutes.do(self.log_status)
        
        logger.info("Agendamentos configurados")
    
    def run_shopee_pipeline(self):
        """Executa pipeline completo do agente Shopee."""
        logger.info("🛒 Iniciando pipeline Shopee...")
        
        try:
            from agente_shopee.agent import ShopeeAgent
            
            if "shopee" not in self.agents:
                self.agents["shopee"] = ShopeeAgent()
            
            agent = self.agents["shopee"]
            
            # Etapa 1: Scraper
            logger.info("📊 Etapa 1/3: Scraping de produtos...")
            products = agent.scrape_products(limit=self.config.SHOPEE_DAILY_PRODUCT_LIMIT)
            logger.info(f"✅ {len(products)} produtos encontrados")
            
            # Etapa 2: Geração de conteúdo
            logger.info("✍️ Etapa 2/3: Gerando conteúdo...")
            contents = agent.generate_content(products[:5])
            logger.info(f"✅ {len(contents)} conteúdos gerados")
            
            # Etapa 3: Distribuição (mock em demo)
            logger.info("📤 Etapa 3/3: Distribuindo conteúdo...")
            posted = agent.distribute_content(contents)
            logger.info(f"✅ {posted} posts enviados")
            
            # Log
            self.db.log_execution("shopee", "pipeline", "success", 
                                 f"{len(products)} produtos, {len(contents)} conteúdos")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no pipeline Shopee: {e}")
            self.db.log_execution("shopee", "pipeline", "error", str(e))
            return False
    
    def _get_video_platforms(self) -> list:
        """Detecta plataformas de vídeo configuradas."""
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
        
        # Se modo DEMO e nenhuma configurada, usa todas
        if self.config.IS_DEMO and not platforms:
            platforms = ["youtube", "tiktok", "instagram", "facebook", "kwai"]
        
        return platforms
    
    def run_youtube_pipeline(self):
        """Executa pipeline completo do agente Video multi-plataforma."""
        logger.info("Iniciando pipeline Video Multi-Plataforma...")
        
        try:
            from agente_video.agent import VideoAgent
            
            if "video" not in self.agents:
                # Detecta plataformas configuradas
                platforms = self._get_video_platforms()
                self.agents["video"] = VideoAgent(platforms)
            
            agent = self.agents["video"]
            
            # Executa pipeline completo
            logger.info("Iniciando pipeline multi-plataforma...")
            result = agent.run_pipeline(content_type="long")
            
            upload_results = result['upload_results']
            logger.info(f"Uploads: {upload_results['success_count']} sucesso, {upload_results['failed_count']} falhas")
            
            # Log
            platforms_str = ", ".join(upload_results['results'].keys())
            self.db.log_execution("video", "pipeline", "success" if upload_results['success_count'] > 0 else "partial", 
                                 f"Video publicado em: {platforms_str}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro no pipeline Video: {e}")
            self.db.log_execution("video", "pipeline", "error", str(e))
            return False
    
    def run_once(self):
        """Executa uma rodada manual de todos os pipelines."""
        logger.info("=" * 60)
        logger.info("EXECUCAO MANUAL INICIADA")
        logger.info("=" * 60)
        
        results = {
            "shopee": self.run_shopee_pipeline(),
            "video": self.run_youtube_pipeline()
        }
        
        logger.info("=" * 60)
        logger.info("RESULTADOS:")
        for agent, success in results.items():
            status = "SUCESSO" if success else "FALHA"
            logger.info(f"  {agent.upper()}: {status}")
        logger.info("=" * 60)
        
        return results
    
    def log_status(self):
        """Loga status atual do sistema."""
        stats = self.db.get_stats()
        logger.info("📈 STATUS DO SISTEMA:")
        logger.info(f"  Produtos: {stats['total_products']} (hoje: {stats['products_today']})")
        logger.info(f"  Vídeos: {stats['total_videos']} (publicados: {stats['videos_published']})")
    
    def start(self):
        """Inicia o loop de agendamento."""
        logger.info("🎯 AgentMoney System iniciado")
        self.setup_schedule()
        self.running = True
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Verifica a cada minuto
        except KeyboardInterrupt:
            logger.info("🛑 Sistema interrompido pelo usuário")
            self.stop()
    
    def stop(self):
        """Para o sistema."""
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("👋 AgentMoney System encerrado")
