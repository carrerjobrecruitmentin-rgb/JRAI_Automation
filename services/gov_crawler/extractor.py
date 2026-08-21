import json
import re
from typing import Dict, Any, Optional
import requests
from common.config import settings
from common.logger import log

try:
    from groq import Groq
except ImportError:
    Groq = None

class GovJobExtractor:
    """
    Extracts structured government recruitment fields from raw notification texts and PDF feeds.
    """

    @classmethod
    def extract_from_text(cls, raw_text: str) -> Optional[Dict[str, Any]]:
        prompt = f"""
You are an expert Government Recruitment Normalizer. Extract official details from this recruitment text and return STRICT, VALID JSON ONLY.

JSON Schema:
{{
  "title": "Post Title / Exam Name",
  "department": "Ministry / Board Name (e.g. UPSC, SSC, Indian Railways)",
  "vacancies_count": 150,
  "salary_range": "₹56,100 - ₹84,150 / month",
  "pay_level": 10,
  "in_hand_approx": "₹68,000 / month",
  "required_degree": "Graduate in any discipline",
  "qualification_summary": "Degree from recognized university",
  "age_limit": "18 - 32 Years",
  "age_relaxation": "OBC +3y, SC/ST +5y",
  "application_fee": "General: ₹100 | SC/ST: Exempted (₹0)",
  "apply_url": "https://official-portal.gov.in",
  "last_date": "YYYY-MM-DD",
  "notification_pdf": "https://portal.gov.in/notice.pdf",
  "description": "2 sentence concise description of the recruitment drive"
}}

Recruitment Notification Text:
\"\"\"
{raw_text[:7000]}
\"\"\"
"""
        # Primary: Gemini Flash
        if settings.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1}
                }
                resp = requests.post(url, json=payload, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    ai_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    cleaned = re.sub(r"^```json\s*", "", ai_text.strip(), flags=re.MULTILINE)
                    cleaned = re.sub(r"^```\s*$", "", cleaned.strip(), flags=re.MULTILINE)
                    return json.loads(cleaned)
            except Exception as e:
                log.warning(f"Gemini gov extractor error: {e}")

        # Fallback: Groq LLaMA
        if settings.GROQ_API_KEY and Groq:
            try:
                client = Groq(api_key=settings.GROQ_API_KEY)
                chat = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a Government Recruitment Normalizer returning JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    model=settings.GROQ_MODEL,
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                return json.loads(chat.choices[0].message.content)
            except Exception as e:
                log.warning(f"Groq gov extractor error: {e}")

        return None
