import os
from fpdf import FPDF

# Ensure output directory exists
os.makedirs("chatbot/laws", exist_ok=True)

class LegalDocPDF(FPDF):
    def __init__(self, title, subtitle):
        super().__init__()
        self.doc_title = title
        self.doc_subtitle = subtitle

    def header(self):
        # Maroon top border bar
        self.set_fill_color(139, 26, 26) # Maroon color
        self.rect(0, 0, 210, 15, 'F')
        
        # Gold accent line below header bar
        self.set_fill_color(212, 175, 55) # Gold color
        self.rect(0, 15, 210, 2, 'F')
        
        # Header text
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        self.set_y(4)
        self.cell(0, 5, 'SIDDHARTHA BANK LIMITED  |  COMPLIANCE & REGULATORY AFFAIRS', 0, 0, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-20)
        # Gold line above footer
        self.set_fill_color(212, 175, 55)
        self.rect(20, 275, 170, 0.5, 'F')
        
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}   |   Internal Compliance Guide - BFI Staff Use Only', 0, 0, 'C')

    def add_title_section(self):
        self.add_page()
        self.set_y(25)
        
        # Document title card
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(139, 26, 26) # Maroon
        self.cell(0, 10, self.doc_title, new_x="LMARGIN", new_y="NEXT")
        
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(212, 175, 55) # Gold
        self.cell(0, 6, self.doc_subtitle, new_x="LMARGIN", new_y="NEXT")
        
        # Divider line
        self.set_fill_color(139, 26, 26)
        self.rect(20, 43, 170, 1, 'F')
        self.ln(12)

    def section_header(self, text):
        self.ln(4)
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(139, 26, 26)
        self.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub_section_header(self, text):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(212, 175, 55)
        self.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def bullet_point(self, title, desc):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(60, 60, 60)
        self.write(6, f"  -  {title}: ")
        self.set_font('Helvetica', '', 10)
        self.set_text_color(40, 40, 40)
        self.write(6, f"{desc}\n")
        self.ln(1)


# ==========================================
# 1. BAFIA 2073 PDF
# ==========================================
pdf1 = LegalDocPDF("Bank & Financial Institutions Act (BAFIA), 2073", "Bank tatha Vittiya Sanstha Sambandhi Ain, 2073")
pdf1.alias_nb_pages()
pdf1.add_title_section()

pdf1.section_header("1. Executive Summary")
pdf1.body_text(
    "The Bank and Financial Institutions Act (BAFIA), 2073 is the primary legislative framework governing commercial banks and financial institutions in Nepal. "
    "Enacted to amend and consolidate laws relating to bank operations, BAFIA aims to promote public confidence in the banking system, protect depositors' interests, "
    "ensure healthy competition, and preserve national financial stability."
)

pdf1.section_header("2. Core Classifications of BFIs (Section 37)")
pdf1.body_text("Under BAFIA, financial institutions in Nepal are classified into four main categories based on capital requirements and activities:")
pdf1.bullet_point("Class A", "Commercial Banks - e.g., Siddhartha Bank Limited. Minimum Paid-up Capital: NRs. 8 Billion.")
pdf1.bullet_point("Class B", "Development Banks. Minimum Capital: NRs. 2.5 Billion (National level).")
pdf1.bullet_point("Class C", "Finance Companies. Minimum Capital: NRs. 800 Million.")
pdf1.bullet_point("Class D", "Microfinance Financial Institutions. Minimum Capital: NRs. 100 Million.")

pdf1.section_header("3. Board of Directors & CEO Governance")
pdf1.sub_section_header("Board Qualifications & Composition (Section 14-22):")
pdf1.body_text(
    " - The Board of Directors must consist of not less than 5 and not more than 7 members.\n"
    " - Directors are appointed by the General Meeting, and must include at least one Independent Director appointed from the NRB approved roster.\n"
    " - Tenure of a director is 4 years, and they can be re-appointed."
)
pdf1.sub_section_header("CEO Appointment & Terms (Section 29):")
pdf1.body_text(
    " - The Chief Executive Officer (CEO) is appointed by the Board of Directors for a term of 4 years, and can be re-appointed for one additional term.\n"
    " - The maximum age limit for a BFI CEO is 65 years (they cannot remain in office after reaching 65)."
)

