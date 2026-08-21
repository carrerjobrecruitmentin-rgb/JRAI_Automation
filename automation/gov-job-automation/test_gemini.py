import os
import sys

# Add the project root to sys.path so we can import automation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automation.llm.extractor import LLMExtractor
import json

def test():
    extractor = LLMExtractor()
    sample_text = """
    GOVERNMENT OF INDIA
    MINISTRY OF DEFENCE
    DEFENCE RESEARCH & DEVELOPMENT ORGANISATION (DRDO)
    
    Advertisement No.: 145
    
    Applications are invited for the post of Scientist 'B'. 
    Total Vacancies: 250
    Age limit for Unreserved candidates is 28 years.
    Salary: Level-10 (Rs. 56,100/-)
    Essential Qualification: At least First Class Bachelor's Degree in Engineering or Technology from a recognized university.
    Closing Date: 31-08-2026
    """
    
    print("Sending text to Gemini...")
    result = extractor.extract_job_details(sample_text)
    print("\nResult from Gemini API:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test()
