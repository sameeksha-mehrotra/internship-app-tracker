# Career Roadmap & Application Tracker

Interactive career roadmap and application tracker built for navigating the path from UT Austin CS → Google Cloud Customer Engineer → Forward Deployed Engineer.

**[Open the tracker →](https://sameeksha-mehrotra.github.io/internship-app-tracker/)**

---

## What's inside

**Application Tracker tab**
- 20+ applications organized by group: Active Assessments, Apply Immediately, Apply Fall 2026, FinTech Companies, Frontier AI Labs, and Rejected
- Per-card status dropdown (Not Started → Researching → Applied → Assessment → Interviewing → Offer → Rejected)
- Interactive 5-star fit rating, expandable notes, and priority badges
- Stats bar: total tracked, applied/active, in assessment, critical priority, offers
- IBM assessment cards pulse orange — they're active right now

**Career Roadmap tab**
- 7 phases from May 2026 → 2035, each with 3 parallel tracks shown side by side
- Checkable tasks per phase with progress bar across all tasks
- Google → Google Cloud internal transfer milestone with tooltip explaining the strategy
- FinTech edge callout (Citibank advantage framing)
- Frontier AI Skills Gap Tracker — clickable progress bars for Anthropic/OpenAI readiness
- TC trajectory chart showing all 3 tracks across 4 career stages

## The 3 tracks

| Track | Color | Path |
|-------|-------|------|
| **Track 1** — CE/AI SE → Google Cloud | Blue | IBM/AWS/Salesforce → Google BOLD intern → core Google → internal transfer to Google Cloud CE → FDE |
| **Track 2** — AI Consulting Bridge | Purple | Deloitte/Accenture → SE role → FDE |
| **Track 3** — Frontier AI Labs | Orange | Portfolio building 2026–28 → apply Anthropic/OpenAI Applied AI Engineer 2029+ → FDE |

### Google vs. Google Cloud distinction
Google and Google Cloud are separate internal orgs. The strategy is to join core Google first (via BOLD/gTech), then transfer internally to Google Cloud CE after 1–2 years. Internal candidates are strongly preferred over external hires for Cloud CE, and BOLD → gTech → Google Cloud CE is a documented, well-trodden path.

## Stack

Single-file React app — no build step, no dependencies to install.

- **React 18** via CDN
- **Tailwind CSS** via CDN
- **Babel standalone** for JSX

Open `tracker.html` directly in a browser or serve it from any static host.

## Background

- CS junior at UT Austin, graduating May 2028
- Two Citibank internships (software engineering + merchant services credit)
- Live RAG chatbot: [sameekshas-rag-chatbot.streamlit.app](https://sameekshas-rag-chatbot.streamlit.app)
- Skills: Python, LangChain, RAG, Hugging Face, PyTorch, TensorFlow, Azure, REST APIs
- Target: Google Cloud CE specializing in AI + FinTech → FDE
