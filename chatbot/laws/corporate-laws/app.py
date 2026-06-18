import os
import streamlit as st
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer, CrossEncoder
from dotenv import load_dotenv
import anthropic
from google import genai
import database
import pandas as pd
import re

# -------------------------------------------------------------------
# Streamlit Page Config
# -------------------------------------------------------------------
st.set_page_config(
    page_title="NexSight Law",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# Custom CSS for Aesthetics
# -------------------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Mukta:wght@300;400;500;600;700;800;900&display=swap');
        
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Global Page Container Adjustments */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 1300px !important;
        }
        
        /* Modern Theme Setup */
        .stApp {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
            font-family: 'Inter', 'Mukta', sans-serif !important;
        }
        
        /* Force dark text and soft theme colors */
        .stApp p, .stApp span, .stApp div, .stApp li, .stApp label {
            color: #0F172A !important;
            font-family: 'Inter', 'Mukta', sans-serif !important;
        }
        
        .main-title {
            font-size: 2.8rem;
            font-weight: 800;
            background: -webkit-linear-gradient(45deg, #0F172A, #1E40AF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 5px;
            font-family: 'Inter', 'Mukta', sans-serif !important;
            letter-spacing: -1px;
        }
        
        /* Sidebar layout styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid rgba(15, 23, 42, 0.06) !important;
        }
        [data-testid="stSidebar"] * {
            color: #0F172A !important;
            font-family: 'Inter', 'Mukta', sans-serif !important;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #1E40AF !important;
            font-family: 'Inter', 'Mukta', sans-serif !important;
            font-weight: 700 !important;
        }
        
        /* General Chat Message styling */
        div[data-testid="stChatMessage"] {
            padding: 22px 26px !important;
            margin-bottom: 16px !important;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.02) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            border-radius: 18px !important;
        }
        
        /* User Chat Message - Indigo Accent, Right Aligned */
        div[data-testid="stChatMessage"][aria-label*="user" i] {
            flex-direction: row-reverse !important;
            background-color: rgba(30, 64, 175, 0.05) !important;
            border: 1px solid rgba(30, 64, 175, 0.1) !important;
            border-bottom-right-radius: 4px !important;
            margin-left: 10% !important;
        }
        
        /* Adjust User Avatar margins when row-reversed */
        div[data-testid="stChatMessage"][aria-label*="user" i] > div[data-testid="stChatMessageAvatar"] {
            margin-left: 12px !important;
            margin-right: 0px !important;
        }
        
        /* Assistant Chat Message - Soft White, Left Aligned */
        div[data-testid="stChatMessage"][aria-label*="assistant" i] {
            background-color: #ffffff !important;
            border: 1px solid rgba(15, 23, 42, 0.06) !important;
            border-bottom-left-radius: 4px !important;
            margin-right: 10% !important;
        }
        
        div[data-testid="stChatMessage"]:hover {
            box-shadow: 0 8px 30px rgba(15, 23, 42, 0.04) !important;
        }
        
        /* Chat Content Typography Re-alignment */
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
            font-size: 0.92rem !important;
            line-height: 1.68 !important;
            color: #0F172A !important;
            margin-bottom: 12px !important;
        }
        
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] ul, 
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] ol {
            padding-left: 22px !important;
            margin-bottom: 14px !important;
        }
        
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
            font-size: 0.92rem !important;
            line-height: 1.68 !important;
            color: #0F172A !important;
            margin-bottom: 8px !important;
        }
        
        /* Chat Content Headings */
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3,
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h4 {
            color: #1E40AF !important;
            font-family: 'Inter', 'Mukta', sans-serif !important;
            font-weight: 700 !important;
            margin-top: 22px !important;
            margin-bottom: 12px !important;
            letter-spacing: -0.3px !important;
        }
        
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 {
            font-size: 1.15rem !important;
            border-bottom: 1px solid rgba(30, 64, 175, 0.08) !important;
            padding-bottom: 6px !important;
        }
        
        /* Custom Blockquote (Key Summary Callout Box) */
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] blockquote {
            border-left: 4px solid #1E40AF !important;
            background-color: rgba(30, 64, 175, 0.03) !important;
            padding: 14px 20px !important;
            border-radius: 4px 14px 14px 4px !important;
            margin: 18px 0 !important;
        }
        
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] blockquote p {
            color: #1E40AF !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            margin-bottom: 0 !important;
        }
        
        /* Inline references code tags */
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] code {
            background-color: rgba(30, 64, 175, 0.04) !important;
            color: #1E40AF !important;
            padding: 3px 7px !important;
            border-radius: 6px !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            border: 1px solid rgba(30, 64, 175, 0.08) !important;
            font-family: 'Inter', 'Mukta', monospace !important;
        }
        
        /* Source Citation Expanders styling */
        div[data-testid="stExpander"] {
            border: 1px solid rgba(15, 23, 42, 0.06) !important;
            border-radius: 14px !important;
            background-color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.01) !important;
            margin-top: 10px !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stExpander"]:hover {
            border-color: rgba(15, 23, 42, 0.12) !important;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.03) !important;
        }
        
        /* General Action Buttons (Accent Blue #1E40AF) */
        div.stButton > button {
            width: 100%;
            border-radius: 10px !important;
            border: 1px solid #1E40AF !important;
            background-color: #1E40AF !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            padding: 12px 14px !important;
            box-shadow: 0 4px 12px rgba(30, 64, 175, 0.1) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            white-space: pre-wrap !important;
            height: auto !important;
            text-align: center !important;
        }
        div.stButton > button:hover {
            transform: scale(1.02) !important;
            background-color: #1D4ED8 !important;
            color: #ffffff !important;
            box-shadow: 0 6px 18px rgba(30, 64, 175, 0.2) !important;
        }
        
        /* Suggested Questions Card-Style overrides */
        div[data-testid="column"]:has(div.stButton) {
            background-color: #ffffff !important;
            border: 1px solid rgba(15, 23, 42, 0.06) !important;
            border-radius: 10px !important;
            padding: 0px !important;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02) !important;
            transition: all 0.25s ease-in-out !important;
        }
        div[data-testid="column"]:has(div.stButton):hover {
            transform: translateY(-4px) !important;
            border-color: #1E40AF !important;
            box-shadow: 0 8px 24px rgba(30, 64, 175, 0.08) !important;
        }
        div[data-testid="column"] div.stButton > button {
            background: transparent !important;
            border: none !important;
            color: #0F172A !important;
            font-weight: 550 !important;
            font-size: 0.88rem !important;
            padding: 20px !important;
            box-shadow: none !important;
            height: 100% !important;
            width: 100% !important;
            text-align: left !important;
            transform: none !important;
        }
        div[data-testid="column"] div.stButton > button:hover {
            background: transparent !important;
            color: #1E40AF !important;
            box-shadow: none !important;
            transform: none !important;
        }
        
        /* Suggested Questions Section Header */
        .sugg-header {
            color: #64748B !important;
            font-size: 0.88rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-top: 24px !important;
            margin-bottom: 12px !important;
        }
        
        /* Chat Input Styling */
        .stChatFloatingInputContainer {
            border-radius: 12px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
            background-color: #ffffff !important;
            padding: 10px !important;
            border: 1px solid #E2E8F0 !important;
        }
        .stChatInput textarea {
            border-radius: 12px !important;
            font-family: 'Inter', 'Mukta', sans-serif !important;
        }
        
        /* Disclaimer Box styling */
        .disclaimer-box {
            border-left: 3px solid #64748B;
            background-color: rgba(100, 116, 139, 0.03);
            padding: 12px 14px;
            border-radius: 0 8px 8px 0;
            margin-top: 15px;
            font-size: 0.82rem;
            line-height: 1.45;
            color: #64748B !important;
        }
        .disclaimer-box p, .disclaimer-box strong {
            color: #64748B !important;
            font-size: 0.82rem;
        }
        
        /* Reference Card Box styling */
        .ref-card-box {
            background-color: #ffffff !important;
            border: 1px solid rgba(15, 23, 42, 0.06) !important;
            border-radius: 12px !important;
            padding: 24px !important;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.02) !important;
            margin-bottom: 16px !important;
        }
        .ref-card-box h3 {
            font-size: 1.15rem !important;
            color: #1E40AF !important;
            font-weight: 700 !important;
            margin-bottom: 12px !important;
            border-bottom: 1px solid rgba(30, 64, 175, 0.08) !important;
            padding-bottom: 6px !important;
        }
        .ref-card-box p {
            font-size: 0.88rem !important;
            color: #334155 !important;
            line-height: 1.55 !important;
            margin-bottom: 10px !important;
        }
        .ref-card-box ul {
            padding-left: 18px !important;
            margin-bottom: 10px !important;
        }
        .ref-card-box li {
            font-size: 0.85rem !important;
            line-height: 1.5 !important;
            color: #334155 !important;
            margin-bottom: 6px !important;
        }
        .ref-badge {
            display: inline-block !important;
            background-color: rgba(30, 64, 175, 0.04) !important;
            color: #1E40AF !important;
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            padding: 3px 8px !important;
            border-radius: 6px !important;
            margin-right: 4px !important;
            margin-bottom: 6px !important;
            border: 1px solid rgba(30, 64, 175, 0.08) !important;
        }
        
        /* Mobile Responsive Adjustments */
        @media (max-width: 768px) {
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 1.5rem !important;
                padding-left: 0.8rem !important;
                padding-right: 0.8rem !important;
            }
            .main-title {
                font-size: 1.8rem !important;
                margin-top: 10px !important;
                margin-bottom: 2px !important;
            }
            div[data-testid="stChatMessage"] {
                padding: 14px 18px !important;
                border-radius: 14px !important;
                margin-bottom: 12px !important;
            }
            div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
            div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
                font-size: 0.88rem !important;
                line-height: 1.55 !important;
            }
            div.stButton > button {
                padding: 12px 14px !important;
                font-size: 0.82rem !important;
                border-radius: 10px !important;
            }
            .sugg-header {
                font-size: 0.78rem !important;
                margin-top: 16px !important;
                margin-bottom: 8px !important;
            }
            
            /* Clean stacking for columns on small devices */
            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
                margin-bottom: 10px !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

