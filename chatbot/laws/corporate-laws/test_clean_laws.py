import re

content = """
**१. संक्षिप्त नाम, विस्तार र प्रारम्भ:** (१) यस ऐनको नाम “सम्पत्ति शुद्धीकरण (मनी लाउन्डरिङ्ग) निवारण ऐन, २०६४” रहेकोछ ।

\* दोस्रो संशोधनद्वारा संशोधित ।

१

www.lawcommission.gov.np

✖(२) यो ऐन नेपालभर लागू हुनेछ र सम्पत्ति शुद्धीकरण तथा आतङ्ककारी कार्यमा वित्तीय लगानी सम्बन्धी कसूर गर्ने नेपालभित्र वा नेपाल बाहिर जहाँसुकै रहे बसेको व्यक्ति समेतलाई लागू हुनेछ ।
"""

content = re.sub(r'www\.lawcommission\.gov\.np\s*', '', content)
content = re.sub(r'^\s*[\d०-९]+\s*$', '', content, flags=re.MULTILINE)
content = re.sub(r'^\s*[\*\♠\Σ\∝\∞\∉\≡\Ψ\∇\⛑\⌧\ठ\+]\s*.*?।\s*$', '', content, flags=re.MULTILINE)
content = re.sub(r'^\s*.*?संशोधनद्वारा (थप|संशोधित|झिकिएको|खारेज).*?।\s*$', '', content, flags=re.MULTILINE)

content = re.sub(r'^\s*(?:परिच्छेद|पररच्छेद)\s*[-–]\s*([\d०-९क-ज्ञ]+)\s*$', r'### परिच्छेद-\1', content, flags=re.MULTILINE)

def dafa_replacer(m):
    num = m.group(1)
    title = m.group(2)
    return f'#### **{num}. {title}**'

content = re.sub(r'^\s*\**([\d०-९]+)\.\s*(.*?[:।])\**\s*$', dafa_replacer, content, flags=re.MULTILINE)

content = re.sub(r'\n{3,}', '\n\n', content)

print("OUTPUT:")
print(content)