pdf1.section_header("4. Prohibited Activities for BFIs (Section 50)")
pdf1.body_text(
    "Banks are strictly prohibited from engaging in the following activities to ensure depositor protection:\n"
    "1. Purchasing their own shares or lending credit against the security of their own shares.\n"
    "2. Engaging in trading of goods or carrying out commercial business (except for credit recovery).\n"
    "3. Purchasing real estate or land, except for their own administrative offices or collateral recovery.\n"
    "4. Advancing loans to Directors, promoters, major shareholders, or their family members."
)
pdf1.output("chatbot/laws/bafia.pdf")


# ==========================================
# 2. NRB Act 2058 PDF
# ==========================================
pdf2 = LegalDocPDF("Nepal Rastra Bank Act, 2058", "Nepal Rastra Bank Ain, 2058")
pdf2.alias_nb_pages()
pdf2.add_title_section()

pdf2.section_header("1. Executive Summary")
pdf2.body_text(
    "The Nepal Rastra Bank Act, 2058 establishes the Nepal Rastra Bank (NRB) as the central bank of Nepal. "
    "It grants the central bank full autonomy to formulate and implement monetary, foreign exchange, and supervision policy. "
    "The Act serves as the legal foundation for central bank regulation and supervision over all commercial banks and financial institutions."
)

pdf2.section_header("2. Objectives of the Central Bank (Section 4)")
pdf2.body_text("The primary objectives of Nepal Rastra Bank under Section 4 of the Act are:")
pdf2.bullet_point("Price Stability", "Formulate and manage monetary and foreign exchange policies to maintain stable prices and control inflation.")
pdf2.bullet_point("Balance of Payments", "Maintain stability in the balance of payments (BOP) and foreign currency reserves.")
pdf2.bullet_point("Financial System Health", "Promote financial stability, safety, and healthy development of the banking system.")
pdf2.bullet_point("Payment System", "Develop and secure an efficient payment system in Nepal.")

pdf2.section_header("3. Supervisory & Regulatory Mandate (Section 79-84)")
pdf2.body_text(
    "The NRB has the absolute power to regulate, inspect, and supervise licensed commercial banks. This includes:\n"
    " - Inspection: The NRB can conduct on-site and off-site inspections of BFIs without prior notice.\n"
    " - Directives: The NRB can issue binding directives regarding capital, liquidity, loans, and corporate governance.\n"
    " - Corrective Action: If a BFI violates regulations, NRB can suspend operations, fine directors, freeze accounts, or initiate liquidation."
)

pdf2.section_header("4. Key Governance Roles")
pdf2.bullet_point("Governor", "The Governor is appointed by the Government of Nepal for a term of 5 years. They act as the Chairman of the Board of Directors of NRB.")
pdf2.bullet_point("Board Structure", "The Board consists of the Governor, Secretary of Ministry of Finance, two Deputy Governors, and three directors appointed from banking, economic, or legal experts.")
pdf2.output("chatbot/laws/nrb_act.pdf")


# ==========================================
# 3. Labor Act 2074 PDF
# ==========================================
pdf3 = LegalDocPDF("Nepal Labor Act, 2074", "Shram Ain, 2074")
pdf3.alias_nb_pages()
pdf3.add_title_section()

pdf3.section_header("1. Applicability to Banking Sector")
pdf3.body_text(
    "The Labor Act, 2074 governs the terms of employment, working hours, benefits, safety, and employee relations for all entities in Nepal, including commercial banks. "
    "Under this Act, bank employees are classified as workers and are entitled to standard leaves, retirement benefits, and fair working hours."
)

pdf3.section_header("2. Working Hours & Overtime (Section 28-30)")
pdf3.bullet_point("Standard Hours", "Maximum of 8 hours per day, and 40 hours per week.")
pdf3.bullet_point("Rest Interval", "At least 30 minutes rest after 5 continuous hours of work.")
pdf3.bullet_point("Overtime", "Maximum of 4 hours per day, and 24 hours per week. Overtime salary must be paid at 1.5 times the basic hourly wage.")