USER_AVATAR = "👤"
BOT_AVATAR = "🏛️"

# -------------------------------------------------------------------
# Caching & Initialization
# -------------------------------------------------------------------
@st.cache_resource
def load_models():
    load_dotenv()
    
    def get_secret(key):
        try:
            return st.secrets[key]
        except Exception:
            return os.environ.get(key)
            
    # Pinecone
    pc_key = get_secret("PINECONE_API_KEY")
    pc = Pinecone(api_key=pc_key)
    index = pc.Index("nepal-corporate-laws")
    
    # Anthropic
    anthropic_key = get_secret("ANTHROPIC_API_KEY")
    if not anthropic_key:
        raise ValueError("ANTHROPIC_API_KEY is missing. Please add it to your Streamlit Secrets or .env file.")
    claude_client = anthropic.Anthropic(api_key=anthropic_key)
    
    # Init Sentence Transformer
    embedder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    
    # Init CrossEncoder for Reranking
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    return index, claude_client, embedder, reranker

try:
    index, claude_client, embedder, reranker = load_models()
except Exception as e:
    st.error(f"⚠️ System Initialization Error: {e}")
    st.stop()

# -------------------------------------------------------------------
# Helper: Robust LLM Caller
# -------------------------------------------------------------------
def translate_query(prompt, history=""):
    translation_prompt = f"""You are an expert bilingual legal assistant. The user will provide a new query, and there might be some conversation history.
Your task is to understand the context from the history (if any), and provide a STANDALONE version of the user's new query in BOTH standard English AND standard Nepali (Devanagari script).
A standalone query means replacing pronouns (it, they) with the actual entity being discussed.

Conversation History:
{history if history else "None"}

New Query: {prompt}

Format your output exactly like this (two lines):
English: [Your standalone English translation]
Nepali: [Your standalone Nepali translation]"""
    
    # Try Anthropic First
    anthropic_models = ["claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-8"]
    text_response = ""
    if claude_client:
        for model in anthropic_models:
            try:
                trans_response = claude_client.messages.create(
                    model=model, max_tokens=1024, messages=[{"role": "user", "content": translation_prompt}]
                )
                text_response = trans_response.content[0].text.strip()
                break
            except Exception as e:
                print(f"Translation failed for {model}: {e}")
                continue
            
    # Parse output
    english_query = prompt
    nepali_query = prompt
    if text_response:
        for line in text_response.split('\n'):
            if line.startswith('English:'):
                english_query = line.replace('English:', '').strip()
            elif line.startswith('Nepali:'):
                nepali_query = line.replace('Nepali:', '').strip()
                
    return english_query, nepali_query

