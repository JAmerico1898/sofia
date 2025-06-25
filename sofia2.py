import streamlit as st
import pandas as pd
import google.generativeai as genai
import re
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from typing import List, Tuple

# Configuração da página
st.set_page_config(
    page_title="Sofia - Assistente Virtual da Rosacruz Áurea",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #DAA520;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .sun-icon {
        font-size: 3rem;
        color: #FFD700;
        text-align: center;
        margin: 1rem 0;
    }
    .sofia-response {
        background-color: #FFF8DC;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #DAA520;
        margin: 1rem 0;
    }
    .user-question {
        background-color: #F0F8FF;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #4682B4;
        margin: 1rem 0;
    }
    .contact-form {
        background-color: #FFE4E1;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #CD853F;
        margin: 1rem 0;
    }
    .links-section {
        background-color: #F5F5DC;
        padding: 1rem;
        border-radius: 10px;
        margin-top: 1rem;
        border: 1px solid #DAA520;
    }
</style>
""", unsafe_allow_html=True)

try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    PUSHOVER_USER_KEY = st.secrets.get("PUSHOVER_USER_KEY", "")
    PUSHOVER_API_TOKEN = st.secrets.get("PUSHOVER_API_TOKEN", "")
except Exception as e:
    st.error(f"Erro ao carregar configurações: {e}")
    st.info("Verifique se o arquivo .streamlit/secrets.toml está configurado corretamente.")
    GEMINI_API_KEY = ""
    PUSHOVER_USER_KEY = ""
    PUSHOVER_API_TOKEN = ""

# Repositórios de material da Rosacruz Áurea
REPOSITORIOS = {
    "Facebook": "https://www.facebook.com/RosacruzAurea/",
    "Instagram": "https://www.instagram.com/rosacruzaureabrasil/",
    "YouTube": "https://www.youtube.com/rosacruzaurea",
    "TikTok": "https://www.tiktok.com/@escoladarosacruzaureabr",
    "Pentagrama": "https://pentagrama.org.br/",
    "Logon Media": "https://logon.media/pt-br/",
    "Civitas Solis": "http://www.civitassolis.org.br/",
    "Spotify": "https://open.spotify.com/show/2iQxfknpnulpl6srIWwn05?si=d4a925bc23b2411e&nd=1&dlsi=5dd18f7129a2429c",
    "Deezer": "https://www.deezer.com/br/show/949072"
}

# Inicializar session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'faq_data' not in st.session_state:
    st.session_state.faq_data = None
if 'embeddings_model' not in st.session_state:
    st.session_state.embeddings_model = None

@st.cache_data
def load_faq_data():
    """Carrega os dados do FAQ"""
    try:
        df = pd.read_csv('faq_novo_homem_completo_2.csv')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo FAQ: {e}")
        return None

@st.cache_resource
def load_embeddings_model():
    """Carrega o modelo de embeddings"""
    try:
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        st.error(f"Erro ao carregar modelo de embeddings: {e}")
        return None

def find_similar_questions(user_question: str, faq_data: pd.DataFrame, model, top_k: int = 3) -> List[Tuple[str, str, float]]:
    """Encontra perguntas similares no FAQ usando embeddings"""
    if model is None or faq_data is None:
        return []
    
    try:
        # Gerar embedding da pergunta do usuário
        user_embedding = model.encode([user_question])
        
        # Gerar embeddings das perguntas do FAQ
        faq_questions = faq_data['user'].tolist()
        faq_embeddings = model.encode(faq_questions)
        
        # Calcular similaridade
        similarities = cosine_similarity(user_embedding, faq_embeddings)[0]
        
        # Encontrar as top_k perguntas mais similares
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.3:  # Threshold de similaridade
                results.append((
                    faq_data.iloc[idx]['user'],
                    faq_data.iloc[idx]['assistant'],
                    similarities[idx]
                ))
        
        return results
    except Exception as e:
        st.error(f"Erro na busca por similaridade: {e}")
        return []

def generate_sofia_response(user_question: str, similar_qa_pairs: List[Tuple[str, str, float]]) -> str:
    """Gera resposta usando Gemini baseada no FAQ"""
    if not GEMINI_API_KEY:
        return "Erro: Chave da API do Gemini não configurada."
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Construir contexto com as perguntas similares encontradas
        context = ""
        if similar_qa_pairs:
            context = "Baseando-se EXCLUSIVAMENTE nas seguintes informações do FAQ da Escola Internacional da Rosacruz Áurea:\n\n"
            for i, (q, a, score) in enumerate(similar_qa_pairs, 1):
                context += f"FAQ {i}:\nPergunta: {q}\nResposta: {a}\n\n"
        
        prompt = f"""
