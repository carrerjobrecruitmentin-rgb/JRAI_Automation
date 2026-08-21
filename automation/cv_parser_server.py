"""
CV Parser Server — Office PC
FastAPI + spaCy + rule-based patterns + optional LLM fallback

Setup (run once):
    pip install fastapi uvicorn pymupdf spacy python-dotenv httpx
    python -m spacy download en_core_web_sm

Create a .env file next to this script:
    SECRET_KEY=your-random-secret-here
    GROQ_API_KEY=your-groq-key
    GEMINI_API_KEY=your-gemini-key

Run:
    uvicorn cv_parser_server:app --host 0.0.0.0 --port 8000

Cloudflare Tunnel (run separately, add to Task Scheduler):
    cloudflared tunnel run --url http://localhost:8000 cv-parser
"""

import sys
import httpx

API_KEY = "hk_secure_token_2026"

# Ensure log directory exists
import re
import base64
import os
import json
import logging
import time
import platform
import threading
import asyncio
from datetime import datetime, timezone
from typing import Optional

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

import httpx

try:
    import fitz  # PyMuPDF
    _HAS_FITZ = True
except ImportError:
    fitz = None
    _HAS_FITZ = False

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    _HAS_SPACY = True
except Exception:
    nlp = None
    _HAS_SPACY = False

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Header
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

LOG_FILE = os.path.join(os.path.dirname(__file__), "cv_parser_requests.jsonl")

SECRET_KEY   = os.getenv("SECRET_KEY", "")
GROQ_KEY     = os.getenv("GROQ_API_KEY", "")
GEMINI_KEY   = os.getenv("GEMINI_API_KEY", "")
GROQ_MODEL   = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.5-flash"

ALLOWED_ROLES = [
    "Administrative Assistant", "Operations Manager", "Back Office Executive",
    "Receptionist / Front Office Executive", "Accountant", "Financial Analyst",
    "Tax Consultant / Auditor", "Payroll Executive", "HR Generalist",
    "Talent Acquisition / Recruiter", "Payroll & Compliance Specialist",
    "Business Development Manager", "Digital Marketer / SEO Specialist",
    "Sales Executive / Field Sales Officer", "Content Creator / Copywriter",
    "IAS (Indian Administrative Service)", "IPS (Indian Police Service)",
    "IFS (Indian Foreign Service)", "Bank PO (Probationary Officer)", "Bank Clerk",
    "RBI Grade B Officer", "SSC CGL/CHSL Position", "Junior Engineer (JE)",
    "PSU Management Trainee", "Software Developer (Full Stack/Backend/Frontend)",
    "Data Scientist / Data Analyst", "Cloud Architect / DevOps Engineer",
    "Cyber Security Analyst", "AI/ML Engineer", "Product Manager",
    "Delivery Partner", "Warehouse Manager / Loader", "Driver",
    "Chef / Baker / Steward", "Nurse / Patient Care Assistant",
    "Housekeeping Staff", "Electrician / Plumber / HVAC Technician",
    "Machine Operator / Fitter / Welder", "Legal Counsel / Corporate Lawyer",
    "Legal Assistant / Paralegal", "Compliance Officer",
    
    "Print Production Supervisor", "Printing Executive", "Printing In-Charge",
    "Printing Engineer", "Printing Operator", "Senior Printing Operator",
    "Rotogravure Operator", "Rotogravure Supervisor", "Rotogravure Printing Operator",
    "Printing Machine Operator", "Flexographic (Flexo) Printing Operator",
    "Flexo Printing Supervisor", "Offset Printing Operator", "Offset Printing Supervisor",
    "Gravure Printing Operator", "Production Supervisor", "Production Executive",
    "Shift Supervisor", "Shift In-Charge", "Production In-Charge", "Machine Operator",
    "Machine Supervisor", "Production Engineer", "Packaging Production Supervisor",
    "Flexible Packaging Supervisor", "Manufacturing Supervisor"
]

INDIAN_LANGUAGES = [
    "Hindi", "English", "Gujarati", "Marathi", "Tamil", "Telugu",
    "Kannada", "Bengali", "Punjabi", "Urdu", "Malayalam", "Odia",
    "Rajasthani", "Sindhi", "Kashmiri", "Assamese", "Sanskrit",
]