def get_technical_flow_info():
    if st.session_state.app_lang == "English":
        return """Our Retrieval-Augmented Generation (RAG) pipeline operates in real-time through the following steps:
1. **Bilingual Standalone Query Generation**: The user's query is converted to a standalone question in both English and Nepali using `Claude 3.5 Sonnet` (resolving pronouns from chat history).
2. **Local Multi-lingual Encoding**: Both queries are converted into high-dimensional vector embeddings using the local deep learning model `paraphrase-multilingual-MiniLM-L12-v2`.
3. **Vector Database Retrieval**: Queries are run against the **Pinecone Vector Database** (containing 1,865 chunks of Corporate Laws) to fetch the top 20 candidate matches.
4. **Neural Reranking**: A local `CrossEncoder` (`ms-marco-MiniLM-L-6-v2`) evaluates user query and candidate texts to select the top 4 highly relevant passages.
5. **Contextual LLM Synthesis**: The top 4 passages and user prompt are passed to **Claude 3.5 Sonnet** to generate a fact-grounded answer with citations.
6. **Interaction Audit Trail**: The prompt, response, and citations are recorded in `chat_logs.db` for the admin monitoring dashboard."""
    else:
        return """हाम्रो Retrieval-Augmented Generation (RAG) पाइपलाइनले यसरी काम गर्दछ:
1. **बाइलिङ्गल प्रश्न रुपान्तरण**: हजुरको प्रश्न र पुराना कुराकानीका आधारमा `Claude 3.5 Sonnet` मार्फत नेपाली र अंग्रेजीमा स्वतन्त्र रूपमा बुझिने प्रश्नहरू तयार गरिन्छ।
2. **स्थानीय मल्टि-लिङ्गल इनकोडिङ**: दुवै भाषाका प्रश्नहरूलाई स्थानीय `SentenceTransformer` (`paraphrase-multilingual-MiniLM-L12-v2`) द्वारा गणितीय संकेत (vector embedding) मा रूपान्तरण गरिन्छ।
3. **भेक्टर डाटाबेस खोज (Retrieval)**: ती गणितीय संकेतहरूलाई **Pinecone Vector Database** (जसमा १८६५ कानुनी बुँदाहरू छन्) मा खोजी शीर्ष २० वटा मिल्दाजुल्दा बुँदाहरू निकालिन्छ।
4. **न्यूरल रि-र्याङ्किङ**: स्थानीय `CrossEncoder` (`ms-marco-MiniLM-L-6-v2`) द्वारा ती २० बुँदाहरूमध्ये सबैभन्दा सान्दर्भिक शीर्ष ४ वटा बुँदाहरू मात्र छनोट गरिन्छ।
5. **आधिकारिक उत्तर संश्लेषण (Synthesis)**: छनोट गरिएका ४ बुँदाहरू र हजुरको प्रश्नलाई **Claude 3.5 Sonnet** मा पठाई तथ्यपरक उत्तर र कानुनी धाराहरू तयार गरिन्छ।
6. **अडिट ट्रेल (Audit Logging)**: यो सम्पुर्ण प्रक्रिया, सोधिएको प्रश्न र स्रोतहरू `chat_logs.db` मा सुरक्षित राखिन्छ ताकी अडिट ड्यासबोर्डमा हेर्न सकियोस्।"""

# -------------------------------------------------------------------
# Bilingual Setup & Sidebar
# -------------------------------------------------------------------
if "app_lang" not in st.session_state:
    st.session_state.app_lang = "नेपाली"

# Read language state
current_lang = st.session_state.app_lang

# Text Dictionaries
if current_lang == "English":
    ui_title = "NexSight Law 🇳🇵"
    ui_subtitle = "Professional Regulatory Compliance & Legal Reference Portal"
    sidebar_title = "NexSight Law"
    sidebar_desc = "A structured regulatory reference portal covering BAFIA, Nepal Rastra Bank Act, Banking Offence and Punishment Act, Anti-Money Laundering Act, Labor Act, and NRB Unified Directives. Designed to support legal reference and compliance checks with precise citations."
    btn_clear = "🧹 Clear Chat History"
    ph_input = "Ask your legal question..."
    msg_welcome = """**Welcome to the NexSight Law Compliance Portal.**

This portal provides structured access to key statutory frameworks in Nepal's corporate and banking sectors, including **BAFIA**, **Nepal Rastra Bank Act**, **Banking Offence and Punishment Act**, **Anti-Money Laundering Act**, **Labor Act**, and **NRB Unified Directives**. 

Please enter your compliance query or legal question below. The system will search the database and present the relevant provisions alongside a detailed regulatory analysis. How may I assist you with your compliance search today?"""
    sugg_heading = "<div class='sugg-header'>💡 Common Regulatory Reference Scenarios</div>"
    sugg_q1 = "Can a person convicted of a banking offense become a bank director? Answer based on BAFIA and the Banking Offence and Punishment Act."
    sugg_q2 = "What action is taken under the Labor Act if an employee's remuneration is not paid, and does it fall under money laundering?"
    sugg_q3 = "Under what circumstances can Nepal Rastra Bank take control of the management of any bank (BAFIA)?"
    sugg_q4 = "What is the liquidation process of a Bank/Financial Institution, and how is the priority of debt recovery determined under BAFIA?"