Você é Sofia, a assistente virtual da Escola Internacional da Rosacruz Áurea, simbolizada por um sol ☀️.

INSTRUÇÕES IMPORTANTES:
1. Responda APENAS com base nas informações fornecidas do FAQ da Escola Internacional da Rosacruz Áurea
2. Use um tom formal, respeitoso e acolhedor
3. Se não houver informações suficientes no FAQ para responder adequadamente, diga claramente que não possui informações suficientes
4. Mantenha o foco nos ensinamentos e princípios da Rosacruz Áurea
5. Seja precisa e não invente informações
6. Não faça referência aos FAQ

{context}

Pergunta do usuário: {user_question}

Resposta da Sofia:
"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Erro ao gerar resposta: {e}"

def suggest_related_links(user_question: str) -> List[Tuple[str, str]]:
    """Sugere links relacionados baseado na pergunta"""
    # Lógica simples de sugestão baseada em palavras-chave
    keywords_mapping = {
        'meditação': ['YouTube', 'Spotify', 'Pentagrama'],
        'ensinamento': ['Pentagrama', 'Logon Media', 'YouTube'],
        'espiritualidade': ['Pentagrama', 'Civitas Solis', 'YouTube'],
        'filosofia': ['Logon Media', 'Pentagrama', 'Civitas Solis'],
        'rosacruz': ['Facebook', 'Instagram', 'Pentagrama'],
        'escola': ['Facebook', 'Instagram', 'YouTube'],
        'música': ['Spotify', 'Deezer', 'YouTube'],
        'vídeo': ['YouTube', 'TikTok', 'Instagram'],
        'podcast': ['Spotify', 'Deezer', 'Logon Media']
    }
    
    question_lower = user_question.lower()
    suggested_repos = set()
    
    for keyword, repos in keywords_mapping.items():
        if keyword in question_lower:
            suggested_repos.update(repos[:2])  # Adiciona até 2 repositórios por palavra-chave
    
    # Se não encontrou palavras-chave específicas, sugere os principais
    if not suggested_repos:
        suggested_repos = {'YouTube', 'Pentagrama', 'Facebook'}
    
    # Limita a 3 sugestões
    suggested_repos = list(suggested_repos)[:3]
    
    return [(repo, REPOSITORIOS[repo]) for repo in suggested_repos if repo in REPOSITORIOS]

def send_contact_to_admin(user_email: str, user_question: str) -> bool:
    """Envia informações de contato para o administrador via Pushover"""
    if not PUSHOVER_USER_KEY or not PUSHOVER_API_TOKEN:
        return False
    
    try:
        message = f"Nova solicitação de contato - Sofia Chatbot\n\nE-mail: {user_email}\nPergunta: {user_question}"
        
        response = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": message,
            "title": "Sofia - Nova solicitação de contato"
        })
        
        return response.status_code == 200
    except Exception as e:
        st.error(f"Erro ao enviar notificação: {e}")
        return False

