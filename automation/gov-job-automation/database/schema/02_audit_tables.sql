-- ============================================================================
-- GOVERNMENT JOB AUTOMATION PLATFORM
-- PHASE 1: AUDIT & VERSIONING TABLES
-- COMPATIBILITY: MySQL 8.4 LTS (InnoDB, utf8mb4)
-- ============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------------------------------------------
-- 1. AUDIT LOGS (General Actions)
-- ----------------------------------------------------------------------------
CREATE TABLE `audit_logs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `entity_type` ENUM('Job', 'Company', 'Source', 'User', 'System') NOT NULL,
    `entity_id` BIGINT UNSIGNED NULL,
    `action` ENUM('INSERT', 'UPDATE', 'DELETE', 'STATUS_CHANGE', 'VERIFY') NOT NULL,
    `performed_by` BIGINT UNSIGNED NULL, -- User or System ID
    `performed_by_type` ENUM('Admin', 'Employer', 'Candidate', 'System', 'API') NOT NULL DEFAULT 'System',
    `ip_address` VARCHAR(45) NULL,
    `old_values` JSON NULL,
    `new_values` JSON NULL,
    `request_id` VARCHAR(100) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_audit_entity` (`entity_type`, `entity_id`),
    INDEX `idx_audit_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ----------------------------------------------------------------------------
-- 2. JOB VERSIONS (For Corrigendum/Updates Tracking)
-- ----------------------------------------------------------------------------
CREATE TABLE `jobs_versions` (
    `version_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `job_id` BIGINT UNSIGNED NOT NULL,
    `version_number` INT UNSIGNED NOT NULL DEFAULT 1,
    `title` VARCHAR(255) NOT NULL,
    `vacancies` INT UNSIGNED NULL,
    `salary_raw_text` VARCHAR(255) NULL,
    `last_date` DATE NULL,
    `notification_pdf_url` VARCHAR(1024) NULL,
    `changed_columns` JSON NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`version_id`),
    CONSTRAINT `fk_jv_job` FOREIGN KEY (`job_id`) REFERENCES `jobs`(`id`) ON DELETE CASCADE,
    INDEX `idx_jv_job` (`job_id`, `version_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 3. DUPLICATE DETECTION LOGS
-- ----------------------------------------------------------------------------
CREATE TABLE `duplicate_jobs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `source_id` BIGINT UNSIGNED NOT NULL,
    `original_job_id` BIGINT UNSIGNED NULL,
    `detected_title` VARCHAR(255) NOT NULL,
    `content_hash` CHAR(64) NOT NULL, -- SHA256 of extracted content
    `pdf_hash` CHAR(64) NULL, -- SHA256 of the downloaded PDF
    `similarity_score` DECIMAL(5,2) NULL, -- 0.00 to 100.00
    `action_taken` ENUM('Archived', 'Merged', 'Flagged_For_Review', 'Ignored') NOT NULL DEFAULT 'Archived',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_dup_source` FOREIGN KEY (`source_id`) REFERENCES `source_registry`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_dup_job` FOREIGN KEY (`original_job_id`) REFERENCES `jobs`(`id`) ON DELETE SET NULL,
    INDEX `idx_dup_hash` (`content_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