pdf3.section_header("3. Approved Leaves (Section 40-45)")
pdf3.body_text("Every bank employee is legally entitled to the following leaves:")
pdf3.bullet_point("Weekly Off", "1 day off per week (normally Sunday or Saturday).")
pdf3.bullet_point("Public Holidays", "13 days per year (14 days for female employees including International Women's Day).")
pdf3.bullet_point("Home Leave (Annual)", "1 day of home leave for every 20 days worked (accumulable up to 90 days).")
pdf3.bullet_point("Sick Leave", "12 days per year with full pay (accumulable up to 45 days).")
pdf3.bullet_point("Maternity Leave", "98 days total (14 weeks). 60 days must be fully paid. The remaining 38 days can be unpaid or adjusted against other leaves.")
pdf3.bullet_point("Paternity Leave", "15 days with full pay for male employees.")
pdf3.bullet_point("Mourning Leave", "13 days with full pay.")

pdf3.section_header("4. Compulsory Benefits & Retirals")
pdf3.bullet_point("Provident Fund", "10% of basic salary contributed by the employee, and 10% matched by the Bank (deposited in Social Security Fund or CIT).")
pdf3.bullet_point("Gratuity", "An amount equivalent to 8.33% of the basic salary must be deposited monthly into the Social Security Fund (SSF).")
pdf3.bullet_point("Accident Insurance", "Minimum coverage of NRs. 700,000 premium fully paid by the employer.")
pdf3.bullet_point("Medical Insurance", "Minimum coverage of NRs. 100,000 premium shared or fully paid by the employer.")
pdf3.output("chatbot/laws/labor_act.pdf")


# ==========================================
# 4. Banking Offence Act 2064 PDF
# ==========================================
pdf4 = LegalDocPDF("Banking Offence and Punishment Act, 2064", "Banking Kasoor tatha Sajaya Ain, 2064")
pdf4.alias_nb_pages()
pdf4.add_title_section()

pdf4.section_header("1. Executive Summary")
pdf4.body_text(
    "The Banking Offence and Punishment Act, 2064 defines crimes related to banking and financial transactions in Nepal "
    "and prescribes strict punishments. This Act protects depositors, prevents financial fraud, and ensures security for financial transactions."
)

pdf4.section_header("2. Core Banking Offences Defined")
pdf4.bullet_point("Unauthorized Accounts", "Opening accounts or demanding withdrawals without authorized credentials (Section 3).")
pdf4.bullet_point("Check Bounce (Section 7)", "Issuing checks knowing there is no balance in the account, or deliberately blocking payment. This is a criminal offence.")
pdf4.bullet_point("Collateral Valuation Fraud", "Inflating the value of property or collateral to get a higher loan (Section 15). Crucial for credit officers.")
pdf4.bullet_point("Loan Misuse", "Using loans for purposes other than what was approved in the credit agreement.")
pdf4.bullet_point("Unauthorized Access", "Hacking, modifying, or accessing CBS (Core Banking System) or customer cards illegally.")

pdf4.section_header("3. Punishments and Penalties")
pdf4.sub_section_header("Check Bounce Punishment (Section 7 & 15):")
pdf4.body_text(
    "If a check bounces, the offender faces:\n"
    " - Repayment of the check amount to the victim.\n"
    " - A fine equivalent to the check amount.\n"
    " - Imprisonment for up to 3 months depending on severity."
)
pdf4.sub_section_header("Collateral Valuation & Loan Fraud:")
pdf4.body_text(
    " - Return of the loan amount (claim recovery).\n"
    " - Fines up to the loan value.\n"
    " - Imprisonment from 1 to 5 years depending on the fraud amount."
)

pdf4.section_header("4. Internal Staff Liability")
pdf4.body_text(
    "If any bank employee (director, CEO, officer, teller) is found colluding, facilitating, or directly committing a banking offence, "
    "they are subject to double the standard punishment under Section 17. The bank will also immediately fire them and blacklist them."
)
pdf4.output("chatbot/laws/banking_offence.pdf")


# ==========================================
# 5. AML/CFT Act 2064 PDF
# ==========================================
pdf5 = LegalDocPDF("Anti-Money Laundering Act (ALPA), 2064", "Sampatti Shuddhikarana Nibarana Ain, 2064")
pdf5.alias_nb_pages()
pdf5.add_title_section()

