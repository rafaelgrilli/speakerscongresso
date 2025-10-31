import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from datetime import datetime
import pandas as pd
from typing import Dict, Any
import json # Adicionado para processar o segredo do Firebase

# --- DADOS INICIAIS (Estrutura de dados para o Firestore) ---
INITIAL_SPEAKERS_DATA = {
    # Transformação Digital & Indústria (IDs minúsculos e hifenizados)
    "andrew-ng": {"name": "Andrew Ng", "theme": "digital", "bio": "Cofundador do Coursera e da Google Brain, Andrew Ng é uma autoridade global em IA. Ele defende a 'IA para Todos', focando em como a inteligência artificial pode ser aplicada de forma prática para transformar indústrias, otimizar a manufatura e criar novos modelos de negócios, tornando a tecnologia acessível e útil.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Andrew+Ng"},
    "zia-yusuf": {"name": "Zia Yusuf", "theme": "digital", "bio": "Como CEO da Boston Dynamics, Zia Yusuf está na vanguarda da robótica avançada. Suas palestras demonstram o impacto real de robôs móveis e ágeis na logística, manufatura e inspeção industrial. Ele oferece uma visão prática e inspiradora de como a automação está redefinindo a eficiência e a segurança no chão de fábrica.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Zia+Yusuf"},
    "peter-diamandis": {"name": "Peter Diamandis", "theme": "digital", "bio": "Fundador da XPRIZE e da Singularity University, Diamandis é um evangelista das tecnologias exponenciais (IA, robótica, 3D printing). Ele conecta o otimismo futurista com a inovação empresarial, inspirando líderes a adotar uma 'mentalidade de abundância' e usar a tecnologia para resolver grandes desafios industriais e globais.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Peter+Diamandis"},
    "kate-darling": {"name": "Kate Darling", "theme": "digital", "bio": "Especialista do MIT Media Lab em interação humano-robô e ética da tecnologia. Darling traz uma perspectiva crucial sobre como os trabalhadores irão interagir e colaborar com máquinas inteligentes. Ela explora as implicações sociais e éticas da automação na indústria, focando no futuro da colaboração entre humanos e robôs.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Kate+Darling"},
    "gerd-leonhard": {"name": "Gerd Leonhard", "theme": "digital", "bio": "Futurista e humanista, Leonhard foca na relação entre humanidade e tecnologia. Ele questiona como a digitalização e a automação impactarão o trabalho e a sociedade, defendendo que 'humanidade será o ativo mais valioso'. É ideal para discutir o aspecto humano da Indústria 4.0 e a necessidade de habilidades 'humanas' no futuro.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Gerd+Leonhard"},
    "michio-kaku": {"name": "Michio Kaku", "theme": "digital", "bio": "Físico teórico e futurista de renome mundial. Kaku tem a capacidade de explicar conceitos complexos (como IA, computação quântica e nanotecnologia) de forma acessível. Ele pode pintar um quadro vívido do 'futuro da indústria', conectando a ciência de ponta com as transformações tecnológicas que definirão as próximas décadas.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Michio+Kaku"},
    "nina-schick": {"name": "Nina Schick", "theme": "digital", "bio": "Especialista em Inteligência Artificial Generativa (GenAI). Schick foca em como a GenAI está transformando a criação de conteúdo, design e informação. Para a indústria, sua perspectiva é vital para entender como a GenAI pode acelerar o design de produtos, criar simulações (digital twins) e revolucionar o marketing e a personalização.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Nina+Schick"},
    "pascal-gauthier": {"name": "Pascal Gauthier", "theme": "digital", "bio": "CEO da Ledger, Gauthier é uma voz líder em segurança de ativos digitais e Web3. Sua perspectiva é relevante para a indústria de transformação ao discutir a 'tokenização' de ativos, rastreabilidade da cadeia de suprimentos (supply chain) via blockchain e a segurança necessária para a infraestrutura de IoT e Indústria 4.0.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Pascal+Gauthier"},
    
    # Transição Ecológica
    "ellen-macarthur": {"name": "Ellen MacArthur", "theme": "ecologica", "bio": "Após sua carreira recorde na vela, fundou a Ellen MacArthur Foundation, tornando-se a principal defensora global da Economia Circular. Ela articula de forma poderosa como as indústrias podem redesenhar sistemas para eliminar o desperdício, circular materiais e regenerar a natureza, provando que é um modelo econômico viável.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Ellen+MacArthur"},
    "kate-raworth": {"name": "Kate Raworth", "theme": "ecologica", "bio": "Economista de Oxford, criadora da 'Economia Donut'. Raworth propõe um modelo visual e poderoso para o desenvolvimento sustentável, equilibrando as necessidades humanas essenciais (o 'piso social') com os limites do planeta (o 'teto ecológico'). É uma palestra que redefine o que significa 'sucesso' para uma empresa no século 21.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Kate+Raworth"},
    "paul-hawken": {"name": "Paul Hawken", "theme": "ecologica", "bio": "Ambientalista e autor, líder do 'Project Drawdown', que mapeou as 100 soluções mais substantivas para reverter o aquecimento global. Hawken foca em soluções práticas e existentes, da eficiência energética à agricultura regenerativa. Ele muda a narrativa do 'medo' para a 'oportunidade' na ação climática industrial.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Paul+Hawken"},
    "christiana-figueres": {"name": "Christiana Figueres", "theme": "ecologica", "bio": "Ex-Secretária Executiva da Convenção-Quadro da ONU sobre Mudança Climática, foi a arquiteta-chefe do Acordo de Paris. Figueres fala com autoridade e otimismo sobre a necessidade de colaboração global e a responsabilidade do setor privado na descarbonização. Ela é uma voz poderosa sobre política climática e investimento verde.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Christiana+Figueres"},
    "gunter-pauli": {"name": "Gunter Pauli", "theme": "ecologica", "bio": "Autor de 'A Economia Azul', Pauli promove modelos de negócios que usam a inspiração da natureza (biomimética) para criar valor a partir de resíduos. Ele apresenta casos de estudo fascinantes de como os 'resíduos' de um processo industrial podem se tornar a 'matéria-prima' de outro, criando novos fluxos de receita e eliminando a poluição.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Gunter+Pauli"},
    "amory-lovins": {"name": "Amory Lovins", "theme": "ecologica", "bio": "Cofundador do Rocky Mountain Institute, Lovins é um dos maiores especialistas do mundo em eficiência energética e design sustentável. Ele argumenta que a eficiência radical não é apenas lucrativa, mas essencial para a competitividade industrial. Suas palestras são repletas de dados e exemplos de 'design integrativo' que economiza energia e dinheiro.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Amory+Lovins"},
    "johan-rockstrom": {"name": "Johan Rockström", "theme": "ecologica", "bio": "Cientista climático, co-criador do framework 'Fronteiras Planetárias' (Planetary Boundaries). Rockström fornece a base científica que define o 'espaço operacional seguro' para a humanidade e, por extensão, para a indústria. Ele é fundamental para empresas que buscam alinhar suas estratégias de sustentabilidade com a ciência climática real.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Johan+Rockström"},
    "vandana-shiva": {"name": "Vandana Shiva", "theme": "ecologica", "bio": "Ativista ambiental e acadêmica indiana. Shiva oferece uma perspectiva crítica sobre globalização, patentes e o impacto da indústria na biodiversidade e na soberania alimentar. Ela é uma voz poderosa que desafia o 'business as usual' e defende a responsabilidade corporativa radical, a biodiversidade e as economias locais.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Vandana+Shiva"},
    
    # Liderança & Inovação
    "simon-sinek": {"name": "Simon Sinek", "theme": "lideranca", "bio": "Autor de 'Comece pelo Porquê' (Start With Why), Sinek é uma referência em liderança e cultura organizacional. Ele argumenta que o propósito é o motor da inovação e do engajamento. Sua palestra é essencial para líderes que buscam inspirar suas equipes durante períodos de transformação digital ou ecológica, alinhando todos a uma missão clara.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Simon+Sinek"},
    "brene-brown": {"name": "Brené Brown", "theme": "lideranca", "bio": "Pesquisadora sobre vulnerabilidade, coragem, vergonha e empatia. Brené Brown transformou a conversa sobre liderança. Ela defende que a coragem de ser vulnerável é essencial para a inovação e para criar equipes resilientes. É uma palestra fundamental sobre a 'humanidade' necessária para liderar em tempos de incerteza e automação.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Brené+Brown"},
    "adam-grant": {"name": "Adam Grant", "theme": "lideranca", "bio": "Psicólogo organizacional e autor de 'Originais'. Grant explora como fomentar a criatividade, como discordar de forma produtiva e como construir uma cultura de 'doadores' (givers). Ele oferece insights baseados em dados sobre como as empresas podem repensar o trabalho, o burnout e a inovação para prosperar em meio à disrupção.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Adam+Grant"},
    "yuval-noah-harari": {"name": "Yuval Noah Harari", "theme": "lideranca", "bio": "Historiador e autor de 'Sapiens'. Harari oferece uma visão macroscópica da humanidade e dos desafios futuros, especialmente da inteligência artificial e da biotecnologia. Ele força a audiência a pensar sobre as grandes questões éticas e filosóficas da transformação tecnológica, um contraponto essencial às discussões técnicas.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Yuval+Noah+Harari"},
    "satya-nadella": {"name": "Satya Nadella", "theme": "lideranca", "bio": "CEO da Microsoft. Nadella liderou uma das maiores reviravoltas corporativas da história, focando em 'empatia' e 'growth mindset' (mentalidade de crescimento). Ele fala sobre como transformar uma cultura de 'sabe-tudo' para 'aprende-tudo', essencial para qualquer indústria que precise se adaptar à nuvem, IA e novas formas de trabalho.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Satya+Nadella"},
    "angela-duckworth": {"name": "Angela Duckworth", "theme": "lideranca", "bio": "Psicóloga e autora de 'Grit' (Garra). Duckworth explora o poder da paixão e da perseverança para o sucesso a longo prazo. Em um mundo de rápidas mudanças tecnológicas, ela argumenta que a 'garra' é um diferencial competitivo. Sua palestra é inspiradora para desenvolver a resiliência necessária para enfrentar longos ciclos de inovação.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Angela+Duckworth"},
    "malala-yousafzai": {"name": "Malala Yousafzai", "theme": "lideranca", "bio": "Ativista e laureada com o Nobel da Paz. Malala é um símbolo global de coragem, propósito e resiliência. Sua história pessoal de lutar pela educação contra todas as adversidades é profundamente inspiradora. Ela traz uma perspectiva poderosa sobre propósito, o poder da voz individual e a importância de defender valores fundamentais.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Malala+Yousafzai"},
    "whitney-johnson": {"name": "Whitney Johnson", "theme": "lideranca", "bio": "Especialista em inovação e disrupção pessoal, autora de 'Disrupt Yourself'. Johnson aplica os princípios da inovação disruptiva de Clayton Christensen aos indivíduos e equipes. Ela fornece um framework para que líderes e colaboradores abracem a mudança, aprendam novas habilidades e impulsionem a inovação de dentro para fora.", "image": "https://placehold.co/400x400/E2E8F0/4A5568?text=Whitney+Johnson"},
}

