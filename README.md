# 🏦 Siddhartha Bank — AI Solutions Demo

> **Interview Demo Project** | Powered by Google Gemini 2.0 Flash AI

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-blue)](https://yourusername.github.io/siddhartha-bank-ai)

---

## 🚀 तीन वटा AI Solutions

| # | Project | Description |
|---|---------|-------------|
| 1 | 🤖 **Bank Customer Chatbot** | Nepali+English AI customer service, 24/7 |
| 2 | 📢 **AI Marketing Tool** | Pomelli-inspired brand-consistent content generator |
| 3 | 👔 **Branch Manager Assistant** | Dashboard, complaint analyzer, meeting notes |

---

## 🛠️ Technology Stack

- **AI Model:** Google Gemini 2.0 Flash (latest, fastest, free tier available)
- **Frontend:** HTML5 + CSS3 + Vanilla JavaScript (zero framework, zero cost)
- **Charts:** Chart.js 4.4
- **Hosting:** GitHub Pages (free)
- **Total Infrastructure Cost:** ₹0

---

## ⚡ Local मा चलाउने तरिका

```bash
# Option 1: Direct file open
open index.html

# Option 2: Local server (recommended)
python3 -m http.server 8080
# Browser मा जानुस्: http://localhost:8080
```

---

## 🔑 API Key Setup

1. [Google AI Studio](https://aistudio.google.com/app/apikey) मा जानुस्
2. Free API key generate गर्नुस्
3. App को sidebar/header मा API key enter गर्नुस्

> ⚠️ **Security:** API key कहिल्यै code मा hardcode नगर्नुस्। यो app मा user ले runtime मा enter गर्छ।

---

## 📁 Project Structure & Layout (प्रोजेक्टको पूर्ण संरचना)

यो प्रोजेक्टलाई तीनवटा मुख्य व्यवसायिक समाधान (Business Solutions) मा विभाजन गरिएको छ:

```
siddhartha-bank-ai/
├── index.html                ← Main Landing Page (प्रवेशद्वार)
├── chatbot/
│   ├── index.html            ← Customer Service Chatbot (ग्राहक सेवा च्याटबट)
│   └── laws/
│       └── corporate-laws/   ← NexSight Law (एड्भान्स कानुनी च्याटबट)
│           ├── app.py        ← Application Interface (मुख्य स्क्रिन)
│           ├── database.py   ← SQLite database logger (प्रश्न-उत्तर रेकर्ड गर्ने डायरी)
│           └── chunks/       ← 1,865 database sections (कानुनका टुक्राहरू)
├── marketing/
│   └── index.html            ← AI Marketing Copywriter (विज्ञापन सामग्री लेखक)
└── branch-manager/
    └── index.html            ← Manager's AI Dashboard (शाखा प्रबन्धक ड्यासबोर्ड)
```

### 🏢 १. मुख्य गेटवे (Main Gateway)
* **`index.html`**: यो एपको साझा गृहपृष्ठ (Landing Page) हो। यसले सिद्धार्थ बैंकको नीलो र सुन्तला रङको ब्रान्डिङसहित एउटै ठाउँबाट सबै ३ वटा AI सेवाहरू खोल्न मद्दत गर्दछ।

### 💻 २. तत्काल चल्ने प्रोटोटाइपहरू (Frontend-Only Apps)
यी एप्लिकेसनहरू सिधै युजरको ब्राउजरमा चल्छन् र यसका लागि कुनै महँगो सर्भर वा डाटाबेस सेटअप चाहिँदैन (Zero-cost infrastructure):
* **`chatbot/index.html` (Customer Chatbot)**: बैंकका बचत खाता, ब्याजदर र डिजिटल सेवाहरूका बारेमा ग्राहकहरूले नेपाली र अंग्रेजीमा २४/७ जानकारी लिन मिल्ने च्याट विन्डो।
* **`marketing/index.html` (AI Marketing Writer)**: सिद्धार्थ बैंकको ब्रान्ड टोनसँग मिल्ने फेसबुक पोस्ट, इमेल र एसएमएस सामग्री स्वतः लेखिदिने सृजनात्मक AI टूल।
* **`branch-manager/index.html` (Branch Manager Assistant)**: प्रबन्धकहरूले ग्राहकका जटिल गुनासाहरूको विश्लेषण गर्न, मिटिङ नोटहरू स्वतः तयार पार्न र शाखाको रिपोर्ट हेर्न प्रयोग गर्ने ड्यासबोर्ड।

### ⚖️ ३. एड्भान्स बैंकिङ तथा कर्पोरेट कानुन प्रणाली — **NexSight Law** (`chatbot/laws/corporate-laws/`)
यो यो प्रोजेक्टकै सबैभन्दा बौद्धिक र शक्तिशाली व्यावसायिक AI प्रणाली हो। यसले नेपालको बैंकिङ र कर्पोरेट कानुनका पुस्तकहरू पढेर वकिल सरह सटिक जवाफ दिन्छ:
* **`app.py` (मुख्य एप्लिकेसन)**: कानुन सम्बन्धी प्रश्न सोध्ने र Claude AI को सहायताले सटिक बुँदागत उत्तर देखाउने मुख्य इन्टरफेस।
* **`database.py` र `chat_logs.db`**: भविष्यमा विश्लेषण गर्न र कानुनी सुरक्षाका लागि कुन युजरले के प्रश्न सोधे र AI ले के उत्तर दियो भनेर रेकर्ड राख्ने कानुनी डायरी।
* **कानुनका पुस्तकहरू (`.pdf` Files)**: BAFIA, नेपाल राष्ट्र बैंक ऐन, बैंकिङ कसूर ऐन, सम्पत्ति शुद्धीकरण निवारण ऐन, र श्रम ऐन जस्ता आधिकारिक सरकारी कानुनी दस्तावेजहरू।
* **डाटा लोड गर्ने संयन्त्र (`ingest_to_pinecone.py`)**: कानुनका १,८६५ वटा भन्दा बढी दफाहरूलाई टुक्रा-टुक्रा पारेर सुरक्षित क्लाउड डाटाबेसमा राख्ने कोड, ताकि च्याटबटले सेकेन्डमै दफा खोज्न सकोस्।

---

## 🎯 Interview Key Points

1. **Cost-effective:** Gemini free tier = Rs. 0 infrastructure cost
2. **Scalable:** Prototype to production in 3 months
3. **Nepali Language:** First-class support for Nepali customers
4. **No vendor lock-in:** Standard HTML/JS, deployable anywhere
5. **Google Pomelli concept:** Bank DNA-aware marketing AI

---

*Built for Siddhartha Bank Limited AI Solutions Interview Demo*
