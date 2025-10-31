import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from datetime import datetime
import pandas as pd
import json 
from typing import Dict, Any

# --- MÉTODOS AUXILIARES E DADOS INICIAIS ---

THEME_MAP = {
    "digital": "Transformação Digital & Indústria",
    "ecologica": "Transição Ecológica",
    "lideranca": "Liderança & Inovação"
}

INITIAL_SPEAKERS_DATA = [
    {"name": "Andrew Ng", "theme": "digital", "bio": "Cofundador do Coursera e da Google Brain, Andrew Ng é uma autoridade global em IA. Ele defende a 'IA para Todos', focando em como a inteligência artificial pode ser aplicada de forma prática para transformar indústrias, otimizar a manufatura e criar novos modelos de negócios, tornando a tecnologia acessível e útil.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Andrew+Ng"},
    {"name": "Zia Yusuf", "theme": "digital", "bio": "Como CEO da Boston Dynamics, Zia Yusuf está na vanguarda da robótica avançada. Suas palestras demonstram o impacto real de robôs móveis e ágeis na logística, manufatura e inspeção industrial. Ele oferece uma visão prática e inspiradora de como a automação está redefinindo a eficiência e a segurança no chão de fábrica.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Zia+Yusuf"},
    {"name": "Peter Diamandis", "theme": "digital", "bio": "Fundador da XPRIZE e da Singularity University, Diamandis é um evangelista das tecnologias exponenciais (IA, robótica, 3D printing). Ele conecta o otimismo futurista com a inovação empresarial, inspirando líderes a adotar uma 'mentalidade de abundância' e usar a tecnologia para resolver grandes desafios industriais e globais.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Peter+Diamandis"},
    {"name": "Kate Darling", "theme": "digital", "bio": "Especialista do MIT Media Lab em interação humano-robô e ética da tecnologia. Darling traz uma perspectiva crucial sobre como os trabalhadores irão interagir e colaborar com máquinas inteligentes. Ela explora as implicações sociais e éticas da automação na indústria, focando no futuro da colaboração entre humanos e robôs.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Kate+Darling"},
    {"name": "Gerd Leonhard", "theme": "digital", "bio": "Futurista e humanista, Leonhard foca na relação entre humanidade e tecnologia. Ele questiona como a digitalização e a automação impactarão o trabalho e a sociedade, defendendo que 'humanidade será o ativo mais valioso'. É ideal para discutir o aspecto humano da Indústria 4.0 e a necessidade de habilidades 'humanas' no futuro.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Gerd+Leonhard"},
    {"name": "Michio Kaku", "theme": "digital", "bio": "Físico teórico e futurista de renome mundial. Kaku tem a capacidade de explicar conceitos complexos (como IA, computação quântica e nanotecnologia) de forma acessível. Ele pode pintar um quadro vívido do 'futuro da indústria', conectando a ciência de ponta com as transformações tecnológicas que definirão as próximas décadas.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Michio+Kaku"},
    {"name": "Nina Schick", "theme": "digital", "bio": "Especialista em Inteligência Artificial Generativa (GenAI). Schick foca em como a GenAI está transformando a criação de conteúdo, design e informação. Para a indústria, sua perspectiva é vital para entender como a GenAI pode acelerar o design de produtos, criar simulações (digital twins) e revolucionar o marketing e a personalização.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Nina+Schick"},
    {"name": "Pascal Gauthier", "theme": "digital", "bio": "CEO da Ledger, Gauthier é uma voz líder em segurança de ativos digitais e Web3. Sua perspectiva é relevante para a indústria de transformação ao discutir a 'tokenização' de ativos, rastreabilidade da cadeia de suprimentos (supply chain) via blockchain e a segurança necessária para a infraestrutura de IoT e Indústria 4.0.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Pascal+Gauthier"},
    {"name": "Ellen MacArthur", "theme": "ecologica", "bio": "Após sua carreira recorde na vela, fundou a Ellen MacArthur Foundation, tornando-se a principal defensora global da Economia Circular. Ela articula de forma poderosa como as indústrias podem redesenhar sistemas para eliminar o desperdício, circular materiais e regenerar a natureza, provando que é um modelo econômico viável.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Ellen+MacArthur"},
    {"name": "Kate Raworth", "theme": "ecologica", "bio": "Economista de Oxford, criadora da 'Economia Donut'. Raworth propõe um modelo visual e poderoso para o desenvolvimento sustentável, equilibrando as necessidades humanas essenciais (o 'piso social') com os limites do planeta (o 'teto ecológico'). É uma palestra que redefine o que significa 'sucesso' para uma empresa no século 21.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Kate+Raworth"},
    {"name": "Paul Hawken", "theme": "ecologica", "bio": "Ambientalista e autor, líder do 'Project Drawdown', que mapeou as 100 soluções mais substantivas para reverter o aquecimento global. Hawken foca em soluções práticas e existentes, da eficiência energética à agricultura regenerativa. Ele muda a narrativa do 'medo' para a 'oportunidade' na ação climática industrial.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Paul+Hawken"},
    {"name": "Christiana Figueres", "theme": "ecologica", "bio": "Ex-Secretária Executiva da Convenção-Quadro da ONU sobre Mudança Climática, foi a arquiteta-chefe do Acordo de Paris. Figueres fala com autoridade e otimismo sobre a necessidade de colaboração global e a responsabilidade do setor privado na descarbonização. Ela é uma voz poderosa sobre política climática e investimento verde.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Christiana+Figueres"},
    {"name": "Gunter Pauli", "theme": "ecologica", "bio": "Autor de 'A Economia Azul', Pauli promove modelos de negócios que usam a inspiração da natureza (biomimética) para criar valor a partir de resíduos. Ele apresenta casos de estudo fascinantes de como os 'resíduos' de um processo industrial podem se tornar a 'matéria-prima' de outro, criando novos fluxos de receita e eliminando a poluição.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Gunter+Pauli"},
    {"name": "Amory Lovins", "theme": "ecologica", "bio": "Cofundador do Rocky Mountain Institute, Lovins é um dos maiores especialistas do mundo em eficiência energética e design sustentável. Ele argumenta que a eficiência radical não é apenas lucrativa, mas essencial para a competitividade industrial. Suas palestras são repletas de dados e exemplos de 'design integrativo' que economiza energia e dinheiro.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Amory+Lovins"},
    {"name": "Johan Rockström", "theme": "ecologica", "bio": "Cientista climático, co-criador do framework 'Fronteiras Planetárias' (Planetary Boundaries). Rockström fornece a base científica que define o 'espaço operacional seguro' para a humanidade e, por extensão, para a indústria. Ele é fundamental para empresas que buscam alinhar suas estratégias de sustentabilidade com a ciência climática real.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Johan+Rockström"},
    {"name": "Vandana Shiva", "theme": "ecologica", "bio": "Ativista ambiental e acadêmica indiana. Shiva oferece uma perspectiva crítica sobre globalização, patentes e o impacto da indústria na biodiversidade e na soberania alimentar. Ela é uma voz poderosa que desafia o 'business as usual' e defende a responsabilidade corporativa radical, a biodiversidade e as economias locais.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Vandana+Shiva"},
    {"name": "Simon Sinek", "theme": "lideranca", "bio": "Autor de 'Comece pelo Porquê' (Start With Why), Sinek é uma referência em liderança e cultura organizacional. Ele argumenta que o propósito é o motor da inovação e do engajamento. Sua palestra é essencial para líderes que buscam inspirar suas equipes durante períodos de transformação digital ou ecológica, alinhando todos a uma missão clara.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Simon+Sinek"},
    {"name": "Brené Brown", "theme": "lideranca", "bio": "Pesquisadora sobre vulnerabilidade, coragem, vergonha e empatia. Brené Brown transformou a conversa sobre liderança. Ela defende que a coragem de ser vulnerável é essencial para a inovação e para criar equipes resilientes. É uma palestra fundamental sobre a 'humanidade' necessária para liderar em tempos de incerteza e automação.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Brené+Brown"},
    {"name": "Adam Grant", "theme": "lideranca", "bio": "Psicólogo organizacional e autor de 'Originais'. Grant explora como fomentar a criatividade, como discordar de forma produtiva e como construir uma cultura de 'doadores' (givers). Ele oferece insights baseados em dados sobre como as empresas podem repensar o trabalho, o burnout e a inovação para prosperar em meio à disrupção.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Adam+Grant"},
    {"name": "Yuval Noah Harari", "theme": "lideranca", "bio": "Historiador e autor de 'Sapiens'. Harari oferece uma visão macroscópica da humanidade e dos desafios futuros, especialmente da inteligência artificial e da biotecnologia. Ele força a audiência a pensar sobre as grandes questões éticas e filosóficas da transformação tecnológica, um contraponto essencial às discussões técnicas.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Yuval+Noah+Harari"},
    {"name": "Satya Nadella", "theme": "lideranca", "bio": "CEO da Microsoft. Nadella liderou uma das maiores reviravoltas corporativas da história, focando em 'empatia' e 'growth mindset' (mentalidade de crescimento). Ele fala sobre como transformar uma cultura de 'sabe-tudo' para 'aprende-tudo', essencial para qualquer indústria que precise se adaptar à nuvem, IA e novas formas de trabalho.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Satya+Nadella"},
    {"name": "Angela Duckworth", "theme": "lideranca", "bio": "Psicóloga e autora de 'Grit' (Garra). Duckworth explora o poder da paixão e da perseverança para o sucesso a longo prazo. Em um mundo de rápidas mudanças tecnológicas, ela argumenta que a 'garra' é um diferencial competitivo. Sua palestra é inspiradora para desenvolver a resiliência necessária para enfrentar longos ciclos de inovação.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Angela+Duckworth"},
    {"name": "Malala Yousafzai", "theme": "lideranca", "bio": "Ativista e laureada com o Nobel da Paz. Malala é um símbolo global de coragem, propósito e resiliência. Sua história pessoal de lutar pela educação contra todas as adversidades é profundamente inspiradora. Ela traz uma perspectiva poderosa sobre propósito, o poder da voz individual e a importância de defender valores fundamentais.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Malala+Yousafzai"},
    {"name": "Whitney Johnson", "theme": "lideranca", "bio": "Especialista em inovação e disrupção pessoal, autora de 'Disrupt Yourself'. Johnson aplica os princípios da inovação disruptiva de Clayton Christensen aos indivíduos e equipes. Ela fornece um framework para que líderes e colaboradores abracem a mudança, aprendam novas habilidades e impulsionem a inovação de dentro para fora.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Whitney+Johnson"},
]