THEME_MAP = {
    "digital": "Transformação Digital & Indústria",
    "ecologica": "Transição Ecológica",
    "lideranca": "Liderança & Inovação"
}
# --- FIM DOS DADOS INICIAIS ---

# --- CONFIGURAÇÃO E CONEXÃO FIREBASE ---

def initialize_firebase():
    """Inicializa o Firebase Admin SDK usando Streamlit Secrets."""
    if not firebase_admin._apps:
        try:
            # Novo método para carregar o dicionário JSON inteiro do Streamlit Secrets
            cred_dict = json.loads(st.secrets["firebase_service_account"])
            
            # O Admin SDK espera um dicionário JSON como argumento
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            st.session_state.db = firestore.client()
        except KeyError:
            st.error(
                "Erro: A chave 'firebase_service_account' não foi encontrada. "
                "Verifique se o seu `.streamlit/secrets.toml` está configurado com a chave única."
            )
            st.stop()
        except Exception as e:
            # Este erro é o que estava ocorrendo, corrigido pela abordagem JSON.loads
            st.error(f"Erro ao inicializar o Firebase: {e}") 
            st.stop()
    else:
        st.session_state.db = firestore.client()
    return st.session_state.db

# --- FUNÇÕES DE INTERAÇÃO COM O BANCO DE DADOS ---

