-- ============================================================================
-- GOVERNMENT JOB AUTOMATION PLATFORM
-- PHASE 1: SEO & ANALYTICS TABLES
-- COMPATIBILITY: MySQL 8.4 LTS (InnoDB, utf8mb4)
-- ============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------------------------------------------
-- 1. SEO METADATA (Per Job/Company/Page)
-- ----------------------------------------------------------------------------
CREATE TABLE `seo_metadata` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `entity_type` ENUM('Job', 'Company', 'Page') NOT NULL,
    `entity_id` BIGINT UNSIGNED NOT NULL,
    `slug` VARCHAR(512) NOT NULL,
    `meta_title` VARCHAR(255) NULL,
    `meta_description` VARCHAR(512) NULL,
    `focus_keywords` VARCHAR(512) NULL,
    `canonical_url` VARCHAR(1024) NULL,
    `open_graph_image` VARCHAR(1024) NULL,
    `schema_markup` JSON NULL, -- JSON-LD Schema.org Data
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_seo_slug` (`slug`),
    UNIQUE KEY `idx_seo_entity` (`entity_type`, `entity_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 2. DAILY ANALYTICS & REPORTS
-- ----------------------------------------------------------------------------
CREATE TABLE `analytics_daily` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `report_date` DATE NOT NULL,
    `total_jobs_crawled` INT UNSIGNED DEFAULT 0,
    `total_jobs_published` INT UNSIGNED DEFAULT 0,
    `total_jobs_failed` INT UNSIGNED DEFAULT 0,
    `total_duplicates_found` INT UNSIGNED DEFAULT 0,
    `total_pdf_parsed` INT UNSIGNED DEFAULT 0,
    `total_ocr_processed` INT UNSIGNED DEFAULT 0,
    `llm_tokens_used` BIGINT UNSIGNED DEFAULT 0,
    `llm_cost_usd` DECIMAL(10, 4) DEFAULT 0.0000,
    `active_sources` INT UNSIGNED DEFAULT 0,
    `failed_sources` INT UNSIGNED DEFAULT 0,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_analytics_date` (`report_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