else:
        ui_title = "NexSight Law 🇳🇵"
        ui_subtitle = "नेपालको बैंकिङ तथा कर्पोरेट क्षेत्रको आधिकारिक कानुनी सन्दर्भ पोर्टल"
        sidebar_title = "NexSight Law"
        sidebar_desc = "नेपालको वित्तीय र कर्पोरेट क्षेत्रका प्रमुख ऐन तथा नीतिगत व्यवस्थाहरूको एकीकृत प्रणाली। बैंक तथा वित्तीय संस्था ऐन, नेपाल राष्ट्र बैंक ऐन, बैंकिङ कसूर ऐन, सम्पत्ति शुद्धीकरण निवारण ऐन, श्रम ऐन र राष्ट्र बैंक एकिकृत निर्देशनहरू सम्बन्धी प्रावधानहरूको कानुनी सन्दर्भ र अनुपालन विश्लेषण।"
        btn_clear = "🧹 कुराकानी मेट्नुहोस् (Clear Chat)"
        ph_input = "कानुनसम्बन्धी आफ्नो प्रश्न सोध्नुहोस्..."
        msg_welcome = """**NexSight Law कानुनी अनुपालन (Compliance) पोर्टलमा स्वागत छ।**

यो पोर्टल नेपालको बैंकिङ तथा संगठित क्षेत्रका प्रमुख कानुनी दस्तावेजहरू जस्तै— **बैंक तथा वित्तीय संस्था ऐन (BAFIA)**, **नेपाल राष्ट्र बैंक ऐन**, **बैंकिङ कसूर तथा सजाय ऐन**, **सम्पत्ति शुद्धीकरण निवारण ऐन**, **श्रम ऐन** र **नेपाल राष्ट्र बैंक एकिकृत निर्देशनहरू** का प्रावधानहरूको सटिक विश्लेषण र जानकारी प्रदान गर्न डिजाइन गरिएको हो।

तपाईंले आफ्नो जिज्ञासा वा कानुनी प्रश्न तल राख्न सक्नुहुन्छ। प्रणालीले आधिकारिक दफाहरूको सन्दर्भ सहित सटिक विश्लेषणात्मक विवरण प्रस्तुत गर्नेछ। आज म तपाईंलाई कुन कानुनी विषयमा मद्दत गरौं?"""
        sugg_heading = "<div class='sugg-header'>💡 धेरै सोधिने केही कानुनी व्यवस्थाहरू (नमूना)</div>"
        sugg_q1 = "बैंकिङ कसुर लागेको व्यक्तिले बैंकको सञ्चालक (Director) बन्न पाउँछ कि पाउँदैन? BAFIA र बैंकिङ कसूर ऐनको आधारमा भन्नुहोस्।"
        sugg_q2 = "कर्मचारीको पारिश्रमिक नदिएमा श्रम ऐन अनुसार कस्तो कारबाही हुन्छ र के यो सम्पत्ति शुद्धीकरणको दायरामा आउँछ सम्पत्ति शुद्धीकरण ऐन अनुसार?"
        sugg_q3 = "नेपाल राष्ट्र बैंकले कुन अवस्थामा कुनै पनि बैंकको व्यवस्थापन आफ्नो नियन्त्रणमा लिन सक्छ? राष्ट्र बैंक ऐन र BAFIA अनुसार स्पष्ट पार्नुहोस्।"
        sugg_q4 = "बैंक वा वित्तीय संस्था खारेजी (Liquidation) को प्रक्रिया के हो र यसमा निक्षेपकर्ता वा ऋण असुलीको प्राथमिकता कसरी निर्धारण हुन्छ BAFIA अनुसार?"

# Sidebar Layout
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6033/6033333.png", width=80)
    st.title(sidebar_title)
    st.markdown(sidebar_desc)
    st.divider()
    if st.button(btn_clear, use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.suggested_questions = []
        st.rerun()
    st.divider()
    
    # Secure Developer / Admin Mode Check
    admin_pwd = os.environ.get("ADMIN_CODE", "admin123")
    try:
        admin_pwd = st.secrets["ADMIN_CODE"]
    except Exception:
        pass
        
    with st.expander("🔑 Admin Settings"):
        admin_code = st.text_input("Access Code:", type="password", key="dev_access_input")
        is_admin = (admin_code == admin_pwd)
        if is_admin:
            st.success("Developer Mode Unlocked!")
            
    if is_admin:
        st.subheader("🛠️ View Mode / मोड")
        app_mode = st.radio(
            "Select Screen / स्क्रिन:",
            ["⚖️ Compliance Assistant", "📊 Monitoring Dashboard"],
            index=0,
            label_visibility="collapsed"
        )
        st.divider()
        st.caption("Powered by: **Claude Sonnet 4.6**")
    else:
        app_mode = "⚖️ Compliance Assistant"
        
    st.divider()
    # Bilingual Legal Disclaimer Block
    disclaimer_text = (
        "⚠️ **Disclaimer**: This tool provides AI-based legal guidance for informational purposes only and does not constitute official legal counsel or binding legal advice."
        if st.session_state.app_lang == "English"
        else "⚠️ **अस्वीकरण**: यो उपकरणले सूचनामूलक उद्देश्यका लागि AI-आधारित कानुनी मार्गदर्शन मात्र प्रदान गर्दछ र यसलाई आधिकारिक कानुनी सल्लाह वा बाध्यकारी कानुनी राय मान्न सकिँदैन।"
    )
    st.markdown(f"<div class='disclaimer-box'>{disclaimer_text}</div>", unsafe_allow_html=True)

# Session State & Main UI
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []

if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": msg_welcome,
        "sources": []
    })