LLM_PROMPT = (
    "You are a precise resume parser. Extract these fields: "
    "Desired Role (must exactly match ONE of: " + ", ".join(ALLOWED_ROLES) + "), "
    "Full Name, Email Address, Phone Number, Location (full address as written), "
    "Current Designation, Current Salary, Expected Salary, Education, Experience "
    "(total years, e.g. '5 Years'), Notice Period, Languages Known. "
    "If not found, leave as empty string. "
    'Respond ONLY in valid JSON: {"desired_role":"","name":"","email":"","phone":"",'
    '"location":"","current_designation":"","current_salary":"","expected_salary":"",'
    '"education":"","experience":"","notice_period":"","languages":""}. No markdown.'
)

app = FastAPI(title="CV Parser")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
_START_TIME = time.monotonic()


@app.on_event("startup")
async def _raise_threadpool_limit():
    """Allow many CVs to be parsed in parallel (spaCy + PDF run in threads).
    Default anyio threadpool is 40; bump it so concurrent recruiters don't queue."""
    try:
        import anyio
        limiter = anyio.to_thread.current_default_thread_limiter()
        limiter.total_tokens = 64
        log.info("Threadpool limit raised to 64 for concurrent parsing")
    except Exception as e:
        log.warning(f"Could not raise threadpool limit: {e}")


# Lock so concurrent requests never interleave/corrupt the JSONL log
_LOG_LOCK = threading.Lock()


def write_log(entry: dict):
    """Append one JSON line to the request log file (thread-safe)."""
    try:
        with _LOG_LOCK:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        log.warning(f"Log write failed: {e}")


def extract_pdf_text(pdf_b64: str) -> str:
    """Decode + extract text from a base64 PDF. CPU-bound — run in a thread."""
    pdf_bytes = base64.b64decode(pdf_b64)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)


def extract_pdf_images(pdf_b64: str) -> list[str]:
    """Convert a base64 PDF into a list of base64 JPEG images (max 3 pages). CPU-bound."""
    pdf_bytes = base64.b64decode(pdf_b64)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    # Limit to first 3 pages to save API tokens and time
    for page_num in range(min(3, len(doc))):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("jpeg")
        images.append(base64.b64encode(img_bytes).decode('utf-8'))
    return images

def scrub_pdf_bytes(pdf_b64: str) -> str:
    """Decodes PDF, redacts emails/phones/links, returns base64 PDF."""
    pdf_bytes = base64.b64decode(pdf_b64)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # regex for emails and phones (basic ones)
    email_re = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
    phone_re = re.compile(r"(?:\+?91[-\s]?)?([6-9]\d{9})")
    phone2_re = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    
    for page in doc:
        # Remove or black-out text matching regex
        for regex in [email_re, phone_re, phone2_re]:
            matches = page.search_for(regex)
            # PyMuPDF search_for doesn't easily do regex directly unless using specific methods, 
            # let's just find the text via get_text("dict") and match regex, then redact.
        
        # A better way in PyMuPDF: get words, match regex
        words = page.get_text("words")
        for w in words:
            text = w[4]
            rect = fitz.Rect(w[0], w[1], w[2], w[3])
            if email_re.search(text) or phone_re.search(text) or phone2_re.search(text) or "linkedin.com" in text.lower() or "github.com" in text.lower():
                page.add_redact_annot(rect, fill=(0, 0, 0))
                
        # Also redact links
        links = page.get_links()
        for link in links:
            if "uri" in link:
                page.add_redact_annot(link["from"], fill=(0, 0, 0))
                
        page.apply_redactions()

    # Re-save the PDF securely
    out_pdf = doc.write(encryption=fitz.PDF_ENCRYPT_AES_256, user_pw="jobrecruitment", owner_pw="jobrecruitment", permissions=fitz.PDF_PERM_PRINT)
    return base64.b64encode(out_pdf).decode('utf-8')


# ---------------------------------------------------------------------------
# Auth middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def check_secret(request: Request, call_next):
    if request.url.path in ("/health", "/", "/docs", "/redoc", "/openapi.json", "/favicon.ico", "/logs"):
        return await call_next(request)
    if SECRET_KEY and request.headers.get("X-Secret") != SECRET_KEY:
        return JSONResponse(status_code=401, content={"success": False, "message": "Unauthorized"})
    return await call_next(request)


