# Guia: Como Obter OAuth2 do YouTube para Upload

> **Diferenca:** API Key = apenas leitura | OAuth2 = upload de videos

---

## 📋 RESUMO DO PROCESSO

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Google Cloud   │───→│  Tela Consent.   │───→│  OAuth2 Playgr. │
│    Console      │    │    OAuth         │    │  (get tokens)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   Criar Projeto           Configurar App         Obter Refresh
   Ativar API              Scopes YouTube          Token
```

---

## PASSO 1: Acessar Google Cloud Console

1. Va para: https://console.cloud.google.com/
2. Faca login com sua conta Google
3. Clique no seletor de projeto (topo) → **"Novo Projeto"**
4. Nomeie: `AgentMoney-YouTube`
5. Clique em **Criar**

---

## PASSO 2: Ativar YouTube Data API

1. No menu lateral, va em: **APIs e Servicos** → **Biblioteca**
2. Pesquise: `YouTube Data API v3`
3. Clique no resultado e depois em **ATIVAR**
4. Aguarde a ativacao (pode levar 1-2 minutos)

---

## PASSO 3: Configurar Tela de Consentimento OAuth

1. No menu lateral: **APIs e Servicos** → **Tela de consentimento OAuth**
2. Selecione: **Externo** (para qualquer usuario)
3. Clique em **CRIAR**

### Preencha os dados do app:

| Campo | Valor |
|-------|-------|
| **Nome do app** | AgentMoney Video Uploader |
| **Email de suporte** | seu-email@gmail.com |
| **Logotipo** | (opcional) |
| **Dominio** | (deixe em branco por enquanto) |
| **Email de contato** | seu-email@gmail.com |

4. Clique em **SALVAR E CONTINUAR**

---

## PASSO 4: Adicionar Escopos (Scopes)

1. Na tela de escopos, clique em **ADICIONAR OU REMOVER ESCOPOS**
2. Pesquise e selecione:
   - ✅ `youtube.upload` - Fazer upload de videos
   - ✅ `youtube` - Gerenciar conta YouTube
   - ✅ `youtube.readonly` - Ver dados do canal
3. Clique em **ATUALIZAR**
4. **SALVAR E CONTINUAR**

---

## PASSO 5: Adicionar Usuarios de Teste

1. Na tela de usuarios de teste, clique **ADICIONAR USUARIOS**
2. Digite seu email do YouTube: `seu-email@gmail.com`
3. **SALVAR E CONTINUAR**
4. Clique em **VOLTAR PARA O PAINEL**

---

## PASSO 6: Criar Credenciais OAuth2

1. Menu lateral: **APIs e Servicos** → **Credenciais**
2. Clique em **+ CRIAR CREDENCIAIS** → **ID do cliente OAuth**
3. Tipo de aplicativo: **Aplicativo de desktop** (ou "Outros")
4. Nome: `AgentMoney Desktop`
5. Clique em **CRIAR**
6. **BAIXE O JSON** (clique no icone de download ⬇️)
7. Renomeie o arquivo para: `client_secret.json`

### Dentro do JSON voce encontrara:
```json
{
  "installed": {
    "client_id": "123456789-xxxxxxxx.apps.googleusercontent.com",
    "client_secret": "GOCSPX-xxxxxxxx",
    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
  }
}
```

---

## PASSO 7: Obter Refresh Token (Metodo Facil)

Use o **OAuth 2.0 Playground** do Google:

### 7.1 Acesse:
https://developers.google.com/oauthplayground

### 7.2 Configurar:
1. Clique no icone de **engrenagem** ⚙️ (topo direito)
2. Marque: ✅ **Use your own OAuth credentials**
3. Preencha:
   - **OAuth Client ID**: (do seu `client_secret.json`)
   - **OAuth Client Secret**: (do seu `client_secret.json`)
4. Clique **Close**

### 7.3 Selecionar Escopos:
1. Na lista a esquerda, procure: **YouTube Data API v3**
2. Selecione:
   - ✅ `https://www.googleapis.com/auth/youtube.upload`
   - ✅ `https://www.googleapis.com/auth/youtube`
3. Clique **Authorize APIs**

### 7.4 Autorizar:
1. Faca login com sua conta do YouTube
2. Clique em **Permitir** nas telas de permissao
3. Voce vera: "Authorization code received"

### 7.5 Trocar por Tokens:
1. Clique no botao **Exchange authorization code for tokens**
2. Copie o valor de **Refresh token** (comeca com `1//`)

---

## PASSO 8: Configurar no AgentMoney

Edite seu arquivo `.env`:

```env
# YouTube API (voce ja tem)
YOUTUBE_API_KEY=AIzaSyCsbx8OQyfr1jA1BFHb2iN-iEVlJ5J3kYo

# YouTube OAuth2 (NOVO - adicione esses 3)
YOUTUBE_CLIENT_ID=123456789-xxxxxxxx.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-xxxxxxxx
YOUTUBE_REFRESH_TOKEN=1//04xxxxxxxxxxxxxxxxxxxxxxxxxx

# Opcional: ID do seu canal
YOUTUBE_CHANNEL_ID=UCxxxxxxxxxxxxxxxxxxx
```

---

## ✅ VERIFICAR SE FUNCIONOU

```bash
python main.py status
```

Voce deve ver:
```
YouTube: OK
```

---

## 🚨 IMPORTANTE: Limite de Cotas

| Tipo | Limite Diario |
|------|---------------|
| Uploads | 100 videos/dia |
| API Calls | 10.000 unidades/dia |

**Custo de cada operacao:**
- Upload de video: ~1600 unidades
- Pesquisa: 100 unidades
- Estatisticas: 1 unidade

---

## 🐛 PROBLEMAS COMUNS

### "Error 403: access_denied"
→ Verifique se adicionou seu email em "Usuarios de teste"

### "Invalid client"
→ Copiou o client_id completo? Deve terminar com `.apps.googleusercontent.com`

### "Token expired"
→ O refresh token e valido por 6 meses (se nao usar). Gere outro.

### "Upload failed"
→ Verifique se ativou a API no Google Cloud e se tem quota disponivel

---

## 📞 PRECISA DE AJUDA?

Se travar em algum passo, me diga qual erro aparece que eu ajudo!