# -------------------------------------------------------------------
# Monitoring Dashboard Page (Renders if selected, stops further execution)
# -------------------------------------------------------------------
if app_mode == "📊 Monitoring Dashboard":
    st.markdown("<div class='main-title' style='text-align: left; font-size: 2.3rem;'>📊 System Monitoring Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div style='color: #4b5563; font-size: 1.05rem; font-weight: 500; margin-bottom: 20px;'>Real-time analytical view of NexSight Law interactions</div>", unsafe_allow_html=True)
    st.divider()
    
    # Read logs from SQLite
    logs = database.get_all_logs()
    
    if not logs:
        st.info("ℹ️ No logs found. Start chatting with the assistant to generate interaction logs.")
    else:
        # Convert to DataFrame
        df = pd.DataFrame(logs)
        
        # Display KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric(label="👥 Total Interactions", value=len(df))
        with kpi2:
            st.metric(label="🛡️ Active AI Engine", value="Claude 3.5 Sonnet")
        with kpi3:
            st.metric(label="🔎 Unique Queries", value=df["user_query"].nunique())
            
        st.divider()
        
        # Analytics Chart
        col_chart, col_empty = st.columns([2, 1])
        with col_chart:
            # Count occurrences of main acts in logs
            act_counts = {
                "BAFIA": 0, 
                "NRB Act": 0, 
                "Banking Offence": 0, 
                "Money Laundering": 0, 
                "Labor Act": 0, 
                "NRB Directives": 0
            }
            for src_str in df["sources_used"].dropna():
                for act in act_counts.keys():
                    if act.lower() in src_str.lower() or (act == "Money Laundering" and "money" in src_str.lower()) or (act == "Banking Offence" and "offence" in src_str.lower()):
                        act_counts[act] += 1
            
            chart_df = pd.DataFrame({
                "Document Name": list(act_counts.keys()),
                "Hits / Searches": list(act_counts.values())
            }).set_index("Document Name")
            
            st.subheader("📚 Consulted Legal Documents (Search Popularity)")
            st.bar_chart(chart_df)
            
        st.divider()
        
        # Raw Logs Data Table with search filter
        st.subheader("📋 Interaction Log Auditing Table")
        
        # Add a search filter box
        search_query = st.text_input("🔍 Filter logs by query keyword:", "")
        if search_query:
            filtered_df = df[df["user_query"].str.contains(search_query, case=False, na=False)]
        else:
            filtered_df = df
            
        # Select columns to display in a clean layout
        display_df = filtered_df[["timestamp", "user_query", "bot_response", "sources_used", "model_used"]].copy()
        
        st.dataframe(
            display_df, 
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Date & Time", format="YYYY-MM-DD HH:mm:ss"),
                "user_query": st.column_config.TextColumn("User Query", width="medium"),
                "bot_response": st.column_config.TextColumn("AI Response", width="large"),
                "sources_used": st.column_config.TextColumn("Citations Used", width="medium"),
                "model_used": st.column_config.TextColumn("Model", width="small")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # CSV Export Button
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Export Audit Logs to CSV",
            data=csv_data,
            file_name="nexsight_law_audit_logs.csv",
            mime="text/csv",
            use_container_width=True
        )
    st.stop()

# Main Header with Title & Language Toggle
col_title, col_toggle = st.columns([3, 1])
with col_title:
    st.markdown(f"<div class='main-title' style='text-align: left; font-size: 2.3rem;'>{ui_title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color: #4b5563; font-size: 1.05rem; font-weight: 500; margin-bottom: 20px;'>{ui_subtitle}</div>", unsafe_allow_html=True)
with col_toggle:
    st.write("") # vertical spacing helper
    # Styled Toggle Switch for Language
    is_english = st.toggle("🌐 English", value=(st.session_state.app_lang == "English"))
    new_lang = "English" if is_english else "नेपाली"
    
    # If language changed, update state, update welcome message, and rerun
    if new_lang != st.session_state.app_lang:
        st.session_state.app_lang = new_lang
        new_msg_welcome = (
            """**Welcome to the NexSight Law Compliance Portal.**

This portal provides structured access to key statutory frameworks in Nepal's corporate and banking sectors, including **BAFIA**, **Nepal Rastra Bank Act**, **Banking Offence and Punishment Act**, **Anti-Money Laundering Act**, **Labor Act**, and **NRB Unified Directives**. 

Please enter your compliance query or legal question below. The system will search the database and present the relevant provisions alongside a detailed regulatory analysis. How may I assist you with your compliance search today?"""
            if new_lang == "English"
            else """**NexSight Law कानुनी अनुपालन (Compliance) पोर्टलमा स्वागत छ।**

यो पोर्टल नेपालको बैंकिङ तथा संगठित क्षेत्रका प्रमुख कानुनी दस्तावेजहरू जस्तै— **बैंक तथा वित्तीय संस्था ऐन (BAFIA)**, **नेपाल राष्ट्र बैंक ऐन**, **बैंकिङ कसूर तथा सजाय ऐन**, **सम्पत्ति शुद्धीकरण निवारण ऐन**, **श्रम ऐन** र **नेपाल राष्ट्र बैंक एकिकृत निर्देशनहरू** का प्रावधानहरूको सटिक विश्लेषण र जानकारी प्रदान गर्न डिजाइन गरिएको हो।

तपाईंले आफ्नो जिज्ञासा वा कानुनी प्रश्न तल राख्न सक्नुहुन्छ। प्रणालीले आधिकारिक दफाहरूको सन्दर्भ सहित सटिक विश्लेषणात्मक विवरण प्रस्तुत गर्नेछ। आज म तपाईंलाई कुन कानुनी विषयमा मद्दत गरौं?"""
        )
        if len(st.session_state.messages) > 0:
            st.session_state.messages[0]["content"] = new_msg_welcome
        st.rerun()

