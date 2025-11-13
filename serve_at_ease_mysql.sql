
-- =====================================================
-- Serve at Ease - MySQL Database Schema
-- Import this file in phpMyAdmin (XAMPP)
-- =====================================================

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- =====================================================
-- Database: serve_at_ease
-- =====================================================

CREATE DATABASE IF NOT EXISTS `serve_at_ease` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `serve_at_ease`;

-- =====================================================
-- Table: users
-- =====================================================

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `name` varchar(100) NOT NULL,
  `role` varchar(20) NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: plumbers
-- =====================================================

DROP TABLE IF EXISTS `plumbers`;
CREATE TABLE `plumbers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `specialty` varchar(200) DEFAULT NULL,
  `location` varchar(200) DEFAULT NULL,
  `hourly_rate` float DEFAULT NULL,
  `experience_years` int(11) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `available` tinyint(1) DEFAULT 1,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `plumbers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: bookings
-- =====================================================

DROP TABLE IF EXISTS `bookings`;
CREATE TABLE `bookings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_id` int(11) NOT NULL,
  `plumber_id` int(11) NOT NULL,
  `service_description` text NOT NULL,
  `scheduled_date` datetime NOT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `price` float DEFAULT NULL,
  `rating` int(11) DEFAULT NULL,
  `review` text DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `completed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  KEY `plumber_id` (`plumber_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`plumber_id`) REFERENCES `plumbers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: trust_scores
-- =====================================================

DROP TABLE IF EXISTS `trust_scores`;
CREATE TABLE `trust_scores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `plumber_id` int(11) DEFAULT NULL,
  `overall_score` float DEFAULT 50.0,
  `completion_rate` float DEFAULT 0.0,
  `review_authenticity` float DEFAULT 50.0,
  `response_time_score` float DEFAULT 50.0,
  `dispute_count` int(11) DEFAULT 0,
  `anomaly_score` float DEFAULT 0.0,
  `total_transactions` int(11) DEFAULT 0,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `plumber_id` (`plumber_id`),
  CONSTRAINT `trust_scores_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `trust_scores_ibfk_2` FOREIGN KEY (`plumber_id`) REFERENCES `plumbers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: fraud_alerts
-- =====================================================

DROP TABLE IF EXISTS `fraud_alerts`;
CREATE TABLE `fraud_alerts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `plumber_id` int(11) DEFAULT NULL,
  `booking_id` int(11) DEFAULT NULL,
  `alert_type` varchar(100) NOT NULL,
  `risk_score` float NOT NULL,
  `description` text DEFAULT NULL,
  `status` varchar(50) DEFAULT 'pending',
  `flagged_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `resolved_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `plumber_id` (`plumber_id`),
  KEY `booking_id` (`booking_id`),
  CONSTRAINT `fraud_alerts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fraud_alerts_ibfk_2` FOREIGN KEY (`plumber_id`) REFERENCES `plumbers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fraud_alerts_ibfk_3` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: local_model_updates
-- =====================================================

DROP TABLE IF EXISTS `local_model_updates`;
CREATE TABLE `local_model_updates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) DEFAULT NULL,
  `plumber_id` int(11) DEFAULT NULL,
  `model_version` int(11) NOT NULL,
  `update_data` text NOT NULL,
  `data_samples_count` int(11) DEFAULT 0,
  `submitted_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `aggregated` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `plumber_id` (`plumber_id`),
  CONSTRAINT `local_model_updates_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `local_model_updates_ibfk_2` FOREIGN KEY (`plumber_id`) REFERENCES `plumbers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Table: global_models
-- =====================================================

DROP TABLE IF EXISTS `global_models`;
CREATE TABLE `global_models` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `version` int(11) NOT NULL,
  `model_data` text NOT NULL,
  `accuracy` float DEFAULT NULL,
  `updates_aggregated` int(11) DEFAULT 0,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `version` (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- Sample Data Insertion
-- =====================================================

-- Insert Admin User
INSERT INTO `users` (`email`, `password_hash`, `name`, `role`) VALUES
('admin@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJxrzHB/C', 'Admin User', 'admin');

-- Insert Sample Customers
INSERT INTO `users` (`email`, `password_hash`, `name`, `role`) VALUES
('customer1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJxrzHB/C', 'Customer 1', 'customer'),
('customer2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJxrzHB/C', 'Customer 2', 'customer');

-- Insert Sample Plumber Users
INSERT INTO `users` (`email`, `password_hash`, `name`, `role`) VALUES
('plumber1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJxrzHB/C', 'John Smith', 'plumber'),
('plumber2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJxrzHB/C', 'Sarah Johnson', 'plumber');

-- Insert Plumber Profiles
INSERT INTO `plumbers` (`user_id`, `specialty`, `location`, `hourly_rate`, `experience_years`, `bio`, `available`) VALUES
(4, 'Residential Plumbing', 'Bengaluru North', 45, 8, 'Professional residential plumbing expert with 8 years of experience.', 1),
(5, 'Commercial Plumbing', 'Bengaluru South', 60, 12, 'Professional commercial plumbing expert with 12 years of experience.', 1);

-- Insert Trust Scores
INSERT INTO `trust_scores` (`user_id`, `overall_score`, `completion_rate`, `review_authenticity`, `response_time_score`, `dispute_count`, `anomaly_score`, `total_transactions`) VALUES
(2, 75.5, 85.0, 80.0, 70.0, 0, 10.0, 5),
(3, 82.3, 90.0, 85.0, 75.0, 1, 5.0, 8);

INSERT INTO `trust_scores` (`plumber_id`, `overall_score`, `completion_rate`, `review_authenticity`, `response_time_score`, `dispute_count`, `anomaly_score`, `total_transactions`) VALUES
(1, 88.5, 95.0, 90.0, 85.0, 0, 8.0, 25),
(2, 92.1, 98.0, 95.0, 88.0, 0, 5.0, 42);

-- Insert Global Model
INSERT INTO `global_models` (`version`, `model_data`, `accuracy`, `updates_aggregated`, `is_active`) VALUES
(1, '[0.1, -0.2, 0.3, -0.1, 0.4, -0.3, 0.2, -0.4, 0.1, 0.0]', 0.0, 0, 1);

COMMIT;

-- =====================================================
-- Password for all sample accounts: password123
-- Admin password: admin
-- =====================================================
