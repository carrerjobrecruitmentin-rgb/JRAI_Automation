-- ============================================================================
-- GOVERNMENT JOB AUTOMATION PLATFORM
-- PHASE 1: AI & OCR PROCESSING TABLES
-- COMPATIBILITY: MySQL 8.4 LTS (InnoDB, utf8mb4)
-- ============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------------------------------------------
-- 1. LLM PROMPTS & METRICS
-- ----------------------------------------------------------------------------
CREATE TABLE `ai_prompts` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `prompt_name` VARCHAR(100) NOT NULL,
    `version` INT UNSIGNED NOT NULL DEFAULT 1,
    `system_prompt` TEXT NOT NULL,
    `user_prompt_template` TEXT NOT NULL,
    `model_name` VARCHAR(50) NOT NULL DEFAULT 'gpt-4o',
    `temperature` DECIMAL(3,2) DEFAULT 0.00,
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_ai_prompt_ver` (`prompt_name`, `version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `ai_execution_logs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `source_id` BIGINT UNSIGNED NULL,
    `job_id` BIGINT UNSIGNED NULL,
    `prompt_id` BIGINT UNSIGNED NOT NULL,
    `input_tokens` INT UNSIGNED DEFAULT 0,
    `output_tokens` INT UNSIGNED DEFAULT 0,
    `latency_ms` INT UNSIGNED DEFAULT 0,
    `cost_usd` DECIMAL(10, 6) DEFAULT 0.000000,
    `confidence_score` DECIMAL(5,2) NULL, -- 0-100
    `raw_input` LONGTEXT NULL,
    `raw_output` LONGTEXT NULL,
    `status` ENUM('Success', 'Failed', 'Timeout', 'Validation_Error') NOT NULL,
    `error_message` TEXT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_aiel_prompt` FOREIGN KEY (`prompt_id`) REFERENCES `ai_prompts`(`id`) ON DELETE CASCADE,
    INDEX `idx_aiel_status` (`status`),
    INDEX `idx_aiel_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 2. OCR PROCESSING LOGS
-- ----------------------------------------------------------------------------
CREATE TABLE `ocr_jobs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `source_id` BIGINT UNSIGNED NOT NULL,
    `document_url` VARCHAR(1024) NOT NULL,
    `total_pages` INT UNSIGNED DEFAULT 0,
    `language` VARCHAR(50) DEFAULT 'eng+hin',
    `status` ENUM('Pending', 'Processing', 'Completed', 'Failed') DEFAULT 'Pending',
    `extracted_text` LONGTEXT NULL,
    `confidence_score` DECIMAL(5,2) NULL,
    `error_message` TEXT NULL,
    `started_at` DATETIME NULL,
    `completed_at` DATETIME NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_ocr_source` FOREIGN KEY (`source_id`) REFERENCES `source_registry`(`id`) ON DELETE CASCADE,
    INDEX `idx_ocr_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