st.divider()

# Render Chat Messages & Sidebar Desk Layout
col_main, col_ref = st.columns([2.2, 1])

with col_main:
    for message in st.session_state.messages:
        avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                if is_admin:
                    col_exp1, col_exp2 = st.columns(2)
                    with col_exp1:
                        exp_title = "📚 Legal Sources" if st.session_state.app_lang == "English" else "📚 कानुनी स्रोतहरू (Legal Sources)"
                        with st.expander(exp_title):
                            seen = set()
                            for src in message["sources"]:
                                key = f"{src['act']}-{src['section']}"
                                if key not in seen:
                                    seen.add(key)
                                    st.markdown(f"**{src['act']} ({src['section']})**")
                                    st.caption(f"{src['text'][:150]}...")
                    with col_exp2:
                        tech_title = "⚙️ Technical Flow" if st.session_state.app_lang == "English" else "⚙️ प्राविधिक प्रक्रिया (Technical Flow)"
                        with st.expander(tech_title):
                            st.markdown(get_technical_flow_info())
                else:
                    exp_title = "📚 Legal Sources" if st.session_state.app_lang == "English" else "📚 कानुनी स्रोतहरू (Legal Sources)"
                    with st.expander(exp_title):
                        seen = set()
                        for src in message["sources"]:
                            key = f"{src['act']}-{src['section']}"
                            if key not in seen:
                                seen.add(key)
                                st.markdown(f"**{src['act']} ({src['section']})**")
                                st.caption(f"{src['text'][:150]}...")

    # Render Suggested Questions (Always Visible at the bottom of the chat history)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(sugg_heading, unsafe_allow_html=True)

    if st.session_state.get("suggested_questions"):
        display_questions = st.session_state.suggested_questions[:4]
    else:
        display_questions = [sugg_q1, sugg_q2, sugg_q3, sugg_q4]

    col1, col2 = st.columns(2)
    for idx, q_text in enumerate(display_questions):
        col = col1 if idx % 2 == 0 else col2
        with col:
            # Unique key based on index and length of messages to prevent DuplicateWidgetID
            btn_key = f"sugg_{idx}_{len(st.session_state.messages)}"
            if st.button(q_text, key=btn_key, use_container_width=True):
                st.session_state.suggested_prompt = q_text
                st.rerun()

    prompt = st.chat_input(ph_input)
    if "suggested_prompt" in st.session_state:
        prompt = st.session_state.suggested_prompt
        del st.session_state.suggested_prompt

    if prompt:
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar=BOT_AVATAR):
            response_placeholder = st.empty()
            
            with st.spinner("🔍 कानुनका किताबहरू पल्टाउँदै..." if st.session_state.app_lang != "English" else "🔍 Consulting statutes..."):
                # Prepare conversation history for memory
                history_text = ""
                recent_msgs = st.session_state.messages[-5:] if len(st.session_state.messages) > 1 else []
                for m in recent_msgs:
                    if m["role"] in ["user", "assistant"]:
                        role_name = "User" if m["role"] == "user" else "AI"
                        # Trim assistant content so prompt doesn't get too large, 500 chars is safer
                        content_preview = m['content'][:500].replace('\n', ' ')
                        history_text += f"{role_name}: {content_preview}\n"
                        
                english_query, nepali_query = translate_query(prompt, history=history_text)
                
                en_vector = embedder.encode(english_query).tolist()
                np_vector = embedder.encode(nepali_query).tolist()
                
                try:
                    # Fetch top 20 for better recall before reranking
                    res_en = index.query(vector=en_vector, top_k=20, include_metadata=True)
                    res_np = index.query(vector=np_vector, top_k=20, include_metadata=True)
                except Exception as e:
                    print(f"Pinecone Database search error: {e}")
                    if st.session_state.app_lang == "English":
                        response_placeholder.error("⚠️ The server is currently experiencing unusually high traffic. Please try again in a few minutes.")
                    else:
                        response_placeholder.error("⚠️ सर्भरमा अत्यधिक चाप भएकाले सेवा अस्थायी रूपमा अवरुद्ध छ। कृपया केही समयपछि पुनः प्रयास गर्नुहोला।")
                    st.stop()
                
                # Merge and deduplicate matches
                all_matches = {}
                for match in list(res_en.matches) + list(res_np.matches):
                    if match.id not in all_matches:
                        all_matches[match.id] = match
                            
                # RERANKING
                # We use the english_query because the CrossEncoder is English-optimized
                pairs = []
                match_list = list(all_matches.values())
                for match in match_list:
                    pairs.append((english_query, match.metadata.get("text", "")))
                    
                if pairs:
                    scores = reranker.predict(pairs)
                    # Combine match and score into a tuple, sort by score descending, take top 4
                    scored_matches = sorted(zip(match_list, scores), key=lambda x: x[1], reverse=True)[:4]
                    best_matches = [sm[0] for sm in scored_matches]
                else:
                    best_matches = []
                
                contexts = []
                source_metadata = []
                
                # Filter matches by an absolute threshold if needed, cross-encoder scores vary but > 0 usually means somewhat relevant.
                for match in best_matches:
                        act_name = match.metadata.get("Act Name", "Unknown Act")
                        section = str(match.metadata.get("Section", "")).replace("**", "")
                        text = match.metadata.get("text", "")
                        
                        contexts.append(f"Source: {act_name} - {section}\nText: {text}")
                        source_metadata.append({"act": act_name, "section": section, "text": text})
                
                if not contexts:
                    error_msg = "माफ गर्नुहोला, तपाईंको प्रश्नसँग सम्बन्धित कुनै पनि कानुनी दफा मेरो डाटाबेसमा भेटिएन।" if st.session_state.app_lang != "English" else "I apologize, but no relevant legal sections were found in the database for your query."
                    response_placeholder.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
                    
            if not contexts:
                st.stop()

            full_context = "\n\n---\n\n".join(contexts)
            llm_prompt = f"""You are an excellent and reliable expert AI in Nepal Corporate Laws. 
Read the legal context provided below and answer the user's question clearly and accurately.

LANGUAGE RULES FOR YOUR RESPONSE:
1. If the user explicitly asks you to reply in a specific language, you MUST answer in that language.
2. If no language is explicitly requested, answer in the same language the user used in their question (e.g., if they asked in English, reply in English).
3. CRITICAL RULE: If the user asks the question in Romanized Nepali (Nepali written using the English alphabet), you MUST answer in Standard Nepali using the Devanagari script. Never reply in Romanized Nepali.

FORMATTING AND LOGIC RULES:
1. You MUST explicitly mention the Act Name and Section number (from the context) that your answer is based on.
2. SYNTHESIS (MULTI-HOP): If the user's question involves multiple topics or spans multiple acts, you MUST synthesize the information comprehensively from all relevant provided contexts. Explicitly compare or combine the rules from different acts as required to provide a complete, high-quality, and logical legal answer.
3. RESPONSE STRUCTURE & AESTHETICS:
   Format your response professionally with this exact structure:
   - **Key Takeaway / मुख्य निष्कर्ष**: Start with a concise, 1-2 sentence key legal answer wrapped in a blockquote (`> **Key Takeaway / मुख्य निष्कर्ष**: ...`).
   - **Legal Analysis / कानुनी विश्लेषण**: Divide your detailed answer into logical sections using clean markdown headings (e.g., `### 🔍 Analysis` or `### ⚖️ Applicable Rules`).
   - **Relevant Provisions / सम्बद्ध कानुनी व्यवस्थाहरू**: List key sections cited, formatted as clean bullet points (e.g., `- 📌 **BAFIA, Section 12**: [Brief provision summary]`).
   Use bold text for critical terms to make the response highly scannable and easy to read. Keep the language professional, authoritative, and structured. Do not use very large headers or excessive markdown formatting outside of this layout.
4. DYNAMIC FOLLOW-UP SUGGESTIONS: At the very end of your response, you MUST generate exactly 3 logical, relevant follow-up questions that the user might want to ask next based on your response and the context. Format them on a new line at the end of your response exactly like this:
[Suggestions: Question 1? || Question 2? || Question 3?]
The suggestions must be in the same language as your response (English or Nepali). Do not include any other text inside the brackets.
5. CONCISENESS & TOKEN OPTIMIZATION: Be highly concise, clear, and direct. Avoid repeating the provided context sentences literally. Keep explanations brief and focused entirely on answering the user's specific query. Aim to keep the total response length under 250 words.

[Context Start]
{full_context}
[Context End]

Question: {prompt}"""

            with st.spinner("✍️ आधिकारिक उत्तर तयार गर्दै (Claude)..." if st.session_state.app_lang != "English" else "✍️ Synthesizing legal analysis (Claude)..."):
                full_response = ""
                success = False
                
                # 1. Try Anthropic
                if claude_client:
                    anthropic_models = ["claude-sonnet-4-6", "claude-haiku-4-5", "claude-opus-4-8"]
                    for model in anthropic_models:
                        try:
                            with claude_client.messages.stream(
                                model=model, max_tokens=2048, messages=[{"role": "user", "content": llm_prompt}]
                            ) as stream:
                                for text in stream.text_stream:
                                    full_response += text
                                    # Hide suggestions markup during streaming
                                    display_response = re.sub(r"\[Suggestions:.*", "", full_response, flags=re.DOTALL).strip()
                                    response_placeholder.markdown(display_response + " ▌")
                            success = True
                            break
                        except Exception as e:
                            print(f"Generation failed for {model}: {e}")
                            continue

                if not success:
                    if st.session_state.app_lang == "English":
                        st.error("⚠️ The server is currently experiencing unusually high traffic. Please try again in a few minutes.")
                    else:
                        st.error("⚠️ सर्भरमा अत्यधिक चाप भएकाले सेवा अस्थायी रूपमा अवरुद्ध छ। कृपया केही समयपछि पुनः प्रयास गर्नुहोला।")

            if success:
                # Extract suggestions
                suggestions = []
                match = re.search(r"\[Suggestions:\s*(.*?)\s*\]", full_response, re.DOTALL)
                if match:
                    raw_suggs = match.group(1)
                    suggestions = [s.strip() for s in raw_suggs.split("||") if s.strip()]
                    full_response = re.sub(r"\[Suggestions:\s*(.*?)\s*\]", "", full_response, flags=re.DOTALL).strip()
                
                if suggestions:
                    st.session_state.suggested_questions = suggestions
                
                response_placeholder.markdown(full_response)
                
                if is_admin:
                    col_exp1, col_exp2 = st.columns(2)
                    with col_exp1:
                        exp_title = "📚 Legal Sources" if st.session_state.app_lang == "English" else "📚 कानुनी स्रोतहरू (Legal Sources)"
                        with st.expander(exp_title):
                            seen = set()
                            for src in source_metadata:
                                key = f"{src['act']}-{src['section']}"
                                if key not in seen:
                                    seen.add(key)
                                    st.markdown(f"**{src['act']} ({src['section']})**")
                                    st.caption(f"{src['text'][:150]}...")
                    with col_exp2:
                        tech_title = "⚙️ Technical Flow" if st.session_state.app_lang == "English" else "⚙️ प्राविधिक प्रक्रिया (Technical Flow)"
                        with st.expander(tech_title):
                            st.markdown(get_technical_flow_info())
                else:
                    exp_title = "📚 Legal Sources" if st.session_state.app_lang == "English" else "📚 कानुनी स्रोतहरू (Legal Sources)"
                    with st.expander(exp_title):
                        seen = set()
                        for src in source_metadata:
                            key = f"{src['act']}-{src['section']}"
                            if key not in seen:
                                seen.add(key)
                                st.markdown(f"**{src['act']} ({src['section']})**")
                                st.caption(f"{src['text'][:150]}...")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "sources": source_metadata
                })
                
                # LOGGING: Save to SQLite database
                database.log_interaction(prompt, full_response, source_metadata, "Claude")

