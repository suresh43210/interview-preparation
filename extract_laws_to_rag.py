import os
import sys
import json
import asyncio
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Pre-compiled high-quality compliance database fallback (based on real Nepal corporate laws)
# Used if LLAMA_CLOUD_API_KEY is not set or LlamaParse fails.
FALLBACK_DATABASE = {
  "chunks": [
    # BAFIA chunks
    {
      "id": "bafia_chunk_0",
      "doc": "bank_and_financial_institutions_act_2073",
      "doc_title": "Bank & Financial Institutions Act (BAFIA), 2073",
      "section": "Chapter 1: Preliminary & Objectives",
      "content": "The Bank and Financial Institutions Act (BAFIA), 2073 (2017) is the primary governing legislation for BFIs in Nepal. Enacted to amend and consolidate laws relating to bank operations, BAFIA aims to promote public confidence in the banking system, protect depositors' interests, ensure healthy competition, and preserve national financial stability.",
      "entities": ["BAFIA", "Class A BFI", "Siddhartha Bank"]
    },
    {
      "id": "bafia_chunk_1",
      "doc": "bank_and_financial_institutions_act_2073",
      "doc_title": "Bank & Financial Institutions Act (BAFIA), 2073",
      "section": "Section 37: BFI Classifications & Capital Requirements",
      "content": "Under Section 37 of BAFIA, financial institutions in Nepal are classified into four classes based on capital requirements and authorized activities:\n1. Class A: Commercial Banks (e.g. Siddhartha Bank Limited). Minimum paid-up capital required is NRs. 8 Billion.\n2. Class B: Development Banks. Minimum capital required is NRs. 2.5 Billion (national level).\n3. Class C: Finance Companies. Minimum capital required is NRs. 800 Million.\n4. Class D: Microfinance Financial Institutions. Minimum capital required is NRs. 100 Million.",
      "entities": ["BAFIA", "Class A BFI", "Class B BFI", "Class C BFI", "Class D BFI"]
    },
    {
      "id": "bafia_chunk_2",
      "doc": "bank_and_financial_institutions_act_2073",
      "doc_title": "Bank & Financial Institutions Act (BAFIA), 2073",
      "section": "Section 14-22: Board of Directors & Governance",
      "content": "The Board of Directors (BOD) of a licensed BFI must consist of not less than 5 and not more than 7 members. Directors are elected by the General Meeting. At least one Independent Director must be appointed from the approved roster maintained by Nepal Rastra Bank. The tenure of a director is 4 years and they are eligible for re-appointment.",
      "entities": ["BAFIA", "Board of Directors"]
    },
    {
      "id": "bafia_chunk_3",
      "doc": "bank_and_financial_institutions_act_2073",
      "doc_title": "Bank & Financial Institutions Act (BAFIA), 2073",
      "section": "Section 29: Appointment & Tenure of CEO",
      "content": "The Board of Directors appoints a Chief Executive Officer (CEO) to manage the bank's operations. The term of office of the CEO is 4 years. The CEO may be re-appointed for one additional term. Under BAFIA, the maximum age limit for a BFI CEO is 65 years. A CEO cannot continue in office after attaining 65 years of age.",
      "entities": ["BAFIA", "CEO"]
    },
    {
      "id": "bafia_chunk_4",
      "doc": "bank_and_financial_institutions_act_2073",
      "doc_title": "Bank & Financial Institutions Act (BAFIA), 2073",
      "section": "Section 50: Prohibited Banking Operations",
      "content": "Licensed BFIs are strictly prohibited from engaging in the following activities to ensure depositor protection:\n- Purchasing their own shares or lending against their own shares.\n- Engaging in direct trade of goods or carrying out commercial business (except recovery of collateral).\n- Purchasing real estate or land, except for their own administrative offices or collateral recovery.\n- Advancing loans to Directors, promoters, substantial shareholders, or their family members.",
      "entities": ["BAFIA", "Board of Directors", "CEO"]
    },
    
    # NRB Act Chunks
    {
      "id": "nrb_act_chunk_0",
      "doc": "nepal_rastra_bank_act_2058",
      "doc_title": "Nepal Rastra Bank Act, 2058",
      "section": "Section 4: Objectives of the Central Bank",
      "content": "Nepal Rastra Bank (NRB) is the central bank of Nepal established under the NRB Act, 2058. Section 4 defines its main objectives:\n- Price Stability: Formulate and implement monetary and foreign exchange policies to maintain price stability and control inflation.\n- Balance of Payments (BOP): Maintain stability of the balance of payments and manage foreign exchange reserves.\n- Financial Stability: Ensure a healthy, secure, and efficient banking and payment system to promote public confidence.",
      "entities": ["NRB Act", "Check Bounce", "STR", "TTR"]
    },
    {
      "id": "nrb_act_chunk_1",
      "doc": "nepal_rastra_bank_act_2058",
      "doc_title": "Nepal Rastra Bank Act, 2058",
      "section": "Section 79-84: Regulatory & Supervisory Powers",
      "content": "Nepal Rastra Bank has the absolute power to regulate, inspect, and supervise all licensed banks and financial institutions in Nepal. Under Section 79, NRB issues binding Unified Directives and circulars. Under Section 84, NRB can conduct on-site and off-site inspections without notice, suspend operations, fine directors, freeze bank accounts, or take over BFI management.",
      "entities": ["NRB Act", "Board of Directors", "NPL", "STR", "TTR"]
    },
    {
      "id": "nrb_act_chunk_2",
      "doc": "nepal_rastra_bank_act_2058",
      "doc_title": "Nepal Rastra Bank Act, 2058",
      "section": "Section 14: Governor Appointment & Board Structure",
      "content": "The Governor of NRB is appointed by the Government of Nepal for a term of 5 years. The Governor acts as the Chairman of the Board of Directors of NRB. The Board consists of the Governor, Secretary of Ministry of Finance, two Deputy Governors, and three directors appointed from banking, economic, or legal experts.",
      "entities": ["NRB Act", "Board of Directors"]
    },

    # Labor Act Chunks
    {
      "id": "labor_act_chunk_0",
      "doc": "labor_act_2074",
      "doc_title": "Nepal Labor Act, 2074",
      "section": "Section 28-30: Working Hours & Overtime",
      "content": "The Labor Act, 2074 governs the terms of employment, working hours, benefits, safety, and employee relations in Nepal, including the banking sector. Under Section 28, standard working hours are a maximum of 8 hours per day and 40 hours per week. A rest interval of 30 minutes must be provided after 5 continuous working hours. Overtime is limited to a maximum of 4 hours per day and 24 hours per week, paid at 1.5 times the basic hourly wage.",
      "entities": ["Labor Act"]
    },
    {
      "id": "labor_act_chunk_1",
      "doc": "labor_act_2074",
      "doc_title": "Nepal Labor Act, 2074",
      "section": "Section 40-45: Leave Entitlements for Employees",
      "content": "Employees are legally entitled to the following leave types:\n- Weekly Off: 1 day off per week.\n- Public Holidays: 13 days per year (14 days for female employees).\n- Home Leave: 1 day of leave for every 20 days worked (accumulable up to 90 days).\n- Sick Leave: 12 days per year with full pay (accumulable up to 45 days).\n- Maternity Leave: 98 days total (14 weeks), of which 60 days must be fully paid.\n- Paternity Leave: 15 days with full pay.\n- Mourning Leave: 13 days with full pay.",
      "entities": ["Labor Act"]
    },
    {
      "id": "labor_act_chunk_2",
      "doc": "labor_act_2074",
      "doc_title": "Nepal Labor Act, 2074",
      "section": "Section 52-55: Provident Fund, Gratuity & Insurances",
      "content": "The Labor Act mandates key social security benefits:\n- Provident Fund: Minimum of 10% of basic salary from the employee, matched by 10% from the employer, deposited in Social Security Fund (SSF) or CIT.\n- Gratuity: 8.33% of basic salary deposited monthly into the SSF.\n- Accident Insurance: Minimum coverage of NRs. 700,000 premium paid by employer.\n- Medical Insurance: Minimum coverage of NRs. 100,000 premium paid by employer.",
      "entities": ["Labor Act"]
    },

    # Banking Offence Act Chunks
    {
      "id": "banking_offence_chunk_0",
      "doc": "banking_offence_and_punishment_act_2064",
      "doc_title": "Banking Offence & Punishment Act, 2064",
      "section": "Section 3 & 7: Check Bounce Offence",
      "content": "The Banking Offence and Punishment Act, 2064 governs crimes in banking. Under Section 7, check bounce is defined as drawing a check on a BFI knowing there are insufficient funds or deliberately blocking payment. If a check bounces, the offender faces: repayment of the check amount to the victim, a fine equivalent to the check amount, and imprisonment for up to 3 months.",
      "entities": ["Banking Offence", "Check Bounce"]
    },
    {
      "id": "banking_offence_chunk_1",
      "doc": "banking_offence_and_punishment_act_2064",
      "doc_title": "Banking Offence & Punishment Act, 2064",
      "section": "Section 15: Collateral Valuation Fraud & Loan Misuse",
      "content": "Section 15 defines collateral valuation fraud as inflating property value to obtain a higher loan than the collateral warrants. Loan misuse is defined as using loan funds for purposes other than what was approved in the credit agreement. Punishment includes recovery of the loan, a fine equivalent to the loan value, and imprisonment from 1 to 5 years depending on the fraud amount.",
      "entities": ["Banking Offence", "CEO", "Board of Directors"]
    },
    {
      "id": "banking_offence_chunk_2",
      "doc": "banking_offence_and_punishment_act_2064",
      "doc_title": "Banking Offence & Punishment Act, 2064",
      "section": "Section 17: Double Liability for BFI Staff",
      "content": "Under Section 17, if any bank director, CEO, officer, teller, or employee is found colluding, facilitating, or directly committing any banking offence (such as loan fraud, hacking CBS, or card cloning), they are subject to double the standard punishment. The BFI must immediately terminate their employment and place them on the banking blacklist.",
      "entities": ["Banking Offence", "CEO", "Board of Directors"]
    },

    # AML/CFT Act Chunks
    {
      "id": "aml_chunk_0",
      "doc": "anti_money_laundering_act_2064",
      "doc_title": "Anti-Money Laundering Act, 2064",
      "section": "Section 7: Customer Due Diligence (KYC)",
      "content": "The Asset (Money) Laundering Prevention Act, 2064 governs money laundering in Nepal. Section 7 mandates strict Customer Due Diligence (CDD) and KYC (Know Your Customer) rules. Banks must verify customer identity using citizenship certificates or passports, trace ultimate beneficial owners, and obtain senior management approval for Politically Exposed Persons (PEPs) with enhanced transaction monitoring.",
      "entities": ["AML/CFT", "CEO", "Board of Directors"]
    },
    {
      "id": "aml_chunk_1",
      "doc": "anti_money_laundering_act_2064",
      "doc_title": "Anti-Money Laundering Act, 2064",
      "section": "Reporting Duties: TTR and STR Reports",
      "content": "Banks must report suspicious and threshold transactions to the Financial Information Unit (FIU) of NRB:\n- Threshold Transaction Report (TTR): Cash transactions of NRs. 10 Lakhs (1 Million) or above in a single day must be reported to the FIU within 15 days.\n- Suspicious Transaction Report (STR): Any transaction suspected to be proceeds of crime or linked to terrorism must be reported to the FIU within 3 days. There is no minimum monetary limit for STR reporting.",
      "entities": ["AML/CFT", "STR", "TTR"]
    },
    {
      "id": "aml_chunk_2",
      "doc": "anti_money_laundering_act_2064",
      "doc_title": "Anti-Money Laundering Act, 2064",
      "section": "Section 32: Non-Compliance Penalties",
      "content": "Under the AML/CFT Act, if a BFI fails to maintain records, verify KYC, or file STR/TTR reports, the regulatory body (NRB) can fine the bank up to NRs. 10 Million. Employees colluding or failing compliance duties face criminal prosecution, fines, and imprisonment.",
      "entities": ["AML/CFT", "STR", "TTR"]
    },
    
    # Unified Directives Chunks
    {
      "id": "directives_chunk_0",
      "doc": "nrb_directives",
      "doc_title": "NRB Unified Directives",
      "section": "Directive 1: Capital Adequacy Framework (CAR)",
      "content": "Under Directive 1 of NRB Unified Directives, commercial banks must maintain minimum capital to cover risk-weighted assets:\n- Core Capital (Tier 1): Minimum 8.5% of total Risk-Weighted Assets (RWA).\n- Capital Adequacy Ratio (CAR) / Total Capital: Minimum 11.0% of total RWA. Failure to meet these ratios triggers Prompt Corrective Action (PCA) by NRB.",
      "entities": ["NRB Act", "BAFIA"]
    },
    {
      "id": "directives_chunk_1",
      "doc": "nrb_directives",
      "doc_title": "NRB Unified Directives",
      "section": "Directive 2: Credit Classification & Provisioning",
      "content": "Directive 2 compiles the rules for classifying loans and maintaining provisions against potential loan losses:\n- Performing Loans:\n  - Pass Loan: Overdue by 0 to 1 month. Provision required: 1.1% general reserve.\n  - Watchlist: Overdue by 1 to 3 months, or showing operational distress. Provision required: 5% general reserve.\n- Non-Performing Loans (NPL):\n  - Substandard: Overdue by 3 to 6 months. Provision required: 25% specific reserve.\n  - Doubtful: Overdue by 6 to 12 months. Provision required: 50% specific reserve.\n  - Loss: Overdue by more than 12 months, or client bankrupt. Provision required: 100% specific reserve.",
      "entities": ["NRB Act", "NPL"]
    },
    {
      "id": "directives_chunk_2",
      "doc": "nrb_directives",
      "doc_title": "NRB Unified Directives",
      "section": "Directive 6: Corporate Governance & Single Obligor Limit",
      "content": "Directive 6 enforces structural governance rules to prevent conflict of interest. An Audit Committee must be chaired by a non-executive director to oversee internal audit. The Single Obligor Limit restricts a BFI from lending more than 25% of its core capital to a single borrower or business group to mitigate credit risk.",
      "entities": ["NRB Act", "BAFIA", "Board of Directors"]
    }
  ],
  "graph": {
    "nodes": [
      {"id": "BAFIA", "label": "BAFIA 2073", "type": "law", "desc": "Bank & Financial Institutions Act, 2073"},
      {"id": "NRB Act", "label": "NRB Act 2058", "type": "law", "desc": "Nepal Rastra Bank Act, 2058"},
      {"id": "Labor Act", "label": "Labor Act 2074", "type": "law", "desc": "Nepal Labor Act, 2074"},
      {"id": "Banking Offence", "label": "Banking Offence Act 2064", "type": "law", "desc": "Banking Offence and Punishment Act, 2064"},
      {"id": "AML/CFT", "label": "AML/CFT Act 2064", "type": "law", "desc": "Anti-Money Laundering Act, 2064"},
      
      {"id": "CEO", "label": "CEO Term & Age", "type": "governance", "desc": "CEO term limit of 4 years, max age 65 (BAFIA Sec 29)"},
      {"id": "Board of Directors", "label": "Board of Directors", "type": "governance", "desc": "BOD size 5-7 members, tenure 4 years (BAFIA Sec 14-22)"},
      
      {"id": "Class A BFI", "label": "Class A BFI", "type": "category", "desc": "Commercial Banks. Minimum Paid-up Capital: NRs. 8 Billion."},
      {"id": "Class B BFI", "label": "Class B BFI", "type": "category", "desc": "Development Banks. Minimum Capital: NRs. 2.5 Billion."},
      {"id": "Class C BFI", "label": "Class C BFI", "type": "category", "desc": "Finance Companies. Minimum Capital: NRs. 800 Million."},
      {"id": "Class D BFI", "label": "Class D BFI", "type": "category", "desc": "Microfinance BFIs. Minimum Capital: NRs. 100 Million."},
      
      {"id": "Check Bounce", "label": "Check Bounce", "type": "offence", "desc": "Check bounce penalty: fine & jail up to 3 months (BOPA Sec 7)"},
      {"id": "STR", "label": "STR Report", "type": "compliance", "desc": "Suspicious Transaction Report (STR) within 3 days to FIU"},
      {"id": "TTR", "label": "TTR Report", "type": "compliance", "desc": "Threshold Transaction Report (TTR) for >= NRs 10 Lakhs in 15 days"},
      {"id": "NPL", "label": "NPL Classification", "type": "directives", "desc": "Pass (1.1%), Watchlist (5%), Substandard (25%), Doubtful (50%), Loss (100%) provisioning"}
    ],
    "edges": [
      {"source": "BAFIA", "target": "Class A BFI", "relation": "defines"},
      {"source": "BAFIA", "target": "Class B BFI", "relation": "defines"},
      {"source": "BAFIA", "target": "Class C BFI", "relation": "defines"},
      {"source": "BAFIA", "target": "Class D BFI", "relation": "defines"},
      {"source": "BAFIA", "target": "CEO", "relation": "governs"},
      {"source": "BAFIA", "target": "Board of Directors", "relation": "governs"},
      
      {"source": "NRB Act", "target": "BAFIA", "relation": "empowers"},
      {"source": "NRB Act", "target": "NPL", "relation": "authorizes"},
      
      {"source": "Banking Offence", "target": "Check Bounce", "relation": "defines"},
      {"source": "Banking Offence", "target": "CEO", "relation": "holds_liable"},
      {"source": "Banking Offence", "target": "Board of Directors", "relation": "holds_liable"},
      
      {"source": "AML/CFT", "target": "STR", "relation": "requires"},
      {"source": "AML/CFT", "target": "TTR", "relation": "requires"},
      
      {"source": "NRB Act", "target": "STR", "relation": "supervises"},
      {"source": "NRB Act", "target": "TTR", "relation": "supervises"}
    ]
  }
}