def main():
    # Header
    st.markdown('<div class="sun-icon">☀️</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">Sofia - Assistente Virtual da Rosacruz Áurea</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p><em>Olá! Eu sou Sofia, sua assistente virtual. Estou aqui para responder suas perguntas sobre a Escola Internacional da Rosacruz Áurea.</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados e modelo
    if st.session_state.faq_data is None:
        with st.spinner("Carregando base de conhecimento..."):
            st.session_state.faq_data = load_faq_data()
    
    if st.session_state.embeddings_model is None:
        with st.spinner("Inicializando sistema de busca..."):
            st.session_state.embeddings_model = load_embeddings_model()
    
    if st.session_state.faq_data is None:
        st.error("Não foi possível carregar a base de conhecimento. Verifique o arquivo FAQ.")
        return
    
    user_question = st.text_area(
    "Faça sua pergunta:",
    placeholder="Olá, Pesquisador! Digite sua pergunta sobre a Rosacruz Áurea...",
    height=100
)

    # Botões lado a lado
    col_btn1, col_btn2 = st.columns([2, 1])
    with col_btn1:
        ask_button = st.button("Perguntar à Sofia", type="primary")
    with col_btn2:
        clear_button = st.button("Limpar Chat", type="secondary")        

    # Processar ações dos botões
    if clear_button:
        st.session_state.conversation_history = []
        st.rerun()

    if ask_button and user_question.strip():
        with st.spinner("Sofia está pensando..."):
            # Adicionar pergunta ao histórico
            st.session_state.conversation_history.append(("user", user_question))
            
            # Buscar perguntas similares
            similar_qa = find_similar_questions(
                user_question, 
                st.session_state.faq_data, 
                st.session_state.embeddings_model
            )
            
            # Gerar resposta
            sofia_response = generate_sofia_response(user_question, similar_qa)
            
            # Verificar se a resposta é satisfatória
            unsatisfactory_indicators = [
                "não possuo informações suficientes",
                "não tenho informações",
                "não encontrei",
                "não está disponível"
            ]
            
            is_unsatisfactory = any(indicator in sofia_response.lower() for indicator in unsatisfactory_indicators)
            
            # Adicionar resposta ao histórico
            st.session_state.conversation_history.append(("sofia", sofia_response))
    
    # Exibir conversação
    if st.session_state.conversation_history:
        st.markdown("---")
        
        for i in range(len(st.session_state.conversation_history)-1, -1, -1):
            role, message = st.session_state.conversation_history[i]
            
            if role == "user":
                st.markdown(f'<div class="user-question"><strong>Você perguntou:</strong><br>{message}</div>', unsafe_allow_html=True)
            else:  # sofia
                st.markdown(f'<div class="sofia-response"><strong>☀️ Sofia responde:</strong><br>{message}</div>', unsafe_allow_html=True)
                
                # Verificar se precisa de formulário de contato
                last_response = st.session_state.conversation_history[-1][1] if st.session_state.conversation_history else ""
                unsatisfactory_indicators = [
                    "não possuo informações suficientes",
                    "não tenho informações",
                    "não encontrei",
                    "não está disponível"
                ]
                
                if any(indicator in last_response.lower() for indicator in unsatisfactory_indicators):
                    st.markdown('<div class="contact-form">', unsafe_allow_html=True)
                    st.markdown("**📧 Não encontrei uma resposta completa para sua pergunta.**")
                    st.markdown("Se desejar, deixe seu e-mail que nosso administrador entrará em contato:")
                    
                    with st.form("contact_form"):
                        user_email = st.text_input("Seu e-mail:", placeholder="seu@email.com")
                        submit_contact = st.form_submit_button("Solicitar Contato")
                        
                        if submit_contact and user_email:
                            if re.match(r'^[^@]+@[^@]+\.[^@]+$', user_email):
                                if send_contact_to_admin(user_email, st.session_state.conversation_history[-2][1]):
                                    st.success("✅ Sua solicitação foi enviada! Nosso administrador entrará em contato em breve.")
                                else:
                                    st.warning("⚠️ Não foi possível enviar sua solicitação no momento. Tente novamente mais tarde.")
                            else:
                                st.error("❌ Por favor, insira um e-mail válido.")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Sugerir links relacionados
                if i == len(st.session_state.conversation_history)-1:  # Apenas para a última resposta
                    last_question = st.session_state.conversation_history[-2][1] if len(st.session_state.conversation_history) >= 2 else ""
                    if last_question:
                        related_links = suggest_related_links(last_question)
                        
                        if related_links:
                            st.markdown('<div class="links-section">', unsafe_allow_html=True)
                            st.markdown("**🔗 Material complementar relacionado ao seu tema:**")
                            
                            for name, url in related_links:
                                st.markdown(f"• [{name}]({url})")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
            
            if i < len(st.session_state.conversation_history) - 1:
                st.markdown("---")
    
    # Sidebar com informações
    with st.sidebar:
        st.markdown("### ☀️ Sofia")
        st.markdown("Assistente Virtual da Escola Internacional da Rosacruz Áurea")
        
        st.markdown("### 📚 Recursos Disponíveis")
        for name, url in REPOSITORIOS.items():
            st.markdown(f"• [{name}]({url})")
        

if __name__ == "__main__":
    main()