# --- SESSÃO E VARIÁVEIS DE ESTADO ---

if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'db' not in st.session_state:
    st.session_state.db = None
if 'my_rankings' not in st.session_state:
    st.session_state.my_rankings = {}

# --- FIREBASE ADMIN SDK E CONEXÃO ---

def initialize_firebase():
    """Inicializa o Firebase Admin SDK usando Streamlit Secrets de forma segura."""
    if not firebase_admin._apps:
        try:
            # 1. Copia o dicionário de segredos para torná-lo MUTÁVEL
            cred_dict = dict(st.secrets["firestore"])
            
            # 2. Limpeza ROBUSTA da private_key
            if isinstance(cred_dict.get('private_key'), str):
                private_key = cred_dict['private_key']
                
                # Limpa aspas extras e variações de quebra de linha (correção essencial)
                private_key = private_key.strip().strip('"').strip("'")
                private_key = private_key.replace('\\n', '\n')
                private_key = private_key.replace('\\\\n', '\n') 
                
                # Garante que começa e termina corretamente (ajuste de MalformedFraming)
                if not private_key.startswith('-----BEGIN'):
                    st.error("Chave privada não começa com '-----BEGIN PRIVATE KEY-----'")
                    st.stop()
                
                # Atualiza o dicionário mutável
                cred_dict['private_key'] = private_key
            
            # 3. Passa o dicionário limpo para o Firebase Admin SDK
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            st.session_state.db = firestore.client()
            st.success("✅ Firebase inicializado com sucesso!")
            
        except KeyError:
            st.error(
                "Erro: A chave 'firestore' não foi encontrada. "
                "Verifique se o seu `.streamlit/secrets.toml` está configurado com a seção [firestore]."
            )
            st.stop()
        except Exception as e:
            st.error(f"Erro ao inicializar o Firebase: {e}")
            st.error(f"Tipo do erro: {type(e).__name__}")
            st.stop()
    else:
        st.session_state.db = firestore.client()
    
    return st.session_state.db

