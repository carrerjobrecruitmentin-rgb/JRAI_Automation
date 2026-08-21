-- ============================================================================
-- GOVERNMENT JOB AUTOMATION PLATFORM
-- PHASE 1: SEED DATA
-- COMPATIBILITY: MySQL 8.4 LTS (InnoDB, utf8mb4)
-- ============================================================================

SET NAMES utf8mb4;

-- Insert Base Sources to jumpstart crawler
INSERT INTO `source_registry` (`source_name`, `domain`, `website_url`, `recruitment_url`, `source_type`, `priority`, `status`, `supports_rss`, `adapter_name`) VALUES
('UPSC', 'upsc.gov.in', 'https://upsc.gov.in', 'https://upsc.gov.in/recruitment', 'UPSC', 'Critical', 'Active', 1, 'UPSCAdapter'),
('SSC', 'ssc.gov.in', 'https://ssc.gov.in', 'https://ssc.gov.in/notices', 'SSC', 'Critical', 'Active', 0, 'SSCAdapter'),
('RRB Chandigarh', 'rrbcdg.gov.in', 'https://rrbcdg.gov.in', 'https://rrbcdg.gov.in/employment', 'Railway', 'High', 'Active', 0, 'RRBAdapter'),
('IBPS', 'ibps.in', 'https://ibps.in', 'https://ibps.in/careers', 'Bank', 'High', 'Active', 0, 'IBPSAdapter'),
('DRDO', 'drdo.gov.in', 'https://drdo.gov.in', 'https://drdo.gov.in/careers', 'Defense', 'Medium', 'Active', 0, 'DRDOAdapter'),
('ISRO', 'isro.gov.in', 'https://www.isro.gov.in', 'https://www.isro.gov.in/Careers.html', 'Defense', 'Medium', 'Active', 0, 'ISROAdapter');

-- Insert Initial AI Prompts
INSERT INTO `ai_prompts` (`prompt_name`, `version`, `system_prompt`, `user_prompt_template`, `model_name`) VALUES
('Job_Normalization', 1, 
 'You are a highly skilled AI specializing in extracting and standardizing government job notices into structured JSON. You must ONLY return a valid JSON object without markdown formatting.',
 'Extract the following job data from this raw text. The JSON keys must be exactly: title, vacancies (integer), salary_text, last_date (YYYY-MM-DD), qualification, age_limit, apply_url. Raw Text: {text}',
 'gpt-4o');

