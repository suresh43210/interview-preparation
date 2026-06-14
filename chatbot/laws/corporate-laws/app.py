import os
import streamlit as st
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer, CrossEncoder
from dotenv import load_dotenv
import anthropic
from google import genai
import database

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
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1E3A8A;
            text-align: center;
            margin-bottom: 0px;
            font-family: 'Inter', sans-serif;
        }
        .sub-title {
            text-align: center;
            color: #6B7280;
            font-size: 1.1rem;
            margin-bottom: 30px;
        }
        div.stButton > button {
            width: 100%;
            border-radius: 10px;
            border: 1px solid #E5E7EB;
            background-color: #F9FAFB;
            color: #374151;
            transition: all 0.2s ease;
        }
        div.stButton > button:hover {
            border-color: #3B82F6;
            background-color: #EFF6FF;
            color: #1D4ED8;
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
    
    # Pinecone
    pc_key = os.environ.get("PINECONE_API_KEY")
    pc = Pinecone(api_key=pc_key)
    index = pc.Index("nepal-corporate-laws")
    
    # Anthropic
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    claude_client = anthropic.Anthropic(api_key=anthropic_key) if anthropic_key else None
    
    # Gemini
    gemini_key = os.environ.get("GEMINI_API_KEY")
    gemini_client = genai.Client(api_key=gemini_key) if gemini_key else None
    
    # Init Sentence Transformer
    embedder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    
    # Init CrossEncoder for Reranking
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    return index, claude_client, gemini_client, embedder, reranker

try:
    index, claude_client, gemini_client, embedder, reranker = load_models()
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
    anthropic_models = ["claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"]
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
                if "not_found_error" in str(e):
                    continue
                break
    
    # Fallback to Gemini
    if not text_response and gemini_client:
        try:
            trans_response = gemini_client.models.generate_content(
                model='gemini-2.5-flash', contents=translation_prompt
            )
            text_response = trans_response.text.strip()
        except Exception:
            pass
            
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
# Session State
# -------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "**नमस्ते!** म नेपालको कर्पोरेट कानुनसम्बन्धी (Corporate Law) AI Assistant हुँ।\n\nमलाई **बैंक तथा वित्तीय संस्था (BAFIA)**, **कम्पनी ऐन**, **श्रम ऐन**, वा **बिमा ऐन** सँग सम्बन्धित कुनै पनि कानुनी प्रश्न सोध्न सक्नुहुन्छ। म तपाईंलाई आधिकारिक कानुनी दफाहरू सहित सटिक उत्तर दिनेछु। म कसरी सहयोग गरौं?",
        "sources": []
    })

# -------------------------------------------------------------------
# Sidebar
# -------------------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6033/6033333.png", width=80)
    st.title("कानुन च्याटबट")
    st.markdown("Pinecone Vector Database मा रहेका **१८६५ कानुनी दफाहरू** पढेर सटिक उत्तर दिने AI।")
    st.divider()
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
    st.divider()
    st.caption("Powered by: **Claude 3.5 Sonnet** (Primary) & **Gemini** (Fallback)")

# -------------------------------------------------------------------
# Main UI
# -------------------------------------------------------------------
st.markdown("<div class='main-title'>नेपाल कर्पोरेट कानुन AI 🇳🇵</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>तपाईंको भरपर्दो कानुनी सल्लाहकार (Corporate Law Assistant)</div>", unsafe_allow_html=True)

for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📚 कानुनी स्रोतहरू (Legal Sources)"):
                seen = set()
                for src in message["sources"]:
                    key = f"{src['act']}-{src['section']}"
                    if key not in seen:
                        seen.add(key)
                        st.markdown(f"**{src['act']} ({src['section']})**")
                        st.caption(f"{src['text'][:150]}...")

