import re

text = """
## परिच्छेद–१

### प्रारम्भिक

**१. संक्षिप्त नाम, विस्तार र प्रारम्भ:** (१) यस ऐनको नाम “सम्पत्ति शुद्धीकरण (मनी लाउन्डरिङ्ग) निवारण ऐन, २०६४” रहेकोछ ।

\* दोस्रो संशोधनद्वारा संशोधित ।

१

www.lawcommission.gov.np

✖(२) यो ऐन नेपालभर लागू हुनेछ र सम्पत्ति शुद्धीकरण तथा आतङ्ककारी कार्यमा वित्तीय लगानी सम्बन्धी कसूर गर्ने नेपालभित्र वा नेपाल बाहिर जहाँसुकै रहे बसेको व्यक्ति समेतलाई लागू हुनेछ ।
"""

TAGS_TO_STRIP = r'</?(u|sup|sub)[^>]*>'
SYMBOLS_TO_STRIP = r'[∝∞∉≡ΨठΣ✖♦♣♠♥]'

def is_block_starter(line):
    pattern = r'^\s*(#|-|\*|\d+\.|\([a-zA-Z0-9क-ज्ञ०-९]+\)|[a-zA-Zक-ज्ञ०-९]+\.|<table|<tr|<th|<td|<thead|<tbody|</table|</tr|</th|</td|</thead|</tbody|<br|\||<!--|>)'
    return bool(re.match(pattern, line))

def is_footnote_def(line):
    if re.match(r'^\s*[∝∞∉≡ΨठΣ✖♦♣♠♥]\s*.*', line):
        return True
    return False

lines = text.strip().split('\n')
cleaned_lines = []
for line in lines:
    c_line = re.sub(TAGS_TO_STRIP, '', line)
    if is_footnote_def(c_line):
        continue
    c_line = re.sub(SYMBOLS_TO_STRIP, '', c_line)
    cleaned_lines.append(c_line)

unwrapped = []
for line in cleaned_lines:
    stripped = line.rstrip()
    if not stripped:
        unwrapped.append(stripped)
        continue
    if re.match(r'^\s*\.{3,}\s*$', stripped):
        continue
    if not unwrapped:
        unwrapped.append(stripped)
        continue
    prev_line = unwrapped[-1]
    if not prev_line.strip():
        unwrapped.append(stripped)
        continue
    if is_block_starter(stripped):
        unwrapped.append(stripped)
        continue
    
    is_date_split = False
    if prev_line.strip().endswith('।') and re.search(r'[\d०-९]।$', prev_line.strip()):
        if re.match(r'^[\d०-९]', stripped.lstrip()):
            is_date_split = True

    if not is_date_split and prev_line.strip().endswith(('.', '।', '?', '!', ':', ';', '>')):
        unwrapped.append(stripped)
        continue
        
    unwrapped[-1] = prev_line + " " + stripped.lstrip()

print("\n".join(unwrapped))
