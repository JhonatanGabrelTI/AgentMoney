"""
AgentMoney - Agente Video Multi-Plataforma
Automação de canais faceless em YouTube, TikTok, Instagram, Facebook e Kwai.
"""

from .agent import VideoAgent
from .research import NicheResearcher
from .audio import AudioGenerator
from .thumbnail import ThumbnailGenerator
from .video import VideoAssembler

__all__ = [
    "VideoAgent", 
    "NicheResearcher", 
    "AudioGenerator",
    "ThumbnailGenerator",
    "VideoAssembler"
]