@st.cache_data(ttl=5) # Cacheia por 5 segundos para simular "quase-real-time"
def get_votable_speakers(_db) -> Dict[str, Any]:
    """Obtém a lista mestre de palestrantes do Firestore (ou inicializa se vazia)."""
    # Usando uma coleção simples 'speakers'
    speakers_ref = _db.collection("speakers")
    speakers_docs = speakers_ref.stream()
    speakers = {doc.id: doc.to_dict() for doc in speakers_docs}
    
    if not speakers:
        # Inicializa se a coleção estiver vazia
        # NOTA: O ID do documento é o mesmo ID da chave no dicionário
        for speaker_id, data in INITIAL_SPEAKERS_DATA.items():
            speakers_ref.document(speaker_id).set(data)
        # Recarregar após a inicialização
        speakers_docs = speakers_ref.stream()
        speakers = {doc.id: doc.to_dict() for doc in speakers_docs}
        
    return speakers

def save_ranking(db, user_id, speaker_id, rank):
    """Salva a classificação do usuário em um documento de ranking."""
    # Usando uma coleção simples 'rankings' onde o ID do documento é o user_id
    rank_ref = db.collection("rankings").document(user_id)
    # Garante que o rank é um inteiro
    rank_int = int(rank) 
    rank_ref.set({
        speaker_id: rank_int, 
        "timestamp": datetime.now()
    }, merge=True)
    st.session_state.my_rankings[speaker_id] = rank_int
    st.toast(f"Classificação salva: {speaker_id} = {rank_int}")
    # Limpa o cache dos rankings agregados para forçar o recálculo na próxima execução
    get_all_rankings.clear() 

