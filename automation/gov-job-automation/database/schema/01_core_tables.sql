-- ============================================================================
-- GOVERNMENT JOB AUTOMATION PLATFORM
-- PHASE 1: CORE TABLES
-- COMPATIBILITY: MySQL 8.4 LTS (InnoDB, utf8mb4)
-- ============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------------------------------------------
-- 1. SOURCE REGISTRY & DISCOVERY
-- ----------------------------------------------------------------------------
CREATE TABLE `source_registry` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `source_name` VARCHAR(255) NOT NULL,
    `domain` VARCHAR(255) NOT NULL,
    `website_url` VARCHAR(512) NOT NULL,
    `recruitment_url` VARCHAR(512) NULL,
    `source_type` ENUM('UPSC', 'SSC', 'Railway', 'PSU', 'StatePSC', 'Police', 'Defense', 'Bank', 'University', 'Other') NOT NULL DEFAULT 'Other',
    `state_code` CHAR(2) NULL, -- 'GJ', 'MH', 'DL', 'ALL'
    `language` VARCHAR(50) DEFAULT 'English',
    `priority` ENUM('Low', 'Medium', 'High', 'Critical') NOT NULL DEFAULT 'Medium',
    `status` ENUM('Active', 'Inactive', 'Broken', 'Under_Maintenance') NOT NULL DEFAULT 'Active',
    `supports_rss` BOOLEAN DEFAULT FALSE,
    `supports_sitemap` BOOLEAN DEFAULT FALSE,
    `supports_api` BOOLEAN DEFAULT FALSE,
    `requires_login` BOOLEAN DEFAULT FALSE,
    `uses_javascript` BOOLEAN DEFAULT FALSE,
    `uses_pdf` BOOLEAN DEFAULT FALSE,
    `uses_ocr` BOOLEAN DEFAULT FALSE,
    `last_crawl_at` DATETIME NULL,
    `next_crawl_at` DATETIME NULL,
    `health_score` TINYINT UNSIGNED DEFAULT 100, -- 0 to 100
    `adapter_name` VARCHAR(100) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_domain` (`domain`),
    INDEX `idx_next_crawl` (`status`, `next_crawl_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 2. COMPANIES / ORGANIZATIONS
-- ----------------------------------------------------------------------------
CREATE TABLE `companies` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `company_uuid` CHAR(36) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `logo_url` VARCHAR(512) NULL,
    `cover_image_url` VARCHAR(512) NULL,
    `email` VARCHAR(255) NULL,
    `phone_number` VARCHAR(50) NULL,
    `website` VARCHAR(512) NULL,
    `description` TEXT NULL,
    `industry` VARCHAR(100) NULL,
    `company_type` VARCHAR(100) NULL, -- Private, Public, Startup, NGO, Govt Body
    `employee_count_range` VARCHAR(50) NULL,
    `founded_year` YEAR NULL,
    `headquarters` VARCHAR(255) NULL,
    `address` VARCHAR(512) NULL,
    `city` VARCHAR(100) NULL,
    `state` VARCHAR(100) NULL,
    `country` VARCHAR(100) DEFAULT 'India',
    `pincode` VARCHAR(20) NULL,
    `gst_number` VARCHAR(50) NULL,
    `cin_number` VARCHAR(50) NULL,
    `social_links` JSON NULL, -- LinkedIn, FB, Twitter, Instagram
    `working_days` VARCHAR(100) NULL,
    `office_timing` VARCHAR(100) NULL,
    `hr_contact_name` VARCHAR(255) NULL,
    `hr_designation` VARCHAR(255) NULL,
    `hr_email` VARCHAR(255) NULL,
    `hr_mobile` VARCHAR(50) NULL,
    `verification_status` ENUM('Pending', 'Verified', 'Rejected') DEFAULT 'Pending',
    `profile_visibility` ENUM('Public', 'Private', 'Internal') DEFAULT 'Public',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_company_uuid` (`company_uuid`),
    INDEX `idx_verification` (`verification_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 3. JOBS / NOTIFICATIONS