# ---------------------------------------------------------------------------
# Rule-based extractors
# ---------------------------------------------------------------------------

def extract_email(text: str) -> str:
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return m.group(0).lower() if m else ""


def extract_phone(text: str) -> str:
    # Strip pincodes first so they don't get matched as phone numbers
    text_clean = re.sub(r"\b[1-9]\d{5}\b", "", text)
    clean = re.sub(r"\s+", "", text_clean)
    # Match Indian mobile: starts with 6-9, 10 digits (with optional +91/91 prefix)
    m = re.search(r"(?:\+?91[-\s]?)?([6-9]\d{9})", clean)
    if m:
        digits = re.sub(r"\D", "", m.group(1))[-10:]
        return f"+91 {digits[:5]} {digits[5:]}"
    # Multiple numbers separated by - or , (take first valid one)
    for chunk in re.split(r"[-,|]", text_clean):
        chunk = chunk.strip()
        digits = re.sub(r"\D", "", chunk)
        if len(digits) == 10 and digits[0] in "6789":
            return f"+91 {digits[:5]} {digits[5:]}"
    return ""


def extract_name_spacy(text: str) -> str:
    doc = nlp(text[:1500])
    for ent in doc.ents:
        if ent.label_ == "PERSON" and 2 <= len(ent.text.split()) <= 4:
            return ent.text.title()
    return ""


def extract_location_spacy(text: str) -> str:
    # Try pincode anchor — take only the last line/segment before the pincode
    m = re.search(r"([^\n]{0,120})\b([1-9]\d{5})\b", text)
    if m:
        segment = m.group(1).strip().rstrip(" -,.")
        # Strip common label prefixes
        segment = re.sub(r"^(?:location|address|residing|city|add)[:\s]+", "", segment, flags=re.IGNORECASE).strip()
        # Take only the last meaningful part if multiple separators present
        for sep in ["\n", " | ", " - "]:
            if sep in segment:
                segment = segment.rsplit(sep, 1)[-1].strip()
        if segment:
            return f"{segment} - {m.group(2)}"
        return m.group(2)
        return f"{segment} - {m.group(2)}" if segment else m.group(2)
    # spaCy GPE fallback
    doc = nlp(text[:2000])
    locs = [e.text for e in doc.ents if e.label_ in ("GPE", "LOC")]
    return locs[0] if locs else ""


def extract_designation_spacy(text: str) -> str:
    title_kw = ["engineer", "manager", "executive", "analyst", "developer",
                "designer", "consultant", "specialist", "officer", "coordinator",
                "director", "lead", "head", "accountant", "recruiter", "architect"]
    # First pass: check for labeled line "Current Designation: ..."
    m = re.search(r"(?:current\s+designation|designation|current\s+role)[:\s]+([^\n]{3,60})", text, re.IGNORECASE)
    if m:
        val = re.sub(r"\s+at\s+.*$", "", m.group(1), flags=re.IGNORECASE).strip()
        return val.title() if val else ""
    # Second pass: short standalone lines with title keywords
    for line in text.splitlines()[:40]:
        ll = line.lower().strip()
        if len(line) > 55 or len(line) < 4:
            continue
        if any(kw in ll for kw in title_kw):
            clean = re.sub(r"[^A-Za-z /&\-()]", "", line).strip()
            if 5 <= len(clean) <= 55:
                return clean.title()
    return ""


def extract_salary(text: str, kind: str) -> str:
    if kind == "current":
        pat = r"(?:current\s+(?:ctc|salary|package)|ctc|salary)"
    else:
        pat = r"(?:expected\s+(?:ctc|salary|package)|expected|desired\s+salary)"
    m = re.search(pat + r"[:\s*]+(\d+(?:\.\d+)?)\s*(?:LPA|lac|lakh|lakhs?|CTC|p\.?a\.?)", text, re.IGNORECASE)
    if m:
        return f"{m.group(1)} LPA"
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:LPA|lac|lakh|lakhs?)", text, re.IGNORECASE)
    return f"{m.group(1)} LPA" if m else ""


