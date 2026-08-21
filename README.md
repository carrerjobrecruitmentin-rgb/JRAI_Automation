# JobRecruitmentAI Automation Engine & Microservices API Gateway 🤖⚡

Comprehensive, production-ready microservices architecture and centralized API Gateway for **[JobRecruitmentAI](https://jobrecruitment.ai)** (`jobrecruitment.ai`), configured for instant deployment on **Render.com** (Docker) and Cloudflare.

---

## 🏛️ Microservices & API Gateway Architecture

```mermaid
graph TD
    Client[Client / PHP Backend / Portal] -->|HTTPS Requests| Cloudflare[Cloudflare / Render Edge]
    Cloudflare -->|Port: $PORT| Gateway[FastAPI API Gateway: main.py]
    
    subgraph Microservices Layer
        Gateway -->|/api/v1/cv-parser/*| MS1[CV & Resume Parser Microservice]
        Gateway -->|/api/v1/matcher/*| MS2[AI Job Matching & Webhook Microservice]
        Gateway -->|/api/v1/crawler/*| MS3[Govt Job Scraper Microservice]
        Gateway -->|/health, /docs| Health[Observability & OpenAPI Interactive Docs]
    end
    
    subgraph Engine & AI Models
        MS1 --> OCR[Tesseract OCR & PyPDF2]
        MS1 --> LLM1[Gemini 2.5 Flash / Groq LLaMA 3.3]
        MS2 --> LLM2[Semantic Matching Engine]
        MS2 --> DB[(Hostinger MySQL DB)]
        MS3 --> DB
    end
    
    subgraph Background Workers (Render Worker)
        Worker[Background Crawler Scheduler] -->|Periodic Scrapes| MS3
    end
```

---

## 🚀 Key Microservices & API Endpoints

### 1. 📄 CV & Resume Parser Service (`/api/v1/cv-parser`)
- **`POST /api/v1/cv-parser/upload`**:
  - Multi-part document upload (`.pdf`, `.docx`, `.png`, `.jpg`, `.txt`).
  - Automated OCR text extraction via Tesseract.
  - Multi-tier AI normalization into structured JSON (skills, experience, education, contact info, summary).
- **`POST /api/v1/cv-parser/parse-text`**:
  - Direct raw text resume parsing.

### 2. 🎯 AI Job Matching Service (`/api/v1/matcher`)
- **`POST /api/v1/matcher/match-score`**:
  - Computes exact compatibility score (0-100%) between candidate profile and job requirements.
  - Skill intersection, title alignment, experience matching, and location scoring.
- **`POST /api/v1/matcher/webhook/application-match`**:
  - Asynchronous webhook to calculate and update application match score directly in MySQL database.

### 3. 🏛️ Government Job Crawler Service (`/api/v1/crawler`)
- **`POST /api/v1/crawler/extract-notification`**:
  - AI extraction of structured official recruitment fields from PDF/raw text.
- **`POST /api/v1/crawler/publish-notification`**:
  - Extracts and publishes new government jobs to the live database.

### 4. 🩺 Health & Observability
- **`GET /health`**:
  - Liveness probe returning status of gateway and all microservices.
- **`GET /docs`**:
  - Interactive Swagger / OpenAPI documentation UI.

---

## ☁️ Deploying on Render.com (1-Click Deployment)

### Option A: Using Render Blueprint (`render.yaml`)
1. Go to **[Render Dashboard](https://dashboard.render.com/)**.
2. Click **New +** -> **Blueprint**.
3. Connect repository: `https://github.com/carrerjobrecruitmentin-rgb/JRAI_Automation`.
4. Render will automatically read `render.yaml` and configure:
   - **Web Service:** `jrai-automation-gateway` (Docker, Port `$PORT`)
   - **Background Worker:** `jrai-gov-crawler-worker` (Cron scheduler)
5. Fill in your environment variables:
   - `GEMINI_API_KEY`
   - `GROQ_API_KEY`
   - `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`
6. Click **Apply**!

### Option B: Manual Web Service Setup
1. In Render, select **New Web Service** -> **Deploy from Git repository**.
2. Select `JRAI_Automation` repository.
3. Runtime: **Docker** (Dockerfile path: `./Dockerfile`).
4. Health Check Path: `/health`.
5. Add Environment Variables (from `.env.example`).
6. Click **Create Web Service**.

---

## 💻 Local Development & Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run API Gateway Locally
```bash
python main.py
```
Or with Uvicorn reload:
```bash
uvicorn gateway.app:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation available at: `http://localhost:8000/docs`

---
© 2026 **JobRecruitmentAI** (`jobrecruitment.ai`). All rights reserved.
