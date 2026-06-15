import os
import streamlit as st
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer, CrossEncoder
from dotenv import load_dotenv
import anthropic
from google import genai
import database
import re

# -------------------------------------------------------------------
# Streamlit Page Config
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Nepal Corporate Law Chatbot",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# Custom CSS for Aesthetics
# -------------------------------------------------------------------
st.markdown("""
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Modern Glassmorphism & Siddhartha Bank Theme */
        .stApp {
            background-color: #F8F9FA !important;
            color: #0A3B7C !important;
        }
        
        /* Force text colors to fix Dark Mode unreadability */
        .stMarkdown, p, div, span {
            color: #1f2937;
        }
        
        .main-title {
            font-size: 2.8rem;
            font-weight: 800;
            background: -webkit-linear-gradient(45deg, #0A3B7C, #F39200);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 5px;
            font-family: 'Inter', sans-serif;
            letter-spacing: -1px;
        }
        .sub-title {
            text-align: center;
            color: #4b5563;
            font-size: 1.15rem;
            margin-bottom: 40px;
            font-weight: 500;
        }
        
        /* Beautiful Buttons */
        div.stButton > button {
            width: 100%;
            border-radius: 12px;
            border: 1px solid rgba(10, 59, 124, 0.2);
            background: #ffffff;
            color: #0A3B7C !important;
            font-weight: 600;
            padding: 15px 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            white-space: pre-wrap; /* Allows long text to wrap beautifully */
            height: auto;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(243, 146, 0, 0.2);
            border-color: #F39200;
            color: #F39200 !important;
            background: white;
        }
        
        /* Chat Input Styling */
        .stChatFloatingInputContainer {
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
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
                st.error(f"Translation failed for {model}: {e}")
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
    ui_title = "Nepal Corporate Law AI 🇳🇵"
    ui_subtitle = "Your intelligent legal companion for Nepal's Corporate Sector"
    sidebar_title = "Corporate Law AI"
    sidebar_desc = "Instantly navigate through **1,865 provisions** from BAFIA, NRB Act, Banking Offence Act, AML Act, Labor Act, and NRB Unified Directives. Get precise, AI-powered insights with exact legal citations to ensure compliance and mitigate risks."
    btn_clear = "🧹 Clear Chat History"
    ph_input = "Ask your legal question..."
    msg_welcome = "**Hello!** I am your AI Assistant for Nepal's Corporate & Banking Laws.

You can ask me any legal question related to **BAFIA**, **NRB Act**, **Banking Offence Act**, **Anti-Money Laundering Act**, **Labor Act**, or **NRB Directives**. I will provide you with accurate answers including official legal citations. How can I help you today?"
    sugg_heading = "💡 **Logical & Complex Questions (Suggested):**"
    sugg_q1 = "Can a person convicted of a banking offense become a bank director? Answer based on BAFIA and the Banking Offence and Punishment Act."
    sugg_q2 = "What action is taken under the Labor Act if an employee's remuneration is not paid, and does it fall under money laundering?"
    sugg_q3 = "Under what circumstances can Nepal Rastra Bank take control of the management of any bank (BAFIA)?"
    sugg_q4 = "What is the liquidation process of a Bank/Financial Institution, and how is the priority of debt recovery determined under BAFIA?"
else:
        ui_title = "नेपाल कर्पोरेट कानुन AI 🇳🇵"
        ui_subtitle = "तपाईंको भरपर्दो कानुनी सल्लाहकार (Corporate Law Assistant)"
        sidebar_title = "कानुन च्याटबट"
        sidebar_desc = "Pinecone Vector Database मा रहेका **१८६५ कानुनी दफाहरू** (BAFIA, राष्ट्र बैंक ऐन, बैंकिङ कसूर ऐन, सम्पत्ति शुद्धीकरण निवारण ऐन, श्रम ऐन र राष्ट्र बैंक एकिकृत निर्देशनहरू) पढेर सटिक उत्तर दिने AI।"
        btn_clear = "🧹 कुराकानी मेट्नुहोस् (Clear Chat)"
        ph_input = "कानुनसम्बन्धी आफ्नो प्रश्न सोध्नुहोस्..."
        msg_welcome = "**नमस्ते!** म नेपालको कर्पोरेट तथा बैंकिङ कानुनसम्बन्धी AI Assistant हुँ।

मलाई **बैंक तथा वित्तीय संस्था ऐन (BAFIA)**, **नेपाल राष्ट्र बैंक ऐन**, **बैंकिङ कसूर ऐन**, **सम्पत्ति शुद्धीकरण निवारण ऐन**, **श्रम ऐन**, वा **नेपाल राष्ट्र बैंक एकिकृत निर्देशनहरू** सँग सम्बन्धित कुनै पनि कानुनी प्रश्न सोध्न सक्नुहुन्छ। म तपाईंलाई आधिकारिक कानुनी दफाहरू सहित सटिक उत्तर दिनेछु। म कसरी सहयोग गरौं?"
        sugg_heading = "💡 **जटिल र लजिकल प्रश्नहरू (Suggested):**"
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
            "**Hello!** I am your AI Assistant for Nepal's Corporate & Banking Laws.

You can ask me any legal question related to **BAFIA**, **NRB Act**, **Banking Offence Act**, **Anti-Money Laundering Act**, **Labor Act**, or **NRB Directives**. I will provide you with accurate answers including official legal citations. How can I help you today?"
            if new_lang == "English"
            else "**नमस्ते!** म नेपालको कर्पोरेट तथा बैंकिङ कानुनसम्बन्धी AI Assistant हुँ।

मलाई **बैंक तथा वित्तीय संस्था ऐन (BAFIA)**, **नेपाल राष्ट्र बैंक ऐन**, **बैंकिङ कसूर ऐन**, **सम्पत्ति शुद्धीकरण निवारण ऐन**, **श्रम ऐन**, वा **नेपाल राष्ट्र बैंक एकिकृत निर्देशनहरू** सँग सम्बन्धित कुनै पनि कानुनी प्रश्न सोध्न सक्नुहुन्छ। म तपाईंलाई आधिकारिक कानुनी दफाहरू सहित सटिक उत्तर दिनेछु। म कसरी सहयोग गरौं?"
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
st.markdown(sugg_heading)

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
                response_placeholder.error(f"⚠️ Pinecone Database मा खोज्दा समस्या आयो: {e}")
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
                # Combine match and score into a tuple, sort by score descending, take top 7
                scored_matches = sorted(zip(match_list, scores), key=lambda x: x[1], reverse=True)[:7]
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
3. Use bullet points for readability where appropriate.
4. DYNAMIC FOLLOW-UP SUGGESTIONS: At the very end of your response, you MUST generate exactly 3 logical, relevant follow-up questions that the user might want to ask next based on your response and the context. Format them on a new line at the end of your response exactly like this:
[Suggestions: Question 1? || Question 2? || Question 3?]
The suggestions must be in the same language as your response (English or Nepali). Do not include any other text inside the brackets.

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
                        st.error(f"Generation failed for {model}: {e}")
                        continue

            if not success:
                st.error("Claude API ले उत्तर दिन सकेन। कृपया आफ्नो API Key वा Credit चेक गर्नुहोस्।")

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