pdf5.section_header("1. Executive Summary")
pdf5.body_text(
    "The Asset (Money) Laundering Prevention Act, 2064 is Nepal's primary framework to combat money laundering and terrorist financing. "
    "It mandates all banks and financial institutions to implement strict Customer Due Diligence (CDD), monitor transactions, "
    "and report suspicious activities to the Financial Information Unit (FIU) of Nepal Rastra Bank."
)

pdf5.section_header("2. Know Your Customer (KYC) & CDD (Section 7)")
pdf5.body_text(
    "Banks must verify client identity before opening any account or providing services:\n"
    " - Customer Verification: Citizenship certificate, passport, official ID, and photos.\n"
    " - Beneficial Ownership: Identify the ultimate natural person controlling the account (beneficial owner).\n"
    " - High-Risk Customers: PEPs (Politically Exposed Persons) require senior management approval and enhanced monitoring."
)

pdf5.section_header("3. Mandatory Reporting Requirements")
pdf5.bullet_point("TTR (Threshold Transaction Report)", "Any single or aggregated cash transaction of NRs. 10 Lakhs (1 Million NPR) or more in a single day must be reported to the FIU within 15 days.")
pdf5.bullet_point("STR (Suspicious Transaction Report)", "If there is reasonable ground to suspect that funds are proceeds of crime or linked to terrorism, the bank must file an STR to the FIU within 3 days. There is NO minimum threshold limit for STR.")

pdf5.section_header("4. Penalties for Compliance Failures")
pdf5.body_text(
    " - If a BFI fails to report STR/TTR or perform KYC, the regulator (NRB) can fine the bank up NRs. 10 Million.\n"
    " - Employees violating compliance can face criminal prosecution, fines, and imprisonment."
)
pdf5.output("chatbot/laws/aml_cft.pdf")


# ==========================================
# 6. NRB Unified Directives PDF
# ==========================================
pdf6 = LegalDocPDF("NRB Unified Directives", "Nepal Rastra Bank Ekikrit Nirdeshanaharoo")
pdf6.alias_nb_pages()
pdf6.add_title_section()

pdf6.section_header("1. Introduction")
pdf6.body_text(
    "The Nepal Rastra Bank Unified Directives are the primary operational rules compiled and updated annually by the central bank. "
    "They govern the balance sheets, capital requirements, credit activities, and risk parameters of Class A, B, and C financial institutions."
)

pdf6.section_header("2. Capital Adequacy Framework (Directive 1)")
pdf6.body_text(
    "Commercial banks must maintain minimum Capital Adequacy Ratio (CAR) to absorb losses:\n"
    " - Minimum Core Capital (Tier 1): 8.5% of Risk-Weighted Assets.\n"
    " - Minimum Total Capital (Tier 1 + Tier 2): 11% of Risk-Weighted Assets."
)

pdf6.section_header("3. Credit Classification & Provisioning (Directive 2)")
pdf6.body_text("Every BFI must classify outstanding loans into Performing and Non-Performing Loans (NPL) and maintain a credit loss reserve:")
pdf6.sub_section_header("Performing Loans:")
pdf6.bullet_point("Pass Loan", "Overdue by 0 to 1 month. Provision requirement: 1.1% of loan amount (general reserve).")
pdf6.bullet_point("Watchlist", "Overdue by 1 to 3 months, or signs of operational distress. Provision requirement: 5% of loan amount.")
pdf6.sub_section_header("Non-Performing Loans (NPL):")
pdf6.bullet_point("Substandard", "Overdue by 3 to 6 months. Provision requirement: 25% of loan amount.")
pdf6.bullet_point("Doubtful", "Overdue by 6 to 12 months. Provision requirement: 50% of loan amount.")
pdf6.bullet_point("Loss", "Overdue by more than 12 months, or client bankrupt. Provision requirement: 100% of loan amount.")

pdf6.section_header("4. Institutional Governance (Directive 6)")
pdf6.body_text(
    " - Conflict of Interest: A board director cannot influence credit decisions for personal business.\n"
    " - Audit Committee: Must be chaired by a non-executive director to ensure independent audit reporting.\n"
    " - Single Obligor Limit: A BFI cannot lend more than 25% of its core capital to a single business group."
)
pdf6.output("chatbot/laws/nrb_directives.pdf")

print("All 6 legal acts PDFs generated successfully!")
