# ☀️ Sofia - Assistente Virtual da Rosacruz Áurea

Sofia é um assistente virtual inteligente desenvolvido especificamente para a **Escola Internacional da Rosacruz Áurea**. Ela utiliza inteligência artificial para responder perguntas dos visitantes do website, baseando-se exclusivamente na base de conhecimento oficial da escola.

![Sofia Banner](https://img.shields.io/badge/Sofia-Assistente%20Virtual-gold?style=for-the-badge&logo=sun)

## 🌟 Características Principais

- **IA Especializada**: Respostas baseadas exclusivamente no FAQ oficial da Rosacruz Áurea
- **Busca Semântica**: Encontra respostas relevantes usando embeddings e similaridade coseno
- **Design Temático**: Interface personalizada com cores e símbolos da escola
- **Sistema de Contato**: Coleta dados para atendimento posterior quando necessário
- **Links Relacionados**: Sugere materiais complementares automaticamente
- **Notificações**: Sistema integrado com Pushover para administradores

## 🛠️ Tecnologias Utilizadas

- **Streamlit** - Interface web interativa
- **Google Gemini AI** - Geração de respostas inteligentes
- **Sentence Transformers** - Processamento de linguagem natural
- **Pandas** - Manipulação de dados
- **Scikit-learn** - Algoritmos de machine learning
- **Pushover** - Sistema de notificações

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Chave da API do Google Gemini
- Conta do Pushover (opcional, para notificações)
- Arquivo `faq_novo_homem_completo.csv` com as perguntas e respostas

## 🚀 Instalação

### 1. Clone ou baixe os arquivos do projeto

```bash
# Estrutura de pastas necessária:
projeto-sofia/
├── sofia_chatbot.py
├── requirements.txt
├── faq_novo_homem_completo.csv
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml
└── README.md
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as credenciais

Crie o arquivo `.streamlit/secrets.toml` com suas chaves:

```toml
GEMINI_API_KEY = "sua_chave_gemini_aqui"
PUSHOVER_USER_KEY = "sua_chave_pushover_aqui"
PUSHOVER_API_TOKEN = "seu_token_pushover_aqui"
```

### 4. Execute a aplicação

```bash
streamlit run sofia_chatbot.py
```

## 🔑 Configuração das APIs

### Google Gemini API

1. Acesse [Google AI Studio](https://makersuite.google.com/)
2. Crie uma conta ou faça login
3. Gere uma nova chave de API
4. Adicione a chave no arquivo `secrets.toml`

### Pushover (Opcional)

1. Crie uma conta em [pushover.net](https://pushover.net/)
2. Crie uma aplicação para obter o API Token
3. Anote sua User Key
4. Adicione ambas as chaves no arquivo `secrets.toml`

## 📁 Estrutura do Arquivo FAQ

O arquivo `faq_novo_homem_completo.csv` deve conter:

| Coluna | Descrição |
|--------|-----------|
| `user` | Pergunta do usuário |
| `assistant` | Resposta oficial da escola |

Exemplo:
```csv
user,assistant
"O que é a Rosacruz Áurea?","A Rosacruz Áurea é uma escola espiritual..."
"Como participar das atividades?","Para participar das atividades..."
```

## 🎯 Como Funciona

1. **Pergunta do Usuário**: Visitante faz uma pergunta sobre a Rosacruz Áurea
2. **Busca Inteligente**: Sofia analisa a pergunta e busca respostas similares no FAQ
3. **Geração de Resposta**: Gemini AI elabora uma resposta formal baseada no conhecimento oficial
4. **Resposta Insatisfatória**: Se não houver informação suficiente, Sofia solicita contato por e-mail
5. **Notificação**: Administrador recebe notificação via Pushover
6. **Links Relacionados**: Sofia sugere 3 materiais complementares automaticamente

## 🔗 Repositórios de Material

Sofia pode sugerir links dos seguintes repositórios oficiais:

- [Facebook](https://www.facebook.com/RosacruzAurea/)
- [Instagram](https://www.instagram.com/rosacruzaureabrasil/)
- [YouTube](https://www.youtube.com/rosacruzaurea)
- [TikTok](https://www.tiktok.com/@escoladarosacruzaureabr)
- [Pentagrama](https://pentagrama.org.br/)
- [Logon Media](https://logon.media/pt-br/)
- [Civitas Solis](http://www.civitassolis.org.br/)
- [Spotify](https://open.spotify.com/show/2iQxfknpnulpl6srIWwn05)
- [Deezer](https://www.deezer.com/br/show/949072)

## ⚙️ Configurações Avançadas

### Personalização da Interface

Edite o arquivo `.streamlit/config.toml` para alterar cores e tema:

```toml
[theme]
primaryColor = "#DAA520"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#FFF8DC"
textColor = "#000000"
font = "serif"
```

### Ajuste de Similaridade

No código, você pode ajustar o threshold de similaridade:

```python
if similarities[idx] > 0.3:  # Ajuste este valor (0.0 a 1.0)
```

### Número de Sugestões de Links

Altere o número de links sugeridos:

```python
suggested_repos = list(suggested_repos)[:3]  # Altere o número aqui
```

## 🚨 Solução de Problemas

### Erro de Secrets
```
StreamlitSecretNotFoundError: Error parsing secrets file
```
**Solução**: Verifique se o arquivo `.streamlit/secrets.toml` existe e está formatado corretamente.

### Erro de Modelo de Embeddings
```
Error loading embeddings model
```
**Solução**: Verifique sua conexão com internet e reinstale: `pip install sentence-transformers`

### Erro de API Gemini
```
Error generating response
```
**Solução**: Verifique se sua chave da API Gemini está correta e ativa.

## 📊 Monitoramento

### Logs de Conversas
Sofia mantém histórico da conversa durante a sessão. Para logs persistentes, considere integrar com:
- Google Analytics
- Streamlit Cloud Analytics
- Banco de dados personalizado

### Métricas Importantes
- Taxa de perguntas respondidas satisfatoriamente
- Número de solicitações de contato
- Temas mais frequentes

## 🔧 Desenvolvimento

### Adicionando Novas Funcionalidades

1. **Novos Repositórios**: Adicione no dicionário `REPOSITORIOS`
2. **Palavras-chave**: Edite `keywords_mapping` para melhor sugestão de links
3. **Validações**: Adicione validações no formulário de contato

### Estrutura do Código

```python
# Funções principais:
- load_faq_data()           # Carrega CSV
- find_similar_questions()  # Busca semântica
- generate_sofia_response() # Geração com Gemini
- suggest_related_links()   # Sugestão de materiais
- send_contact_to_admin()   # Notificações
```

## 📝 Licença

Este projeto foi desenvolvido especificamente para a **Escola Internacional da Rosacruz Áurea**. 

## 🤝 Suporte

Para suporte técnico ou dúvidas sobre o funcionamento:

1. Verifique a seção de solução de problemas
2. Consulte os logs do Streamlit
3. Entre em contato com o administrador do sistema

## 📈 Roadmap

- [ ] Integração com banco de dados
- [ ] Dashboard de analytics
- [ ] Suporte multilíngue
- [ ] API REST
- [ ] Integração com WhatsApp
- [ ] Sistema de feedback dos usuários

---

**Desenvolvido com ☀️ para a Escola Internacional da Rosacruz Áurea**

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=flat-square&logo=streamlit)
![License](https://img.shields.io/badge/License-Escola%20Rosacruz%20Áurea-gold?style=flat-square)