# --- LÓGICA DE DADOS (CRIAÇÃO E RECUPERAÇÃO) ---

@st.cache_data(ttl=3600, show_spinner="Verificando dados iniciais...")
def initialize_speakers_once(_db):
    """Cria os speakers iniciais se a coleção estiver vazia."""
    col_ref = _db.collection("all_votable_speakers")
    
    # Tenta obter um único documento para verificar se a coleção está vazia
    if not list(col_ref.limit(1).stream()):
        print("Inicializando lista de palestrantes...")
        for speaker in INITIAL_SPEAKERS_DATA:
            col_ref.add(speaker)
        
        # Invalida o cache para que a próxima chamada carregue os dados
        list_speakers.clear()
        return True
    return False

@st.cache_data(ttl=5, show_spinner="Atualizando lista de palestrantes...")
def list_speakers(_db):
    """Retorna todos os palestrantes votáveis (iniciais + sugeridos) com cache de 5s."""
    speakers = {}
    col_ref = _db.collection("all_votable_speakers")
    for doc in col_ref.stream():
        speaker_data = doc.to_dict()
        speakers[doc.id] = {
            "id": doc.id,
            "name": speaker_data.get("name", "Nome Desconhecido"),
            "theme": speaker_data.get("theme", "lideranca"),
            "bio": speaker_data.get("bio", "Sugestão da comunidade."),
            "image": speaker_data.get("image", "https://placehold.co/400x400/E2E8F0/4A5568?text=Sugestão")
        }
    return speakers