def extract_education(text: str) -> str:
    m = re.search(
        r"\b(B\.?\s*Tech|B\.?\s*E|B\.?\s*Com|B\.?\s*Sc|B\.?\s*A|MBA|MCA|M\.?\s*Tech|"
        r"M\.?\s*Com|M\.?\s*Sc|M\.?\s*A|Ph\.?\s*D|Diploma|12th|HSC|SSC|10th|BCA|BBA|MBBS|LLB)[^\n]{0,80}?"
        r"(University|College|Institute|School|Vidyalaya|IIT|NIT|BITS)",
        text, re.IGNORECASE
    )
    if m:
        return re.sub(r"\s+", " ", m.group(0)).strip()
    m = re.search(
        r"\b(B\.?\s*Tech|B\.?\s*E|B\.?\s*Com|B\.?\s*Sc|MBA|MCA|M\.?\s*Tech|"
        r"Ph\.?\s*D|Diploma|12th|HSC|SSC|BCA|BBA|MBBS|LLB)\b",
        text, re.IGNORECASE
    )
    return m.group(1).upper().replace(" ", "") if m else ""


def extract_experience(text: str) -> str:
    m = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)", text, re.IGNORECASE)
    if m:
        return f"{m.group(1)} Years"
    m = re.search(r"(?:experience|exp)[:\s]+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", text, re.IGNORECASE)
    if m:
        return f"{m.group(1)} Years"
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s+(?:of\s+)?(?:work|industry|total|professional)", text, re.IGNORECASE)
    return f"{m.group(1)} Years" if m else ""


def extract_notice_period(text: str) -> str:
    m = re.search(r"(?:notice\s*period|notice)[:\s]+([^\n,;.]{3,40})", text, re.IGNORECASE)
    if m:
        val = re.sub(r"[|\/\\].+", "", m.group(1)).strip()
        if 3 <= len(val) <= 30:
            return val.capitalize()
    m = re.search(
        r"\b(immediate(?:ly)?|serving\s+notice|currently\s+serving|(\d+)\s*(?:days?|months?|weeks?)(?:\s*notice)?)\b",
        text, re.IGNORECASE
    )
    return m.group(1).capitalize() if m else ""


def extract_languages(text: str) -> str:
    m = re.search(r"(?:languages?\s*(?:known|spoken|proficiency)?)[:\s]+([A-Za-z ,&/\-]+)", text, re.IGNORECASE)
    if m:
        langs = re.split(r"[\n\r]", m.group(1))[0].strip(", \t")
        if 3 <= len(langs) <= 100:
            return langs
    found = [lang for lang in INDIAN_LANGUAGES if re.search(rf"\b{lang}\b", text, re.IGNORECASE)]
    return ", ".join(found)


def extract_role(text: str) -> str:
    text_lower = text.lower()
    best, best_score = "", 0
    for role in ALLOWED_ROLES:
        words = re.split(r"[\s/&()]+", role.lower())
        hits = sum(1 for w in words if len(w) >= 3 and w in text_lower)
        if hits > best_score:
            best_score, best = hits, role
    return best if best_score >= 1 else ""


def rule_extract(text: str) -> dict:
    return {
        "desired_role":        extract_role(text),
        "name":                extract_name_spacy(text),
        "email":               extract_email(text),
        "phone":               extract_phone(text),
        "location":            extract_location_spacy(text),
        "current_designation": extract_designation_spacy(text),
        "current_salary":      extract_salary(text, "current"),
        "expected_salary":     extract_salary(text, "expected"),
        "education":           extract_education(text),
        "experience":          extract_experience(text),
        "notice_period":       extract_notice_period(text),
        "languages":           extract_languages(text),
    }


def confidence(data: dict) -> float:
    fields = ["desired_role", "name", "email", "phone", "location",
              "current_designation", "education", "experience",
              "notice_period", "languages", "current_salary", "expected_salary"]
    filled = sum(1 for f in fields if data.get(f, "").strip())
    return filled / len(fields)


# ---------------------------------------------------------------------------
# LLM fallback
# ---------------------------------------------------------------------------

async def llm_groq(text: str) -> Optional[dict]:
    if not GROQ_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                json={"model": GROQ_MODEL,
                      "messages": [{"role": "system", "content": LLM_PROMPT},
                                   {"role": "user", "content": f"Resume:\n\n{text[:8000]}"}],
                      "temperature": 0.1, "response_format": {"type": "json_object"}},
            )
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            return json.loads(content)
    except Exception as e:
        log.warning(f"Groq error: {e}")
    return None