-- ----------------------------------------------------------------------------
CREATE TABLE `jobs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `job_uuid` CHAR(36) NOT NULL,
    `source_id` BIGINT UNSIGNED NULL, -- NULL for manual postings
    `company_id` BIGINT UNSIGNED NULL,
    
    -- Basic Information
    `title` VARCHAR(255) NOT NULL,
    `department` VARCHAR(255) NULL,
    `organization` VARCHAR(255) NULL,
    `job_category` VARCHAR(100) NULL,
    `employment_type` ENUM('Full Time', 'Part Time', 'Internship', 'Contract', 'Freelance', 'Temporary') NOT NULL DEFAULT 'Full Time',
    `work_mode` ENUM('On-site', 'Remote', 'Hybrid') NOT NULL DEFAULT 'On-site',
    
    -- Location
    `country` VARCHAR(100) DEFAULT 'India',
    `state` VARCHAR(100) NULL,
    `city` VARCHAR(100) NULL,
    `address` VARCHAR(512) NULL,
    `pincode` VARCHAR(20) NULL,
    
    -- Salary
    `salary_type` ENUM('Monthly', 'Annual', 'Hourly') DEFAULT 'Monthly',
    `min_salary` DECIMAL(12, 2) NULL,
    `max_salary` DECIMAL(12, 2) NULL,
    `currency` CHAR(3) DEFAULT 'INR',
    `salary_negotiable` BOOLEAN DEFAULT FALSE,
    `hide_salary` BOOLEAN DEFAULT FALSE,
    `salary_raw_text` VARCHAR(255) NULL, -- The raw extracted text
    
    -- Experience & Education
    `min_experience_years` TINYINT UNSIGNED DEFAULT 0,
    `max_experience_years` TINYINT UNSIGNED NULL,
    `min_qualification` VARCHAR(100) NULL,
    `preferred_qualification` VARCHAR(100) NULL,
    
    -- Job Description
    `description` LONGTEXT NULL,
    `responsibilities` TEXT NULL,
    `requirements` TEXT NULL,
    
    -- Hiring Details
    `vacancies` INT UNSIGNED NULL,
    `gender_preference` ENUM('Any', 'Male', 'Female') DEFAULT 'Any',
    `min_age` TINYINT UNSIGNED NULL,
    `max_age` TINYINT UNSIGNED NULL,
    
    -- Application Details
    `last_date` DATE NULL,
    `apply_method` ENUM('Website', 'Email', 'External Link', 'Physical Form') DEFAULT 'External Link',
    `apply_url` VARCHAR(1024) NULL,
    `recruiter_email` VARCHAR(255) NULL,
    `notification_number` VARCHAR(100) NULL,
    `notification_pdf_url` VARCHAR(1024) NULL,
    
    -- Status & Admin
    `job_status` ENUM('Draft', 'Pending', 'Approved', 'Rejected', 'Expired', 'Closed') DEFAULT 'Pending',
    `is_featured` BOOLEAN DEFAULT FALSE,
    `is_urgent` BOOLEAN DEFAULT FALSE,
    `featured_until` DATETIME NULL,
    
    -- Metrics
    `total_views` INT UNSIGNED DEFAULT 0,
    `total_applications` INT UNSIGNED DEFAULT 0,
    
    -- Timestamps
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_job_uuid` (`job_uuid`),
    CONSTRAINT `fk_job_source` FOREIGN KEY (`source_id`) REFERENCES `source_registry`(`id`) ON DELETE SET NULL,
    CONSTRAINT `fk_job_company` FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`) ON DELETE CASCADE,
    INDEX `idx_job_search` (`job_status`, `state`, `city`, `employment_type`),
    INDEX `idx_job_dates` (`created_at`, `last_date`),
    FULLTEXT KEY `ft_job_title_desc` (`title`, `description`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- JSON Extracted arrays (Many-to-Many logic handled via JSON for speed or link tables if strictly normalized)
-- For enterprise scale and flexible querying, we'll use linking tables.

CREATE TABLE `job_skills` (
    `job_id` BIGINT UNSIGNED NOT NULL,
    `skill_name` VARCHAR(100) NOT NULL,
    `is_required` BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (`job_id`, `skill_name`),
    CONSTRAINT `fk_js_job` FOREIGN KEY (`job_id`) REFERENCES `jobs`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `job_benefits` (
    `job_id` BIGINT UNSIGNED NOT NULL,
    `benefit_name` VARCHAR(100) NOT NULL,
    PRIMARY KEY (`job_id`, `benefit_name`),
    CONSTRAINT `fk_jb_job` FOREIGN KEY (`job_id`) REFERENCES `jobs`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