def save_ranking(_db, user_id: str, speaker_id: str, rank: int):
    """Salva a classificação de um usuário para um palestrante."""
    doc_ref = _db.collection("keynote_rankings").document(user_id)
    try:
        # Usa um dicionário para atualizar apenas o ranking do speaker específico
        doc_ref.set(
            {
                speaker_id: int(rank),
                "timestamp": firestore.SERVER_TIMESTAMP
            }, 
            merge=True
        )
        # Atualiza o estado local
        st.session_state.my_rankings[speaker_id] = int(rank)
        # Força o recálculo dos resultados na próxima execução
        calculate_aggregated_results.clear() 
    except Exception as e:
        st.error(f"Erro ao salvar ranking: {e}")

@st.cache_data(ttl=5, show_spinner="Calculando resultados agregados...")
def calculate_aggregated_results(_db):
    """Agrega os rankings de todos os usuários."""
    col_ref = _db.collection("keynote_rankings")
    all_rankings = {}
    total_voters = 0
    
    for doc in col_ref.stream():
        user_rankings = doc.to_dict()
        total_voters += 1
        
        for speaker_id, rank in user_rankings.items():
            if isinstance(rank, int) and 1 <= rank <= 10:
                if speaker_id not in all_rankings:
                    all_rankings[speaker_id] = {"sum": 0, "count": 0}
                
                all_rankings[speaker_id]["sum"] += rank
                all_rankings[speaker_id]["count"] += 1
                
    return all_rankings, total_voters

