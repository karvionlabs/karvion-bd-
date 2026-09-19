# KARVION BD — Bangladesh Public AI Service Orchestration Platform

**KARVION BD** একটি ইউনিফাইড বাংলা সার্ভিস প্ল্যাটফর্ম যা সাধারণ নাগরিকদের বিভিন্ন সরকারি ও নাগরিক সেবার (myGov, 333, DNCRP, GRS, কৃষি বিপণন) অফিসিয়াল পোর্টালের সাথে AI ও অটোমেশনের মাধ্যমে সংযুক্ত করে। এটি একটি সার্ভিস অর্কেস্ট্রেটর যা নাগরিকদের সেবা গ্রহণ প্রক্রিয়াকে সহজ ও সাবলীল করে।

## Architecture & Tech Stack

- **Frontend:** Next.js (App Router), Tailwind CSS, Lucide React, Bengali Language Support (Hind Siliguri/Kalpurush).
- **Backend Orchestrator:** FastAPI (Python) - Master Agent Router.
- **Automation Engine:** n8n (Webhooks & external service orchestration).
- **Database:** PostgreSQL (Supabase) + pgvector (for AI Knowledge Base).

## Project Structure (Monorepo)

```text
karvion-bd/
├── apps/
│   ├── web/                # Next.js client with Bangla audio/text input UI
│   └── api/                # FastAPI Master Agent Router and Orchestration Service
├── packages/
│   └── agents/             # Domain agents: student, consumer, citizen, farmer, market, waste
├── workflows/
│   └── n8n/                # n8n workflow configurations and JSON templates
├── docker-compose.yml      # Infrastructure setup (n8n, Postgres, etc.)
├── package.json            # Root workspace config (if using npm/pnpm/yarn workspaces)
└── README.md
```

## Services & Connections

1. **Web Client (`apps/web`):**
   - User Interface for citizens.
   - Accepts text and audio input in Bangla.
   - Communicates directly with the Master API.
2. **Master Agent API (`apps/api`):**
   - Central router receiving requests from the web client.
   - Uses specialized domain agents (`packages/agents`) to understand intent.
   - Triggers appropriate n8n workflows or direct API calls to government services.
3. **Domain Agents (`packages/agents`):**
   - **Student Agent:** Handles education-related queries.
   - **Consumer Agent (DNCRP):** Assists with consumer rights and complaints.
   - **Citizen Agent (myGov, 333, GRS):** Manages general citizen services and grievance redressal.
   - **Farmer/Market Agent:** Provides agricultural and market price information.
   - **Waste Management Agent:** Orchestrates local waste management requests.
4. **n8n Orchestration (`workflows/n8n`):**
   - Connects to external third-party services (myGov APIs, DNCRP portals, SMS gateways, etc.).
   - Triggered via Webhooks from the Master API.
5. **Knowledge Base (PostgreSQL + pgvector):**
   - Stores embeddings of service manuals, government forms, and previous interactions.
   - Used by the agents for RAG (Retrieval-Augmented Generation) to provide accurate information.

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python 3.10+
- Docker & Docker Compose

### Setup

1. **Infrastructure (PostgreSQL, n8n):**
   ```bash
   docker-compose up -d
   ```
2. **Backend API:**
   ```bash
   cd apps/api
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```
3. **Frontend Web Client:**
   ```bash
   cd apps/web
   npm install
   npm run dev
   ```
