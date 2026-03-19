#!/usr/bin/env python3
"""
AgentMoney System - Ponto de entrada principal.

Uso:
    python main.py --help
    python main.py run-once      # Executa uma rodada
    python main.py start         # Inicia agendamento
    python main.py status        # Mostra status
    python main.py demo          # Executa demonstração
"""

import sys
from pathlib import Path

# Adiciona diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

import click
from colorama import init
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from core_engine.orchestrator import AgentMoneyOrchestrator
from core_engine.config import Config
from core_engine.logger import get_logger
from core_engine.database import Database

# Inicializa colorama
init(autoreset=True)
console = Console()
logger = get_logger("CLI")


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Modo verbose')
def cli(verbose):
    """AgentMoney - Sistema de Automação de Renda"""
    if verbose:
        console.print("[dim]Modo verbose ativado[/dim]")


@cli.command()
def status():
    """Mostra status do sistema."""
    config = Config()
    db = Database()
    
    # Painel de configuração
    mode = "[DEMO]" if config.IS_DEMO else "[PRODUCAO]"
    config_text = f"""Modo: {mode}
Log Level: {config.LOG_LEVEL}
Diretorio: {config.BASE_DIR}
Database: {config.DATABASE_URL}"""
    console.print(Panel(config_text, title="[bold blue]Configuracao[/bold blue]", box=box.ROUNDED))
    
    # Tabela de estatísticas
    stats = db.get_stats()
    table = Table(title="Estatisticas", box=box.ROUNDED)
    table.add_column("Metrica", style="cyan")
    table.add_column("Valor", style="green")
    
    table.add_row("Total Produtos", str(stats['total_products']))
    table.add_row("Produtos Hoje", str(stats['products_today']))
    table.add_row("Total Videos", str(stats['total_videos']))
    table.add_row("Videos Publicados", str(stats['videos_published']))
    
    console.print(table)
    
    # Status de APIs
    api_table = Table(title="APIs Configuradas", box=box.ROUNDED)
    api_table.add_column("Serviço", style="cyan")
    api_table.add_column("Status", style="green")
    
    apis = [
        ("OpenAI", "OK" if config.OPENAI_API_KEY != "demo-key" else "DEMO"),
        ("Suno", "OK" if config.SUNO_API_KEY != "demo-key" else "DEMO"),
        ("YouTube", "OK" if config.YOUTUBE_CLIENT_ID else "OFF"),
        ("Shopee", "OK" if config.SHOPEE_AFFILIATE_ID else "OFF"),
    ]
    
    for name, status in apis:
        api_table.add_row(name, status)
    
    console.print(api_table)


@cli.command()
def demo():
    """Executa demonstração completa do sistema."""
    console.print(Panel.fit(
        "[bold green]AgentMoney System - Modo Demonstracao[/bold green]\n"
        "Todas as APIs estao em modo simulacao.\n"
        "Execute 'cp .env.example .env' e configure para producao.",
        box=box.DOUBLE
    ))
    
    orchestrator = AgentMoneyOrchestrator()
    orchestrator.run_once()
    
    console.print("\n[bold green]Demonstracao concluida![/bold green]")
    console.print("Use 'python main.py status' para ver resultados.")


@cli.command()
def run_once():
    """Executa uma rodada manual de todos os agentes."""
    console.print("[bold yellow]Executando rodada manual...[/bold yellow]")
    
    orchestrator = AgentMoneyOrchestrator()
    results = orchestrator.run_once()
    
    # Resultados
    for agent, success in results.items():
        if success:
            console.print(f"[green]{agent.upper()}: Sucesso[/green]")
        else:
            console.print(f"[red]{agent.upper()}: Falha[/red]")


@cli.command()
def start():
    """Inicia o sistema em modo de agendamento."""
    console.print(Panel.fit(
        "[bold green]AgentMoney System Online[/bold green]\n"
        "Agendamentos:\n"
        "  - Shopee: A cada 2 horas\n"
        "  - YouTube: Diariamente as 08:00\n"
        "Pressione Ctrl+C para parar",
        box=box.DOUBLE
    ))
    
    orchestrator = AgentMoneyOrchestrator()
    orchestrator.start()


@cli.command()
def init_db():
    """Inicializa/reset banco de dados."""
    console.print("[yellow]Inicializando banco de dados...[/yellow]")
    db = Database()
    console.print("[green]Banco de dados pronto![/green]")


if __name__ == "__main__":
    cli()