def load_user_rankings_from_db(_db, user_id):
    """Carrega os rankings do usuário atual para o estado da sessão."""
    if st.session_state.my_rankings and st.session_state.my_rankings.get('loaded', False):
        return
        
    doc_ref = _db.collection("keynote_rankings").document(user_id)
    try:
        doc = doc_ref.get()
        if doc.exists:
            st.session_state.my_rankings = doc.to_dict()
            st.session_state.my_rankings['loaded'] = True
        else:
            st.session_state.my_rankings = {'loaded': True}
    except Exception as e:
        # Erro de leitura, mas não fatal para a aplicação
        print(f"Erro ao carregar rankings do usuário: {e}")
        st.session_state.my_rankings = {'loaded': True}

# --- COMPONENTES DE UI ---

def render_speaker_card(_db, speaker_id, speaker):
    """Renderiza o cartão de palestrante com o slider de classificação."""
    current_rank = st.session_state.my_rankings.get(speaker_id, 1)

    with st.container(border=True):
        st.markdown(f"**{speaker['name']}**")
        st.markdown(f"**Tema:** *{THEME_MAP.get(speaker['theme'], 'Outros')}*")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(speaker.get("image"), use_column_width="always", caption=speaker['name'])
        
        with col2:
            st.caption("Resumo (Max 5 linhas)")
            st.markdown(f"*{speaker['bio']}*")
            
            st.markdown("---")
            
            # Slider de Classificação
            rank = st.slider(
                "Classificar (1 - 10):",
                min_value=1,
                max_value=10,
                value=current_rank,
                key=f"slider_{speaker_id}",
                label_visibility="visible",
                on_change=lambda s_id=speaker_id: save_ranking(
                    _db, 
                    st.session_state.user_id, 
                    s_id, 
                    st.session_state[f"slider_{s_id}"]
                )
            )

def render_suggestion_form(_db):
    """Renderiza o formulário de sugestão de novo speaker."""
    st.header("Sugira um Novo Keynote")
    st.info("Não encontrou o nome que procurava? Sugira um novo palestrante. Ele será adicionado à lista votável instantaneamente!")

    with st.form("suggestion_form", clear_on_submit=True):
        sug_name = st.text_input("Nome Completo do Palestrante", max_chars=100)
        sug_theme = st.selectbox(
            "Tema Sugerido",
            options=["Transformação Digital", "Transição Ecológica", "Liderança e Inovação", "Outros"]
        )
        sug_bio = st.text_area("Por que devemos contratá-lo? (Breve resumo para o slide)", max_chars=350)
        
        submitted = st.form_submit_button("Adicionar Sugestão e Tornar Votável")

        if submitted and sug_name:
            # Converte o tema para o ID de tema que usamos no Firestore
            theme_key = next((k for k, v in THEME_MAP.items() if v == sug_theme), "lideranca")
            
            new_speaker = {
                "name": sug_name,
                "theme": theme_key,
                "bio": sug_bio,
                "image": f"https://placehold.co/400x400/E2E8F0/4A5568?text={sug_name.replace(' ', '+')}",
                "suggestedBy": st.session_state.user_id,
                "timestamp": firestore.SERVER_TIMESTAMP
            }
            
            try:
                _db.collection("all_votable_speakers").add(new_speaker)
                st.success(f"Palestrante '{sug_name}' sugerido e adicionado à lista votável!")
                
                # CORREÇÃO DO BUG: Limpa o cache e força o re-run para exibir o novo speaker imediatamente
                list_speakers.clear() 
                st.rerun() # Força a re-execução do script
            except Exception as e:
                st.error(f"Erro ao salvar sugestão: {e}")
        elif submitted:
            st.warning("O nome do palestrante é obrigatório.")

