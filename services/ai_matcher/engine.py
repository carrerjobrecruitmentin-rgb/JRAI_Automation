import re
from typing import List, Dict, Any, Optional
from common.logger import log

class AIMatchingEngine:
    """
    Candidate-to-Job & Job-to-Candidate AI Compatibility Engine.
    Computes exact percentage match score (0 - 100%) based on:
    - Skill overlap (50% weight)
    - Title / Role semantic alignment (25% weight)
    - Experience requirement matching (15% weight)
    - Location / Work Mode compatibility (10% weight)
    """

    @classmethod
    def calculate_match(cls, candidate_profile: Dict[str, Any], job_posting: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates compatibility score between candidate and job posting.
        """
        # 1. Skill Score (50%)
        candidate_skills = [s.lower().strip() for s in (candidate_profile.get("skills") or [])]
        job_skills = [s.lower().strip() for s in (job_posting.get("skills") or [])]

        if not job_skills and job_posting.get("requirements"):
            # Extract common skills from requirements text
            common_kw = ["python", "php", "javascript", "react", "laravel", "mysql", "aws", "docker", "figma", "sales", "hr", "accounting"]
            req_text = str(job_posting.get("requirements")).lower()
            job_skills = [k for k in common_kw if k in req_text]

        skill_score = 0.0
        matching_skills = []
        missing_skills = []

        if job_skills:
            for js in job_skills:
                matched = any(js in cs or cs in js for cs in candidate_skills)
                if matched:
                    matching_skills.append(js)
                else:
                    missing_skills.append(js)
            skill_score = (len(matching_skills) / len(job_skills)) * 50.0
        else:
            skill_score = 40.0  # Default baseline if no explicit skills required

        # 2. Title & Role Alignment (25%)
        candidate_title = str(candidate_profile.get("current_role") or candidate_profile.get("title") or "").lower()
        job_title = str(job_posting.get("title") or "").lower()

        title_score = 0.0
        if candidate_title and job_title:
            cand_tokens = set(re.findall(r"\w+", candidate_title))
            job_tokens = set(re.findall(r"\w+", job_title))
            intersection = cand_tokens.intersection(job_tokens)
            if intersection:
                title_score = min(25.0, (len(intersection) / max(1, len(job_tokens))) * 25.0 + 10.0)
            else:
                title_score = 5.0
        else:
            title_score = 15.0

        # 3. Experience Match (15%)
        candidate_exp = float(candidate_profile.get("total_experience_years") or candidate_profile.get("experience_years") or 0.0)
        job_min_exp = float(job_posting.get("min_experience") or 0.0)
        job_max_exp = float(job_posting.get("max_experience") or 20.0)

        exp_score = 0.0
        if candidate_exp >= job_min_exp:
            exp_score = 15.0
        else:
            diff = job_min_exp - candidate_exp
            exp_score = max(0.0, 15.0 - (diff * 5.0))

        # 4. Location & Work Mode Match (10%)
        cand_loc = str(candidate_profile.get("location") or "").lower()
        job_loc = str(job_posting.get("location_text") or job_posting.get("location") or "").lower()
        work_mode = str(job_posting.get("work_mode") or "").lower()

        loc_score = 5.0
        if "remote" in work_mode:
            loc_score = 10.0
        elif cand_loc and job_loc and (cand_loc in job_loc or job_loc in cand_loc):
            loc_score = 10.0

        total_score = min(100, int(round(skill_score + title_score + exp_score + loc_score)))

        # Tier breakdown
        if total_score >= 85:
            match_tier = "Excellent Match"
            recommendation = "Strongly Recommended"
        elif total_score >= 65:
            match_tier = "Good Match"
            recommendation = "Recommended"
        elif total_score >= 45:
            match_tier = "Moderate Match"
            recommendation = "Potential Fit"
        else:
            match_tier = "Low Match"
            recommendation = "Skills Gap"

        return {
            "score": total_score,
            "tier": match_tier,
            "recommendation": recommendation,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "breakdown": {
                "skill_score": round(skill_score, 1),
                "title_score": round(title_score, 1),
                "exp_score": round(exp_score, 1),
                "loc_score": round(loc_score, 1)
            }
        }
