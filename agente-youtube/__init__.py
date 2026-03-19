"""
AgentMoney - Agente YouTube Music IA
Automação de canais faceless com música e vídeos.
"""

from .agent import YouTubeAgent
from .research import NicheResearcher
from .audio import AudioGenerator
from .thumbnail import ThumbnailGenerator
from .video import VideoAssembler
from .uploader import YouTubeUploader

__all__ = [
    "YouTubeAgent", 
    "NicheResearcher", 
    "AudioGenerator",
    "ThumbnailGenerator",
    "VideoAssembler",
    "YouTubeUploader"
]
