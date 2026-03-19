"""
Camada de persistência do AgentMoney.
Suporta SQLite (demo) e PostgreSQL (produção).
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict

from .config import Config
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class Product:
    """Modelo de produto Shopee."""
    id: str
    name: str
    price: float
    original_price: float
    discount: int
    rating: float
    sales: int
    commission_rate: float
    commission_value: float
    category: str
    affiliate_link: str
    image_url: str
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class Video:
    """Modelo de vídeo YouTube."""
    id: str
    title: str
    description: str
    tags: List[str]
    category: str
    audio_path: str
    thumbnail_path: str
    video_path: Optional[str]
    youtube_id: Optional[str]
    status: str  # pending, processing, uploaded, published, error
    created_at: str = None
    uploaded_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class Database:
    """Banco de dados do AgentMoney."""
    
    def __init__(self):
        self.config = Config
        self.config.ensure_directories()
        self.db_path = self.config.DATA_DIR / "agentmoney.db"
        self._init_db()
    
    def _get_connection(self):
        """Retorna conexão SQLite."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Inicializa tabelas do banco."""
        with self._get_connection() as conn:
            # Tabela de produtos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    original_price REAL,
                    discount INTEGER,
                    rating REAL,
                    sales INTEGER,
                    commission_rate REAL,
                    commission_value REAL,
                    category TEXT,
                    affiliate_link TEXT,
                    image_url TEXT,
                    created_at TEXT,
                    content_generated INTEGER DEFAULT 0,
                    posted_telegram INTEGER DEFAULT 0,
                    posted_whatsapp INTEGER DEFAULT 0
                )
            """)
            
            # Tabela de vídeos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    tags TEXT,
                    category TEXT,
                    audio_path TEXT,
                    thumbnail_path TEXT,
                    video_path TEXT,
                    youtube_id TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT,
                    uploaded_at TEXT
                )
            """)
            
            # Tabela de logs de execução
            conn.execute("""
                CREATE TABLE IF NOT EXISTS execution_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT,
                    details TEXT,
                    created_at TEXT
                )
            """)
            
            conn.commit()
        logger.info("Banco de dados inicializado")
    
    # ==================== PRODUTOS ====================
    
    def save_product(self, product: Product) -> bool:
        """Salva ou atualiza um produto."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO products 
                    (id, name, price, original_price, discount, rating, sales,
                     commission_rate, commission_value, category, affiliate_link,
                     image_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product.id, product.name, product.price, product.original_price,
                    product.discount, product.rating, product.sales,
                    product.commission_rate, product.commission_value,
                    product.category, product.affiliate_link, product.image_url,
                    product.created_at
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar produto: {e}")
            return False
    
    def get_products(self, category: Optional[str] = None, 
                     limit: int = 100) -> List[Product]:
        """Recupera produtos do banco."""
        query = "SELECT * FROM products"
        params = []
        
        if category:
            query += " WHERE category = ?"
            params.append(category)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        
        products = []
        for row in rows:
            data = dict(row)
            data['tags'] = []  # Compatibilidade
            products.append(Product(**{k: v for k, v in data.items() 
                                     if k in Product.__dataclass_fields__}))
        return products
    
    def get_products_pending_content(self, limit: int = 5) -> List[Product]:
        """Recupera produtos sem conteúdo gerado."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM products WHERE content_generated = 0 LIMIT ?",
                (limit,)
            ).fetchall()
        
        products = []
        for row in rows:
            data = dict(row)
            products.append(Product(**{k: v for k, v in data.items() 
                                     if k in Product.__dataclass_fields__}))
        return products
    
    def mark_product_content_generated(self, product_id: str):
        """Marca produto como processado."""
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE products SET content_generated = 1 WHERE id = ?",
                (product_id,)
            )
            conn.commit()
    
    # ==================== VÍDEOS ====================
    
    def save_video(self, video: Video) -> bool:
        """Salva ou atualiza um vídeo."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO videos 
                    (id, title, description, tags, category, audio_path,
                     thumbnail_path, video_path, youtube_id, status,
                     created_at, uploaded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    video.id, video.title, video.description,
                    json.dumps(video.tags), video.category, video.audio_path,
                    video.thumbnail_path, video.video_path, video.youtube_id,
                    video.status, video.created_at, video.uploaded_at
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar vídeo: {e}")
            return False
    
    def get_videos(self, status: Optional[str] = None, 
                   limit: int = 100) -> List[Video]:
        """Recupera vídeos do banco."""
        query = "SELECT * FROM videos"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        
        videos = []
        for row in rows:
            data = dict(row)
            data['tags'] = json.loads(data['tags']) if data['tags'] else []
            videos.append(Video(**{k: v for k, v in data.items() 
                                  if k in Video.__dataclass_fields__}))
        return videos
    
    def update_video_status(self, video_id: str, status: str, 
                           youtube_id: Optional[str] = None):
        """Atualiza status do vídeo."""
        uploaded_at = datetime.now().isoformat() if status == "published" else None
        
        with self._get_connection() as conn:
            conn.execute(
                """UPDATE videos SET status = ?, youtube_id = ?, uploaded_at = ?
                   WHERE id = ?""",
                (status, youtube_id, uploaded_at, video_id)
            )
            conn.commit()
    
    # ==================== LOGS ====================
    
    def log_execution(self, agent: str, action: str, 
                      status: str, details: str = ""):
        """Registra log de execução."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO execution_logs (agent, action, status, details, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (agent, action, status, details, datetime.now().isoformat()))
            conn.commit()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema."""
        with self._get_connection() as conn:
            total_products = conn.execute(
                "SELECT COUNT(*) FROM products"
            ).fetchone()[0]
            
            products_today = conn.execute(
                "SELECT COUNT(*) FROM products WHERE date(created_at) = date('now')"
            ).fetchone()[0]
            
            total_videos = conn.execute(
                "SELECT COUNT(*) FROM videos"
            ).fetchone()[0]
            
            videos_published = conn.execute(
                "SELECT COUNT(*) FROM videos WHERE status = 'published'"
            ).fetchone()[0]
            
            return {
                "total_products": total_products,
                "products_today": products_today,
                "total_videos": total_videos,
                "videos_published": videos_published
            }