async def parse_pdf(file_path, parser):
    print(f"Starting parsing for {file_path} using LlamaParse...")
    try:
        # Load markdown using LlamaParse
        documents = await parser.aload_data(file_path)
        print(f"Finished parsing {file_path}. Extracted {len(documents)} pages/sections.")
        return "\n\n".join([doc.text for doc in documents])
    except Exception as e:
        print(f"Error parsing {file_path} via LlamaParse API: {e}")
        return None

def chunk_markdown(text, doc_name, doc_title):
    # Split text into logical sections by Markdown titles or common legal terms
    lines = text.split("\n")
    chunks = []
    current_chunk = []
    current_section = "General Provisions"
    chunk_idx = 0
    
    # Match section headers, e.g. "Chapter", "Section", "दफा", "परिच्छेद", "##"
    for line in lines:
        stripped = line.strip()
        is_header = False
        if stripped.startswith("#"):
            is_header = True
            current_section = stripped.lstrip("# ").strip()
        elif stripped.lower().startswith("chapter") or stripped.lower().startswith("section"):
            is_header = True
            current_section = stripped
        elif stripped.startswith("दफा") or stripped.startswith("परिच्छेद") or stripped.startswith("अनुसूची"):
            is_header = True
            current_section = stripped

        if is_header and current_chunk:
            chunk_text = "\n".join(current_chunk).strip()
            if chunk_text:
                chunks.append({
                    "id": f"{doc_name}_chunk_{chunk_idx}",
                    "doc": doc_name,
                    "doc_title": doc_title,
                    "section": current_section,
                    "content": chunk_text,
                    "entities": extract_entities_from_text(chunk_text)
                })
                chunk_idx += 1
            current_chunk = []
            
        current_chunk.append(line)
        
    if current_chunk:
        chunk_text = "\n".join(current_chunk).strip()
        if chunk_text:
            chunks.append({
                "id": f"{doc_name}_chunk_{chunk_idx}",
                "doc": doc_name,
                "doc_title": doc_title,
                "section": current_section,
                "content": chunk_text,
                "entities": extract_entities_from_text(chunk_text)
            })
            
    return chunks