if len(st.session_state.messages) == 1:
    st.markdown("💡 **प्राय: सोधिने प्रश्नहरू (Suggested):**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("लघुवित्त खोल्न कति चुक्ता पुँजी चाहिन्छ?"):
            st.session_state.suggested_prompt = "लघुवित्त खोल्न कति चुक्ता पुँजी चाहिन्छ?"
            st.rerun()
        if st.button("श्रम ऐन अनुसार महिला सुत्केरी बिदा कति दिन पाइन्छ?"):
            st.session_state.suggested_prompt = "श्रम ऐन अनुसार महिला सुत्केरी बिदा कति दिन पाइन्छ?"
            st.rerun()
    with col2:
        if st.button("कर्मचारीलाई कस्तो अवस्थामा जागिरबाट हटाउन सकिन्छ?"):
            st.session_state.suggested_prompt = "कर्मचारीलाई कस्तो अवस्थामा जागिरबाट हटाउन सकिन्छ?"
            st.rerun()
        if st.button("कम्पनी दर्ता गर्दा के के कागजात चाहिन्छ?"):
            st.session_state.suggested_prompt = "कम्पनी दर्ता गर्दा के के कागजात चाहिन्छ?"
            st.rerun()

prompt = st.chat_input("कानुनसम्बन्धी आफ्नो प्रश्न सोध्नुहोस्...")
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
                    # Trim assistant content so prompt doesn't get too large
                    content_preview = m['content'][:200].replace('\n', ' ')
                    history_text += f"{role_name}: {content_preview}\n"
                    
            english_query, nepali_query = translate_query(prompt, history=history_text)
            
            en_vector = embedder.encode(english_query).tolist()
            np_vector = embedder.encode(nepali_query).tolist()
            
            try:
                # Fetch top 10 for better recall before reranking
                res_en = index.query(vector=en_vector, top_k=10, include_metadata=True)
                res_np = index.query(vector=np_vector, top_k=10, include_metadata=True)
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
                # Combine match and score into a tuple, sort by score descending, take top 3
                scored_matches = sorted(zip(match_list, scores), key=lambda x: x[1], reverse=True)[:3]
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

FORMATTING RULES:
1. You MUST explicitly mention the Act Name and Section number (from the context) that your answer is based on.
2. Use bullet points for readability where appropriate.

[Context Start]
{full_context}
[Context End]

Question: {prompt}"""

        with st.spinner("✍️ आधिकारिक उत्तर तयार गर्दै (Claude)..."):
            full_response = ""
            success = False
            
            # 1. Try Anthropic
            if claude_client:
                anthropic_models = ["claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620", "claude-3-haiku-20240307"]
                for model in anthropic_models:
                    try:
                        with claude_client.messages.stream(
                            model=model, max_tokens=2048, messages=[{"role": "user", "content": llm_prompt}]
                        ) as stream:
                            for text in stream.text_stream:
                                full_response += text
                                response_placeholder.markdown(full_response + " ▌")
                        success = True
                        break
                    except Exception as e:
                        if "not_found_error" in str(e):
                            continue # try next model
                        else:
                            st.warning(f"Anthropic API Error: {e}")
                            break # Fallback to gemini

            # 2. Try Gemini Fallback
            if not success and gemini_client:
                try:
                    response_stream = gemini_client.models.generate_content_stream(
                        model='gemini-2.5-flash', contents=llm_prompt
                    )
                    for chunk in response_stream:
                        if chunk.text:
                            full_response += chunk.text
                            response_placeholder.markdown(full_response + " ▌")
                    success = True
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        response_placeholder.error("⏳ **Limit Reached:** गुगलको नि:शुल्क एकाउन्टमा लिमिट पुग्यो। कृपया १ मिनेट पर्खेर फेरि सोध्नुहोला!")
                    else:
                        response_placeholder.error(f"⚠️ Gemini API Error: {e}")
                    success = False
            
            if not success:
                st.warning("कुनै पनि AI मोडलले उत्तर दिन सकेन। कृपया १ मिनेट पर्खनुहोस् वा API Key चेक गर्नुहोस्।")

        if success:
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
            used_model = "Anthropic (Claude)" if "claude" in str(success) else "Gemini" 
            # wait, 'success' is just a boolean. Let's just say we don't know exactly which model unless we track it.
            # We can use a simple check.
            database.log_interaction(prompt, full_response, source_metadata, "LLM")
