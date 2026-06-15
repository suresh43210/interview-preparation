import os
import json

# Langchain बाट आवश्यक Chunking tools हरू तान्ने
# यो चलाउन `pip install langchain-text-splitters` गर्नुहोला
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# फाइलहरू भएको र सेभ गर्ने फोल्डरको लोकेसन
FINAL_DIR = "/Users/sureshneupane/Documents/suresh/antigriavity/interview-preparetion/chatbot/laws/corporate-laws/final"
OUTPUT_DIR = "/Users/sureshneupane/Documents/suresh/antigriavity/interview-preparetion/chatbot/laws/corporate-laws/chunks"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def chunk_legal_document(filename):
    file_path = os.path.join(FINAL_DIR, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        document_text = f.read()

    # ==========================================
    # चरण १: MarkdownHeaderTextSplitter (संरचनात्मक विभाजन)
    # किन? : कानुनी डकुमेन्टलाई दफा र परिच्छेदको आधारमा छुट्याउन। 
    # कसरी? : हामीले क्लिनिङ गर्दा बनाएको Markdown हेडिङ (### र ####) लाई आधार मानेर।
    # यसले गर्दा हरेक Chunk सँग त्यो कुन परिच्छेद र कुन दफाको हो भन्ने Metadata आफैं जोडिन्छ।
    # ==========================================
    headers_to_split_on = [
        ("#", "Act Name"),         # ऐनको नाम (Header 1)
        ("##", "Part"),            # भाग वा खण्ड (Header 2)
        ("###", "Chapter"),        # परिच्छेद (Header 3)
        ("####", "Section")        # दफा (Header 4)
    ]
    
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    
    # यसले डकुमेन्टलाई हेडिङको आधारमा टुक्र्याउँछ र Metadata पनि राख्छ
    md_header_splits = markdown_splitter.split_text(document_text)

    # ==========================================
    # चरण २: RecursiveCharacterTextSplitter (लामो दफालाई टुक्र्याउने)
    # किन? : कुनै कुनै दफाहरू (जस्तै 'परिभाषा' वा लामो नियम) एउटै हेडिङमा भए पनि धेरै लामा हुन्छन् 
    # जसले LLM को Context Limit भर्न सक्छ।
    # कसरी? : यदि कुनै दफा 1000 अक्षरभन्दा लामो छ भने त्यसलाई टुक्र्याउने र अर्थ नबिग्रियोस् 
    # भनेर 200 अक्षरको Overlap (ओभरल्याप) राख्ने।
    # ==========================================
    chunk_size = 1000
    chunk_overlap = 200
    
    # उपदफा (१) र बुँदा (क) को आधारमा ठ्याक्कै टुक्र्याउन Regex Separator प्रयोग गर्ने
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n", 
            "\n(?=\([०-९]+\))", # उपदफा जस्तै: (१), (२) को अगाडि टुक्र्याउने
            "\n(?=\([क-ज्ञ]\))",   # खण्ड/बुँदा जस्तै: (क), (ख) को अगाडि टुक्र्याउने
            "\n", 
            "।", 
            " ", 
            ""
        ],
        is_separator_regex=True # Regex सपोर्ट अन गर्ने
    )
    
    # Markdown बाट निस्किएका Chunks लाई फेरि साइजको आधारमा प्रोसेस गर्ने
    final_chunks = text_splitter.split_documents(md_header_splits)
    
    # नतिजा सेभ गर्ने
    output_data = []
    for i, chunk in enumerate(final_chunks):
        output_data.append({
            "chunk_id": f"{filename}_chunk_{i}",
            "metadata": chunk.metadata,
            "text": chunk.page_content
        })
        
    out_file = os.path.join(OUTPUT_DIR, filename.replace('.md', '_chunks.json'))
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ {filename} को Chunking सफल भयो! जम्मा Chunks: {len(final_chunks)}")


if __name__ == "__main__":
    # Final फोल्डरमा भएका सबै Markdown फाइलहरू पढ्ने
    files = [f for f in os.listdir(FINAL_DIR) if f.endswith('.md')]
    
    print("कानुनी डकुमेन्टहरूको Chunking सुरु हुँदैछ...\n" + "="*40)
    for file in files:
        chunk_legal_document(file)
    print("="*40 + "\n🎉 सबै फाइलहरूको Chunking सम्पन्न भयो!")
