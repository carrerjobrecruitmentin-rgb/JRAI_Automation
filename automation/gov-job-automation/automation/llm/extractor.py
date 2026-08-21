import json
import logging
from typing import Dict, Any, Optional
from groq import Groq

import os

logger = logging.getLogger(__name__)

class LLMExtractor:
    """
    Handles AI normalization of messy government PDF text into structured JSON using Groq.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        # Initialize Groq client
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        
    def extract_job_details(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """
        Takes raw OCR/PDF text and prompts the Groq LLM to extract normalized fields using JSON mode.
        """
        # Define the strict schema we want Groq to follow
        schema = {
            "title": "The exact job title or post name",
            "department": "The specific department or ministry name",
            "organization": "The parent organization (e.g., SSC, UPSC, DRDO)",
            "vacancies": "Integer only. Total number of vacancies. Or null if not stated",
            "salary_raw_text": "The raw string mentioning pay scale, level, or exact salary",
            "min_qualification": "Minimum educational qualification required",
            "last_date": "The last date to apply in YYYY-MM-DD format. Null if not found",
            "age_limit": "The required age limit or range"
        }
        
        prompt = f"""
        You are an expert government job data extractor. 
        Extract the required job data from this raw text. Ensure extreme accuracy.
        You MUST return ONLY a valid JSON object matching this schema:
        {json.dumps(schema, indent=2)}

        Raw Text to parse:
        {raw_text[:8000]} 
        """
        
        logger.info("Calling Groq API for Extraction...")
        try:
            # Using llama-3.1-8b-instant or llama-3.3-70b-versatile for fast json output
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a JSON-only API that extracts job data. Return ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            result_json = response.choices[0].message.content
            extracted_data = json.loads(result_json)
            logger.info(f"Successfully extracted: {extracted_data.get('title')}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Groq API Extraction failed: {str(e)}")
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    extractor = LLMExtractor()
    sample_text = "The Staff Selection Commission will hold a competitive examination for recruitment to the posts of Lower Divisional Clerk (LDC). There are approximately 3712 vacancies. The pay scale is Level-2 (Rs. 19,900 to 63,200). Candidates must have passed 12th Standard or equivalent. Age limit is 18-27 years. Last date for receipt of online applications is 07-05-2024."
    print("Testing Extractor with Groq...")
    result = extractor.extract_job_details(sample_text)
    print("\nResult from Groq API:")
    print(json.dumps(result, indent=2))