async def llm_gemini(text: str) -> Optional[dict]:
    if not GEMINI_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": LLM_PROMPT + f"\n\nResume:\n\n{text[:8000]}"}]}],
                      "generationConfig": {"temperature": 0.1}},
            )
        if r.status_code == 200:
            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            raw = re.sub(r"```json|```", "", raw).strip()
            return json.loads(raw)
    except Exception as e:
        log.warning(f"Gemini error: {e}")
    return None


async def llm_gemini_vision(images_b64: list[str]) -> Optional[dict]:
    if not GEMINI_KEY:
        return None
    try:
        parts = [{"text": LLM_PROMPT + "\n\nExtract details from the following resume images. Ensure the response is valid JSON."}]
        for img_b64 in images_b64:
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img_b64
                }
            })
            
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": parts}],
                    "generationConfig": {
                        "temperature": 0.1, 
                        "responseMimeType": "application/json"
                    }
                },
            )
        if r.status_code == 200:
            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(raw)
    except Exception as e:
        log.warning(f"Gemini Vision error: {e}")
    return None


def merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if isinstance(v, str) and v.strip() and not result.get(k, "").strip():
            result[k] = v
    return result


SEP  = "-" * 50
SEP2 = "-" * 24

def dbg_request(ip: str, input_type: str, text: str):
    preview = "\n  ".join(text[:300].splitlines())
    print(f"\n{SEP}")
    print(f"  NEW REQUEST")
    print(SEP)
    print(f"  IP         : {ip}")
    print(f"  Input type : {input_type}")
    print(f"  Text length: {len(text)} chars")
    print(f"  Preview (first 300 chars):")
    print(f"  {preview}")
    print(SEP)

def dbg_fields(data: dict, conf: float, llm_needed: bool):
    print(f"\n  {SEP2} Rule Extraction {SEP2}")
    for k, v in data.items():
        val = v if v else "<empty>"
        print(f"  {k:<22}: {val}")
    print(f"  {SEP2}")
    decision = "→ LLM fallback needed" if llm_needed else "→ spacy_rules (no LLM needed)"
    print(f"  Confidence : {conf:.2f}  {decision}")

def dbg_final(source: str, conf: float, elapsed_ms: int, data: dict):
    print(f"\n  {SEP2} Final Response {SEP2}")
    print(f"  source     : {source}")
    print(f"  confidence : {conf:.2f}")
    print(f"  elapsed_ms : {elapsed_ms}ms")
    print(f"  data       : {json.dumps(data, ensure_ascii=False)}")
    print(SEP + "\n")


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@app.post("/generate_email")
async def generate_email(request: Request):
    if request.headers.get("X-API-Key") != API_KEY:
        raise HTTPException(401, "Unauthorized")
        
    try:
        body = await request.json()
        client_name = body.get("client_name", "Client")
        job_role = body.get("job_role", "Candidate")
        email_type = body.get("type", "standard")
        
        prompt = f"Write a professional {email_type} email to {client_name} regarding {job_role}. Keep it concise and polite."
        
        # Use Groq or Gemini
        llm_data = await llm_groq(prompt)
        # Assuming our llm_groq extracts JSON, but we just want text. We should write a small raw text generator.
        # Actually, let's just do a quick httpx call here for text generation, or return a placeholder if we don't have one ready.
        if GROQ_KEY:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                    json={"model": GROQ_MODEL,
                          "messages": [{"role": "system", "content": "You are a professional HR assistant. Write only the email body."},
                                       {"role": "user", "content": prompt}],
                          "temperature": 0.5},
                )
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"]
                return JSONResponse({"success": True, "email_body": content.strip()})
                
        return JSONResponse({"success": True, "email_body": f"Dear {client_name},\n\nPlease find attached the resume for {job_role}.\n\nBest Regards,\nJobRecruitment"})
    except Exception as e:
        return JSONResponse({"success": False, "message": str(e)})

