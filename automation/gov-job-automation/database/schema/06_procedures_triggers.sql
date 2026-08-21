-- ============================================================================
-- GOVERNMENT JOB AUTOMATION PLATFORM
-- PHASE 1: PROCEDURES, TRIGGERS & FUNCTIONS
-- COMPATIBILITY: MySQL 8.4 LTS (InnoDB, utf8mb4)
-- ============================================================================

DELIMITER //

-- ----------------------------------------------------------------------------
-- 1. UUID GENERATION TRIGGER FOR JOBS
-- ----------------------------------------------------------------------------
CREATE TRIGGER `before_insert_jobs`
BEFORE INSERT ON `jobs`
FOR EACH ROW
BEGIN
    IF NEW.job_uuid IS NULL OR NEW.job_uuid = '' THEN
        SET NEW.job_uuid = UUID();
    END IF;
END //

-- ----------------------------------------------------------------------------
-- 2. UUID GENERATION TRIGGER FOR COMPANIES
-- ----------------------------------------------------------------------------
CREATE TRIGGER `before_insert_companies`
BEFORE INSERT ON `companies`
FOR EACH ROW
BEGIN
    IF NEW.company_uuid IS NULL OR NEW.company_uuid = '' THEN
        SET NEW.company_uuid = UUID();
    END IF;
END //

-- ----------------------------------------------------------------------------
-- 3. AUDIT TRIGGER - UPDATE JOB
-- ----------------------------------------------------------------------------
CREATE TRIGGER `after_update_jobs`
AFTER UPDATE ON `jobs`
FOR EACH ROW
BEGIN
    -- Only log if essential fields changed (preventing spam)
    IF OLD.job_status != NEW.job_status OR OLD.vacancies != NEW.vacancies OR OLD.last_date != NEW.last_date THEN
        INSERT INTO `audit_logs` (
            `entity_type`, `entity_id`, `action`, `performed_by_type`, `old_values`, `new_values`
        ) VALUES (
            'Job', NEW.id, 'UPDATE', 'System', 
            JSON_OBJECT('status', OLD.job_status, 'vacancies', OLD.vacancies, 'last_date', OLD.last_date),
            JSON_OBJECT('status', NEW.job_status, 'vacancies', NEW.vacancies, 'last_date', NEW.last_date)
        );
    END IF;
END //

-- ----------------------------------------------------------------------------
-- 4. FUNCTION - GENERATE SEO SLUG
-- ----------------------------------------------------------------------------
CREATE FUNCTION `generate_slug`(input_str VARCHAR(255))
RETURNS VARCHAR(255)
DETERMINISTIC
BEGIN
    DECLARE slug VARCHAR(255);
    -- Lowercase
    SET slug = LOWER(input_str);
    -- Replace non-alphanumeric with hyphens
    SET slug = REGEXP_REPLACE(slug, '[^a-z0-9]+', '-');
    -- Trim hyphens from ends
    SET slug = TRIM(BOTH '-' FROM slug);
    RETURN slug;
END //

-- ----------------------------------------------------------------------------
-- 5. STORED PROCEDURE - ARCHIVE EXPIRED JOBS
-- ----------------------------------------------------------------------------
CREATE PROCEDURE `archive_expired_jobs`()
BEGIN
    UPDATE `jobs`
    SET `job_status` = 'Expired', `updated_at` = CURRENT_TIMESTAMP
    WHERE `last_date` < CURDATE() AND `job_status` IN ('Approved', 'Pending', 'Draft');
    
    -- Log the archiving action for analytics tracking if needed
END //

-- ----------------------------------------------------------------------------
-- 6. EVENT - DAILY RUN ARCHIVE
-- (Requires EVENT SCHEDULER = ON)
-- ----------------------------------------------------------------------------
CREATE EVENT IF NOT EXISTS `daily_archive_jobs`
ON SCHEDULE EVERY 1 DAY STARTS (TIMESTAMP(CURRENT_DATE) + INTERVAL 1 DAY)
DO
BEGIN
    CALL `archive_expired_jobs`();
END //

DELIMITER ;
