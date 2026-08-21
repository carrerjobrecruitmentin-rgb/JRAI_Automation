import uuid
from typing import Dict, Any
from common.database import get_db_connection
from common.logger import log

class GovJobPublisher:
    """
    Inserts validated Government Job recruitments into the MySQL database.
    """

    @classmethod
    def publish_job(cls, job_data: Dict[str, Any]) -> bool:
        conn = get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                # Check for existing job by title and department
                cursor.execute(
                    "SELECT id FROM jobs WHERE title = %s AND (department = %s OR company_name = %s) LIMIT 1",
                    (job_data.get("title"), job_data.get("department"), job_data.get("department"))
                )
                existing = cursor.fetchone()
                if existing:
                    log.info(f"Gov Job already exists: {job_data.get('title')}")
                    return True

                job_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO jobs (
                        id, title, department, company_name, is_gov, type, vacancies_count,
                        salary_range, pay_level, in_hand_approx, required_degree, qualification_summary,
                        age_limit, age_relaxation, application_fee, apply_url, official_portal,
                        notification_pdf, last_date, description, status, created_at
                    ) VALUES (
                        %s, %s, %s, %s, 1, 'Full-Time', %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, 'active', NOW()
                    )
                """, (
                    job_id,
                    job_data.get("title"),
                    job_data.get("department"),
                    job_data.get("department", "Government Department"),
                    job_data.get("vacancies_count", "As per Notification"),
                    job_data.get("salary_range", "7th Pay Commission"),
                    job_data.get("pay_level"),
                    job_data.get("in_hand_approx"),
                    job_data.get("required_degree"),
                    job_data.get("qualification_summary"),
                    job_data.get("age_limit"),
                    job_data.get("age_relaxation"),
                    job_data.get("application_fee"),
                    job_data.get("apply_url", "https://india.gov.in"),
                    job_data.get("apply_url", "https://india.gov.in"),
                    job_data.get("notification_pdf"),
                    job_data.get("last_date"),
                    job_data.get("description", "Official government recruitment notification.")
                ))
                log.info(f"Published new Government Job: {job_data.get('title')} (ID: {job_id})")
                return True
        except Exception as e:
            log.error(f"Failed to publish gov job: {e}")
            return False
        finally:
            conn.close()