@app.post("/redact")
async def redact_cv(request: Request):
    if request.headers.get("X-API-Key") != API_KEY:
        raise HTTPException(401, "Unauthorized")
        
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")
        
    pdf_b64 = body.get("pdf_base64", body.get("pdfBase64", ""))
    if not pdf_b64:
        return JSONResponse({"success": False, "message": "No pdfBase64 provided"})
        
    try:
        # Offload to a thread because it's CPU bound and uses PyMuPDF
        scrubbed_b64 = await asyncio.to_thread(scrub_pdf_bytes, pdf_b64)
        return JSONResponse({"success": True, "redacted_pdf_base64": scrubbed_b64})
    except Exception as e:
        log.error(f"Scrub error: {e}")
        return JSONResponse({"success": False, "message": str(e)})

@app.post("/parse-cv")
async def parse_cv(request: Request):
    t_start  = time.monotonic()
    client_ip = request.headers.get("CF-Connecting-IP") or request.headers.get("X-Forwarded-For") or request.client.host

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")

    pdf_b64  = body.get("pdfBase64", "")
    image_b64 = body.get("imageBase64", "")
    text_in  = body.get("text", "")
    input_type = "pdf" if pdf_b64 else ("image" if image_b64 else "text")

    # Extract text from PDF if provided — offload to a thread (CPU-bound,
    # would otherwise block the event loop and serialize concurrent requests)
    text = text_in
    if pdf_b64 and not text:
        try:
            text = await asyncio.to_thread(extract_pdf_text, pdf_b64)
        except Exception as e:
            log.warning(f"PDF extract failed: {e}")
            text = text_in

    # VISION FALLBACK: If no text was extracted, it's likely a scanned PDF or direct image upload
    if not text.strip() and (pdf_b64 or image_b64):
        log.info("No text extracted. Falling back to Gemini Vision OCR...")
        images_b64 = []
        if pdf_b64:
            try:
                images_b64 = await asyncio.to_thread(extract_pdf_images, pdf_b64)
            except Exception as e:
                log.warning(f"PDF image extract failed: {e}")
        elif image_b64:
            images_b64 = [image_b64]
            
        if images_b64:
            vision_data = await llm_gemini_vision(images_b64)
            if vision_data:
                elapsed_ms = round((time.monotonic() - t_start) * 1000)
                final_conf = confidence(vision_data)
                
                write_log({
                    "ts": datetime.now(timezone.utc).isoformat(), "ip": client_ip,
                    "input": "image/scanned_pdf", "name": vision_data.get("name", ""),
                    "success": True, "source": "gemini_vision", "confidence": round(final_conf, 2),
                    "ms": elapsed_ms, "fields_filled": {k: bool(v) for k, v in vision_data.items() if not k.endswith("_source")}
                })
                return JSONResponse({
                    "success": True, "degraded": False, "source": "gemini_vision",
                    "provider_used": "gemini_vision", "confidence": round(final_conf, 2),
                    "data": vision_data
                })

    if not text.strip():
        write_log({"ts": datetime.now(timezone.utc).isoformat(), "ip": client_ip,
                   "input": input_type, "success": False, "error": "no_text_or_vision_failed", "ms": 0})
        return JSONResponse({"success": False, "message": "No text could be extracted from the CV, and Vision fallback failed."})

    dbg_request(client_ip, input_type, text)

    # Rule-based extraction (spaCy NER is CPU-bound — run off the event loop)
    data = await asyncio.to_thread(rule_extract, text)
    conf = confidence(data)
    source = "spacy_rules"
    llm_needed = conf < 0.70
    dbg_fields(data, conf, llm_needed)

    # LLM fallback only when confidence is low
    if llm_needed:
        print(f"\n  ⚠  Confidence {conf:.2f} < 0.70 — calling Groq LLM...")
        llm_data = await llm_groq(text)
        if llm_data:
            print(f"  Groq response  : {json.dumps(llm_data, ensure_ascii=False)}")
            data   = merge(data, llm_data)
            source = "spacy_rules+llm"
            print(f"  After merge conf: {confidence(data):.2f}")
        else:
            print(f"  Groq failed — trying Gemini...")
            llm_data = await llm_gemini(text)
            if llm_data:
                print(f"  Gemini response: {json.dumps(llm_data, ensure_ascii=False)}")
                data   = merge(data, llm_data)
                source = "spacy_rules+llm"
                print(f"  After merge conf: {confidence(data):.2f}")
            else:
                print(f"  Gemini also failed — returning spacy_rules only")

    elapsed_ms = round((time.monotonic() - t_start) * 1000)
    final_conf = confidence(data)
    dbg_final(source, final_conf, elapsed_ms, data)
    write_log({
        "ts":         datetime.now(timezone.utc).isoformat(),
        "ip":         client_ip,
        "input":      input_type,
        "name":       data.get("name", ""),
        "success":    True,
        "source":     source,
        "confidence": round(final_conf, 2),
        "ms":         elapsed_ms,
        "fields_filled": {k: bool(v) for k, v in data.items() if not k.endswith("_source")},
    })
    log.info(f"Parsed in {elapsed_ms}ms | source={source} | conf={final_conf:.2f} | ip={client_ip}")

    return JSONResponse({
        "success":       True,
        "degraded":      False,
        "source":        source,
        "provider_used": source,
        "confidence":    round(final_conf, 2),
        "data":          data,
    })