@st.cache_data(ttl=5)
def get_all_rankings(_db):
    """Agrega as classificações de todos os usuários."""
    rankings_ref = _db.collection("rankings")
    all_rankings_docs = rankings_ref.stream()
    
    aggregation = {}
    voter_count = 0
    
    # Processa os rankings de cada usuário
    for doc in all_rankings_docs:
        user_rankings = doc.to_dict()
        user_voted = False
        for speaker_id, rank in user_rankings.items():
            # Filtra apenas classificações válidas (1-10) e garante que é um número
            if isinstance(rank, int) and 1 <= rank <= 10:
                if speaker_id not in aggregation:
                    aggregation[speaker_id] = {"sum": 0, "count": 0}
                aggregation[speaker_id]["sum"] += rank
                aggregation[speaker_id]["count"] += 1
                user_voted = True
        if user_voted:
            voter_count += 1
            
    return aggregation, voter_count

def add_speaker_suggestion(db, user_id, name, theme, bio):
    """Adiciona um novo palestrante à lista mestre."""
    # Cria um ID de documento amigável
    speaker_id = name.lower().strip().replace(" ", "-").replace("ç", "c").replace("ã", "a").replace(".", "").replace(",", "")
    
    # Normaliza o tema
    theme_key = theme.lower().strip()
    if "digital" in theme_key:
        final_theme = "digital"
    elif "ecologica" in theme_key or "sustentabilidade" in theme_key:
        final_theme = "ecologica"
    else:
        final_theme = "lideranca"

    new_speaker_data = {
        "name": name,
        "theme": final_theme,
        "bio": bio if bio else f"Sugestão da comunidade por {user_id}. Tema: {THEME_MAP[final_theme]}.",
        "image": f"https://placehold.co/400x400/E2E8F0/4A5568?text={name.replace(' ', '+')}",
        "suggested_by": user_id,
        "timestamp": datetime.now()
    }
    
    # Salva na coleção "speakers"
    db.collection("speakers").document(speaker_id).set(new_speaker_data)
    
    # Limpa o cache para que todos os usuários vejam o novo palestrante imediatamente
    get_votable_speakers.clear() 
    
    st.toast(f"Sugestão '{name}' adicionada e pronta para votação!")
    # Força a atualização da interface para exibir o novo palestrante
    st.rerun() 

# --- LÓGICA DE INTERFACE E ESTADO ---

def setup_session_state(db):
    """Define o estado inicial da sessão (roda apenas uma vez por usuário)."""
    # O user_id deve ser persistente por sessão
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
        
    # Carrega a lista mestre de palestrantes
    st.session_state.speakers = get_votable_speakers(db)

    # Carrega as classificações do usuário atual
    user_rank_doc = db.collection("rankings").document(st.session_state.user_id).get()
    if user_rank_doc.exists:
        st.session_state.my_rankings = user_rank_doc.to_dict()
    else:
        st.session_state.my_rankings = {}

def render_speaker_card(db, speaker_id, speaker):
    """Renderiza o cartão de palestrante com o slider de classificação."""
    current_rank = st.session_state.my_rankings.get(speaker_id, 1)

    with st.container(border=True):
        st.markdown(f"**{speaker['name']}**")
        st.markdown(f"**Tema:** *{THEME_MAP.get(speaker['theme'], 'Outros')}*")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Correção do f-string: apenas o nome é usado como caption
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
                    db, 
                    st.session_state.user_id, 
                    s_id, 
                    st.session_state[f"slider_{s_id}"]
                )
            )

def render_suggestion_form(db):
    """Renderiza o formulário de sugestão de novo palestrante."""
    st.subheader("Contribuir com Novos Nomes")
    st.info("Sua sugestão será adicionada à lista votável instantaneamente. O ranking será atualizado automaticamente em 5 segundos.")
    
    with st.form("suggestion_form", clear_on_submit=True):
        name = st.text_input("Nome do Palestrante", max_chars=100)
        theme = st.text_input("Tema Principal (Ex: Digital, Ecológica, Liderança)", max_chars=50)
        bio = st.text_area("Por que esta sugestão? (Bio/Relevância)", max_chars=500)
        
        submitted = st.form_submit_button("Enviar Sugestão")
        
        if submitted and name and theme:
            add_speaker_suggestion(db, st.session_state.user_id, name, theme, bio)