def render_results(_db, speakers):
    """Renderiza a tabela de resultados agregados."""
    aggregated_results, total_voters = calculate_aggregated_results(_db)
    
    st.header("Resultados Agregados (Classificação Média)")
    st.info(f"Total de Avaliadores Únicos: **{total_voters}**")

    data = []
    
    for speaker_id, speaker in speakers.items():
        results = aggregated_results.get(speaker_id)
        if results:
            avg_rank = results['sum'] / results['count']
            vote_count = results['count']
        else:
            avg_rank = 0.0
            vote_count = 0
            
        data.append({
            "Palestrante": speaker['name'],
            "Tema": THEME_MAP.get(speaker['theme'], 'Outros'),
            "Média (1-10)": f"{avg_rank:.2f}",
            "Votos": vote_count,
            "sortable_rank": avg_rank # Coluna para ordenação
        })
        
    df = pd.DataFrame(data).sort_values(by="sortable_rank", ascending=False).drop(columns=['sortable_rank'])
    
    # Renderiza a tabela do Pandas
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Média (1-10)": st.column_config.ProgressColumn(
                "Média (1-10)",
                help="Classificação Média de 10",
                format="%.2f",
                min_value=1,
                max_value=10,
                width="small"
            )
        }
    )

# --- FUNÇÃO PRINCIPAL ---

def main():
    """Função principal da aplicação Streamlit."""
    st.set_page_config(
        page_title="Ranking de Keynotes", 
        layout="wide", 
        initial_sidebar_state="collapsed"
    )

    # 1. Tenta inicializar o Firebase
    db = initialize_firebase()
    if not db:
        st.stop()
        
    # 2. Garante que os speakers iniciais existam
    # O uso de uma função cache_data de 1 hora evita que essa checagem seja feita a cada 5s
    initialize_speakers_once(db)
    
    # 3. Carrega a lista de speakers (cache de 5s para tempo real)
    speakers = list_speakers(db)
    
    # 4. Carrega os rankings do usuário atual (sem cache)
    load_user_rankings_from_db(db, st.session_state.user_id)

    # --- UI/UX ---
    
    st.title("Plataforma Colaborativa de Ranking de Keynotes")
    st.caption(f"Seu ID de Avaliador: **{st.session_state.user_id}**. Use este ID para rastrear seus votos.")
    
    # Cria as abas de navegação
    themes = list(THEME_MAP.values())
    themes.append("Resultados")
    themes.append("Sugestão")
    
    tabs = st.tabs(themes)
    
    # Renderiza a aba "Transformação Digital"
    with tabs[0]:
        st.subheader(THEME_MAP["digital"])
        st.markdown("Especialistas que conectam IA, robótica e futurismo com a **Indústria de Transformação**.")
        col_speakers = [s for s in speakers.values() if s['theme'] == 'digital']
        
        for speaker in col_speakers:
            render_speaker_card(db, speaker['id'], speaker)

    # Renderiza a aba "Transição Ecológica"
    with tabs[1]:
        st.subheader(THEME_MAP["ecologica"])
        st.markdown("Líderes focados em **Economia Circular**, **Sustentabilidade** e frameworks como a **Economia Donut**.")
        col_speakers = [s for s in speakers.values() if s['theme'] == 'ecologica']
        
        for speaker in col_speakers:
            render_speaker_card(db, speaker['id'], speaker)

    # Renderiza a aba "Liderança & Inovação"
    with tabs[2]:
        st.subheader(THEME_MAP["lideranca"])
        st.markdown("Palestrantes inspiradores sobre **cultura organizacional**, **resiliência** e o **aspecto humano** da transformação.")
        col_speakers = [s for s in speakers.values() if s['theme'] == 'lideranca']
        
        for speaker in col_speakers:
            render_speaker_card(db, speaker['id'], speaker)

    # Renderiza a aba "Resultados"
    with tabs[3]:
        render_results(db, speakers)
        
    # Renderiza a aba "Sugestão"
    with tabs[4]:
        render_suggestion_form(db)


if __name__ == "__main__":
    main()