with col_ref:
    if st.session_state.app_lang == "English":
        st.markdown("""
        <div class="ref-card-box">
            <h3>⚖️ Legal Reference Desk</h3>
            <p>This system references the official statutes, regulations, and circulars of Nepal. Use this panel to understand the coverage and maximize search accuracy.</p>
            
            <h4 style="margin-top:16px; font-weight:600; color:#1E40AF; font-size:0.95rem;">📚 Covered Statutes</h4>
            <div style="margin-bottom: 12px;">
                <span class="ref-badge">BAFIA, 2073</span>
                <span class="ref-badge">NRB Act, 2058</span>
                <span class="ref-badge">Banking Offence Act, 2064</span>
                <span class="ref-badge">AML Act, 2064</span>
                <span class="ref-badge">Labor Act, 2074</span>
                <span class="ref-badge">NRB Directives 2080</span>
            </div>
            
            <h4 style="margin-top:16px; font-weight:600; color:#1E40AF; font-size:0.95rem;">💡 Query Recommendations</h4>
            <ul>
                <li><strong>Cross-Act Synthesis:</strong> Try asking questions that span multiple laws, such as comparing labor disputes and banking penalties.</li>
                <li><strong>Romanized Input:</strong> You can type queries in Romanized Nepali (e.g. <code>sanchalak ko yogyata</code>). The portal will translate and respond in official Devanagari.</li>
                <li><strong>Provision Search:</strong> Cite specific sections if known (e.g., "Section 29 of BAFIA") for direct reference lookup.</li>
            </ul>
            
            <h4 style="margin-top:16px; font-weight:600; color:#1E40AF; font-size:0.95rem;">🔄 Dataset Information</h4>
            <p style="font-size: 0.82rem; color: #64748B; margin-bottom: 0;">
                • <strong>Status:</strong> Active & Synced<br/>
                • <strong>Knowledge Index:</strong> 1,865 provisions<br/>
                • <strong>Last Update:</strong> June 2026 (including latest NRB circulars)
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="ref-card-box">
            <h3>⚖️ कानुनी सन्दर्भ सहायता</h3>
            <p>यस पोर्टलले नेपालका आधिकारिक ऐन, नियम र नेपाल राष्ट्र बैंकका निर्देशनहरूलाई सन्दर्भ सामग्रीको रूपमा प्रयोग गर्दछ। पोर्टलको अधिकतम सदुपयोगका लागि तलका जानकारीहरू हेर्नुहोला।</p>
            
            <h4 style="margin-top:16px; font-weight:600; color:#1E40AF; font-size:0.95rem;">📚 समेटिएका कानुनहरू</h4>
            <div style="margin-bottom: 12px;">
                <span class="ref-badge">बाफिया (BAFIA), २०७३</span>
                <span class="ref-badge">नेपाल राष्ट्र बैंक ऐन, २०५८</span>
                <span class="ref-badge">बैंकिङ कसूर ऐन, २०६४</span>
                <span class="ref-badge">सम्पत्ति शुद्धीकरण ऐन, २०६४</span>
                <span class="ref-badge">श्रम ऐन, २०७४</span>
                <span class="ref-badge">राष्ट्र बैंक निर्देशन २०८०</span>
            </div>
            
            <h4 style="margin-top:16px; font-weight:600; color:#1E40AF; font-size:0.95rem;">💡 खोज सम्बन्धी सुझावहरू</h4>
            <ul>
                <li><strong>बहु-ऐन विश्लेषण:</strong> एकभन्दा बढी ऐन आकर्षित हुने जटिल कानुनी अवस्थाबारे सोध्न सक्नुहुन्छ (जस्तै: बैंकिङ कसूर र श्रम ऐन बीचको अन्तरसम्बन्ध)।</li>
                <li><strong>रोमन नेपाली खोज:</strong> तपाईंले रोमन अंग्रेजीमा (जस्तै: <code>sanchalak ko yogyata</code>) लेखी पनि प्रश्न सोध्न सक्नुहुन्छ, उत्तर देवनागरी नेपालीमा प्राप्त हुनेछ।</li>
                <li><strong>विशिष्ट दफाहरू:</strong> कानुनी दफा थाहा भएमा सिधै उल्लेख गर्नुहोस् (जस्तै: "बाफियाको दफा २९"), पोर्टलले सिधै सन्दर्भ खोज्नेछ।</li>
            </ul>
            
            <h4 style="margin-top:16px; font-weight:600; color:#1E40AF; font-size:0.95rem;">🔄 डाटाबेसको अवस्था</h4>
            <p style="font-size: 0.82rem; color: #64748B; margin-bottom: 0;">
                • <strong>अवस्था:</strong> सक्रिय र अद्यावधिक (Active)<br/>
                • <strong>कानुनी बुँदाहरू:</strong> १८६५ दफाहरू<br/>
                • <strong>अन्तिम परिमार्जन:</strong> जुन २०२६ (NRB का पछिल्ला परिपत्रहरू सहित)
            </p>
        </div>
        """, unsafe_allow_html=True)