def extract_entities_from_text(text):
    keywords = {
        "BAFIA": ["bafia", "bank and financial institutions act", "बैंक तथा वित्तीय संस्था", "section 37", "section 14", "section 29", "section 50"],
        "NRB Act": ["nrb act", "nepal rastra bank", "नेपाल राष्ट्र बैंक", "governor", "section 4", "section 79"],
        "Labor Act": ["labor", "shram ain", "श्रम ऐन", "overtime", "maternity", "sick leave", "provident fund", "gratuity"],
        "Banking Offence": ["banking offence", "banking kasoor", "बैंकिङ्ग कसूर", "check bounce", "cheque bounce", "collateral valuation", "punishment"],
        "AML/CFT": ["aml", "cft", "money laundering", "sampatti suddhikaran", "सम्पत्ति शुद्धीकरण", "str", "ttr", "fiu"],
        "CEO": ["ceo", "chief executive", "प्रमुख कार्यकारी"],
        "Board of Directors": ["board of directors", "director", "संचालक समिति", "bod"],
        "Class A BFI": ["class a", "commercial bank", "वाणिज्य बैंक"],
        "Class B BFI": ["class b", "development bank", "विकास बैंक"],
        "Class C BFI": ["class c", "finance company", "वित्त कम्पनी"],
        "Class D BFI": ["class d", "microfinance", "लघुवित्त"],
        "Check Bounce": ["check bounce", "cheque bounce", "चेक बाउन्स"],
        "STR": ["str", "suspicious transaction", "शंकास्पद कारोबार"],
        "TTR": ["ttr", "threshold transaction", "सीमा कारोबार"],
        "NPL": ["npl", "non-performing loan", "निष्क्रिय कर्जा", "provisioning", "pass loan", "watchlist", "substandard", "doubtful", "loss"]
    }
    
    found_entities = []
    text_lower = text.lower()
    for entity, kw_list in keywords.items():
        for kw in kw_list:
            if kw in text_lower:
                found_entities.append(entity)
                break
    return found_entities