def render_results_table(db):
    """Renderiza a tabela de resultados agregados."""
    aggregation, voter_count = get_all_rankings(db)
    
    st.info(f"Número total de avaliadores únicos: **{voter_count}**")

    data = []
    
    # Itera sobre a lista MESTRE de palestrantes
    for speaker_id, speaker_data in st.session_state.speakers.items():
        agg_data = aggregation.get(speaker_id)
        
        if agg_data:
            avg_rank = agg_data["sum"] / agg_data["count"]
            vote_count = agg_data["count"]
            avg_rank_str = f"{avg_rank:.2f}" 
        else:
            avg_rank = 0.0
            vote_count = 0
            avg_rank_str = "N/A"
            
        data.append({
            "Palestrante": speaker_data["name"],
            "Tema": THEME_MAP.get(speaker_data["theme"], "Outros"),
            "Média Rank (1-10)": avg_rank_str,
            "Nº de Votos": vote_count,
            "_sort_key": avg_rank
        })
        
    # Ordenar por Média Rank (maior para o menor)
    df = pd.DataFrame(data).sort_values(by="_sort_key", ascending=False).drop(columns=["_sort_key"])

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Média Rank (1-10)": st.column_config.ProgressColumn(
                "Média Rank (1-10)",
                help="Classificação média de 1 a 10",
                format="%f",
                min_value=1,
                max_value=10,
            ),
        }
    )

# --- APLICAÇÃO PRINCIPAL ---

def main():
    """Função principal da aplicação Streamlit."""
    st.set_page_config(
        layout="wide", 
        page_title="Ranking Keynotes",
        initial_sidebar_state="collapsed"
    )

    db = initialize_firebase()
    setup_session_state(db)
    
    st.title("Plataforma de Ranking de Keynotes")
    st.markdown("Avalie os palestrantes sugeridos para o nosso próximo evento. Os resultados são atualizados em tempo real (cache de 5 segundos).")
    st.caption(f"Seu ID de Avaliador: **{st.session_state.user_id}**")
    st.markdown("---")

    # Mapeamento dos palestrantes por tema
    speakers_by_theme = {key: [] for key in THEME_MAP.keys()}
    for speaker_id, speaker in st.session_state.speakers.items():
        theme = speaker.get("theme", "lideranca") # Default
        if theme in speakers_by_theme:
            speakers_by_theme[theme].append((speaker_id, speaker))

    # Definir as abas
    tab_digital, tab_ecologica, tab_lideranca, tab_resultados = st.tabs([
        THEME_MAP["digital"], 
        THEME_MAP["ecologica"], 
        THEME_MAP["lideranca"], 
        "Resultados (Agregados)"
    ])

    with tab_digital:
        st.header(THEME_MAP["digital"])
        st.markdown("Foco em Futurismo, IA e Robótica aplicados à Indústria de Transformação.")
        cols = st.columns(2) 
        for i, (speaker_id, speaker) in enumerate(speakers_by_theme["digital"]):
            with cols[i % 2]:
                render_speaker_card(db, speaker_id, speaker)

    with tab_ecologica:
        st.header(THEME_MAP["ecologica"])
        st.markdown("Líderes em Sustentabilidade, Economia Circular e frameworks de Transição Ecológica.")
        cols = st.columns(2)
        for i, (speaker_id, speaker) in enumerate(speakers_by_theme["ecologica"]):
            with cols[i % 2]:
                render_speaker_card(db, speaker_id, speaker)

    with tab_lideranca:
        st.header(THEME_MAP["lideranca"])
        st.markdown("Especialistas em Cultura, Propósito, Resiliência e Psicologia da Inovação.")
        cols = st.columns(2)
        for i, (speaker_id, speaker) in enumerate(speakers_by_theme["lideranca"]):
            with cols[i % 2]:
                render_speaker_card(db, speaker_id, speaker)

    with tab_resultados:
        st.header("Resultados Agregados (Em Tempo Real)")
        st.markdown("Média das classificações de todos os avaliadores. **As classificações e novas sugestões são atualizadas automaticamente (cache de 5 segundos).**")
        render_results_table(db)
        st.markdown("---")
        render_suggestion_form(db)


if __name__ == "__main__":
    if 'db' not in st.session_state:
        # A chamada a initialize_firebase define st.session_state.db
        initialize_firebase() 
    main()
