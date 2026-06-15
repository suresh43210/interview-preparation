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
    layout="centered",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# Custom CSS for Aesthetics
# -------------------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700;800&display=swap');
        
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Modern Siddhartha Bank Theme Setup */
        .stApp {
            background-color: #F8F9FA !important;
            color: #2D3748 !important;
            font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif !important;
        }
        
        /* Prevent browser dark mode issues with soft dark text */
        .stApp p, .stApp span, .stApp div, .stApp li, .stApp label {
            color: #2D3748 !important;
            font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif !important;
        }
        
        .main-title {
            font-size: 2.8rem;
            font-weight: 800;
            background: -webkit-linear-gradient(45deg, #0A3B7C, #F39200);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 5px;
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -1px;
        }
        
        /* Sidebar layout styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid rgba(10, 59, 124, 0.08) !important;
        }
        [data-testid="stSidebar"] * {
            color: #2D3748 !important;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #0A3B7C !important;
            font-family: 'Outfit', sans-serif !important;
        }
        
        /* Premium Chat Container Card styling */
        div[data-testid="stChatMessage"] {
            background-color: #ffffff !important;
            border: 1px solid rgba(10, 59, 124, 0.06) !important;
            border-radius: 18px !important;
            padding: 22px 26px !important;
            box-shadow: 0 4px 25px rgba(10, 59, 124, 0.03) !important;
            margin-bottom: 16px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div[data-testid="stChatMessage"]:hover {
            box-shadow: 0 8px 30px rgba(10, 59, 124, 0.06) !important;
            border-color: rgba(10, 59, 124, 0.12) !important;
        }
        
        /* Chat Content Typography Re-alignment */
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
            font-size: 0.91rem !important;
            line-height: 1.68 !important;
            color: #2D3748 !important;
            margin-bottom: 12px !important;
        }
        
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] ul, 
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] ol {
            padding-left: 22px !important;
            margin-bottom: 14px !important;
        }
        
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
            font-size: 0.91rem !important;
            line-height: 1.68 !important;
            color: #2D3748 !important;
            margin-bottom: 8px !important;
        }
        
        /* Chat Content Headings */
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3,
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h4 {
            color: #0A3B7C !important;
            font-family: 'Outfit', sans-serif !important;
            font-weight: 700 !important;
            margin-top: 22px !important;
            margin-bottom: 12px !important;
            letter-spacing: -0.3px !important;
        }
        
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 {
            font-size: 1.12rem !important;
            border-bottom: 1px solid rgba(10, 59, 124, 0.08) !important;
            padding-bottom: 6px !important;
        }
        
        /* Custom Blockquote (Key Summary Callout Box) */
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] blockquote {
            border-left: 4px solid #F39200 !important;
            background-color: rgba(243, 146, 0, 0.04) !important;
            padding: 14px 20px !important;
            border-radius: 4px 14px 14px 4px !important;
            margin: 18px 0 !important;
        }
        
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] blockquote p {
            color: #0A3B7C !important;
            font-weight: 600 !important;
            font-size: 0.91rem !important;
            margin-bottom: 0 !important;
        }
        
        /* Inline references code tags */
        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] code {
            background-color: rgba(10, 59, 124, 0.05) !important;
            color: #0A3B7C !important;
            padding: 2px 6px !important;
            border-radius: 6px !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            border: 1px solid rgba(10, 59, 124, 0.1) !important;
            font-family: 'Plus Jakarta Sans', monospace !important;
        }
        
        /* Source Citation Expanders styling */
        div[data-testid="stExpander"] {
            border: 1px solid rgba(10, 59, 124, 0.08) !important;
            border-radius: 14px !important;
            background-color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(10, 59, 124, 0.01) !important;
            margin-top: 10px !important;
            transition: all 0.3s ease !important;
        }
        div[data-testid="stExpander"]:hover {
            border-color: rgba(10, 59, 124, 0.15) !important;
            box-shadow: 0 6px 18px rgba(10, 59, 124, 0.03) !important;
        }
        
        /* Premium Buttons (Suggested Questions & Clear Chat) */
        div.stButton > button {
            width: 100%;
            border-radius: 12px;
            border: 1px solid rgba(10, 59, 124, 0.08);
            background: #ffffff;
            color: #0A3B7C !important;
            font-weight: 500;
            font-size: 0.9rem !important;
            padding: 12px 14px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            white-space: pre-wrap;
            height: auto;
            text-align: left;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(243, 146, 0, 0.15);
            border-color: #F39200;
            color: #F39200 !important;
            background: #ffffff;
        }
        
        /* Suggested Questions Section Header */
        .sugg-header {
            color: #718096 !important;
            font-size: 0.88rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-top: 24px !important;
            margin-bottom: 12px !important;
        }
        
        /* Chat Input Styling */
        .stChatFloatingInputContainer {
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(10, 59, 124, 0.08);
            background-color: #ffffff !important;
            padding: 8px !important;
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
    ui_subtitle = "Your intelligent legal companion for Nepal's Corporate Sector"
    sidebar_title = "NexSight Law"
    sidebar_desc = "Instantly navigate through **1,865 provisions** from BAFIA, NRB Act, Banking Offence Act, AML Act, Labor Act, and NRB Unified Directives. Get precise, AI-powered insights with exact legal citations to ensure compliance and mitigate risks."
    btn_clear = "🧹 Clear Chat History"
    ph_input = "Ask your legal question..."
    msg_welcome = """**Hello!** I am your AI Assistant for Nepal's Corporate & Banking Laws.

You can ask me any legal question related to **BAFIA**, **NRB Act**, **Banking Offence Act**, **Anti-Money Laundering Act**, **Labor Act**, or **NRB Directives**. I will provide you with accurate answers including official legal citations. How can I help you today?"""
    sugg_heading = "<div class='sugg-header'>💡 Logical & Complex Questions (Suggested)</div>"
    sugg_q1 = "Can a person convicted of a banking offense become a bank director? Answer based on BAFIA and the Banking Offence and Punishment Act."
    sugg_q2 = "What action is taken under the Labor Act if an employee's remuneration is not paid, and does it fall under money laundering?"
    sugg_q3 = "Under what circumstances can Nepal Rastra Bank take control of the management of any bank (BAFIA)?"
    sugg_q4 = "What is the liquidation process of a Bank/Financial Institution, and how is the priority of debt recovery determined under BAFIA?"
else:
        ui_title = "NexSight Law 🇳🇵"
        ui_subtitle = "तपाईंको भरपर्दो कानुनी सल्लाहकार (Corporate Law Assistant)"
        sidebar_title = "NexSight Law"
        sidebar_desc = "Pinecone Vector Database मा रहेका **१८६५ कानुनी दफाहरू** (BAFIA, राष्ट्र बैंक ऐन, बैंकिङ कसूर ऐन, सम्पत्ति शुद्धीकरण निवारण ऐन, श्रम ऐन र राष्ट्र बैंक एकिकृत निर्देशनहरू) पढेर सटिक उत्तर दिने AI।"
        btn_clear = "🧹 कुराकानी मेट्नुहोस् (Clear Chat)"
        ph_input = "कानुनसम्बन्धी आफ्नो प्रश्न सोध्नुहोस्..."
        msg_welcome = """**नमस्ते!** म नेपालको कर्पोरेट तथा बैंकिङ कानुनसम्बन्धी AI Assistant हुँ।

मलाई **बैंक तथा वित्तीय संस्था ऐन (BAFIA)**, **नेपाल राष्ट्र बैंक ऐन**, **बैंकिङ कसूर ऐन**, **सम्पत्ति शुद्धीकरण निवारण ऐन**, **श्रम ऐन**, वा **नेपाल राष्ट्र बैंक एकिकृत निर्देशनहरू** सँग सम्बन्धित कुनै पनि कानुनी प्रश्न सोध्न सक्नुहुन्छ। म तपाईंलाई आधिकारिक कानुनी दफाहरू सहित सटिक उत्तर दिनेछु। म कसरी सहयोग गरौं?"""
        sugg_heading = "<div class='sugg-header'>💡 जटिल र लजिकल प्रश्नहरू (Suggested)</div>"
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
    st.subheader("🛠️ View Mode / मोड")
    app_mode = st.radio(
        "Select Screen / स्क्रिन:",
        ["⚖️ Compliance Assistant", "📊 Monitoring Dashboard"],
        index=0,
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("Powered by: **Claude Sonnet 4.6**")

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
            """**Hello!** I am your AI Assistant for Nepal's Corporate & Banking Laws.

You can ask me any legal question related to **BAFIA**, **NRB Act**, **Banking Offence Act**, **Anti-Money Laundering Act**, **Labor Act**, or **NRB Directives**. I will provide you with accurate answers including official legal citations. How can I help you today?"""
            if new_lang == "English"
            else """**नमस्ते!** म नेपालको कर्पोरेट तथा बैंकिङ कानुनसम्बन्धी AI Assistant हुँ।

मलाई **बैंक तथा वित्तीय संस्था ऐन (BAFIA)**, **नेपाल राष्ट्र बैंक ऐन**, **बैंकिङ कसूर ऐन**, **सम्पत्ति शुद्धीकरण निवारण ऐन**, **श्रम ऐन**, वा **नेपाल राष्ट्र बैंक एकिकृत निर्देशनहरू** सँग सम्बन्धित कुनै पनि कानुनी प्रश्न सोध्न सक्नुहुन्छ। म तपाईंलाई आधिकारिक कानुनी दफाहरू सहित सटिक उत्तर दिनेछु। म कसरी सहयोग गरौं?"""
        )
        if len(st.session_state.messages) > 0:
            st.session_state.messages[0]["content"] = new_msg_welcome
        st.rerun()

st.divider()

# Render Chat Messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
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
        
        with st.spinner("🔍 कानुनका किताबहरू पल्टाउँदै..."):
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
                error_msg = "माफ गर्नुहोला, तपाईंको प्रश्नसँग सम्बन्धित कुनै पनि कानुनी दफा मेरो डाटाबेसमा भेटिएन।"
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

        with st.spinner("✍️ आधिकारिक उत्तर तयार गर्दै (Claude)..."):
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
            
            with st.expander("📚 कानुनी स्रोतहरू (Legal Sources)"):
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
