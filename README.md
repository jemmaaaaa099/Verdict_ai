# Verdict AI – Know Your Rights
*Justice begins with awareness.*

A Flask website that gives plain-language legal guidance to ordinary Indian citizens. It is **not a lawyer or a court** and never decides guilt or innocence.

> **Before public use:** verify every law, helpline number, deadline and link in `data/knowledge_base.json` and `templates/index.html` against official Indian government sources (for example nalsa.gov.in, consumerhelpline.gov.in, cybercrime.gov.in, indiacode.nic.in). Laws and numbers change, and rules differ by state. Have a qualified lawyer review the content.

## Run it
1. Install Python 3.9 or newer.
2. In this folder: `python -m venv venv`
3. Activate it: Windows `venv\Scripts\activate` · macOS/Linux `source venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python app.py`
6. Open http://127.0.0.1:5000

**Optional Live AI (Gemini):** set the key before step 5.
Windows: `set GEMINI_API_KEY=your_key` · macOS/Linux: `export GEMINI_API_KEY=your_key`
Optional: `GEMINI_MODEL` to change the model (default `gemini-2.5-flash`; check the current name in Google's docs).
Without a key, everything works in **Demo** mode.

**Test on a phone:** run `HOST=0.0.0.0 python app.py` (Windows: `set HOST=0.0.0.0`), then open `http://<your-computer-IP>:5000` on the same Wi-Fi.

## Files
- `app.py` – Flask routes, security headers, optional Gemini step
- `nlp.py` – tokeniser, stop words, stemmer, TF-IDF, cosine similarity, urgent-word check
- `data/knowledge_base.json` – 11 topics (edit or add topics here)
- `templates/index.html`, `static/style.css`, `static/app.js` – the website

## How the chatbot works
1. **Tokenisation:** the question is lowercased and split into words.
2. **Stop-word removal:** common words ("the", "my", "is") are dropped.
3. **Stemming:** a small suffix stripper maps "arrested" and "arrests" to "arrest".
4. **TF-IDF:** each knowledge-base topic is a weighted word vector. Rare, meaningful words count more.
5. **Cosine similarity:** the question is compared with every topic. The best score picks the topic.
6. **Confidence:** High (0.30+), Medium (0.18+), Low (0.10+). Below 0.10 the bot says it found no good match.
7. **Optional Gemini:** only rewords the knowledge-base facts. The user's question is never sent to Gemini, and if the reply looks wrong the Demo text is used.

## Class 12 AI syllabus mapping
| Syllabus area | Where it appears |
|---|---|
| Natural Language Processing | Tokenisation, stop words, stemming, TF-IDF in `nlp.py` |
| Classification / similarity | Cosine similarity assigns a question to one of 11 topics, with a confidence level |
| Knowledge-based systems | `knowledge_base.json` is a hand-written expert knowledge base with rules (urgent words, thresholds) |
| Generative AI | Optional Gemini rewording, kept inside the knowledge-base facts |
| AI ethics | Honest "no match" answers, Demo/Live AI labels, disclaimers, no storage of questions, urgent-help banner, no verdicts, bias and access discussion below |

## Responsible-AI choices
- Questions are not stored or logged (request logging is switched off, no database).
- Answers are built with `textContent`, never raw HTML. A Content-Security-Policy blocks inline scripts.
- Only `https://` links from the knowledge base are shown.
- Users are told not to share Aadhaar, bank or password details.

## Limitations
- Only 11 topics. Questions outside them get "no good match".
- Keyword-style matching does not understand meaning, negation or context. "I did not borrow money" may still match the loan topic.
- English only. The stemmer is simple and makes mistakes.
- Content is general. It ignores state-specific rules, deadlines and the facts of your case.
- Laws, fees, limits and helplines change. The text may be out of date.
- The urgent-word check can miss danger or flag safe messages.
- Live AI rewording can still lose nuance. It is checked only for shape, not meaning.
- No accounts, no history, no lawyer review built in.
- Not suitable for real legal decisions without verification by a professional.
