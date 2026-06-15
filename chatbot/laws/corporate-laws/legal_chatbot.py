import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# Use the NEW official Google GenAI SDK
from google import genai

# Initialize rich console for nice UI
console = Console()

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

INDEX_NAME = "nepal-corporate-laws"

def main():
    console.print(Panel.fit("🇳🇵 [bold green]Nepal Corporate Law AI Chatbot[/bold green] 🇳🇵\nInitializing Brain... Please wait.", border_style="green"))

    # 1. Initialize Pinecone
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(INDEX_NAME)
    except Exception as e:
        console.print(f"[bold red]Pinecone Error:[/bold red] {e}")
        return

    # 2. Initialize Gemini (using the NEW SDK)
    if not GEMINI_API_KEY:
        console.print("[bold red]Error: GEMINI_API_KEY not found in .env![/bold red]")
        return
        
    try:
        # Initialize the new genai Client
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        console.print(f"[bold red]Gemini Client Error:[/bold red] {e}")
        return

    # 3. Load Embedding Model
    with console.status("[bold cyan]Loading Language Model (Multilingual)...[/bold cyan]", spinner="dots"):
        embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    
    console.print("[bold green]✅ System Ready![/bold green] (Type 'exit' or 'quit' to stop)\n")

    # 4. Chat Loop
    while True:
        try:
            query = console.input("\n[bold yellow]तपाईंको प्रश्न सोध्नुहोस्:[/bold yellow] ")
            if query.lower() in ['exit', 'quit', 'बाहिर']:
                console.print("[bold green]धन्यवाद! फेरि भेटौंला।[/bold green]")
                break
            if not query.strip():
                continue

            with console.status("[bold cyan]कानुनका किताबहरू पल्टाउँदै...[/bold cyan]", spinner="dots"):
                # Embed query
                query_vector = embedding_model.encode(query).tolist()

                # Search Pinecone
                search_results = index.query(
                    vector=query_vector,
                    top_k=4,
                    include_metadata=True
                )

                # Extract context
                contexts = []
                sources = []
                for match in search_results.matches:
                    meta = match.metadata
                    act_name = meta.get("Act Name", "Unknown Act")
                    section = meta.get("Section", "")
                    text = meta.get("text", "")
                    score = match.score
                    
                    if score > 0.3:
                        context_str = f"Source: {act_name} - {section}\nText: {text}"
                        contexts.append(context_str)
                        clean_section = str(section).replace("**", "") if section else ""
                        sources.append(f"{act_name} ({clean_section})")

                if not contexts:
                    console.print("[bold red]माफ गर्नुहोला, यो प्रश्नसँग सम्बन्धित कुनै कानुनी दफा भेटिएन।[/bold red]")
                    continue

                full_context = "\n\n---\n\n".join(contexts)
                
                # Construct Prompt
                prompt = f"""तपाईं नेपालको कर्पोरेट कानुन (Nepal Corporate Laws) को विशेषज्ञ AI हुनुहुन्छ। 
तल दिइएको कानुनी सन्दर्भ (Context) पढेर सोधिएको प्रश्नको उत्तर नेपालीमा दिनुहोस्। 
कुन ऐन र दफा हो भनेर पनि खुलाउनुहोस्।

[सन्दर्भ सुरु]
{full_context}
[सन्दर्भ अन्त्य]

प्रश्न: {query}"""

            with console.status("[bold cyan]उत्तर तयार गर्दै...[/bold cyan]", spinner="dots"):
                # Use the new API to generate content with gemini-2.5-flash
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                
            # Print Output nicely
            console.print("\n[bold cyan]🤖 उत्तर:[/bold cyan]")
            console.print(Markdown(response.text))
            
            # Print Sources
            unique_sources = list(set(sources))
            console.print(f"\n[italic gray]स्रोत (Sources): {', '.join(unique_sources)}[/italic gray]")
            console.print("━" * 60)

        except KeyboardInterrupt:
            console.print("\n[bold green]धन्यवाद! फेरि भेटौंला।[/bold green]")
            break
        except Exception as e:
            console.print(f"[bold red]Gemini API Error:[/bold red] {e}")

if __name__ == "__main__":
    main()