@app.get("/health")
async def health():
    uptime_sec = int(time.monotonic() - _START_TIME)
    h, m, s = uptime_sec // 3600, (uptime_sec % 3600) // 60, uptime_sec % 60
    uptime_str = f"{h}h {m}m {s}s"

    ram_info = {}
    if _HAS_PSUTIL:
        mem = psutil.virtual_memory()
        proc = psutil.Process()
        ram_info = {
            "system_total_mb": round(mem.total / 1024 / 1024),
            "system_used_pct": mem.percent,
            "process_mb": round(proc.memory_info().rss / 1024 / 1024),
        }

    log_count = 0
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, encoding="utf-8") as f:
            log_count = sum(1 for line in f if line.strip())

    return {
        "status": "ok",
        "version": "1.0.0",
        "uptime": uptime_str,
        "model": nlp.meta["name"] if nlp else "rules+llm-multimodal",
        "groq_configured": bool(GROQ_KEY),
        "gemini_configured": bool(GEMINI_KEY),
        "total_requests_logged": log_count,
        "ram": ram_info,
        "platform": platform.system(),
    }


@app.get("/logs")
async def get_logs(request: Request, last: int = 50):
    """Return last N request log entries + summary stats. Protected by X-Secret."""
    if SECRET_KEY and request.headers.get("X-Secret") != SECRET_KEY:
        return JSONResponse(status_code=401, content={"success": False, "message": "Unauthorized"})

    entries = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass

    recent   = entries[-last:]
    total    = len(entries)
    ok       = sum(1 for e in entries if e.get("success"))
    avg_ms   = round(sum(e.get("ms", 0) for e in entries if e.get("success")) / max(ok, 1))
    sources  = {}
    for e in entries:
        s = e.get("source", "error")
        sources[s] = sources.get(s, 0) + 1

    return JSONResponse({
        "total_requests": total,
        "successful":     ok,
        "failed":         total - ok,
        "avg_ms":         avg_ms,
        "by_source":      sources,
        "recent":         recent,
    })


# ---------------------------------------------------------------------------
# Background AI Matching Engine Integration
# ---------------------------------------------------------------------------
class JobMatchPayload(BaseModel):
    job_id: str


def _run_matching_task(job_id: str):
    try:
        from ai_matching_engine import run_ai_matching
        log.info(f"🟢 [MATCH-JOB] Starting AI matching for Job ID '{job_id}'...")
        res = run_ai_matching(job_id)
        if res.get("success"):
            log.info(f"✅ [MATCH-JOB] AI matching finished for Job '{job_id}'.")
        else:
            log.warning(f"⚠️ [MATCH-JOB] AI matching note: {res.get('error')}")
    except Exception as e:
        log.error(f"❌ [MATCH-JOB] Matching task failed: {e}")


@app.post("/api/match_job")
async def trigger_match_job(payload: JobMatchPayload, background_tasks: BackgroundTasks, x_api_key: Optional[str] = Header(None)):
    expected_key = os.getenv("AI_WORKER_API_KEY", "your_secret_api_key_123")
    if expected_key and x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized API Key")
    background_tasks.add_task(_run_matching_task, payload.job_id)
    return {
        "status": "success",
        "message": f"Job {payload.job_id} received. Matching engine processing in background."
    }

