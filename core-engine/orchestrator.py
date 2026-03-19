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
    
    def run_youtube_pipeline(self):
        """Executa pipeline completo do agente YouTube."""
        logger.info("🎬 Iniciando pipeline YouTube...")
        
        try:
            from agente_youtube.agent import YouTubeAgent
            
            if "youtube" not in self.agents:
                self.agents["youtube"] = YouTubeAgent()
            
            agent = self.agents["youtube"]
            
            # Etapa 1: Pesquisa de nicho
            logger.info("🔍 Etapa 1/5: Pesquisando nichos...")
            niche = agent.research_niche()
            logger.info(f"✅ Nicho selecionado: {niche['name']}")
            
            # Etapa 2: Produção de áudio
            logger.info("🎵 Etapa 2/5: Produzindo áudio...")
            audio_path = agent.generate_audio(niche)
            logger.info(f"✅ Áudio gerado: {audio_path}")
            
            # Etapa 3: Geração de thumbnail
            logger.info("🖼️ Etapa 3/5: Criando thumbnail...")
            thumbnail_path = agent.generate_thumbnail(niche)
            logger.info(f"✅ Thumbnail criada: {thumbnail_path}")
            
            # Etapa 4: Montagem do vídeo
            logger.info("🎥 Etapa 4/5: Montando vídeo...")
            video_path = agent.assemble_video(audio_path, thumbnail_path, niche)
            logger.info(f"✅ Vídeo montado: {video_path}")
            
            # Etapa 5: Upload (simulado em demo)
            logger.info("📤 Etapa 5/5: Fazendo upload...")
            video_id = agent.upload_video(video_path, niche)
            logger.info(f"✅ Vídeo publicado (ID: {video_id})")
            
            # Log
            self.db.log_execution("youtube", "pipeline", "success", 
                                 f"Vídeo {video_id} publicado em {niche['name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no pipeline YouTube: {e}")
            self.db.log_execution("youtube", "pipeline", "error", str(e))
            return False
    
    def run_once(self):
        """Executa uma rodada manual de todos os pipelines."""
        logger.info("=" * 60)
        logger.info("🚀 EXECUÇÃO MANUAL INICIADA")
        logger.info("=" * 60)
        
        results = {
            "shopee": self.run_shopee_pipeline(),
            "youtube": self.run_youtube_pipeline()
        }
        
        logger.info("=" * 60)
        logger.info("📊 RESULTADOS:")
        for agent, success in results.items():
            status = "✅ SUCESSO" if success else "❌ FALHA"
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