async def main():
    api_key = os.environ.get("LLAMA_CLOUD_API_KEY")
    output_path = "chatbot/laws_db.json"
    
    if not api_key:
        print("💡 LLAMA_CLOUD_API_KEY is not set. Using pre-compiled high-quality corporate compliance database...")
        # Write pre-compiled fallback directly
        os.makedirs("chatbot", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(FALLBACK_DATABASE, f, indent=2, ensure_ascii=False)
        print(f"✅ Success: Fallback compliance database written to {output_path} with {len(FALLBACK_DATABASE['chunks'])} chunks.")
        return
        
    try:
        from llama_parse import LlamaParse
    except ImportError:
        print("❌ error: llama-parse python library is not installed. Using fallback database...")
        os.makedirs("chatbot", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(FALLBACK_DATABASE, f, indent=2, ensure_ascii=False)
        print(f"✅ Success: Fallback compliance database written to {output_path}.")
        return

    print("🔑 LlamaParse API Key detected. Initializing parser...")
    parser = LlamaParse(
        api_key=api_key,
        result_type="markdown",
        verbose=True
    )
    
    docs_to_parse = [
        {
            "name": "nepal_rastra_bank_act_2058",
            "title": "Nepal Rastra Bank Act, 2058",
            "file": "chatbot/laws/corporate-laws/nepal_rastra_bank_act_2058.pdf"
        },
        {
            "name": "bank_and_financial_institutions_act_2073",
            "title": "Bank & Financial Institutions Act (BAFIA), 2073",
            "file": "chatbot/laws/corporate-laws/bank_and_financial_institutions_act_2073.pdf"
        },
        {
            "name": "anti_money_laundering_act_2064",
            "title": "Anti-Money Laundering Act, 2064",
            "file": "chatbot/laws/corporate-laws/anti_money_laundering_act_2064.pdf"
        },
        {
            "name": "labor_act_2074",
            "title": "Nepal Labor Act, 2074",
            "file": "chatbot/laws/corporate-laws/labor_act_2074.pdf"
        },
        {
            "name": "banking_offence_and_punishment_act_2064",
            "title": "Banking Offence & Punishment Act, 2064",
            "file": "chatbot/laws/corporate-laws/banking_offence_and_punishment_act_2064.pdf"
        }
    ]
    
    all_chunks = []
    tasks = []
    valid_docs = []
    
    for doc in docs_to_parse:
        if os.path.exists(doc["file"]):
            tasks.append(parse_pdf(doc["file"], parser))
            valid_docs.append(doc)
        else:
            print(f"⚠️ File {doc['file']} not found. Skipping.")
            
    if not tasks:
        print("❌ No files found to parse. Using fallback database...")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(FALLBACK_DATABASE, f, indent=2, ensure_ascii=False)
        print(f"✅ Success: Fallback database written to {output_path}.")
        return
        
    print(f"⚡ Starting parallel parsing of {len(tasks)} files...")
    results = await asyncio.gather(*tasks)
    
    for idx, doc in enumerate(valid_docs):
        markdown_text = results[idx]
        if markdown_text:
            chunks = chunk_markdown(markdown_text, doc["name"], doc["title"])
            all_chunks.extend(chunks)
            print(f"📝 Generated {len(chunks)} chunks for {doc['title']}.")
        else:
            print(f"⚠️ Failed to parse {doc['title']}, adding fallback chunks for this document...")
            # Inject fallback chunks for this specific document if LlamaParse failed
            fb_chunks = [c for c in FALLBACK_DATABASE["chunks"] if c["doc"] == doc["name"]]
            all_chunks.extend(fb_chunks)

    # Use default nodes and edges (or enrich with parsed topics if necessary)
    database = {
        "chunks": all_chunks if all_chunks else FALLBACK_DATABASE["chunks"],
        "graph": FALLBACK_DATABASE["graph"]
    }
    
    os.makedirs("chatbot", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
        
    print(f"🚀 Success: Graph RAG database compiled to {output_path} with {len(database['chunks'])} chunks.")

if __name__ == "__main__":
    asyncio.run(main())
