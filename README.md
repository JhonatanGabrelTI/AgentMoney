# 🤖 AgentMoney System

> **Sistema de Automação de Renda** - Agentes inteligentes para monetização via Shopee Affiliate e YouTube faceless.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Mode](https://img.shields.io/badge/Mode-DEMO-yellow.svg)]()

---

## 📋 Visão Geral

O **AgentMoney** é um ecossistema de automação completo projetado para gerar renda passiva através de:

1. **Agente Shopee** - Curadoria automatizada de produtos, geração de copy e distribuição social
2. **Agente Video** - Produção automatizada de canais "faceless" em múltiplas plataformas:
   - YouTube (vídeos e Shorts)
   - TikTok
   - Instagram Reels
   - Facebook
   - Kwai

### Arquitetura

```
AgentMoney/
├── core-engine/          # Orquestrador e infraestrutura
│   ├── orchestrator.py   # Coordenação de agentes
│   ├── config.py         # Configurações
│   ├── database.py       # Persistência (SQLite/PostgreSQL)
│   ├── logger.py         # Logging centralizado
│   └── uploaders/        # Uploaders multi-plataforma
│       ├── base.py       # Classe base
│       ├── manager.py    # Gerenciador de uploads
│       ├── youtube.py    # YouTube uploader
│       ├── tiktok.py     # TikTok uploader
│       ├── instagram.py  # Instagram uploader
│       ├── facebook.py   # Facebook uploader
│       └── kwai.py       # Kwai uploader
├── agente_shopee/        # Agente de afiliados Shopee
│   ├── agent.py          # Orquestração do agente
│   ├── scraper.py        # Browser automation
│   └── content.py        # Geração de copy
├── agente_video/         # Agente de vídeo multi-plataforma
│   ├── agent.py          # Orquestração do agente
│   ├── research.py       # Análise de nichos
│   ├── audio.py          # Geração de música IA
│   ├── thumbnail.py      # Geração de thumbnails
│   └── video.py          # Montagem de vídeo
└── data/                 # Banco de dados e cache
```

---

## 🚀 Instalação Rápida

### 1. Clone o repositório

```bash
git clone https://github.com/JhonatanGabrelTI/AgentMoney.git
cd AgentMoney
```

### 2. Configure ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale dependências

```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com suas credenciais
```

### 5. Execute

```bash
# Ver status do sistema
python main.py status

# Executar demonstração (modo demo)
python main.py demo

# Iniciar em produção
python main.py start
```

---

## ⚙️ Configuração

### Modo Demo (Padrão)

Por padrão, o sistema roda em modo `DEMO` onde:
- Todas as APIs são simuladas
- Nenhuma chamada real é feita
- Dados são gerados aleatoriamente
- Uploads são simulados

Para ativar produção, edite o `.env`:

```env
AGENTMONEY_MODE=production
```

### APIs Necessárias (Produção)

#### OpenAI (Conteúdo)
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

#### YouTube
```env
YOUTUBE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=seu-client-secret
YOUTUBE_REFRESH_TOKEN=seu-refresh-token
```

#### TikTok
```env
TIKTOK_ACCESS_TOKEN=seu-tiktok-access-token
TIKTOK_OPEN_ID=seu-tiktok-open-id
```

#### Instagram
```env
INSTAGRAM_ACCESS_TOKEN=seu-instagram-access-token
INSTAGRAM_ACCOUNT_ID=seu-instagram-account-id
```

#### Facebook
```env
FACEBOOK_ACCESS_TOKEN=seu-facebook-access-token
FACEBOOK_PAGE_ID=seu-facebook-page-id
```

#### Kwai
```env
KWAI_ACCESS_TOKEN=seu-kwai-access-token
KWAI_APP_ID=seu-kwai-app-id
KWAI_APP_SECRET=seu-kwai-app-secret
```

#### Shopee (Afiliados)
```env
SHOPEE_AFFILIATE_ID=seu-id
SHOPEE_AFFILIATE_TOKEN=seu-token
```

#### Música IA (Opcional)
```env
SUNO_API_KEY=sua-key
# ou
UDIO_API_KEY=sua-key
```

#### Imagem IA (Thumbnails)
```env
# RECOMENDADO: Usar DALL-E 3 (ja incluso na OpenAI!)
# Alternativas: Stability AI, Leonardo.ai
STABILITY_API_KEY=sua-key
```

---

## 🛒 Agente Shopee

### Funcionalidades

- **Scraper Inteligente**: Extrai produtos do dashboard de afiliados
- **Filtros de Lucratividade**: +500 vendas, >4.5 estrelas, comissão premium
- **Geração de Copy**: Headlines persuasivas, scripts de vídeo
- **Distribuição**: Postagem automatizada em Telegram/WhatsApp

### Fluxo de Trabalho

```
1. Scraper → Busca produtos com critérios
2. Análise → Classifica por nicho (Casa, Tech, Moda)
3. Conteúdo → Gera copy, scripts, hashtags
4. Distribuição → Posta nas redes
```

### Critérios de Seleção

| Métrica | Mínimo |
|---------|--------|
| Vendas | 500+ |
| Avaliação | 4.5+ |
| Comissão | 5%+ |
| Desconto | 30%+ |

---

## 🎬 Agente Video Multi-Plataforma

### Plataformas Suportadas

| Plataforma | Tipo de Conteúdo | Formato |
|------------|-----------------|---------|
| YouTube | Longos + Shorts | 16:9, 9:16 |
| TikTok | Vídeos curtos | 9:16 |
| Instagram | Reels | 9:16 |
| Facebook | Vídeos + Reels | 16:9, 9:16 |
| Kwai | Vídeos curtos | 9:16 |

### Nichos Suportados

| Nicho | Descrição | Duração | Melhores Plataformas |
|-------|-----------|---------|---------------------|
| Lo-fi | Música para estudar | 3h | YouTube, Instagram, TikTok |
| Meditação | Sons relaxantes | 1h | YouTube, Instagram, Facebook |
| Oração | Devocional | 30min | YouTube, Facebook, Kwai |
| Natureza | Sons da natureza | 10h | YouTube |
| Ambient | Música espacial | 2h | YouTube, TikTok, Instagram |
| Shorts Lo-fi | Vibes rápidas | 60s | TikTok, Instagram, Kwai |
| Motivação | Vídeos inspiradores | 30s | TikTok, Instagram, Kwai |

### Fluxo de Produção

```
1. Research → Analisa nichos e tendências
2. Audio → Gera música com Suno/Udio
3. Thumbnail → Cria imagem com DALL-E 3 (OpenAI)
4. Video → Monta com ffmpeg
5. Upload → Publica em TODAS as plataformas configuradas
```

### Distribuição Automática

O sistema publica simultaneamente em todas as plataformas configuradas:
- Upload paralelo com thread pool
- Metadados otimizados por plataforma
- Retry automático em falhas
- Relatório consolidado de publicação

---

## 📊 KPIs e Metas

### Diárias

| Agente | Meta |
|--------|------|
| Shopee | 10 produtos analisados → 5 conteúdos → 5 posts |
| YouTube | 1 trilha completa → SEO → 1 upload |

### Métricas Monitoradas

- Produtos catalogados
- Taxa de conversão (cliques)
- Views de vídeos
- Crescimento de inscritos

---

## 🛠️ Comandos CLI

```bash
# Status do sistema
python main.py status

# Executar demonstração
python main.py demo

# Rodada manual única
python main.py run-once

# Iniciar agendamento
python main.py start

# Inicializar banco
python main.py init-db

# Ajuda
python main.py --help
```

---

## 🗓️ Agendamentos

| Tarefa | Frequência | Horário |
|--------|------------|---------|
| Shopee Scraper | A cada 2h | Automático |
| Shopee Post | A cada 2h | Automático |
| YouTube Research | Diário | 08:00 |
| YouTube Upload | Diário | Após research |
| Log Status | A cada 30min | Automático |

---

## 📝 Roadmap

### v1.0 (Atual)
- [x] Estrutura base
- [x] Modo demo completo
- [x] Agente Shopee (mock)
- [x] Agente YouTube (mock)
- [x] CLI básico

### v1.1
- [ ] Integração Shopee API real
- [ ] Playwright scraper
- [ ] Telegram bot

### v1.2
- [ ] Integração YouTube API
- [ ] Suno/Udio API
- [ ] Upload automatizado

### v1.3
- [ ] Dashboard web
- [ ] Analytics avançado
- [ ] Múltiplos canais

---

## 🔒 Compliance

### Shopee Affiliate
- ✅ Sem links em páginas oficiais
- ✅ Sem uso de logo institucional
- ✅ Copy original (não copiado)

### YouTube
- ✅ Conteúdo original ou licenciado
- ✅ Sem copyright infringement
- ✅ Community guidelines compliant

---

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 📞 Suporte

- Issues: [GitHub Issues](https://github.com/JhonatanGabrelTI/AgentMoney/issues)
- Email: suporte@agentmoney.local

---

<p align="center">
  <strong>🚀 AgentMoney System - Dinheiro enquanto você dorme</strong>
</p>
