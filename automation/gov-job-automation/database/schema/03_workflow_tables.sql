-- ============================================================================
-- GOVERNMENT JOB AUTOMATION PLATFORM
-- PHASE 1: WORKFLOW & QUEUE TABLES
-- COMPATIBILITY: MySQL 8.4 LTS (InnoDB, utf8mb4)
-- ============================================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------------------------------------------------------
-- 1. QUEUE MANAGEMENT (If using DB as queue fallback to Redis)
-- ----------------------------------------------------------------------------
CREATE TABLE `crawl_queue` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `source_id` BIGINT UNSIGNED NOT NULL,
    `priority` ENUM('Low', 'Medium', 'High', 'Critical') NOT NULL DEFAULT 'Medium',
    `status` ENUM('Pending', 'Processing', 'Completed', 'Failed', 'Retrying') NOT NULL DEFAULT 'Pending',
    `attempts` TINYINT UNSIGNED DEFAULT 0,
    `max_attempts` TINYINT UNSIGNED DEFAULT 3,
    `worker_id` VARCHAR(100) NULL, -- ID of the worker processing this
    `next_retry_at` DATETIME NULL,
    `started_at` DATETIME NULL,
    `completed_at` DATETIME NULL,
    `error_log` TEXT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_cq_source` FOREIGN KEY (`source_id`) REFERENCES `source_registry`(`id`) ON DELETE CASCADE,
    INDEX `idx_cq_status` (`status`, `priority`, `next_retry_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 2. WORKER & CRAWLER REGISTRY
-- ----------------------------------------------------------------------------
CREATE TABLE `crawler_workers` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `worker_uuid` CHAR(36) NOT NULL,
    `node_name` VARCHAR(100) NOT NULL,
    `ip_address` VARCHAR(45) NOT NULL,
    `worker_type` ENUM('HTML', 'Playwright', 'PDF', 'OCR', 'LLM', 'Publisher') NOT NULL,
    `status` ENUM('Online', 'Busy', 'Offline', 'Dead') DEFAULT 'Online',
    `current_task_id` BIGINT UNSIGNED NULL,
    `last_heartbeat` DATETIME NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_worker_uuid` (`worker_uuid`),
    INDEX `idx_worker_status` (`status`, `last_heartbeat`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 3. N8N & WORKFLOW EXECUTION LOGS
-- ----------------------------------------------------------------------------
CREATE TABLE `workflow_execution_logs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `workflow_name` VARCHAR(255) NOT NULL,
    `execution_id` VARCHAR(255) NOT NULL,
    `node_name` VARCHAR(255) NOT NULL,
    `status` ENUM('Success', 'Failed', 'Running', 'Warning') NOT NULL,
    `execution_time_ms` INT UNSIGNED NULL,
    `input_data` JSON NULL,
    `output_data` JSON NULL,
    `error_message` TEXT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    INDEX `idx_wf_exec` (`workflow_name`, `status`),
    INDEX `idx_wf_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
